import numpy as np
from skimage.exposure import equalize_hist
from processing.base import BaseFilter

class GlobalHistEqFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """
        Aplica ecualización de histograma global sobre la imagen de alta precisión.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        img_normalized = (img - min_val) / range_val
        
        img_eq = equalize_hist(img_normalized)
        
        result = (img_eq * range_val) + min_val
        return result.astype(img.dtype)