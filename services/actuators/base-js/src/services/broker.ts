import { env } from '../env.js';
import { BrokerClient } from '../libs/broker.js';

export const brokerClient = new BrokerClient({
  brokerConnectOptions: {
    uri: env.BROKER_RABBITMQ_CONNECTION_URI,
  },
});
