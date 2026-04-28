#Este filtro se encarga de aplicar el filtro de CLAHE a la imagen y el archivo tiene el nombre
#clahe.py : "filtro de CLAHE"
#Esto entregara una imagen con el filtro de CLAHE aplicado
#Que hace que la imagen sea mas nitida y con mejor contraste
import cv2
import numpy as np

from processing.base import BaseFilter

class CLAHEFilter(BaseFilter):
    def apply(self, img: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8, 8), **kwargs)->np.ndarray:
        """
        Aplica el filtro de CLAHE a la imagen.
        
        Args:
            img (np.ndarray): Imagen de entrada.
            clipLimit (float): Valor del límite de clip.
            tileGridSize (tuple): Tamaño de la cuadrícula.
            **kwargs: Argumentos adicionales.
            
        Returns:
            np.ndarray: Imagen con el filtro de CLAHE aplicado.
        """
        if isinstance(clipLimit, str):
            clipLimit = float(clipLimit)
        if isinstance(tileGridSize, str):
            tileGridSize = tuple(map(int, tileGridSize.split(',')))
        
        # 1. CLAHE requiere que la imagen sea de 8 bits (uint8)
        if img.dtype != np.uint8:
            if img.dtype in [np.float32, np.float64]:
                img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
            else:
                img = img.astype(np.uint8)
                
        clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
        
        # 2. Si la imagen es a color (3 canales), aplicar solo al canal L (Luminancia)
        # para no arruinar o alterar los verdaderos colores anatómicos.
        if len(img.shape) == 3 and img.shape[2] == 3:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_clahe = clahe.apply(l)
            merged = cv2.merge((l_clahe, a, b))
            img_filtered = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        else:
            img_filtered = clahe.apply(img)
            
        return img_filtered