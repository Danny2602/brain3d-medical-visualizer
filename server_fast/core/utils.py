import cv2
import numpy as np
import base64
import pydicom
import io

def image_to_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode('.png', img)
    return "data:image/png;base64," + base64.b64encode(buffer).decode()

def read_dicom_image(file_bytes: bytes) -> np.ndarray:
    ds = pydicom.dcmread(io.BytesIO(file_bytes))
    pixel_array = ds.pixel_array.astype(float)
    
    if hasattr(ds, 'RescaleIntercept') and hasattr(ds, 'RescaleSlope'):
        pixel_array = pixel_array * ds.RescaleSlope + ds.RescaleIntercept
        
    if hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
        wc = ds.WindowCenter
        ww = ds.WindowWidth
        if isinstance(wc, (list, pydicom.multival.MultiValue)):
            wc = wc[0]
        if isinstance(ww, (list, pydicom.multival.MultiValue)):
            ww = ww[0]
            
        lower_bound = wc - ww / 2
        upper_bound = wc + ww / 2
        pixel_array = np.clip(pixel_array, lower_bound, upper_bound)
        normalized = ((pixel_array - lower_bound) / ww) * 255
        return normalized.astype(np.uint8)
    else:
        min_val = np.min(pixel_array)
        max_val = np.max(pixel_array)
        if max_val - min_val > 0:
            normalized = ((pixel_array - min_val) / (max_val - min_val)) * 255
            return normalized.astype(np.uint8)
        else:
            return np.zeros_like(pixel_array, dtype=np.uint8)
