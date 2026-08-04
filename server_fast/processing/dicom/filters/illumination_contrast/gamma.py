import numpy as np
from skimage.exposure import adjust_gamma
from processing.base import BaseFilter

def _smooth_blend(orig_normalized: np.ndarray, filtered_normalized: np.ndarray, transition_end: float = 0.08) -> np.ndarray:
    weight = np.clip(orig_normalized / max(transition_end, 1e-5), 0.0, 1.0)
    weight_smooth = weight * weight * (3.0 - 2.0 * weight)
    return (1.0 - weight_smooth) * orig_normalized + weight_smooth * filtered_normalized


class GammaFilter(BaseFilter):
    def apply(self, img: np.ndarray, gamma: float = 1.0, **kwargs) -> np.ndarray:
        if isinstance(gamma, str):
            gamma = float(gamma)
            
        min_val = float(np.min(img))
        max_val = float(np.max(img))
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        img_float = img.astype(np.float32)
        img_normalized = (img_float - min_val) / range_val
        
        img_gamma = adjust_gamma(img_normalized, gamma=gamma)
        blended = _smooth_blend(img_normalized, img_gamma)
        
        result = (blended * range_val) + min_val
        return result.astype(img.dtype)
