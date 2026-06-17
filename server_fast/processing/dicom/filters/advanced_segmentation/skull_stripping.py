# Este filtro se encarga de aislar la masa del cerebro y eliminar el cráneo, ojos y grasa.
# skull_stripping.py : "Filtro de extracción cerebral (Skull Stripping)"
# Útil como primer paso para que los filtros posteriores solo busquen tumores dentro del cerebro.

import cv2
import numpy as np
from processing.base import BaseFilter

class SkullStrippingFilter(BaseFilter):
    def apply(self, img: np.ndarray, erosion_iters: int = 5, dilation_iters: int = 5, **kwargs) -> np.ndarray:
        """
        Extrae el cerebro eliminando el cráneo (Skull Stripping básico).
        
        Funcionamiento:
        1. Binariza la imagen para obtener la silueta general de la cabeza.
        2. Aplica una fuerte erosión para romper los puentes finos entre el cerebro y el cráneo/ojos.
        3. Encuentra la masa continua más grande (que será el cerebro).
        4. Aplica una dilatación para devolver el cerebro a su tamaño original.
        5. Usa esa máscara para recortar la imagen original.
        
        Args:
            img (np.ndarray): Imagen de entrada (escala de grises).
            erosion_iters (int): Cuántas veces encoger la máscara para romper conexiones.
            dilation_iters (int): Cuántas veces expandir la máscara al final para recuperar el tamaño.
            
        Returns:
            np.ndarray: La imagen original pero solo mostrando el cerebro (el resto en negro).
        """
        # Asegurar formato correcto
        if img.dtype != np.uint8:
            img = cv2.convertScaleAbs(img)
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # 1. Binarización general (para obtener toda la cabeza)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 2. Erosión agresiva para separar el cerebro del cráneo/ojos
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        eroded = cv2.erode(thresh, kernel, iterations=erosion_iters)

        # 3. Mantener solo el objeto más grande (el cerebro)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(eroded, connectivity=8)
        if num_labels <= 1:
            return img # Fallback si algo sale mal
            
        # Ignorar el fondo (índice 0) y buscar el mayor
        areas = stats[1:, cv2.CC_STAT_AREA]
        largest_label = np.argmax(areas) + 1
        
        brain_mask = np.zeros_like(eroded)
        brain_mask[labels == largest_label] = 255

        # 4. Dilatación para restaurar el tamaño original del cerebro
        brain_mask = cv2.dilate(brain_mask, kernel, iterations=dilation_iters)

        # 5. Aplicar la máscara a la imagen original (Opcional, podrías devolver solo la máscara si prefieres)
        # Aquí devolvemos la imagen original recortada (en grises)
        result = cv2.bitwise_and(gray, gray, mask=brain_mask)
        
        return result
