import numpy as np
from scipy.ndimage import grey_dilation, grey_erosion
from processing.base import BaseFilter

class MorphGradientFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 3, **kwargs) -> np.ndarray:
        """
        Gradiente Morfológico (Dilatación - Erosión). Útil para resaltar bordes.
        """
        if isinstance(kernel_size, str): kernel_size = int(kernel_size)
        
        structure = np.ones((kernel_size, kernel_size))
        dilated = grey_dilation(img, footprint=structure)
        eroded = grey_erosion(img, footprint=structure)
        
        gradient = dilated - eroded
        return gradient.astype(img.dtype)
