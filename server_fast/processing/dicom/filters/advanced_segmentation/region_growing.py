import numpy as np
from skimage.segmentation import flood
from processing.base import BaseFilter

class RegionGrowingFilter(BaseFilter):
    def apply(self, img: np.ndarray, seed_x: int = 0, seed_y: int = 0, tolerance: float = 0.05, **kwargs) -> np.ndarray:
        """
        Crecimiento de regiones (Flood fill) a partir de una semilla.
        """
        if isinstance(seed_x, str): seed_x = int(seed_x)
        if isinstance(seed_y, str): seed_y = int(seed_y)
        if isinstance(tolerance, str): tolerance = float(tolerance)
            
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        # Si la tolerancia es menor a 1, se asume que es un porcentaje del rango
        if tolerance <= 1.0:
            tolerance_val = tolerance * range_val
        else:
            tolerance_val = tolerance
            
        # scikit-image usa (row, col) -> (y, x)
        seed_point = (seed_y, seed_x)
        
        h, w = img.shape
        if seed_y < 0 or seed_y >= h or seed_x < 0 or seed_x >= w:
            seed_point = (h // 2, w // 2)
            
        mask = flood(img, seed_point=seed_point, tolerance=tolerance_val)
        
        result = np.where(mask, max_val, min_val)
        return result.astype(img.dtype)
