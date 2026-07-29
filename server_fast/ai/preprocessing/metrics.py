import numpy as np
from scipy.ndimage import sobel

def compute_snr(img: np.ndarray) -> float:
    """
    Calcula la Relación Señal a Ruido (SNR) médica.
    SNR = Media del tejido cerebral / Desviación Estándar del fondo (ruido).
    """
    if img is None or img.size == 0:
        return 0.0
    
    min_val, max_val = np.min(img), np.max(img)
    if min_val == max_val:
        return 0.0
    
    threshold = min_val + 0.15 * (max_val - min_val)
    brain_mask = img > threshold
    bg_mask = ~brain_mask
    
    signal_mean = np.mean(img[brain_mask]) if np.any(brain_mask) else 0.0
    noise_std = np.std(img[bg_mask]) if np.any(bg_mask) else 1e-5
    
    if noise_std < 1e-5:
        noise_std = 1e-5
        
    return float(signal_mean / noise_std)

def compute_cnr(img: np.ndarray) -> float:
    """
    Calcula la Relación Contraste a Ruido (CNR) entre dos regiones de tejido.
    """
    if img is None or img.size == 0:
        return 0.0
        
    min_val, max_val = np.min(img), np.max(img)
    if min_val == max_val:
        return 0.0
        
    mid_low = min_val + 0.3 * (max_val - min_val)
    mid_high = min_val + 0.7 * (max_val - min_val)
    
    region_a = img[(img >= mid_low) & (img < mid_high)]
    region_b = img[img >= mid_high]
    bg = img[img < mid_low]
    
    if region_a.size == 0 or region_b.size == 0:
        return 0.0
        
    mean_a = np.mean(region_a)
    mean_b = np.mean(region_b)
    noise_std = np.std(bg) if bg.size > 0 else 1.0
    if noise_std < 1e-5:
        noise_std = 1e-5
        
    return float(abs(mean_a - mean_b) / noise_std)

def compute_sharpness_tenengrad(img: np.ndarray) -> float:
    """
    Mide la nitidez de los bordes anatómicos usando la magnitud del gradiente de Sobel (Tenengrad).
    """
    if img is None or img.size == 0:
        return 0.0
        
    img_float = img.astype(np.float64)
    gx = sobel(img_float, axis=0)
    gy = sobel(img_float, axis=1)
    
    grad_magnitude = np.sqrt(gx**2 + gy**2)
    return float(np.mean(grad_magnitude))

def compute_composite_quality_score(img: np.ndarray) -> float:
    """
    Puntuación combinada de calidad de imagen para guiado de Optuna:
    Equilibra SNR (bajo ruido), CNR (alto contraste) y Nitidez.
    """
    snr = compute_snr(img)
    cnr = compute_cnr(img)
    sharpness = compute_sharpness_tenengrad(img)
    
    score = (0.4 * snr) + (0.4 * cnr) + (0.2 * sharpness)
    return float(score)
