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
    def apply(self, img: np.ndarray, min_size_pct: float = 0.015, keep_largest_only: bool = True, **kwargs) -> np.ndarray:
        if img.dtype != np.uint8:
            img = img.astype(np.uint8)
            
        # Análisis de componentes conectados (encuentra todas las "islas" blancas)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(img, connectivity=8)
        
        if num_labels <= 1:
            return img

        cleaned_mask = np.zeros_like(img)
        
        # --- NUEVA LÓGICA: Mantener solo el objeto más grande ---
        if keep_largest_only and num_labels > 1:
            # stats[:, cv2.CC_STAT_AREA] tiene las áreas. El índice 0 es el fondo negro, lo ignoramos.
            areas = stats[1:, cv2.CC_STAT_AREA]
            largest_label = np.argmax(areas) + 1 # +1 porque ignoramos el fondo (0)
            
            # Pintamos de blanco SOLO la isla más grande (ej. el cerebro o la mano)
            cleaned_mask[labels == largest_label] = 255
            
        # --- LÓGICA ANTERIOR: Borrar por porcentaje de tamaño ---
        else:
            h, w = img.shape
            min_size = int((h * w) * min_size_pct) 
            
            for i in range(1, num_labels):
                if stats[i, cv2.CC_STAT_AREA] >= min_size:
                    cleaned_mask[labels == i] = 255
                    
        return cleaned_mask
