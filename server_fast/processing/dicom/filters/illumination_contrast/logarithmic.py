import numpy as np
from skimage.exposure import adjust_log
from processing.base import BaseFilter

class LogarithmicFilter(BaseFilter):
    def apply(self, img: np.ndarray, gain: float = 1.0, **kwargs) -> np.ndarray:
        """
        Aplica transformación logarítmica preservando el tipo de dato físico.
        """
        if isinstance(gain, str):
            gain = float(gain)
            
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        img_normalized = (img - min_val) / range_val
        
        img_log = adjust_log(img_normalized, gain=gain)
        
        result = (img_log * range_val) + min_val
        return result.astype(img.dtype)
