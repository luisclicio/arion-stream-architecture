import threading
from abc import ABC, abstractmethod

import imagezmq
import numpy as np

from src.helpers.logger import get_logger


class StreamReceiver:
    """
    Receive images from a sender.

    Implementation based on [PUB/SUB Multithreaded Fast Subscribers for Realtime Processing](https://github.com/jeffbass/imagezmq/blob/master/docs/fast-pub-sub.rst).
    """

    logger = get_logger('StreamReceiver')

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
        self.logger.info('Receiver ready to receive images')
        return self

    def receive(self, timeout=15.0) -> tuple[str, np.ndarray]:
        """
        Returns the most recent data (sender ID and image) received from the sender.
        """
        flag = self._data_ready.wait(timeout=timeout)

        if not flag:
            raise TimeoutError(
                f'Timeout while reading from sender tcp://{self._sender_uri}'
            )

        self._data_ready.clear()
        return self._data

    def _run(self):
        """
        Run the receiver in a separate thread to continuously receive data (sender ID and images) and make the most recent data (sender ID and image) available.
        """
        receiver = imagezmq.ImageHub(f'tcp://{self._sender_uri}', REQ_REP=False)

        while not self._stopped:
            sender_id, image = receiver.recv_image()

            if image is None:
                self.logger.fatal('Received empty image')
                break

            self._data = (sender_id, image)
            self._data_ready.set()

        receiver.close()

    def stop(self):
        """
        Stop the receiver.
        """
        self._stopped = True
        self.logger.info('Receiver stopped')


class StreamHandlerBase(ABC):
    """
    Handle the stream of images from a sender.
    """

    @abstractmethod
    def handle(self, sender_id: str, image: np.ndarray) -> np.ndarray | None:
        """
        Handle the image received from the sender.
        """
        pass


class StreamSender:
    logger = get_logger('StreamSender')

    def __init__(self, port: int, sender_id: str):
        self._port = port
        self._sender_id = sender_id
        self._sender = imagezmq.ImageSender(
            connect_to=f'tcp://*:{self._port}', REQ_REP=False
        )
        self.logger.info('Sender ready to transmit images')

    def send(self, image: np.ndarray | None):
        if image is None:
            self.logger.debug('Image is None')
            return

        self._sender.send_image(self._sender_id, image)

    def stop(self):
        self.logger.info('Stopping stream sender...')
        self._sender.close()


class StreamProcessorController:
    """
    Controller for the stream processor.
    """

    logger = get_logger('StreamProcessorController')

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
        self.logger.info('Starting stream processor controller...')

        try:
            while not self._stopped:
                sender_id, image = self._receiver.receive()

                if image is None:
                    break

                handled_image = self._handler.handle(sender_id, image)
                self._sender.send(handled_image)
        except TimeoutError as error:
            self.logger.error(error)
        finally:
            self._sender.stop()
            self._receiver.stop()
            self.logger.info('Stream processor controller stopped')

    def stop(self):
        """
        Stop the stream processor controller.
        """
        self.logger.info('Stopping stream processor controller...')
        self._stopped = True
