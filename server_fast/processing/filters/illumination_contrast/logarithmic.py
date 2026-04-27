
import numpy as np
from processing.base import BaseFilter

class LogarithmicFilter(BaseFilter):
    """
    Aplica la transformada logarítmica a la imagen.
    """
    def apply(self, img: np.ndarray, **kwargs) -> np.ndarray:
        img_float = img.astype(np.float32) / 255.0 #El divisor  es 255 porque los valores de la imagen estan en el rango de 0 a 255
        # Usar el percentil 99 en lugar del max absoluto evita que un solo píxel brillante arruine el contraste
        max_val = np.percentile(img_float, 99) 
        if max_val == 0: max_val = 1e-5 # Evitar división por cero
        
        c = 1.0 / np.log(1.0 + max_val)
        transformed = c * np.log(1.0 + img_float)
        return np.clip(transformed * 255, 0, 255).astype(np.uint8)
