#Este filtro se encarga de reducir el ruido de la imagen y el archivo tiene el nombre
#bilateral.py : "filtro bilateral"
#Entregara una imagen mas suave pero preservando los bordes 
import cv2
import numpy as np

from processing.base import BaseFilter

class BilateralFilter(BaseFilter):
    def apply(self, img: np.ndarray, diameter: int = 5, sigma_color: int = 50, sigma_space: int = 50, **kwargs)->np.ndarray:
        """
        Aplica el filtro gaussiano.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            diameter (int): Diámetro de la vecindad del píxel.
            sigma_color (int): Desviación estándar en el espacio de color.
            sigma_space (int): Desviación estándar en el espacio de coordenadas.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen filtrada.
        """
        denoised = cv2.bilateralFilter(img, diameter, sigma_color, sigma_space)
        return denoised