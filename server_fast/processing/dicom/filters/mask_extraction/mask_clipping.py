import numpy as np
from processing.base import BaseFilter

class MaskClippingFilter(BaseFilter):
    def apply(self, img: np.ndarray, mask_id: str = None, history: dict = None, **kwargs) -> np.ndarray:
        """
        Usa una máscara precalculada (layer_b u otro nodo del historial) 
        para recortar la imagen original o capa principal (layer_a).
        Soporta valores DICOM y Unidades Hounsfield.
        """
        # Si layer_b fue inyectado dinámicamente como mask_id o parámetro en kwargs
        target_mask_id = kwargs.get('layer_b', mask_id)
        
        if not history or target_mask_id not in history:
            return img.copy()
            
        mask = history[target_mask_id]
        
        if mask.shape != img.shape:
            return img.copy()
            
        min_mask = np.min(mask)
        max_mask = np.max(mask)
        
        # Consideramos la máscara "activa" donde sus valores están por encima de la mitad
        threshold = (max_mask + min_mask) / 2
        binary_mask = mask > threshold
        
        # Recortar: mantener valor original de img donde la máscara es True
        min_img = np.min(img)
        result = np.where(binary_mask, img, min_img)
        
        return result.astype(img.dtype)
