#Este filtro se llama fuzzy_logic.py : "logica difusa"
#Transformaciones gaussianas/campana/triangulares

#Nota:Revisar esto para pruebas y como funciona
import cv2
import numpy as np
from processing.base import BaseFilter

class FuzzyLogicFilter(BaseFilter):
    """
    Filtro de Lógica Difusa.
    Mapea la imagen usando funciones de membresía (Campana, Sigmoide, Triangular) 
    y aplica el Operador de Intensificación de Zadeh para mejorar el contraste
    separando píxeles ruidosos/oscuros de los tejidos estructurados.
    """
    
    def apply(self, img: np.ndarray, history: dict = None, mode: str = "campana", center: float = 0.5, width: float = 0.2, **kwargs) -> np.ndarray:
        """
        Args:
            mode: "campana", "sigmoide" o "triangular".
            center: El centro de la curva de iluminación (0.0 a 1.0).
            width: Qué tan ancha es la campana o triángulo (controla el rango de grises a afectar).
        """
        # 1. Normalizar matemáticamente de [0, 255] a Punto Flotante [0.0, 1.0]
        x = img.astype(np.float32) / 255.0
        
        # ==========================================
        # FASE 1: FUZZIFICACIÓN (Cálculo de Membresía μ)
        # ==========================================
        if mode == "campana":
            # Función Gaussiana (Bell Shape)
            mu = np.exp(-((x - center)**2) / (2 * (width**2)))
            
        elif mode == "sigmoide":
            # Función Sigmoide (Curva S)
            a = 10.0 / width  # Controla qué tan recta o curva es la rampa
            mu = 1.0 / (1.0 + np.exp(-a * (x - center)))
            
        elif mode == "triangular":
            # Función Triangular
            mu = np.maximum(0.0, 1.0 - np.abs(x - center) / width)
            
        else:
            # Fallback a lineal
            mu = x

        # ==========================================
        # FASE 2: INFERENCIA (Operador de Intensificación)
        # ==========================================
        # Lógica: Si el grado μ es < 0.5 (tiende a oscuro/ruido), castigarlo elevándolo al cuadrado.
        # Si μ >= 0.5 (tiende a tejido válido), potenciarlo.
        # np.where actúa como un `if` pero simultáneo para los miles de píxeles al mismo tiempo.
        mu_intensified = np.where(
            mu < 0.5,
            2 * (mu ** 2),
            1 - 2 * ((1 - mu) ** 2)
        )

        # ==========================================
        # FASE 3: DEFUZZIFICACIÓN
        # ==========================================
        # Regresar la matriz de probabilidades a luz [0 a 255]
        img_fuzzy = np.clip(mu_intensified * 255.0, 0, 255)
        
        img_fuzzy = img_fuzzy.astype(np.uint8)

        return img_fuzzy

