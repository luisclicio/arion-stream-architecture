import csv
import os
import threading
import time
from abc import ABC, abstractmethod

import imagezmq
import numpy as np

from src.helpers.logger import get_logger

PROCESSORS_N = 3

PROCESSOR_LABEL = os.getenv('PROCESSOR_LABEL')

evaluation_t1_csv_file_path = f'/benchmarks/stream-processors/evaluation_t1_{PROCESSORS_N}p_p{PROCESSOR_LABEL}_{int(time.time() * 1000)}.csv'
evaluation_t1_fieldnames = [
    'image_id',
    'time_diff_ms',
    'timestamp_start',
    'timestamp_end',
]

os.makedirs(os.path.dirname(evaluation_t1_csv_file_path), exist_ok=True)


with open(evaluation_t1_csv_file_path, mode='w') as evaluation_t1_file:
    evaluation_t1_writer = csv.DictWriter(
        evaluation_t1_file, fieldnames=evaluation_t1_fieldnames
    )
    evaluation_t1_writer.writeheader()


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

        self._images_received = 0

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
            sender_data, image = receiver.recv_image()
            timestamp_end = time.time()

            if image is None:
                self.logger.fatal('Received empty image')
                break

            self._images_received += 1

            sender_id, timestamp_start, image_id = sender_data.split('___')
            timestamp_start = float(timestamp_start)
            time_diff_ms = (timestamp_end - timestamp_start) * 1000

            with open(evaluation_t1_csv_file_path, mode='a') as evaluation_t1_file:
                evaluation_t1_writer = csv.DictWriter(
                    evaluation_t1_file, fieldnames=evaluation_t1_fieldnames
                )
                evaluation_t1_writer.writerow(
                    {
                        'image_id': image_id,
                        'time_diff_ms': time_diff_ms,
                        'timestamp_start': timestamp_start,
                        'timestamp_end': timestamp_end,
                    }
                )

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
    def handle(self, sender_id: str, image: np.ndarray):
        """
        Handle the image received from the sender.
        """
        pass


class StreamReceiverController:
    """
    Controller for the stream receiver.
    """

    logger = get_logger('StreamReceiverController')

    def __init__(self, receiver: StreamReceiver, handler: StreamHandlerBase):
        self._receiver = receiver
        self._handler = handler
        self._stopped = False

    def start(self):
        """
        Start the stream receiver controller.
        """
        self.logger.info('Starting stream receiver controller...')

        try:
            while not self._stopped:
                sender_id, image = self._receiver.receive()

                if image is None:
                    break

                self._handler.handle(sender_id, image)
        except TimeoutError as error:
            self.logger.error(error)
        finally:
            self._receiver.stop()
            self.logger.info('Stream receiver controller stopped')

    def stop(self):
        """
        Stop the stream receiver controller.
        """
        self.logger.info('Stopping stream receiver controller...')
        self._stopped = True
