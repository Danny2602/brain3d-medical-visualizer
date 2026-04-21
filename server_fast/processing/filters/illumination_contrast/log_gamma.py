#Este filtro se encarga de aplicar el filtro de logaritmo y gamma a la imagen y el archivo tiene el nombre
#log_gamma.py : "filtro de logaritmo y gamma"
#Esto entregara una imagen con el filtro de logaritmo o gamma dependiendo del parametro mode
import cv2
import numpy as np

from processing.base import BaseFilter

class LogGammaFilter(BaseFilter):
    def apply(self, img: np.ndarray, mode: str = "gamma", factor: float = 1.2, **kwargs)->np.ndarray:
        """
        Aplica el filtro de logaritmo y gamma.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de logaritmo y gamma aplicado.
        """
        # Convertimos la imagen de [0 a 255] a rango flotante [0.0 a 1.0] 
        # para que las matemáticas exponenciales no den errores de desbordamiento.
        img_float = img.astype(np.float32) / 255.0

        if mode == "log":
            # TRANSFORMACIÓN LOGARÍTMICA: s = c * log(1 + r)
            # Expande drásticamente las zonas negras revelando detalles ocultos en las sombras.
            c = 1.0 / np.log(1.0 + np.max(img_float))
            transformed = c * np.log(1.0 + img_float)

        elif mode == "gamma" or mode == "exp":
            # TRANSFORMACIÓN EXPONENCIAL (Gamma): s = c * r^gamma
            # factor > 1: Efecto "apagar la luz", oscurece todo excepto lo más brillante.
            # factor < 1: Actúa parecido al logaritmo, aclarando la imagen.
            transformed = np.power(img_float, factor)

        else:
            transformed = img_float

        # Regresamos la imagen a escala OpenCV (0 a 255 en uint8)
        img_filtered= (transformed * 255).astype(np.uint8)
        return img_filtered