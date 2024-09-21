import time

import imagezmq
from vidgear.gears import VideoGear

from src.helpers.logger import get_logger

MAX_IMAGES = 1000


class StreamSender:
    logger = get_logger('StreamSender')

    def __init__(self, source_uri: str, port: int, sender_id: str):
        self._source_uri = source_uri
        self._port = port
        self._sender_id = sender_id
        self._stream = VideoGear(source=self._source_uri).start()
        self._sender = imagezmq.ImageSender(
            connect_to=f'tcp://*:{self._port}', REQ_REP=False
        )
        self.logger.info('Sender ready to transmit images')

        self._images_sent = 0

    def start(self):
        self.logger.info('Starting sending images...')
        time.sleep(
            15
        )  # Wait for the stream processors to start, used only for benchmarking

        try:
            while True:
                image = self._stream.read()

                if image is None:
                    self.logger.debug('Image is None')
                    break

                timestamp_start = time.time()
                self._sender.send_image(
                    f'{self._sender_id}___{timestamp_start}___{self._images_sent + 1}',
                    image,
                )
                self._images_sent += 1

                # Sends only a limited number of images
                if self._images_sent >= MAX_IMAGES:
                    break
        except (KeyboardInterrupt, SystemExit):
            self.logger.error('Exit due to interrupt')
        except Exception as error:
            self.logger.error('Error with no exception handler:', error)
        finally:
            self.stop()

    def stop(self):
        self._stream.stop()
        self._sender.close()
