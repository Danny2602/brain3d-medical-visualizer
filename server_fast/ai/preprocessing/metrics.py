import numpy as np
from scipy.ndimage import sobel

def compute_snr(img: np.ndarray) -> float:
    """
    SNR calibrada para imagen médica.
    IMPORTANTE: Se normaliza al rango [0,1] para que no domine a las otras métricas.
    Un filtro que suaviza artificialmente puede inflar el SNR — por eso tiene poco peso final.
    """
    if img is None or img.size == 0:
        return 0.0
    
    min_val, max_val = float(np.min(img)), float(np.max(img))
    if min_val == max_val:
        return 0.0
    
    threshold = min_val + 0.15 * (max_val - min_val)
    brain_mask = img > threshold
    bg_mask = ~brain_mask
    
    signal_mean = float(np.mean(img[brain_mask])) if np.any(brain_mask) else 0.0
    noise_std = float(np.std(img[bg_mask])) if np.any(bg_mask) else 1e-5
    if noise_std < 1e-5:
        noise_std = 1e-5
    
    raw_snr = signal_mean / noise_std
    # Normalizar con tangente hiperbólica para evitar que filtros de borroneo dominen
    return float(np.tanh(raw_snr / 50.0))


def compute_cnr(img: np.ndarray) -> float:
    """
    CNR entre tejidos de intensidad media y alta (materia gris vs materia blanca / lesiones).
    Normalizado a [0,1].
    """
    if img is None or img.size == 0:
        return 0.0
    
    min_val, max_val = float(np.min(img)), float(np.max(img))
    if min_val == max_val:
        return 0.0
    
    mid_low  = min_val + 0.3 * (max_val - min_val)
    mid_high = min_val + 0.7 * (max_val - min_val)
    
    region_a = img[(img >= mid_low) & (img < mid_high)]
    region_b = img[img >= mid_high]
    bg       = img[img < mid_low]
    
    if region_a.size == 0 or region_b.size == 0:
        return 0.0
    
    mean_a    = float(np.mean(region_a))
    mean_b    = float(np.mean(region_b))
    noise_std = float(np.std(bg)) if bg.size > 0 else 1.0
    if noise_std < 1e-5:
        noise_std = 1e-5
    
    raw_cnr = abs(mean_a - mean_b) / noise_std
    return float(np.tanh(raw_cnr / 30.0))


def compute_sharpness_tenengrad(img: np.ndarray) -> float:
    """
    Nitidez de bordes anatómicos (Tenengrad / Sobel). 
    Una imagen borrosa tiene Tenengrad MUY bajo — esto penaliza el sobre-suavizado.
    Normalizado a [0,1].
    """
    if img is None or img.size == 0:
        return 0.0
    
    img_float = img.astype(np.float64)
    gx = sobel(img_float, axis=0)
    gy = sobel(img_float, axis=1)
    grad_mean = float(np.mean(np.sqrt(gx**2 + gy**2)))
    
    # La magnitud de gradiente máxima posible para uint8 es ~255*4
    max_possible = 255.0 * 4.0
    return float(np.clip(grad_mean / max_possible, 0.0, 1.0))


def compute_entropy(img: np.ndarray) -> float:
    """
    Entropía de la imagen (bits de información).
    Un filtro que borra/suaviza REDUCE la entropía, lo cual penaliza la puntuación.
    Normalizada a [0,1] respecto al máximo teórico para 8-bit (8 bits = 8.0 max entropy).
    """
    if img is None or img.size == 0:
        return 0.0
    
    img_uint8 = img.astype(np.uint8)
    hist, _ = np.histogram(img_uint8.ravel(), bins=256, range=(0, 256))
    hist = hist.astype(float)
    hist /= (hist.sum() + 1e-10)
    
    # Entropía de Shannon
    nonzero = hist[hist > 0]
    entropy = float(-np.sum(nonzero * np.log2(nonzero)))
    
    # Máximo teórico 8 bits = 8.0
    return float(np.clip(entropy / 8.0, 0.0, 1.0))


def compute_composite_quality_score(img: np.ndarray) -> float:
    """
    Puntuación compuesta de calidad médica para imágenes cerebrales DICOM.
    
    Pesos calibrados para imagen médica real:
      - CNR      35%: Diferenciación de tejidos (MÁS IMPORTANTE)
      - Nitidez  30%: Preservación de bordes anatómicos (penaliza borroneo)
      - Entropía 25%: Contenido de información (penaliza pérdida de detalle)
      - SNR      10%: Señal/Ruido (poco peso — el suavizado lo infla artificialmente)
    
    Todos los componentes están en [0,1] para una puntuación final en [0,1].
    """
    cnr       = compute_cnr(img)
    sharpness = compute_sharpness_tenengrad(img)
    entropy   = compute_entropy(img)
    snr       = compute_snr(img)
    
    score = (0.35 * cnr) + (0.30 * sharpness) + (0.25 * entropy) + (0.10 * snr)
    return float(np.clip(score, 0.0, 1.0))
