import numpy as np
from scipy.ndimage import white_tophat
from processing.base import BaseFilter

class TopHatMorfFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 5, **kwargs) -> np.ndarray:
        """ 
        Realza objetos brillantes más pequeños que el elemento estructurante.
        Excelente para detectar calcificaciones o vasos sanguíneos en fondo oscuro.
        """
        if isinstance(kernel_size, str): kernel_size = int(kernel_size)
            
        structure = np.ones((kernel_size, kernel_size))
        
        # white_tophat maneja flotantes matemáticamente 
        tophat = white_tophat(img, footprint=structure)
        
        return tophat.astype(img.dtype)