import numpy as np
from scipy.ndimage import binary_fill_holes
from processing.base import BaseFilter

class RegionFillFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """ 
        Rellena los agujeros oscuros dentro de las estructuras anatómicas.
        Ej: Rellenar ventrículos tras detectar el cerebro entero.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        
        threshold = (max_val + min_val) / 2
        binary = img > threshold
        
        # Operación morfológica avanzada ultra rápida
        filled = binary_fill_holes(binary)
        
        result = np.where(filled, max_val, min_val)
        return result.astype(img.dtype)
