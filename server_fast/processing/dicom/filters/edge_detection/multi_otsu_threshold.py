import numpy as np
from skimage.filters import threshold_multiotsu
from processing.base import BaseFilter

class MultiOtsuThresholdFilter(BaseFilter):
    def apply(self, img: np.ndarray, classes: int = 3, **kwargs) -> np.ndarray:
        """
        Umbralización Multi-Otsu para múltiples clases anatómicas.
        """
        if isinstance(classes, str):
            classes = int(classes)
            
        min_val = np.min(img)
        max_val = np.max(img)
        
        if min_val == max_val or classes <= 1:
            return img.copy()
            
        # Calcular múltiples umbrales (devuelve classes-1 umbrales)
        try:
            thresholds = threshold_multiotsu(img, classes=classes)
            regions = np.digitize(img, bins=thresholds)
        except Exception:
            # Fallback en caso de que la imagen sea muy uniforme
            return img.copy()
        
        # Mapear las clases encontradas equitativamente en el rango físico [min_val, max_val]
        mapped = (regions / (classes - 1)) * (max_val - min_val) + min_val
        return mapped.astype(img.dtype)