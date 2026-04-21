#Este filtro se encarga de aplicar el filtro de min-max a la imagen y el archivo tiene el nombre
#min_max.py : "filtro de min-max"
#Esto entregara una imagen con el filtro de min-max aplicado
#Este usa el histograma de la imagen para aplicar el filtro
import cv2
import numpy as np

from processing.base import BaseFilter

class MinMaxFilter(BaseFilter):
    def apply(self, img: np.ndarray, alpha: int = 0, beta: int = 255, **kwargs)->np.ndarray:
        """
        Aplica el filtro de min-max a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            alpha (int): Valor mínimo de la imagen.
            beta (int): Valor máximo de la imagen.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de min-max aplicado.
        """
        img_filtered = cv2.normalize(img, None, alpha=alpha, beta=beta, norm_type=cv2.NORM_MINMAX)
        return img_filtered