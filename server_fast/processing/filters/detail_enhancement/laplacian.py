#Este filtro se encarga de aplicar el filtro de laplaciano a la imagen y el archivo tiene el nombre
#laplacian.py : "filtro de laplaciano"
#Esto entregara una imagen con el filtro de laplaciano aplicado
#Es decir la imagen tendra los bordes mas definidos y con mejor contraste
import cv2
import numpy as np

from processing.base import BaseFilter

class LaplacianFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs)->np.ndarray:
        """
        Aplica el filtro de laplaciano a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de laplaciano aplicado.
        """
        img_filtered = cv2.Laplacian(img, cv2.CV_64F)
        return img_filtered