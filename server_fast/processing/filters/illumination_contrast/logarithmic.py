
import numpy as np
from processing.base import BaseFilter

class LogarithmicFilter(BaseFilter):
    """
    Aplica la transformada logarítmica a la imagen.
    """
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        img_float = img.astype(np.float32) / 255.0
        c = 1.0 / np.log(1.0 + np.max(img_float))
        transformed = c * np.log(1.0 + img_float)
        return (transformed * 255).astype(np.uint8)
