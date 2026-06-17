#Este filtro se encarga de reducir el ruido de la imagen y el archivo tiene el nombre
#bilateral.py : "filtro bilateral"
#Entregara una imagen mas suave pero preservando los bordes 
import numpy as np
from skimage.restoration import _denoise
from processing.base import BaseFilter

class BilateralFilter(BaseFilter):
    def apply(self, img: np.ndarray, diameter: int = 9, sigma_color: float = 0.05, sigma_space: float = 5.0, **kwargs) -> np.ndarray:        
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
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy() # Evitar división por cero
            
        img_normalized = (img - min_val) / range_val

        denoised= _denoise.denoise_bilateral(
            img_normalized,
            diameter=diameter,
            sigma_color=sigma_color,
            sigma_space=sigma_space,
            channel_axis=None
        )
        
        result=(denoised*range_val)+min_val

        return result.astype(img.dtype)