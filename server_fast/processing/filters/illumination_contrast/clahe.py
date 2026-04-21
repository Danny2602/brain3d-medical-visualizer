#Este filtro se encarga de aplicar el filtro de CLAHE a la imagen y el archivo tiene el nombre
#clahe.py : "filtro de CLAHE"
#Esto entregara una imagen con el filtro de CLAHE aplicado
#Que hace que la imagen sea mas nitida y con mejor contraste
import cv2
import numpy as np

from processing.base import BaseFilter

class CLAHEFilter(BaseFilter):
    def apply(self, img: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8, 8), **kwargs)->np.ndarray:
        """
        Aplica el filtro de CLAHE a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            clipLimit (float): Valor del límite de clip.
            tileGridSize (tuple): Tamaño de la cuadrícula.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de CLAHE aplicado.
        """
        clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
        img_filtered = clahe.apply(img)
        return img_filtered