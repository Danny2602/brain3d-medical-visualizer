import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from processing.base import BaseFilter

class WatershedFilter(BaseFilter):
    def apply(self, img: np.ndarray, min_distance: int = 10, **kwargs) -> np.ndarray:
        """
        Segmentación de cuencas (Watershed) para separar objetos unidos.
        """
        if isinstance(min_distance, str): min_distance = int(min_distance)
            
        min_val = np.min(img)
        max_val = np.max(img)
        
        if min_val == max_val:
            return img.copy()
            
        # Binarización
        thresh = threshold_otsu(img)
        binary = img > thresh
        
        # Transformación de distancia euclidiana
        distance = ndi.distance_transform_edt(binary)
        
        # Picos locales
        coords = peak_local_max(distance, min_distance=min_distance, labels=binary)
        
        # Máscara de marcadores
        mask = np.zeros(distance.shape, dtype=bool)
        mask[tuple(coords.T)] = True
        markers, _ = ndi.label(mask)
        
        # Watershed
        labels = watershed(-distance, markers, mask=binary)
        
        num_labels = np.max(labels)
        if num_labels == 0:
            return img.copy()
            
        # Normalizar las etiquetas al rango de escala de grises para visualización
        mapped = (labels / num_labels) * (max_val - min_val) + min_val
        return mapped.astype(img.dtype)
