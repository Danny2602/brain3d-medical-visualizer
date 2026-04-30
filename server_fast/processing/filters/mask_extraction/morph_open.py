#Este filtro se encarga de aplicar el filtro de morph open a la imagen y el archivo tiene el nombre
#morph_open.py : "filtro de morph open"
#esto hace que se abran los pixeles que estan cerca entre si 
#y que se eliminen los pixeles que estan cerca del centro de la imagen
import cv2
import numpy as np

from processing.base import BaseFilter

class MorphOpenFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 3, **kwargs)->np.ndarray:
        """
        Aplica el filtro de morph open a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            kernel_size (int): Tamaño del kernel.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de morph open aplicado.
        """
        #kernel con vecinos de nxn
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        img_filtered = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)



        return img_filtered