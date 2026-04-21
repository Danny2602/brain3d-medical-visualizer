#Este filtro se encarga de aplicar el filtro de ecualización de histograma local a la imagen y el archivo tiene el nombre
#local_statistical.py : "ecualización de histograma local"
#Esto hace que la imagen tenga el contraste mejorado localmente 
# en base a la media y desviacion estandar de la vecindad de cada pixel
import cv2
import numpy as np
from processing.base import BaseFilter

class LocalStatisticalFilter(BaseFilter):
    """
    Mejoramiento local estadístico.
    Usa la media y desviación estándar de la "vecindad" de cada píxel para
    iluminar áreas oscuras sin sobreexponer las áreas ya brillantes.
    """
    
    def apply(self, img: np.ndarray, history: dict = None, kernel_size: int = 15, k_factor: float = 2.0, **kwargs) -> np.ndarray:
        """
        Args:
            kernel_size: El tamaño de la "vecindad" estadística a estudiar (Ej. 15x15 píxeles).
            k_factor: La fuerza o multiplicador de ganancia estadística.
        """
        # Convertimos la imagen a punto flotante (float32) para poder multiplicar
        # y dividir libremente sin que revienten los valores máximos de 255.
        img_float = img.astype(np.float32)

        # Calcular la MEDIA local (E[X]) usando un blur cuadrado rapidísimo
        local_mean = cv2.blur(img_float, (kernel_size, kernel_size))

        # Calcular la DESVIACIÓN ESTÁNDAR local de forma matricial
        # Matemáticamente: Varianza = E[X^2] - (E[X])^2
        img_squared = img_float ** 2
        local_mean_of_squared = cv2.blur(img_squared, (kernel_size, kernel_size))
        
        local_variance = local_mean_of_squared - (local_mean ** 2)
        
        # Evitamos raíces negativas por pequeñísimos errores de decimales en numpy
        local_std = np.sqrt(np.maximum(local_variance, 0))

        # Aplicar la Fórmula Central de Mejora Estadística Local:
        # g(x,y) = k * (f(x,y) - m(x,y)) / (sigma(x,y) + Epsilon) + m(x,y)
        # Epsilon (1.0) evita que el universo explote si la desviación estándar es 0
        epsilon = 1.0 
        
        # Matematica vectorial pura (esto toma microsegundos)
        amplification_matrix = k_factor * (img_float - local_mean) / (local_std + epsilon)
        enhanced_float = local_mean + amplification_matrix

        # Asegurarnos de que el resultado no tenga números por debajo de 0 o encima de 255
        enhanced_clipped = np.clip(enhanced_float, 0, 255)

        # Regresamos la imagen a su tipo original de 8 bits
        img_enhanced = enhanced_clipped.astype(np.uint8)
        return img_enhanced

