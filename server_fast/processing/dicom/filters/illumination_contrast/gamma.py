import numpy as np
from skimage.exposure import adjust_gamma
from processing.base import BaseFilter

class GammaFilter(BaseFilter):
    def apply(self, img: np.ndarray, gamma: float = 1.0, **kwargs) -> np.ndarray:
        """
        Aplica corrección gamma preservando la escala física de DICOM.
        """
        if isinstance(gamma, str):
            gamma = float(gamma)
            
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        img_normalized = (img - min_val) / range_val
        
        img_gamma = adjust_gamma(img_normalized, gamma=gamma)
        
        result = (img_gamma * range_val) + min_val
        return result.astype(img.dtype)
