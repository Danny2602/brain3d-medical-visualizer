import numpy as np
from scipy.ndimage import gaussian_filter
from processing.base import BaseFilter

class GaussianFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 5, **kwargs) -> np.ndarray:
        """
        Aplica el filtro gaussiano en alta precisión usando scipy.
        
        Args:
            img (np.ndarray): Imagen DICOM de entrada.
            kernel_size (int): Tamaño del kernel (se aproxima a sigma).
            
        Returns:
            np.ndarray: Imagen filtrada.
        """
        # SciPy usa sigma en lugar de kernel_size. Aproximamos la conversión estándar de OpenCV:
        sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8 if kernel_size > 3 else 1.0
        
        filtered = gaussian_filter(img, sigma=sigma)
        return filtered.astype(img.dtype)