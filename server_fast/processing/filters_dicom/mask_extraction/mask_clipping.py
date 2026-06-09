import cv2
import numpy as np
from processing.base import BaseFilter

class MaskClippingFilter(BaseFilter):
    """
    Filtro de Recorte: Aplica una máscara binaria sobre una imagen original 
    para extraer la región de interés con su textura médica real.
    """
    def apply(self, img: np.ndarray, history: dict = None, layer_a: str = "", layer_b: str = "", **kwargs) -> np.ndarray:
        """
        Aplica un recorte de máscara sobre una textura.
        - Si se conectan dos nodos: layer_a es la TEXTURA y layer_b es la MÁSCARA.
        - Si solo se conecta uno: img es la MÁSCARA y se usa 'original' (o original_layer) como TEXTURA.
        """
        if not history:
            return img
            
        # 1. Determinar la TEXTURA (la foto médica real)
        # Si hay layer_a, esa es la textura. Si no, usamos 'original_layer' o el respaldo 'original'
        texture_id = layer_a if layer_a else kwargs.get('original_layer', 'original')
        foto_textura = history.get(texture_id, history.get('original', img))
        
        # 2. Determinar la MÁSCARA (el blanco y negro)
        # Si hay layer_b, esa es la máscara. Si no, el nodo conectado (img) es la máscara.
        mask_img = history.get(layer_b, img) if layer_b else img
        
        # Asegurarnos de que la máscara sea uint8 y de un solo canal (escala de grises)
        if mask_img.dtype != np.uint8:
            mask = mask_img.astype(np.uint8)
        else:
            mask = mask_img

        # Si la máscara tiene 3 canales (RGB/BGR), convertir a escala de grises
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            
        # Redimensionar la máscara si no coincide con la textura (por seguridad)
        if foto_textura.shape[:2] != mask.shape[:2]:
            mask = cv2.resize(mask, (foto_textura.shape[1], foto_textura.shape[0]))
        
        # Aplicar el recorte: Mantiene los píxeles de foto_textura donde mask > 0
        return cv2.bitwise_and(foto_textura, foto_textura, mask=mask)
