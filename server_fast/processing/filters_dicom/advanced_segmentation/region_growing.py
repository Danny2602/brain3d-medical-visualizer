# Este filtro segmenta un tumor a partir de un punto inicial (semilla).
# region_growing.py : "Filtro de Crecimiento de Regiones (Flood Fill)"
# Requiere las coordenadas X e Y del tumor y una tolerancia de intensidad.


"""
hacer pruebas para mirar bien la imagen en react y tomar coordenadas 

"""
import cv2
import numpy as np
from processing.base import BaseFilter

class RegionGrowingFilter(BaseFilter):
    def apply(self, img: np.ndarray, seed_x: int = 128, seed_y: int = 128, tolerance: int = 10, **kwargs) -> np.ndarray:
        """
        Segmentación por Crecimiento de Regiones.
        
        Funcionamiento:
        Toma una coordenada inicial (semilla) que debe estar DENTRO del tumor.
        Luego, el algoritmo se expande hacia los píxeles vecinos. Si un píxel vecino
        tiene un brillo similar al píxel semilla (dentro del margen de 'tolerance'),
        lo incluye en el tumor y sigue expandiéndose. Se detiene al chocar con colores diferentes.
        
        Args:
            img (np.ndarray): Imagen de entrada (escala de grises).
            seed_x (int): Coordenada X del punto inicial dentro del tumor.
            seed_y (int): Coordenada Y del punto inicial dentro del tumor.
            tolerance (int): Diferencia de brillo permitida. Si es 10, aceptará píxeles +/- 10 tonos de gris respecto a la semilla.
            
        Returns:
            np.ndarray: Máscara binaria mostrando solo la región que creció desde la semilla.
        """
        if img.dtype != np.uint8:
            img = cv2.convertScaleAbs(img)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
        h, w = img.shape
        
        # Validación básica de coordenadas para no salir de rango
        if seed_x < 0 or seed_x >= w or seed_y < 0 or seed_y >= h:
            return np.zeros_like(img)

        # La función floodFill necesita una máscara que sea 2 píxeles más ancha y alta
        mask = np.zeros((h + 2, w + 2), np.uint8)

        # Imagen base que floodFill va a modificar (necesita ser a color o gris 8bit)
        flooded_img = img.copy()

        # Rellenar desde la semilla (seed_x, seed_y) con el color 255.
        # loDiff = límite inferior de tolerancia, upDiff = límite superior.
        # flags= 4 (conectividad) | (255 << 8) (color de llenado) | cv2.FLOODFILL_MASK_ONLY (solo pintar la máscara)
        flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY
        
        cv2.floodFill(
            image=flooded_img, 
            mask=mask, 
            seedPoint=(seed_x, seed_y), 
            newVal=255, 
            loDiff=(tolerance,), 
            upDiff=(tolerance,), 
            flags=flags
        )

        # La máscara resultante es 2 píxeles más grande, la recortamos a su tamaño original
        final_mask = mask[1:-1, 1:-1]
        
        return final_mask
