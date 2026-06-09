# Este filtro usa topografía para separar manchas blancas que se tocan.
# watershed.py : "Algoritmo de Segmentación Watershed (Cuencas)"
# Ideal para cuando dos tumores o el tumor y el cráneo se están tocando apenas en la máscara binaria.

import cv2
import numpy as np
from processing.base import BaseFilter

class WatershedFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """
        Segmentación Watershed (Cuencas Hidrográficas).
        
        Funcionamiento:
        Imagina que la imagen binaria es un mapa topográfico. El algoritmo encuentra el "centro"
        absoluto de cada mancha blanca y luego empieza a "inundar" desde esos centros.
        Cuando dos inundaciones chocan (ej. un tumor y otro objeto que estaban pegados),
        dibuja una línea de separación perfecta entre ellos.
        
        Args:
            img (np.ndarray): Imagen de entrada (debe ser una máscara binaria proveniente de Otsu o similar).
            
        Returns:
            np.ndarray: La máscara separando los objetos que antes estaban unidos.
        """
        # Asegurarse de tener una imagen en blanco y negro (máscara binaria)
        if img.dtype != np.uint8:
            img = cv2.convertScaleAbs(img)
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
            
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Quitar ruido pequeño
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        # Determinar el área de "fondo seguro"
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # Determinar el área de "frente seguro" (centros de los objetos) usando Transformada de Distancia
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)

        # Encontrar la región desconocida (bordes en disputa)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # Etiquetar los marcadores
        _, markers = cv2.connectedComponents(sure_fg)

        # Sumar 1 a todos los marcadores para que el fondo sea 1 en lugar de 0
        markers = markers + 1

        # Marcar la región desconocida con 0
        markers[unknown == 255] = 0

        # Para aplicar watershed, necesitamos una imagen de 3 canales (aunque sea gris)
        img_color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Aplicar el algoritmo Watershed
        markers = cv2.watershed(img_color, markers)
        
        # Watershed pone los límites (fronteras) con el valor -1
        # Vamos a crear una máscara limpia donde el fondo es negro y los objetos son grises distintos
        result_mask = np.zeros_like(gray)
        
        # Pintamos todo lo que Watershed determinó como objeto (valores mayores a 1)
        result_mask[markers > 1] = 255
        
        # Opcional: dibujar las líneas divisorias en negro para asegurar la separación
        result_mask[markers == -1] = 0

        return result_mask
