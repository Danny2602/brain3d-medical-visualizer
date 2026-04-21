#Este filtro se encarga de aplicar el filtro de componentes conectados a la imagen y el archivo tiene el nombre
#connect_comp.py : "filtro de componentes conectados"
#Este es la ultima etapa del pipeline de segmentacion

import cv2
import numpy as np

from processing.base import BaseFilter

class ConnectComponentsFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs)->np.ndarray:
        """
        Aplica el filtro de componentes conectados a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de componentes conectados aplicado.
        """
        #kernel con vecinos de 3x3
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        img_filtered = cv2.connectedComponentsWithStats(img, 4, cv2.CV_32S)



        return img_filtered