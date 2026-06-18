import numpy as np
from skimage.restoration import denoise_nl_means, estimate_sigma
from processing.base import BaseFilter

class NlMeansFilter(BaseFilter):
    def apply(self, img: np.ndarray, h: float = 0.1, patch_size: int = 7, patch_distance: int = 11, **kwargs) -> np.ndarray:
        """
        Aplica el filtro Non-Local Means en alta precisión usando scikit-image.
        
        Args:
            img (np.ndarray): Imagen DICOM de entrada.
            h (float): Parámetro de suavizado (relativo al ruido).
            patch_size (int): Tamaño de los parches.
            patch_distance (int): Distancia de búsqueda.
            
        Returns:
            np.ndarray: Imagen filtrada.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        # Normalizar a [0, 1] para algoritmos probabilísticos de scikit-image
        img_normalized = (img - min_val) / range_val
        
        # Estimar la desviación estándar del ruido en la imagen
        sigma_est = np.mean(estimate_sigma(img_normalized, channel_axis=None))
        
        denoised = denoise_nl_means(
            img_normalized,
            h=h * sigma_est if sigma_est > 0 else h,
            fast_mode=True,
            patch_size=patch_size,
            patch_distance=patch_distance,
            channel_axis=None
        )
        
        # Desnormalizar
        result = (denoised * range_val) + min_val
        return result.astype(img.dtype)