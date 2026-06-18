import numpy as np
from scipy.ndimage import label
from skimage.measure import regionprops
from processing.base import BaseFilter

class MassCleaningFilter(BaseFilter):
    def apply(self, img: np.ndarray, min_area: int = 100, **kwargs) -> np.ndarray:
        """
        Elimina manchas pequeñas de las máscaras (ruido sal y pimienta a nivel macro).
        Funciona nativamente en DICOM buscando componentes conectados.
        """
        if isinstance(min_area, str): min_area = int(min_area)
        
        min_val = np.min(img)
        max_val = np.max(img)
        
        # Binarizar temporalmente para detectar regiones
        threshold = (max_val + min_val) / 2
        binary = img > threshold
        
        labeled_array, num_features = label(binary)
        
        cleaned_mask = np.zeros_like(binary)
        for region in regionprops(labeled_array):
            if region.area >= min_area:
                cleaned_mask[labeled_array == region.label] = True
                
        # Mapear de vuelta a los valores físicos del scanner
        result = np.where(cleaned_mask, max_val, min_val)
        return result.astype(img.dtype)
