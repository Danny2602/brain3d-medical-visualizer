#Este filtro se encarga de aplicar el filtro de unsharp mask a la imagen y el archivo tiene el nombre
#unsharp_mask.py : "filtro de unsharp mask"
#Esto entregara una imagen con el filtro de unsharp mask aplicado

import cv2
import numpy as np

from processing.base import BaseFilter

class UnsharpMaskFilter(BaseFilter):
    def apply(self, img: np.ndarray, sigma: float = 1.0, **kwargs)->np.ndarray:
        """
        Aplica el filtro de unsharp mask a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            sigma (float): Valor de la desviación estándar del filtro.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de unsharp mask aplicado.
        """
        img_filtered = cv2.addWeighted(img, 1.5, cv2.GaussianBlur(img, (0, 0), sigma), -0.5, 0)
        return img_filtered