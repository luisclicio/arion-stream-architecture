import numpy as np

from src.helpers.logger import get_logger
from src.libs.stream import StreamHandlerBase
from src.services.vision import vision_model


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

        prediction, processed_image = vision_model.predict(image)

        if prediction['people_detected']:
            self.logger.info(
                f'PEOPLE DETECTED: Count: {prediction["people_count"]} - Precision: {prediction["precision"]:.2%}'
            )

            # Can save the processed image to a file, send it to another service, etc.
