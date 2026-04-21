#Este filtro se encarga de aplicar el umbral de Otsu a la imagen y el archivo tiene el nombre
#otsu_threshold.py : "filtro de umbralización de Otsu"
#Esto entregara una imagen con el umbral de Otsu aplicado
import cv2
import numpy as np

from processing.base import BaseFilter

class OtsuThresholdFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs)->np.ndarray:
        """
        Aplica el filtro de umbralización de Otsu.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el umbral de Otsu aplicado.
        """
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh