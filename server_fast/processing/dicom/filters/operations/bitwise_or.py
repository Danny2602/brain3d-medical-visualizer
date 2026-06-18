import numpy as np
from processing.base import BaseFilter

class LogicOrFilter(BaseFilter):
    def apply(self, img: np.ndarray, mask_id: str = None, history: dict = None, **kwargs) -> np.ndarray:
        """
        Unión lógica (OR) entre dos imágenes o máscaras DICOM.
        """
        target_mask_id = kwargs.get('layer_b', mask_id)
        if not history or target_mask_id not in history:
            return img.copy()
            
        mask = history[target_mask_id]
        if mask.shape != img.shape:
            return img.copy()
            
        min_img = np.min(img)
        max_img = np.max(img)
        img_binary = img > (min_img + max_img) / 2
        
        min_mask = np.min(mask)
        max_mask = np.max(mask)
        mask_binary = mask > (min_mask + max_mask) / 2
        
        result_bool = np.logical_or(img_binary, mask_binary)
        
        return np.where(result_bool, max_img, min_img).astype(img.dtype)
