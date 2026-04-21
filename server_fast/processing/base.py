from abc import ABC, abstractmethod

import numpy as np

class BaseFilter(ABC):
    @abstractmethod
    def apply(self, img: np.ndarray, **kwargs):
        pass