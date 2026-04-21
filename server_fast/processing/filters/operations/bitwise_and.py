#Este filtro se encarga de aplicar el filtro de componentes conectados a la imagen y el archivo tiene el nombre
#bitwise_and.py : "operaciones bit a bit"
#Entregara una imagen que es el resultado de la operacion logica AND entre la imagen actual y la imagen del filtro seleccionado
import cv2
import numpy as np
from processing.base import BaseFilter

class LogicAndFilter(BaseFilter):
    """
    Simula el arrastable de fusionar 2 capas.
    """
    def apply(self, img: np.ndarray, history: dict = None, target_layer_name: str = "", **kwargs) -> np.ndarray:
        # img = La imagen de este instante
        # target_layer_name = El nombre del otro filtro pasado con el que queremos fusionar
        
        if history and target_layer_name in history:
            imagen_del_pasado = history[target_layer_name]
            # Hacemos el AND lógico que tenías en views2.py
            return cv2.bitwise_and(img, imagen_del_pasado)
        else:
            print("Error: No se encontró la capa del pasado para fusionar.")
            return img