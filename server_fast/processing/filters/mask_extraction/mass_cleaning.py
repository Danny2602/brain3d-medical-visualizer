#Este filtro se encarga de limpiar la máscara de ruido
#mass_cleaning.py : "filtro de limpieza de masa"
#Este filtro se encarga de limpiar la máscara de ruido te entrega una imagen en blanco y negro con el tumor mas limpio
import cv2
import numpy as np
from processing.base import BaseFilter

class MassCleaningFilter(BaseFilter):
    """
    Filtro de Limpieza de Masa: Elimina objetos pequeños (ruido) en una máscara binaria 
    basándose en su área relativa.
    """
    def apply(self, img: np.ndarray, min_size_pct: float = 0.015, **kwargs) -> np.ndarray:
        if img.dtype != np.uint8:
            img = img.astype(np.uint8)
            
        # Análisis de componentes conectados
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(img, connectivity=8)
        
        if num_labels <= 1:
            return img

        h, w = img.shape
        min_size = int((h * w) * min_size_pct) 
        
        cleaned_mask = np.zeros_like(img)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_size:
                cleaned_mask[labels == i] = 255
                
        return cleaned_mask
