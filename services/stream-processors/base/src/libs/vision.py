import random
import time
from abc import ABC, abstractmethod

import numpy as np


class VisionModelBase(ABC):
    """
    Base class for vision models.
    """

    @abstractmethod
    def predict(self, image) -> tuple[dict, np.ndarray]:
        """
        Process the image and return the prediction result (e.g. class, bounding box, precision, processed image, etc.).
        """
        pass


class VisionModel(VisionModelBase):
    """
    Vision model that simulates people detection.
    """

    # It's possible to implement any internal states, configurations and methods to make robust predictions.

    def predict(self, image: np.ndarray) -> tuple[dict, np.ndarray]:
        """
        Predict the class of the image.
        """
        time.sleep(
            random.uniform(0.1, 0.25)
        )  # Simulate processing time between 100ms and 250ms

        precision = random.uniform(0.1, 0.99)  # Simulate prediction precision
        # people_detected = precision >= 0.8  # Simulate people detection
        people_detected = True  # Force people detection for testing purposes
        people_count = (
            random.randint(1, 5) if people_detected else 0
        )  # Simulate people count

        prediction = {
            "precision": precision,
            "people_detected": people_detected,
            "people_count": people_count,
        }
        processed_image = image  # Simulate image transforming

        return prediction, processed_image
