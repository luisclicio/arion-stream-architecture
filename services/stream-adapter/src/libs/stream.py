import json
import os
from time import sleep

import imagezmq
import simplejpeg
from src.helpers.logger import get_logger
from src.services.benchmark import benchmark_data_saver
from src.services.clock import Clock
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
        self.logger.info("Delaying start for 15 seconds...")
        sleep(15)

        self.logger.info("Starting sending images...")

        while True:
            image = self._stream.get_frame()

            if self._image_id >= 1000:
                # Sleep after 1000 images to grant time for the benchmark to finish
                self.logger.debug("Sleeping after 1000 images...")
                sleep(60 * 10)  # 10 minutes

            if image is None:
                # self.logger.debug("Image is None")
                # break
                continue

            self._image_id += 1
            sending_image_timestamp = Clock.now()
            benchmark_data = {
                "adapter": {
                    "service_name": os.getenv("SERVICE_NAME"),
                    "image_id": self._image_id,
                    "sending_image_timestamp": sending_image_timestamp.isoformat(),
                },
            }
            self._sender.send_jpg(
                json.dumps(
                    {
                        "sender_id": self._sender_id,
                        "image_id": self._image_id,
                        "benchmark": benchmark_data,
                    }
                ),
                simplejpeg.encode_jpeg(image, quality=90, colorspace="BGR"),
            )

            benchmark_data["adapter"]["sending_image_timestamp"] = (
                sending_image_timestamp
            )
            data_to_save = {
                "metadata": {
                    "timestamp": Clock.now(),
                    "service_type": os.getenv("SERVICE_TYPE", "stream-adapter"),
                    "stack_id": os.getenv("STACK_ID"),
                },
                **benchmark_data,
            }
            benchmark_data_saver.save(data_to_save)

            # Send 10 images per second
            sleep(1 / 10)

    def stop(self):
        self.logger.info("Stopping stream sender...")
        self._sender.close()
