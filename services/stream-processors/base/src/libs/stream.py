import json
import os
import threading
from abc import ABC, abstractmethod
from datetime import datetime

import imagezmq
import numpy as np
from src.helpers.logger import get_logger
from src.services.benchmark import benchmark_data_saver


class StreamReceiver:
    """
    Receive images from a sender.

    Implementation based on [PUB/SUB Multithreaded Fast Subscribers for Realtime Processing](https://github.com/jeffbass/imagezmq/blob/master/docs/fast-pub-sub.rst).
    """

    logger = get_logger("StreamReceiver")

    def __init__(self, sender_uri: str):
        self._sender_uri = sender_uri
        self._stopped = False
        self._data = (None, None)
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True

    def start(self):
        """
        Start the receiver thread.
        """
        self._thread.start()
        self.logger.info("Receiver ready to receive images")
        return self

    def receive(self, timeout=15.0) -> tuple[dict, np.ndarray]:
        """
        Returns the most recent data (sender ID and image) received from the sender.
        """
        flag = self._data_ready.wait(timeout=timeout)

        if not flag:
            raise TimeoutError(
                f"Timeout while reading from sender tcp://{self._sender_uri}"
            )

        self._data_ready.clear()
        return self._data

    def _run(self):
        """
        Run the receiver in a separate thread to continuously receive data (sender ID and images) and make the most recent data (sender ID and image) available.
        """
        receiver = imagezmq.ImageHub(f"tcp://{self._sender_uri}", REQ_REP=False)

        while not self._stopped:
            raw_data, image = receiver.recv_image()

            if image is None:
                self.logger.fatal("Received empty image")
                break

            data = json.loads(raw_data)
            self._data = (data, image)
            self._data_ready.set()

        receiver.close()

    def stop(self):
        """
        Stop the receiver.
        """
        self._stopped = True
        self.logger.info("Receiver stopped")


class StreamHandlerBase(ABC):
    """
    Handle the stream of images from a sender.
    """

    @abstractmethod
    def handle(self, data: dict, image: np.ndarray) -> np.ndarray | None:
        """
        Handle the image received from the sender.
        """
        pass


class StreamSender:
    logger = get_logger("StreamSender")

    def __init__(self, port: int, sender_id: str):
        self._port = port
        self._sender_id = sender_id
        self._sender = imagezmq.ImageSender(
            connect_to=f"tcp://*:{self._port}", REQ_REP=False
        )
        self.logger.info("Sender ready to transmit images")

    def send(self, image: np.ndarray | None):
        if image is None:
            self.logger.debug("Image is None")
            return

        self._sender.send_image(self._sender_id, image)

    def stop(self):
        self.logger.info("Stopping stream sender...")
        self._sender.close()


class StreamProcessorController:
    """
    Controller for the stream processor.
    """

    logger = get_logger("StreamProcessorController")

    def __init__(
        self, receiver: StreamReceiver, handler: StreamHandlerBase, sender: StreamSender
    ):
        self._receiver = receiver
        self._handler = handler
        self._sender = sender
        self._stopped = False

    def start(self):
        """
        Start the stream processor controller.
        """
        self.logger.info("Starting stream processor controller...")

        try:
            while not self._stopped:
                data, image = self._receiver.receive(
                    timeout=60 * 10
                )  # Timeout for benchmark
                received_image_timestamp = datetime.now()
                received_image_latency = (
                    received_image_timestamp
                    - datetime.fromisoformat(
                        data["benchmark"]["adapter"]["sending_image_timestamp"]
                    )
                ).total_seconds() * 1000  # ms

                if image is None:
                    break

                sending_data_timestamp = datetime.now()
                benchmark_data = {
                    **data["benchmark"],
                    "processor": {
                        "service_name": os.getenv("SERVICE_NAME"),
                        "received_image_timestamp": received_image_timestamp.isoformat(),
                        "received_image_latency": received_image_latency,
                        "sending_data_timestamp": sending_data_timestamp.isoformat(),
                    },
                }

                handled_image = self._handler.handle(
                    {**data, "benchmark": benchmark_data}, image
                )
                self._sender.send(handled_image)

                benchmark_data["adapter"]["sending_image_timestamp"] = (
                    datetime.fromisoformat(
                        data["benchmark"]["adapter"]["sending_image_timestamp"]
                    )
                )
                benchmark_data["processor"]["received_image_timestamp"] = (
                    received_image_timestamp
                )
                benchmark_data["processor"]["sending_data_timestamp"] = (
                    sending_data_timestamp
                )
                data_to_save = {
                    "metadata": {
                        "timestamp": datetime.now(),
                        "service_type": os.getenv("SERVICE_TYPE", "stream-processor"),
                        "stack_id": os.getenv("STACK_ID"),
                    },
                    **benchmark_data,
                }
                benchmark_data_saver.save(data_to_save)
        except TimeoutError as error:
            self.logger.error(error)
        finally:
            self._sender.stop()
            self._receiver.stop()
            self.logger.info("Stream processor controller stopped")

    def stop(self):
        """
        Stop the stream processor controller.
        """
        self.logger.info("Stopping stream processor controller...")
        self._stopped = True
