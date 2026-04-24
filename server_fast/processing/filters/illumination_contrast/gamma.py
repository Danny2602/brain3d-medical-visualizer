import numpy as np
from processing.base import BaseFilter

class GammaFilter(BaseFilter):
    """
    Aplica la transformada de gamma a la imagen.
    """
    def apply(self, img: np.ndarray, factor: float = 1.2, **kwargs) -> np.ndarray:
        img_float = img.astype(np.float32) / 255.0
        transformed = np.power(img_float, factor)
        return (transformed * 255).astype(np.uint8)
