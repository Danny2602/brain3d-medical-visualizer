import numpy as np
from skimage.filters import threshold_otsu
from processing.base import BaseFilter

class OtsuThresholdFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """
        Binarización de Otsu directamente sobre valores físicos DICOM (HU).
        """
        min_val = np.min(img)
        max_val = np.max(img)
        
        if min_val == max_val:
            return img.copy()
            
        # Calcula el umbral en unidades reales (HU, etc)
        thresh = threshold_otsu(img)
        binary = img > thresh
        
        # Convertir a máscara en rango visible
        result = np.where(binary, max_val, min_val)
        return result.astype(img.dtype)