import datetime
import json

import numpy as np
import pika
from pika.adapters.blocking_connection import BlockingChannel
from src.helpers.logger import get_logger
from src.libs.stream import StreamHandlerBase
from src.services.broker import BROKER_EXCHANGE_NAME
from src.services.vision import vision_model


class StreamHandler(StreamHandlerBase):
    """
    Handle the stream of images from a sender.
    """

    logger = get_logger("StreamHandler")
    _channel: BlockingChannel = None

    def __init__(self, broker_connection: pika.BlockingConnection):
        self._broker_connection = broker_connection
        self._setup_broker_channel()

    def _setup_broker_channel(self):
        """
        Setup the broker channel.
        """
        if self._broker_connection.is_closed:
            self.logger.error("Broker connection is closed")
            raise Exception("Broker connection is closed")

        self._channel = self._broker_connection.channel()

        self._channel.exchange_declare(
            exchange=BROKER_EXCHANGE_NAME,
            exchange_type="topic",
            durable=True,
            auto_delete=False,
        )

    def publish_data_to_broker(self, routing_key: str, data: dict):
        """
        Publish data to the broker.
        """
        self.logger.debug(f"Publishing data to broker with routing key: {routing_key}")

        self._channel.basic_publish(
            exchange=BROKER_EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )

    def build_routing_key(self, sender_id: str):
        """
        Build the routing key.
        """
        return f"arion.processors.analyses.people_detector.{sender_id}"

    def handle(self, data: dict, image: np.ndarray):
        """
        Handle the image received from the sender.
        """
        # Process the image
        sender_id = data["sender_id"]
        self.logger.debug(f"Received image from sender: {sender_id}")

        prediction, processed_image = vision_model.predict(image)

        if prediction["people_detected"]:
            self.logger.debug(
                f"PEOPLE DETECTED: Count: {prediction['people_count']} - Precision: {prediction['precision']:.2%}"
            )

            # Can save the processed image to a file, send it to another service, etc.

            # Publish the data to the broker
            routing_key = self.build_routing_key(sender_id)

            self.publish_data_to_broker(
                routing_key=routing_key,
                data={
                    "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                    "deviceId": sender_id,
                    "model": {
                        "name": "people_detector",
                    },
                    "data": {
                        "peopleDetected": prediction["people_detected"],
                        "peopleCount": prediction["people_count"],
                        "precision": prediction["precision"],
                    },
                    "benchmark": data["benchmark"],
                },
            )

            return processed_image

        return None
