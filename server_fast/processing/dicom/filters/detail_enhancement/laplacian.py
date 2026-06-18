import numpy as np
from scipy.ndimage import laplace
from processing.base import BaseFilter

class LaplacianFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """ Detecta bordes rápidos (Segunda derivada de la imagen). """
        img_float = img.astype(np.float64)
        
        edges = laplace(img_float)
        
        min_val = np.min(edges)
        max_val = np.max(edges)
        if min_val == max_val:
            return img.copy()
            
        orig_min = np.min(img)
        orig_max = np.max(img)
        
        # Mapeamos el gradiente al rango original para que se visualice correctamente
        normalized = (edges - min_val) / (max_val - min_val)
        result = normalized * (orig_max - orig_min) + orig_min
        
        return result.astype(img.dtype)