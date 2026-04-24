#Este filtro se encarga de aplicar el filtro de morph connect a la imagen y el archivo tiene el nombre
#morph_connect.py : "filtro de morph connect"
#esto hace que se conecten los pixeles que estan cerca entre si
import cv2
import numpy as np

from processing.base import BaseFilter

class MorphConnectFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 3, **kwargs)->np.ndarray:
        """
        Aplica el filtro de morph connect a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de morph connect aplicado.
        """
        #kernel con vecinos de nxn
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        img_filtered = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)



        return img_filtered