# fuzzy_logic.py — Sistema de Inferencia Difusa Mamdani
# Pipeline: Fuzzificación → Evaluación de Reglas → Implicación → Agregación → Defuzzificación

import numpy as np
from processing.base import BaseFilter


# ==============================================================================
# FUNCIONES DE MEMBRESÍA (vectorizadas con NumPy)
# ==============================================================================

# def _triangular(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
#     """
#     Función triangular: sube de a→b, baja de b→c.
#     μ = 0 fuera del rango [a, c], pico de 1.0 en b.
#     """
#     left  = np.where(b > a, (x - a) / (b - a), 0.0)
#     right = np.where(c > b, (c - x) / (c - b), 0.0)
#     return np.clip(np.minimum(left, right), 0.0, 1.0)

def _triangular(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    # Usamos un denominador seguro (mínimo 1e-6) para evitar divisiones por cero
    denom_left = max(b - a, 1e-6)
    denom_right = max(c - b, 1e-6)
    
    left  = np.where(b > a, (x - a) / denom_left, 0.0)
    right = np.where(c > b, (c - x) / denom_right, 0.0)
    return np.clip(np.minimum(left, right), 0.0, 1.0)

def _gaussian(x: np.ndarray, center: float, sigma: float) -> np.ndarray:
    """
    Función campana (Gaussiana): pico de 1.0 en center, cae con sigma.
    """
    return np.exp(-((x - center) ** 2) / (2 * sigma ** 2))


def _sigmoid(x: np.ndarray, center: float, slope: float) -> np.ndarray:
    """
    Función sigmoide: 0 en el lado izquierdo, 1 en el derecho.
    slope > 0 → sube de izquierda a derecha.
    slope < 0 → baja de izquierda a derecha (invertida).
    """
    return 1.0 / (1.0 + np.exp(-slope * (x - center)))


# ==============================================================================
# CLASE PRINCIPAL
# ==============================================================================

class FuzzyLogicFilter(BaseFilter):
    """
    Sistema de Inferencia Difusa Mamdani para mejora de contraste médico.

    Variables lingüísticas de ENTRADA: oscuro | gris | blanco
    Variables lingüísticas de SALIDA : mas_oscuro | gris | mas_blanco

    Reglas:
        R1: Si pixel es OSCURO  → volverlo MÁS OSCURO
        R2: Si pixel es GRIS    → dejarlo en GRIS
        R3: Si pixel es BLANCO  → volverlo MÁS BLANCO

    Métodos de membresía configurables: "triangular" | "campana" | "sigmoide"

    Inferencia : Implicación mínima (Mandani clásico)
    Agregación : Máximo de reglas activas
    Defuzz.    : Centroide (centro de gravedad)
    """

    # ------------------------------------------------------------------
    # Universo de discurso de SALIDA: 256 puntos en [0, 1]
    # ------------------------------------------------------------------
    _Y = np.linspace(0.0, 1.0, 256)

    # Conjuntos difusos de SALIDA (siempre triangulares — estándar Mamdani)
    _OUT_DARK  = _triangular(_Y, 0.0,  0.10, 0.30)   # más oscuro
    _OUT_GRAY  = _triangular(_Y, 0.30, 0.50, 0.70)   # gris
    _OUT_WHITE = _triangular(_Y, 0.70, 0.90, 1.0)    # más blanco

    # ------------------------------------------------------------------

    def apply(
        self,
        img: np.ndarray,
        history: dict = None,
        mode: str = "triangular",
        sigma: float = 0.15,
        **kwargs,
    ) -> np.ndarray:
        """
        Args:
            img   : Imagen de entrada uint8 escala de grises.
            mode  : Función de membresía de entrada → "triangular" | "campana" | "sigmoide"
            sigma : Ancho de las funciones campana (solo se usa en modo "campana").
        """

        # ══════════════════════════════════════════════════════════════
        # PASO 0: Normalizar [0, 255] → [0.0, 1.0]  (float32)
        # ══════════════════════════════════════════════════════════════
        x = img.astype(np.float32) / 255.0
        h, w = x.shape[:2]
        x_flat = x.ravel()  # trabajo con vector 1D para eficiencia

        # ══════════════════════════════════════════════════════════════
        # PASO 1: FUZZIFICACIÓN
        # Calcular grado de pertenencia de cada pixel a los conjuntos
        # lingüísticos de ENTRADA: μ_oscuro, μ_gris, μ_blanco
        # ══════════════════════════════════════════════════════════════
        if mode == "triangular":
            # Triángulos que cubren [0,1] sin solapamiento excesivo
            mu_oscuro = _triangular(x_flat, 0.0,  0.0,  0.40)
            mu_gris   = _triangular(x_flat, 0.20, 0.50, 0.80)
            mu_blanco = _triangular(x_flat, 0.60, 1.0,  1.0)

        elif mode == "campana":
            mu_oscuro = _gaussian(x_flat, center=0.10, sigma=sigma)
            mu_gris   = _gaussian(x_flat, center=0.50, sigma=sigma)
            mu_blanco = _gaussian(x_flat, center=0.90, sigma=sigma)

        elif mode == "sigmoide":
            # oscuro = sigmoide invertida (alta en 0, baja en 1)
            # blanco = sigmoide directa   (baja en 0, alta en 1)
            # gris   = diferencia de dos sigmoides (campana asimétrica)
            slope = 1.0 / max(sigma, 1e-6)
            mu_oscuro = _sigmoid(x_flat, center=0.35, slope=-slope * 10)
            mu_blanco = _sigmoid(x_flat, center=0.65, slope= slope * 10)
            mu_gris   = np.clip(
                _sigmoid(x_flat, center=0.35, slope=slope * 10)
                - _sigmoid(x_flat, center=0.65, slope=slope * 10),
                0.0, 1.0
            )

        else:
            # Fallback → modo triangular
            mu_oscuro = _triangular(x_flat, 0.0,  0.0,  0.40)
            mu_gris   = _triangular(x_flat, 0.20, 0.50, 0.80)
            mu_blanco = _triangular(x_flat, 0.60, 1.0,  1.0)

        # ══════════════════════════════════════════════════════════════
        # PASO 2: EVALUACIÓN DE REGLAS + IMPLICACIÓN MÍNIMA (Mamdani)
        #
        # R1: if OSCURO  → then MÁS_OSCURO  | recortar _OUT_DARK  en μ_oscuro
        # R2: if GRIS    → then GRIS         | recortar _OUT_GRAY  en μ_gris
        # R3: if BLANCO  → then MÁS_BLANCO   | recortar _OUT_WHITE en μ_blanco
        #
        # Forma: μ_implicado(y) = min(μ_regla, μ_out(y))
        # Para N píxeles y 256 puntos de salida → shape (N, 256)
        # ══════════════════════════════════════════════════════════════
        n_pixels = x_flat.shape[0]

        # μ_oscuro[:, None] broadcast (N,1) * (256,) → (N, 256)
        impl_r1 = np.minimum(
            mu_oscuro[:, np.newaxis],           # (N, 1)
            self._OUT_DARK[np.newaxis, :]       # (1, 256)
        )                                        # → (N, 256)

        impl_r2 = np.minimum(
            mu_gris[:, np.newaxis],
            self._OUT_GRAY[np.newaxis, :]
        )

        impl_r3 = np.minimum(
            mu_blanco[:, np.newaxis],
            self._OUT_WHITE[np.newaxis, :]
        )

        # ══════════════════════════════════════════════════════════════
        # PASO 3: AGREGACIÓN (máximo entre reglas activas)
        # μ_agregado(y) = max(R1_impl, R2_impl, R3_impl) punto a punto
        # ══════════════════════════════════════════════════════════════
        mu_agregado = np.maximum(impl_r1, np.maximum(impl_r2, impl_r3))  # (N, 256)

        # ══════════════════════════════════════════════════════════════
        # PASO 4: DEFUZZIFICACIÓN — Método del Centroide (CoG)
        # y* = Σ(y_j * μ_agregado_j) / Σ(μ_agregado_j)
        # ══════════════════════════════════════════════════════════════
        Y = self._Y[np.newaxis, :]              # (1, 256)

        numerador   = np.sum(mu_agregado * Y, axis=1)    # (N,)
        denominador = np.sum(mu_agregado,      axis=1)   # (N,)

        # Evitar división por cero (píxel sin regla activa → conservar valor)
        safe_denom = np.where(denominador > 1e-9, denominador, 1.0)
        y_star = np.where(denominador > 1e-9, numerador / safe_denom, x_flat)

        # ══════════════════════════════════════════════════════════════
        # PASO 5: Desnormalizar [0.0, 1.0] → [0, 255] y reconstruir
        # ══════════════════════════════════════════════════════════════
        resultado = np.clip(y_star * 255.0, 0.0, 255.0)
        return resultado.reshape(h, w).astype(np.uint8)

