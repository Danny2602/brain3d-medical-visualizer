#Este filtro se encarga de aplicar el filtro de ecualización de histograma global a la imagen y el archivo tiene el nombre
#global_hist_eq.py : "ecualización de histograma global"
#Entrega una imagen que tiene el contraste mejorado globalmente
import cv2
import numpy as np
from processing.base import BaseFilter

class GlobalHistEqFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """
        Aplica el filtro de ecualización de histograma global a la imagen.
        """
        img_equalized = cv2.equalizeHist(img)
        return img_equalized