import numpy as np
from skimage.exposure import equalize_adapthist
from processing.base import BaseFilter

class CLAHEFilter(BaseFilter):
    def apply(self, img: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8, 8), **kwargs) -> np.ndarray:
        """
        Aplica el filtro de CLAHE (Contrast Limited Adaptive Histogram Equalization) en alta precisión.
        """
        if isinstance(clipLimit, str):
            clipLimit = float(clipLimit)
        if isinstance(tileGridSize, str):
            tileGridSize = tuple(map(int, tileGridSize.split(',')))
            
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        # scikit-image requiere rangos normalizados [0, 1] para ecualización
        img_normalized = (img - min_val) / range_val
        
        # En skimage, clipLimit va de 0 a 1. Adaptamos el parámetro clásico de OpenCV (ej. 2.0).
        skimage_clip_limit = min(max(clipLimit / 255.0, 0.0), 1.0) if clipLimit > 1 else clipLimit
        
        img_clahe = equalize_adapthist(img_normalized, kernel_size=tileGridSize, clip_limit=skimage_clip_limit)
        
        # Restaurar al rango de intensidad física (HU) original
        result = (img_clahe * range_val) + min_val
        return result.astype(img.dtype)