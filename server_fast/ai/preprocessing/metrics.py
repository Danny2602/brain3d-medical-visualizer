import numpy as np
from scipy.ndimage import sobel

def _get_tissue_and_bg_masks(img: np.ndarray):
    """
    Segmenta dinámicamente la máscara de tejido anatómico (ROI) y la máscara de fondo (aire).
    """
    min_val, max_val = float(np.min(img)), float(np.max(img))
    range_val = max_val - min_val
    if range_val < 1e-5:
        return np.ones_like(img, dtype=bool), np.zeros_like(img, dtype=bool)

    bg_threshold = min_val + 0.08 * range_val
    bg_mask = img <= bg_threshold

    tissue_threshold = min_val + 0.12 * range_val
    tissue_mask = img >= tissue_threshold

    return tissue_mask, bg_mask


def compute_background_purity_penalty(img: np.ndarray, bg_mask: np.ndarray) -> float:
    """
    Penaliza fuertemente si un filtro convierte el fondo negro de aire en un tono grisáceo.
    Retorna un factor multiplicador entre 0.1 (totalmente arruinado) y 1.0 (negro puro).
    """
    if bg_mask is None or not np.any(bg_mask):
        return 1.0

    bg_pixels = img[bg_mask].astype(float)
    bg_mean = float(np.mean(bg_pixels))
    
    # Si el fondo promedio excede 10 unidades de brillo (en 0-255), penalizar progresivamente
    if bg_mean <= 5.0:
        return 1.0
    elif bg_mean >= 30.0:
        return 0.1
    else:
        # Caída lineal de 1.0 a 0.1 entre 5 y 30
        return float(1.0 - 0.9 * ((bg_mean - 5.0) / 25.0))


def compute_roi_cnr(img: np.ndarray, tissue_mask: np.ndarray) -> float:
    """
    Calcula la Relación Contraste-Ruido (CNR) evaluada estrictamente DENTRO del tejido cerebral.
    Mide la diferenciación entre sustancia gris (intensidad media) y sustancia blanca/lesiones (alta intensidad).
    """
    if tissue_mask is None or not np.any(tissue_mask):
        return 0.0

    tissue_pixels = img[tissue_mask].astype(float)
    if tissue_pixels.size < 10:
        return 0.0

    min_t, max_t = float(np.min(tissue_pixels)), float(np.max(tissue_pixels))
    if max_t == min_t:
        return 0.0

    mid_threshold = min_t + 0.50 * (max_t - min_t)
    region_gray_matter = tissue_pixels[tissue_pixels < mid_threshold]
    region_white_matter = tissue_pixels[tissue_pixels >= mid_threshold]

    if region_gray_matter.size == 0 or region_white_matter.size == 0:
        return 0.0

    mean_gray = float(np.mean(region_gray_matter))
    mean_white = float(np.mean(region_white_matter))
    std_tissue = float(np.std(tissue_pixels))
    if std_tissue < 1e-5:
        std_tissue = 1e-5

    raw_cnr = abs(mean_white - mean_gray) / std_tissue
    # Normalizado con tanh para mapear suavemente a [0, 1]
    return float(np.tanh(raw_cnr / 2.0))


def compute_roi_sharpness_tenengrad(img: np.ndarray, tissue_mask: np.ndarray) -> float:
    """
    Mide la nitidez de bordes anatómicos reales usando el gradiente Sobel (Tenengrad)
    calculado EXCLUSIVAMENTE dentro del tejido cerebral.
    Penaliza fuertemente las imágenes borrosas o sobre-suavizadas.
    """
    if tissue_mask is None or not np.any(tissue_mask):
        return 0.0

    img_float = img.astype(np.float64)
    gx = sobel(img_float, axis=0)
    gy = sobel(img_float, axis=1)
    grad_magnitude = np.sqrt(gx**2 + gy**2)

    grad_tissue = grad_magnitude[tissue_mask]
    if grad_tissue.size == 0:
        return 0.0

    mean_grad = float(np.mean(grad_tissue))
    # Normalizado a [0, 1]: Gradientes típicos de tejido bien enfocado rondan 25-60
    return float(np.clip(mean_grad / 50.0, 0.0, 1.0))


def compute_roi_entropy(img: np.ndarray, tissue_mask: np.ndarray) -> float:
    """
    Mide la Entropía de Shannon (riqueza de textura e información) restringida AL TEJIDO.
    Una imagen con buen nivel de detalle anatómico tendrá mayor entropía interna.
    """
    if tissue_mask is None or not np.any(tissue_mask):
        return 0.0

    tissue_pixels = img[tissue_mask].astype(np.uint8)
    if tissue_pixels.size == 0:
        return 0.0

    hist, _ = np.histogram(tissue_pixels, bins=256, range=(0, 256))
    hist = hist.astype(float)
    total = hist.sum()
    if total == 0:
        return 0.0
    hist /= total

    nonzero = hist[hist > 0]
    entropy = float(-np.sum(nonzero * np.log2(nonzero)))
    # Normalizado respecto al máximo de 8 bits = 8.0
    return float(np.clip(entropy / 7.5, 0.0, 1.0))


def compute_contrast_preservation_score(img: np.ndarray, orig_img: np.ndarray, tissue_mask: np.ndarray) -> float:
    """
    Penaliza si el contraste interno del tejido se redujo o aplanó (imagen lavada/grisácea).
    Compara la desviación estándar interna de la imagen procesada vs la original.
    """
    if orig_img is None or tissue_mask is None or not np.any(tissue_mask):
        return 1.0

    orig_std = float(np.std(orig_img[tissue_mask]))
    proc_std = float(np.std(img[tissue_mask]))

    if orig_std < 1e-5:
        return 1.0

    std_ratio = proc_std / orig_std
    # Si la desviación estándar cayó a menos del 80% de la original, la imagen se lavó (perdió contraste)
    if std_ratio < 0.8:
        return float(np.clip(std_ratio / 0.8, 0.2, 1.0))
    elif std_ratio > 2.5:
        # Demasiado ruido o artefacto extremo
        return 0.7
    else:
        return 1.0


def compute_composite_quality_score(img: np.ndarray, orig_img: np.ndarray = None) -> float:
    """
    Puntuación compuesta de precisión clínica para imágenes cerebrales DICOM.
    
    Estructura de Evaluación:
      1. Segmentación interna del Tejido (ROI) vs Fondo (Aire).
      2. Medición dentro de la ROI:
         - CNR (Contraste entre tejidos): 35%
         - Nitidez Tenengrad (Detalle de bordes): 35%
         - Entropía (Riqueza de información): 20%
         - Fidelidad de Contraste (Evita imagen lavada): 10%
      3. Multiplicación por Penalización de Fondo (Si el aire se volvió gris, arruina la nota).
    """
    if img is None or img.size == 0:
        return 0.0

    tissue_mask, bg_mask = _get_tissue_and_bg_masks(img)

    cnr = compute_roi_cnr(img, tissue_mask)
    sharpness = compute_roi_sharpness_tenengrad(img, tissue_mask)
    entropy = compute_roi_entropy(img, tissue_mask)

    contrast_preservation = 1.0
    if orig_img is not None:
        contrast_preservation = compute_contrast_preservation_score(img, orig_img, tissue_mask)

    bg_penalty = compute_background_purity_penalty(img, bg_mask)

    base_score = (0.35 * cnr) + (0.35 * sharpness) + (0.20 * entropy) + (0.10 * contrast_preservation)
    final_score = base_score * bg_penalty

    return float(np.clip(final_score, 0.0, 1.0))
