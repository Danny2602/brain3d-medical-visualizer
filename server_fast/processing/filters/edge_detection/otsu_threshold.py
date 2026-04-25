#Este filtro se encarga de aplicar el umbral de Otsu a la imagen y el archivo tiene el nombre
#otsu_threshold.py : "filtro de umbralización de Otsu"
#Esto entregara una imagen con el umbral de Otsu aplicado
import cv2
import numpy as np
from skimage.filters import thresholding
from processing.base import BaseFilter

class OtsuThresholdFilter(BaseFilter):
    def apply(self, img: np.ndarray,classes:int=3, **kwargs)->np.ndarray:
        """
        Aplica el filtro de umbralización de Otsu.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el umbral de Otsu aplicado.
        """
        # Blindaje: Otsu SOLO acepta CV_8UC1 (uint8 escala de grises)
        if img.dtype != np.uint8:
            img = cv2.convertScaleAbs(img)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
        # thresholds = thresholding.threshold_multiotsu(img, classes=classes)
        # regions=np.digitize(img,bins=thresholds)
        # mask = np.zeros_like(img)
        # mask[regions == (classes - 1)] = 255
        # return mask