import numpy as np
from processing.base import BaseFilter

class InvertNotFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """ 
        Inversión fotográfica (NOT).
        Mapea el valor físico respetando la escala.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        
        # Inversion in physical space: new_val = max_val - (val - min_val)
        inverted = max_val - (img - min_val)
        return inverted.astype(img.dtype)
