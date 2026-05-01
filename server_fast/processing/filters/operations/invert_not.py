# invert_not.py : "Filtro de Inversión (NOT)"
# Invierte los valores de la imagen (los negros se vuelven blancos y viceversa).    

import cv2
import numpy as np
from processing.base import BaseFilter

class InvertNotFilter(BaseFilter):
    """
    Invierte los valores de intensidad de la imagen (blanco a negro y viceversa).
    
    Es útil para resaltar áreas que antes eran muy oscuras o para "ver el negativo" de una máscara.
    """
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """
        Aplica la operación NOT a la imagen de entrada.
        
        Funcionamiento:
        1. Asegura que la imagen sea de 8 bits (uint8).
        2. Calcula la imagen invertida usando la fórmula: 255 - valor.
        
        Args:
            img (np.ndarray): Imagen de entrada (escala de grises o color).
            **kwargs: Parámetros adicionales ignorados.
            
        Returns:
            np.ndarray: Imagen con los valores invertidos.
        """
        # Asegurar que la imagen sea de 8 bits para la operación de inversión
        if img.dtype != np.uint8:
            img_processed = cv2.convertScaleAbs(img)
        else:
            img_processed = img.copy()
            
        # Aplicar la operación NOT (inversión de intensidad)
        # 255 - valor : Si el valor es 0 (negro), se convierte en 255 (blanco).
        # Si el valor es 255 (blanco), se convierte en 0 (negro).
        result = cv2.bitwise_not(img_processed)
        
        return result
