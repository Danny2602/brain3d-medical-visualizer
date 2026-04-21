#Este filtro se encarga de detectar los bordes de la imagen y el archivo tiene el nombre
#canny_filter.py : "filtro de detección de bordes canny"

import cv2
import numpy as np

from processing.base import BaseFilter

class CannyEdgesFilter(BaseFilter):
    def apply(self, img: np.ndarray, low_threshold: int = 50, high_threshold: int = 150, **kwargs)->np.ndarray:
        """
        Aplica el filtro de detección de bordes Canny.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            low_threshold (int): Umbral bajo para la detección de bordes.
            high_threshold (int): Umbral alto para la detección de bordes.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con los bordes detectados.
        """
        edges = cv2.Canny(img, low_threshold, high_threshold)
        return edges