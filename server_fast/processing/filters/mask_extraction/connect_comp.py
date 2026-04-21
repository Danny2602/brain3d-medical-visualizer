import cv2
import numpy as np
from processing.base import BaseFilter

class ConnectComponentsFilter(BaseFilter):
    """
    Filtro final: Extrae las masas principales ignorando el polvo brillante, 
    y utiliza la foto cruda original para recortar visualmente el tumor real.
    """
    def apply(self, img: np.ndarray, history: dict = None, min_size_pct: float = 0.015, original_layer_name: str = "original", return_mask_only: bool = False, **kwargs) -> np.ndarray:
        """
        Args:
            img: La máscara binaria actual (blanco y negro).
            min_size_pct: % mínimo de la foto que debe ocupar una mancha para ser "Tumor" (Por defecto 1.5%).
            original_layer_name: De dónde sacamos la textura médica para colorear el tumor.
            return_mask_only: Si es True, solo devuelve la silueta blanca. Si es False, devuelve la foto real recordada.
        """
        # Por seguridad en OpenCV, asegurarnos de que la imagen entrante sea de 8-bits
        if img.dtype != np.uint8:
            img = img.astype(np.uint8)
            
        # Ejecutar el Algoritmo de OpenCV (connectivity=8 igual que tenías)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8, ltype=cv2.CV_32S)
        
        # 3. Invocar al "Pasado" para buscar la fotografía Médica intacta
        if history and original_layer_name in history:
            foto_original = history[original_layer_name]
        else:
            foto_original = img # Failsafe por si algo sale mal
            print(f"Aviso: No se encontró la capa '{original_layer_name}', no se aplicará la textura base.")

        # Si toda la foto es negra
        if num_labels <= 1:
            if return_mask_only:
                return img
            return cv2.bitwise_and(foto_original, foto_original, mask=img)

        #Calcular qué tamaño es aceptable para sobrevivir (Filtrando basura)
        h, w = img.shape
        min_size = int((h * w) * min_size_pct) 
        
        # 5. Dibujar el mapa final ("cleaned_mask")
        cleaned_mask = np.zeros_like(img)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_size:
                # "Encendemos" los pixeles que sí superaron la prueba de tamaño
                cleaned_mask[labels == i] = 255
                
        if return_mask_only:
            return cleaned_mask
        else:
            # Recortar el molde blanco sobre la foto médica original
            tumor_recortado = cv2.bitwise_and(foto_original, foto_original, mask=cleaned_mask)
            return tumor_recortado
