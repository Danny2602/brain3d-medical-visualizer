#Este filtro se encarga de aplicar el filtro de componentes conectados a la imagen y el archivo tiene el nombre
#bitwise_or.py : "operaciones bit a bit"
#Entregara una imagen que es el resultado de la operacion logica OR entre la imagen actual y la imagen del filtro seleccionado
import cv2
import numpy as np
from processing.base import BaseFilter

class LogicOrFilter(BaseFilter):
    """
    Simula el arrastable de fusionar 2 capas.
    """
    def apply(self, img: np.ndarray, history: dict = None, layer_a: str = "", layer_b: str = "", **kwargs) -> np.ndarray:
        if not history:
            print("Error: No hay historial disponible para fusionar.")
            return img
            
        if not layer_a or not layer_b:
            print("Error: Se requiere especificar layer_a y layer_b en los parámetros (params) para Operadores Lógicos.")
            return img
            
        if layer_a not in history or layer_b not in history:
            print(f"Error: Una de las capas no fue encontrada en el historial ({layer_a} o {layer_b}).")
            return img
            
        img_a = history[layer_a]
        img_b = history[layer_b]
                
        return cv2.bitwise_or(img_a, img_b)
