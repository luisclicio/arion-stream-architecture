import threading

import imagezmq
import numpy as np

from src.helpers.logger import get_logger


class StreamReceiver:
    logger = get_logger('StreamReceiver')

    def __init__(self, sender_uri: str):
        self._sender_uri = sender_uri
        self._stopped = False
        self._data = (None, None)
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True

    def start(self):
        self._thread.start()
        self.logger.info('Receiver ready to receive images')
        return self

    def receive(self, timeout=15.0) -> tuple[str, np.ndarray]:
        flag = self._data_ready.wait(timeout=timeout)

        if not flag:
            raise TimeoutError(
                f'Timeout while reading from sender tcp://{self._sender_uri}'
            )

        self._data_ready.clear()
        return self._data

    def _run(self):
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
        self._stopped = True
        self.logger.info('Receiver stopped')
