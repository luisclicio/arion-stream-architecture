import amqp, { type Connection, type Channel } from 'amqplib';

import { logger } from '../services/logger.js';

export type BrokerClientOptions = {
  uri: string;
};

export type BrokerClientProps = {
  brokerConnectOptions: BrokerClientOptions;
};

export class BrokerClient {
  private logger = logger.child({ from: BrokerClient.name });

  private connection!: Connection;
  private channel!: Channel;
  private connected = false;
  private brokerConnectOptions: BrokerClientOptions;

  constructor({ brokerConnectOptions }: BrokerClientProps) {
    this.brokerConnectOptions = brokerConnectOptions;
  }

  async connect() {
    if (this.connected && this.channel) {
      return;
    }

    try {
      this.logger.debug('Connecting to broker...');

      this.connection = await amqp.connect(this.brokerConnectOptions.uri);
      this.connected = true;

      this.logger.debug('Broker connection is ready');

      this.channel = await this.connection.createChannel();

      this.logger.debug('Created broker channel successfully');
    } catch (error) {
      this.logger.fatal(error, 'Failed to connect to broker');
      throw error;
    }
  }

  async close() {
    if (!this.connected) {
      return;
    }

    try {
      this.logger.debug('Disconnecting from broker...');

      await this.channel.close();
      await this.connection.close();

      this.connected = false;

      this.logger.debug('Broker connection is closed');
    } catch (error) {
      this.logger.fatal(error, 'Failed to disconnect from broker');
      throw error;
    }
  }

  async setupChannel<T = void>(
    callback: (channel: Channel) => Promise<T>,
  ): Promise<T> {
    try {
      if (!this.channel) {
        await this.connect();
      }

      const result = await callback(this.channel);

      this.logger.debug('Broker channel is setup');

      return result;
    } catch (error) {
      this.logger.error(error, 'Failed to setup broker channel');
      throw error;
    }
  }

  async publishToExchange<T>(exchange: string, routingKey: string, data: T) {
    try {
      if (!this.channel) {
        await this.connect();
      }

      this.channel.publish(
        exchange,
        routingKey,
        Buffer.from(JSON.stringify(data)),
      );

      this.logger.debug(`Published message to exchange: ${exchange}`);
    } catch (error) {
      this.logger.error(
        error,
        `Failed to publish message to exchange: ${exchange}`,
      );
      throw error;
    }
  }

  async consumeFromQueue<T>(
    queue: string,
    handler: ({ data }: { data: T }) => Promise<{ canAcknowledge: boolean }>,
  ) {
    try {
      if (!this.channel) {
        await this.connect();
      }

      this.channel.consume(
        queue,
        async (message) => {
          if (!message) {
            return;
          }

          this.logger.debug(`Received message from queue: ${queue}`);

          try {
            const data = JSON.parse(message.content.toString());
            const { canAcknowledge } = await handler({ data });

            if (canAcknowledge) {
              this.channel.ack(message);
            } else {
              this.channel.nack(message);
            }
          } catch (error) {
            this.logger.error(
              error,
              `Failed to handle message from queue: ${queue}`,
            );
            this.channel.nack(message);
          }
        },
        { noAck: false }, // Disable auto-acknowledgement
      );
    } catch (error) {
      this.logger.error(
        error,
        `Failed to consume messages from queue: ${queue}`,
      );
      throw error;
    }
  }
}
