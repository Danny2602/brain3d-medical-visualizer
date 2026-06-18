import numpy as np
from scipy.ndimage import uniform_filter
from processing.base import BaseFilter

class LocalStatisticalFilter(BaseFilter):
    """
    Mejoramiento local estadístico en alta precisión.
    Usa la media y desviación estándar de la vecindad de cada píxel para
    iluminar áreas oscuras sin sobreexponer las áreas ya brillantes.
    """
    
    def apply(self, img: np.ndarray, kernel_size: int = 15, k_factor: float = 2.0, **kwargs) -> np.ndarray:
        # Usamos float64 para máxima precisión en el cálculo de varianzas
        img_float = img.astype(np.float64)

        # Calcular MEDIA y VARIANZA local usando uniform_filter de scipy (rapidísimo en N-Dimensiones)
        local_mean = uniform_filter(img_float, size=kernel_size)
        local_mean_of_squared = uniform_filter(img_float ** 2, size=kernel_size)
        
        local_variance = local_mean_of_squared - (local_mean ** 2)
        
        # Evitamos raíces negativas
        local_std = np.sqrt(np.maximum(local_variance, 0))

        # Epsilon (1.0) evita que el universo explote si la desviación estándar es 0
        epsilon = 1.0 
        
        # Matematica vectorial pura
        amplification_matrix = k_factor * (img_float - local_mean) / (local_std + epsilon)
        enhanced_float = local_mean + amplification_matrix

        # Asegurarnos de que el resultado respete los límites físicos originales (HU)
        min_val = np.min(img)
        max_val = np.max(img)
        enhanced_clipped = np.clip(enhanced_float, min_val, max_val)

        return enhanced_clipped.astype(img.dtype)
