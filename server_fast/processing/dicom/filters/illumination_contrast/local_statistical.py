import numpy as np
from scipy.ndimage import uniform_filter
from processing.base import BaseFilter

def _smooth_blend(orig_normalized: np.ndarray, filtered_normalized: np.ndarray, transition_end: float = 0.08) -> np.ndarray:
    weight = np.clip(orig_normalized / max(transition_end, 1e-5), 0.0, 1.0)
    weight_smooth = weight * weight * (3.0 - 2.0 * weight)
    return (1.0 - weight_smooth) * orig_normalized + weight_smooth * filtered_normalized


class LocalStatisticalFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 15, k_factor: float = 2.0, **kwargs) -> np.ndarray:
        img_float = img.astype(np.float64)
        min_val = np.min(img_float)
        max_val = np.max(img_float)
        range_val = max_val - min_val

        if range_val == 0:
            return img.copy()

        img_norm = (img_float - min_val) / range_val

        local_mean = uniform_filter(img_float, size=kernel_size)
        local_mean_of_squared = uniform_filter(img_float ** 2, size=kernel_size)
        local_variance = local_mean_of_squared - (local_mean ** 2)
        local_std = np.sqrt(np.maximum(local_variance, 0))

        epsilon = 1.0 
        amplification_matrix = k_factor * (img_float - local_mean) / (local_std + epsilon)
        enhanced_float = local_mean + amplification_matrix
        enhanced_clipped = np.clip(enhanced_float, min_val, max_val)
        enhanced_norm = (enhanced_clipped - min_val) / range_val

        blended = _smooth_blend(img_norm, enhanced_norm)

        result = (blended * range_val) + min_val
        return result.astype(img.dtype)
