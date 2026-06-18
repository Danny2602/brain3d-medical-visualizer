import numpy as np
from scipy.ndimage import binary_opening, grey_opening
from processing.base import BaseFilter

class MorphOpenFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 5, iterations: int = 1, **kwargs) -> np.ndarray:
        """
        Aplica apertura morfológica (erosión seguida de dilatación). Elimina ruido pequeño.
        """
        if isinstance(kernel_size, str): kernel_size = int(kernel_size)
        if isinstance(iterations, str): iterations = int(iterations)
        
        is_binary = len(np.unique(img)) <= 2
        
        if is_binary:
            structure = np.ones((kernel_size, kernel_size), dtype=bool)
            result = binary_opening(img, structure=structure, iterations=iterations)
        else:
            structure_num = np.ones((kernel_size, kernel_size))
            result = img.copy()
            for _ in range(iterations):
                result = grey_opening(result, footprint=structure_num)
                
        return result.astype(img.dtype)