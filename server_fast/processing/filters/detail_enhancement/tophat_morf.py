#Este filtro se encarga de aplicar el filtro de tophat morf a la imagen y el archivo tiene el nombre
#tophat_morf.py : "filtro de tophat morf"
#Esto entregara una imagen con el filtro de tophat morf aplicado
#Morfologia matematica de contraste que resalta las partes brillantes de la imagen
import cv2
import numpy as np

from processing.base import BaseFilter

class TopHatMorfFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 3, **kwargs)->np.ndarray:
        """
        Aplica el filtro de tophat morf a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            kernel_size (int): Tamaño del kernel.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de tophat morf aplicado.
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        img_filtered = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)
        return img_filtered