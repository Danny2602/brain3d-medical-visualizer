import numpy as np
from skimage.filters import unsharp_mask
from processing.base import BaseFilter

class UnsharpMaskFilter(BaseFilter):
    def apply(self, img: np.ndarray, radius: float = 1.0, amount: float = 1.0, **kwargs) -> np.ndarray:
        """
        Enfoque clásico restando una versión desenfocada a la original.
        """
        if isinstance(radius, str): radius = float(radius)
        if isinstance(amount, str): amount = float(amount)
            
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        img_normalized = (img - min_val) / range_val
        
        enhanced = unsharp_mask(img_normalized, radius=radius, amount=amount)
        enhanced = np.clip(enhanced, 0.0, 1.0)
        
        result = (enhanced * range_val) + min_val
        return result.astype(img.dtype)