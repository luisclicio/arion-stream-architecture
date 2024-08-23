import imagezmq
from vidgear.gears import VideoGear

from src.helpers.logger import get_logger


class StreamSender:
    logger = get_logger('StreamSender')

    def __init__(self, source_uri: str, port: int, sender_id: str):
        self._source_uri = source_uri
        self._port = port
        self._sender_id = sender_id
        self._stream = VideoGear(source=self._source_uri).start()
        self._sender = imagezmq.ImageSender(connect_to=f'tcp://*:{5000}', REQ_REP=False)
        self.logger.info('Sender ready to transmit images')

    def start(self):
        self.logger.info('Starting sending images...')

        try:
            while True:
                image = self._stream.read()

                if image is None:
                    self.logger.debug('Image is None')
                    break

                self._sender.send_image(self._sender_id, image)
        except (KeyboardInterrupt, SystemExit):
            self.logger.error('Exit due to interrupt')
        except Exception as error:
            self.logger.error('Error with no exception handler:', error)
        finally:
            self.stop()

    def stop(self):
        self._stream.stop()
        self._sender.close()
