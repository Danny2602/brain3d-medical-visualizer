#Este filtro se encarga de reducir el ruido de la imagen y el archivo tiene el nombre
#nl_means.py : "filtro de reducción de ruido no local"
#Entrega una imagen mas suave pero preservando los bordes casi igual 
#que el filtro bilateral pero con la diferencia de que este filtro es mas rapido
import cv2
import numpy as np
from processing.base import BaseFilter

class NlMeansFilter(BaseFilter):
    def apply(self, img: np.ndarray, h_value: int = 10, **kwargs):
        """
        Aplica el filtro de reducción de ruido no local.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            h_value (int): Valor de la fuerza del filtro.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen filtrada.
        """
        denoised = cv2.fastNlMeansDenoising(img, None, h=h_value, templateWindowSize=7, searchWindowSize=21)
        return denoised