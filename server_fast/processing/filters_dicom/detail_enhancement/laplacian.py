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
        # cv2.CV_64F para no perder negativos en la derivada, luego regresamos a uint8
        laplacian_raw = cv2.Laplacian(img, cv2.CV_64F, ksize=3)
        laplacian_abs = cv2.convertScaleAbs(laplacian_raw)

        # Mezcla suave: 90% imagen, 10% detalle laplaciano (igual que views2.py)
        img_uint8 = img if img.dtype == np.uint8 else cv2.convertScaleAbs(img)
        img_filtered = cv2.addWeighted(img_uint8, 0.90, laplacian_abs, 0.10, 0)
        return img_filtered