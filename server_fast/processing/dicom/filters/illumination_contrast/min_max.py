import numpy as np
from processing.base import BaseFilter

class MinMaxFilter(BaseFilter):
    def apply(self, img: np.ndarray, alpha: float = 0.0, beta: float = 1.0, **kwargs)->np.ndarray:
        """
        Aplica el filtro de min-max a la imagen. Estira el contraste al rango deseado.
        
        Args:
            img (np.ndarray): Imagen DICOM de entrada.
            alpha (float): Límite inferior físico al que estirar.
            beta (float): Límite superior físico al que estirar.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        
        if min_val == max_val:
            return img.copy()
            
        # Normalizar a 0-1
        normalized = (img.astype(np.float32) - min_val) / (max_val - min_val)
        
        # Estirar al nuevo rango [alpha, beta]
        stretched = normalized * (beta - alpha) + alpha
        
        return stretched.astype(img.dtype)