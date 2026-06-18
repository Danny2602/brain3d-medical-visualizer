import numpy as np
from skimage.feature import canny
from processing.base import BaseFilter

class CannyEdgesFilter(BaseFilter):
    def apply(self, img: np.ndarray, sigma: float = 1.0, low_threshold: float = 0.1, high_threshold: float = 0.2, **kwargs) -> np.ndarray:
        """
        Detección de bordes Canny para imágenes médicas.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return np.zeros_like(img)
            
        img_normalized = (img - min_val) / range_val
        
        # Adaptación para parámetros antiguos que venían en escala 0-255
        if low_threshold > 1.0: low_threshold = low_threshold / 255.0
        if high_threshold > 1.0: high_threshold = high_threshold / 255.0
            
        edges = canny(img_normalized, sigma=sigma, low_threshold=low_threshold, high_threshold=high_threshold)
        
        # Generar máscara binaria respetando las escalas de HU (min y max)
        result = np.where(edges, max_val, min_val)
        return result.astype(img.dtype)