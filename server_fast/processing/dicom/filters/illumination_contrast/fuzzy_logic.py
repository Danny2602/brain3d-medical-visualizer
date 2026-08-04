import numpy as np
from processing.base import BaseFilter

def _triangular(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    denom_left = max(b - a, 1e-6)
    denom_right = max(c - b, 1e-6)
    left  = np.where(b > a, (x - a) / denom_left, 0.0)
    right = np.where(c > b, (c - x) / denom_right, 0.0)
    return np.clip(np.minimum(left, right), 0.0, 1.0)

def _gaussian(x: np.ndarray, center: float, sigma: float) -> np.ndarray:
    return np.exp(-((x - center) ** 2) / (2 * sigma ** 2))

def _sigmoid(x: np.ndarray, center: float, slope: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-slope * (x - center)))

def _smooth_blend(orig_normalized: np.ndarray, filtered_normalized: np.ndarray, transition_end: float = 0.08) -> np.ndarray:
    weight = np.clip(orig_normalized / max(transition_end, 1e-5), 0.0, 1.0)
    weight_smooth = weight * weight * (3.0 - 2.0 * weight)
    return (1.0 - weight_smooth) * orig_normalized + weight_smooth * filtered_normalized


class FuzzyLogicFilter(BaseFilter):
    _Y = np.linspace(0.0, 1.0, 256)
    _OUT_DARK  = _triangular(_Y, 0.0,  0.0,  0.25)
    _OUT_GRAY  = _triangular(_Y, 0.25, 0.50, 0.75)
    _OUT_WHITE = _triangular(_Y, 0.75, 0.90, 1.0)

    def apply(
        self,
        img: np.ndarray,
        history: dict = None,
        mode: str = "triangular",
        sigma: float = 0.15,
        **kwargs,
    ) -> np.ndarray:
        
        min_val = float(np.min(img))
        max_val = float(np.max(img))
        range_val = max_val - min_val
        
        if range_val == 0:
            return img.copy()

        x = (img.astype(np.float32) - min_val) / range_val
        h_dim, w_dim = x.shape[:2]
        x_flat = x.ravel()

        if mode == "triangular":
            mu_oscuro = _triangular(x_flat, 0.0,  0.0,  0.35)
            mu_gris   = _triangular(x_flat, 0.25, 0.55, 0.85)
            mu_blanco = _triangular(x_flat, 0.65, 1.0,  1.0)
        elif mode == "campana":
            mu_oscuro = _gaussian(x_flat, center=0.0,  sigma=sigma)
            mu_gris   = _gaussian(x_flat, center=0.50, sigma=sigma)
            mu_blanco = _gaussian(x_flat, center=1.0,  sigma=sigma)
        elif mode == "sigmoide":
            slope = 1.0 / max(sigma, 1e-6)
            mu_oscuro = _sigmoid(x_flat, center=0.30, slope=-slope * 10)
            mu_blanco = _sigmoid(x_flat, center=0.70, slope= slope * 10)
            mu_gris   = np.clip(
                _sigmoid(x_flat, center=0.30, slope=slope * 10)
                - _sigmoid(x_flat, center=0.70, slope=slope * 10),
                0.0, 1.0
            )
        else:
            mu_oscuro = _triangular(x_flat, 0.0,  0.0,  0.35)
            mu_gris   = _triangular(x_flat, 0.25, 0.55, 0.85)
            mu_blanco = _triangular(x_flat, 0.65, 1.0,  1.0)

        impl_r1 = np.minimum(mu_oscuro[:, np.newaxis], self._OUT_DARK[np.newaxis, :])
        impl_r2 = np.minimum(mu_gris[:, np.newaxis], self._OUT_GRAY[np.newaxis, :])
        impl_r3 = np.minimum(mu_blanco[:, np.newaxis], self._OUT_WHITE[np.newaxis, :])
        
        mu_agregado = np.maximum(impl_r1, np.maximum(impl_r2, impl_r3))

        Y = self._Y[np.newaxis, :]
        numerador   = np.sum(mu_agregado * Y, axis=1)
        denominador = np.sum(mu_agregado,      axis=1)

        safe_denom = np.where(denominador > 1e-9, denominador, 1.0)
        y_star = np.where(denominador > 1e-9, numerador / safe_denom, x_flat)

        y_star_img = y_star.reshape(h_dim, w_dim)
        
        # Mezcla suave para evitar saltos o artefactos de anillo
        blended = _smooth_blend(x, y_star_img)

        resultado = (blended * range_val) + min_val
        return resultado.astype(img.dtype)
