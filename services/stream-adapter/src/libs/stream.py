import imagezmq
from vidgear.gears import VideoGear

from src.helpers.logger import get_logger


class Stream:
    logger = get_logger('Stream')

    def __init__(self, source_uri: str):
        self._source_uri = source_uri
        self._stream = VideoGear(source=self._source_uri)

    def get_frame(self):
        return self._stream.read()

    def start(self):
        self.logger.info('Starting stream...')
        self._stream.start()
        return self

    def stop(self):
        self.logger.info('Stopping stream...')
        self._stream.stop()


class StreamSender:
    logger = get_logger('StreamSender')

    def __init__(self, stream: Stream, port: int, sender_id: str):
        self._port = port
        self._sender_id = sender_id
        self._stream = stream
        self._sender = imagezmq.ImageSender(
            connect_to=f'tcp://*:{self._port}', REQ_REP=False
        )
        self.logger.info('Sender ready to transmit images')

    def start(self):
        self.logger.info('Starting sending images...')

        while True:
            image = self._stream.get_frame()

            if image is None:
                self.logger.debug('Image is None')
                break

            self._sender.send_image(self._sender_id, image)

    def stop(self):
        self.logger.info('Stopping stream sender...')
        self._sender.close()
