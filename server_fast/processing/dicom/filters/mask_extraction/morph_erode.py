import numpy as np
from scipy.ndimage import binary_erosion, grey_erosion
from processing.base import BaseFilter

class MorphErodeFilter(BaseFilter):
    def apply(self, img: np.ndarray, kernel_size: int = 5, iterations: int = 1, **kwargs) -> np.ndarray:
        """
        Aplica erosión morfológica.
        """
        if isinstance(kernel_size, str): kernel_size = int(kernel_size)
        if isinstance(iterations, str): iterations = int(iterations)
        
        is_binary = len(np.unique(img)) <= 2
        
        if is_binary:
            structure = np.ones((kernel_size, kernel_size), dtype=bool)
            result = binary_erosion(img, structure=structure, iterations=iterations)
        else:
            structure_num = np.ones((kernel_size, kernel_size))
            result = img.copy()
            for _ in range(iterations):
                result = grey_erosion(result, footprint=structure_num)
                
        return result.astype(img.dtype)
