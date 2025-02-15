import json
import os
from datetime import datetime

import imagezmq
from src.helpers.logger import get_logger
from src.services.benchmark import benchmark_data_saver
from vidgear.gears import VideoGear


class Stream:
    logger = get_logger("Stream")

    def __init__(self, source_uri: str):
        self._source_uri = source_uri
        self._stream = VideoGear(source=self._source_uri)

    def get_frame(self):
        return self._stream.read()

    def start(self):
        self.logger.info("Starting stream...")
        self._stream.start()
        return self

    def stop(self):
        self.logger.info("Stopping stream...")
        self._stream.stop()


class StreamSender:
    logger = get_logger("StreamSender")

    def __init__(self, stream: Stream, port: int, sender_id: str):
        self._port = port
        self._sender_id = sender_id
        self._stream = stream
        self._sender = imagezmq.ImageSender(
            connect_to=f"tcp://*:{self._port}", REQ_REP=False
        )
        self._image_id = 0
        self.logger.info("Sender ready to transmit images")

    def start(self):
        self.logger.info("Starting sending images...")

        while True:
            image = self._stream.get_frame()

            if image is None:
                self.logger.debug("Image is None")
                break

            self._image_id += 1
            sending_image_timestamp = datetime.now()
            benchmark_data = {
                "adapter": {
                    "service_name": os.getenv("SERVICE_NAME"),
                    "image_id": self._image_id,
                    "sending_image_timestamp": sending_image_timestamp.isoformat(),
                },
            }
            self._sender.send_image(
                json.dumps(
                    {
                        "sender_id": self._sender_id,
                        "image_id": self._image_id,
                        "benchmark": benchmark_data,
                    }
                ),
                image,
            )

            data_to_save = {
                "metadata": {
                    "timestamp": datetime.now(),
                    "service_type": os.getenv("SERVICE_TYPE", "stream-adapter"),
                    "stack_id": os.getenv("STACK_ID"),
                },
                **benchmark_data,
            }
            benchmark_data_saver.save(data_to_save)

    def stop(self):
        self.logger.info("Stopping stream sender...")
        self._sender.close()
