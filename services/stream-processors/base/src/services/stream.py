import time

import numpy as np

from src.helpers.logger import get_logger
from src.libs.stream import StreamHandlerBase


class StreamHandler(StreamHandlerBase):
    """
    Handle the stream of images from a sender.
    """

    logger = get_logger('StreamHandler')

    def handle(self, sender_id: str, image: np.ndarray):
        """
        Handle the image received from the sender.
        """
        # Process the image
        self.logger.debug(f'Received image from sender: {sender_id}')
        time.sleep(0.05)  # Simulate processing time
