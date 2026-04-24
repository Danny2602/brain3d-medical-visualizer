import cv2
import numpy as np
from processing.base import BaseFilter

class MaskClippingFilter(BaseFilter):
    """
    Filtro de Recorte: Aplica una máscara binaria sobre una imagen original 
    para extraer la región de interés con su textura médica real.
    """
    def apply(self, img: np.ndarray, history: dict = None, original_layer: str = "original", **kwargs) -> np.ndarray:
        if not history or original_layer not in history:
            return img # Failsafe
            
        foto_original = history[original_layer]
        
        # Asegurarnos de que la máscara sea uint8
        mask = img.astype(np.uint8) if img.dtype != np.uint8 else img
        
        # Aplicar el recorte
        return cv2.bitwise_and(foto_original, foto_original, mask=mask)
