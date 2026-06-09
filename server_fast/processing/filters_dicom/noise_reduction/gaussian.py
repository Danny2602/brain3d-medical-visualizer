#Este filtro se encarga de reducir el ruido de la imagen y el archivo tiene el nombre
#gaussian.py : "filtro gaussiano"
#Esto entregara una imagen mas suave
import cv2
import numpy as np

from processing.base import BaseFilter

class GaussianFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 5, **kwargs)->np.ndarray:
        """
        Aplica el filtro gaussiano.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            kernel_size (int): Tamaño del kernel.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen filtrada.
        """
        filtered = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        return filtered