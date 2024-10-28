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
        self._sender = imagezmq.ImageSender(
            connect_to=f'tcp://*:{self._port}', REQ_REP=False
        )
        self.logger.info('Sender ready to transmit images')

    def start(self):
        self.logger.info('Starting sending images...')

        while True:
            image = self._stream.read()

            if image is None:
                self.logger.debug('Image is None')
                break

            self._sender.send_image(self._sender_id, image)

    def stop(self):
        self.logger.info('Stopping stream sender...')
        self._stream.stop()
        self._sender.close()
