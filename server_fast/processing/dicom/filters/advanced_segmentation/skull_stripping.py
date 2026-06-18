import numpy as np
from skimage.filters import threshold_otsu
from scipy.ndimage import label, binary_closing, binary_dilation
from skimage.measure import regionprops
from processing.base import BaseFilter

class SkullStrippingFilter(BaseFilter):
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """
        Elimina el cráneo y fondo, dejando únicamente la masa cerebral.
        Algoritmo optimizado para imágenes DICOM reales.
        """
        min_val = np.min(img)
        max_val = np.max(img)
        
        if min_val == max_val:
            return img.copy()
            
        # 1. Binarización inteligente (Otsu sobre HU)
        thresh = threshold_otsu(img)
        binary = img > thresh
        
        # 2. Cerrar pequeños agujeros internos
        struct = np.ones((5, 5), dtype=bool)
        closed = binary_closing(binary, structure=struct)
        
        # 3. Encontrar el componente conectado más grande (Cerebro)
        labeled, num_features = label(closed)
        if num_features == 0:
            return np.full_like(img, min_val)
            
        regions = regionprops(labeled)
        largest_region = max(regions, key=lambda r: r.area)
        
        # 4. Crear máscara solo para el cerebro
        brain_mask = (labeled == largest_region.label)
        
        # 5. Dilatar ligeramente la máscara para no perder la corteza externa
        brain_mask = binary_dilation(brain_mask, structure=np.ones((3,3)))
        
        # 6. Recortar la imagen original
        stripped = np.where(brain_mask, img, min_val)
        return stripped.astype(img.dtype)
