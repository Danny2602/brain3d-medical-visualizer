import numpy as np
from skimage.exposure import equalize_adapthist
from processing.base import BaseFilter

def _smooth_blend(orig_normalized: np.ndarray, filtered_normalized: np.ndarray, transition_end: float = 0.08) -> np.ndarray:
    """
    Mezcla suavemente la imagen original con la filtrada para preservar el fondo negro (0)
    sin crear bordes abruptos ni anillos grises artificiales en el tejido blando.
    """
    # Peso w: 0 en el aire (0.0), 1 en el tejido (>= 0.08)
    weight = np.clip(orig_normalized / max(transition_end, 1e-5), 0.0, 1.0)
    # Suavizado hermite (smoothstep) para continuidad perfecta
    weight_smooth = weight * weight * (3.0 - 2.0 * weight)
    return (1.0 - weight_smooth) * orig_normalized + weight_smooth * filtered_normalized


class CLAHEFilter(BaseFilter):
    def apply(self, img: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8, 8), **kwargs) -> np.ndarray:
        """
        Aplica CLAHE con mezcla suave de preservación de fondo (sin artefactos de anillo).
        """
        if isinstance(clipLimit, str):
            clipLimit = float(clipLimit)
        if isinstance(tileGridSize, str):
            tileGridSize = tuple(map(int, tileGridSize.split(',')))
            
        min_val = float(np.min(img))
        max_val = float(np.max(img))
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()
            
        img_float = img.astype(np.float32)
        img_normalized = (img_float - min_val) / range_val
        
        skimage_clip_limit = min(max(clipLimit / 255.0, 0.005), 1.0) if clipLimit > 1 else clipLimit
        img_clahe = equalize_adapthist(img_normalized, kernel_size=tileGridSize, clip_limit=skimage_clip_limit)
        
        # Mezcla suave continua (elimina completamente el anillo gris)
        blended = _smooth_blend(img_normalized, img_clahe)
        
        result = (blended * range_val) + min_val
        return result.astype(img.dtype)