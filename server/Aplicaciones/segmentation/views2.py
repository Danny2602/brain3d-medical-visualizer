from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import cv2
import numpy as np
import base64
from skimage.morphology import remove_small_objects


class FourierDiagnosticsProcessor:

    def __init__(self, image_bytes):
        # Lectura de la imagen desde bytes
        self.img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

        # Normalización básica
        self.img = cv2.convertScaleAbs(self.img, alpha=1, beta=0)

        # Escala de grises
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)


    # ----------------------------
    # 1. PREPROCESAMIENTO (Denoise)
    # ----------------------------
    def denoise(self):
        denoised = cv2.fastNlMeansDenoising(
            self.img_gray,
            None,
            h=10,
            templateWindowSize=7,
            searchWindowSize=21
        )
        return denoised


    # ----------------------------
    # 2. FOURIER TRANSFORM (Gauss Alta Frecuencia)
    # ----------------------------
    def fourier_filter(self, img):
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)

        rows, cols = img.shape
        crow, ccol = rows // 2, cols // 2

        # Crear matrices de distancias al centro
        x, y = np.meshgrid(np.arange(cols), np.arange(rows))
        dist_center = np.sqrt((x - ccol)**2 + (y - crow)**2)
        
        # Radio de corte Gaussiano (D0)
        D0 = 40.0
        
        # Filtro Gaussiano de Paso Alto
        hpf = 1.0 - np.exp(-(dist_center**2) / (2 * (D0**2)))
        
        # Énfasis de Altas Frecuencias (High-Frequency Emphasis)
        # 0.5 conserva bajas frecuencias, 0.75 resalta bordes
        high_freq_emphasis = 0.5 + 0.75 * hpf
        
        # Aplicar el filtro
        filtered = fshift * high_freq_emphasis

        # Calcular espectro de magnitud para visualización
        magnitude = 20 * np.log(np.abs(fshift) + 1)
        magnitude = cv2.normalize(
            magnitude,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        return filtered, magnitude


    # ----------------------------
    # 3. INVERSE FOURIER
    # ----------------------------
    def inverse_fourier(self, filtered):
        f_ishift = np.fft.ifftshift(filtered)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)

        img_back = cv2.normalize(
            img_back,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        return img_back


    # ----------------------------
    # 4. MEJORA DE CONTRASTE (CLAHE)
    # ----------------------------
    def enhance_contrast(self, img):
        clahe = cv2.createCLAHE(
            clipLimit=2.5,
            tileGridSize=(8, 8)
        )
        clahe_img = clahe.apply(img)

        # Adaptar el kernel al tamaño de la imagen para mejor escalabilidad
        rows, cols = img.shape
        kernel_height = max(1, rows // 200)  # Altura proporcional (pequeña para detalles finos)
        kernel_width = max(1, cols // 50)   # Anchura proporcional (alargada horizontalmente)
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (kernel_height, kernel_width)
        )
        top_hat = cv2.morphologyEx(
            clahe_img,
            cv2.MORPH_TOPHAT,
            kernel
        )
        black_hat = cv2.morphologyEx(
            clahe_img,
            cv2.MORPH_BLACKHAT,
            kernel
        )

        morph = cv2.add(clahe_img, top_hat)
        morph = cv2.subtract(morph, black_hat)

        return clahe_img, morph


    # ----------------------------
    # 5. MEJORA DE DETALLE (Laplaciano)
    # ----------------------------
    def enhance_details(self, img):
        gaussian = cv2.GaussianBlur(img, (0, 0), 3)
        unsharp = cv2.addWeighted(img, 2.0, gaussian, -1.0, 0)

        laplacian = cv2.Laplacian(
            unsharp,
            cv2.CV_64F,
            ksize=3
        )
        laplacian_abs = cv2.convertScaleAbs(laplacian)

        super_detail = cv2.addWeighted(
            unsharp,
            0.85,
            laplacian_abs,
            0.15,
            0
        )

        return unsharp,gaussian, super_detail


    # ----------------------------
    # 6. SEGMENTACIÓN (Otsu & Canny)
    # ----------------------------
    def segmentation(self, img):
        blur = cv2.GaussianBlur(img, (11, 11), 0)

        _, otsu = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        canny = cv2.Canny(img, 350, 400)

        return otsu, canny


    # ----------------------------
    # 7. REFINAMIENTO DE MÁSCARA
    # ----------------------------
    def refine(self, otsu, canny):
        m1 = cv2.bitwise_and(otsu, canny)

        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (4, 4)
        )
        canny_dilated = cv2.dilate(canny, kernel, iterations=2)
        m2 = cv2.bitwise_or(otsu, canny_dilated)

        contours, _ = cv2.findContours(
            otsu,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        m3 = np.zeros_like(otsu)
        cv2.drawContours(
            m3,
            contours,
            -1,
            255,
            thickness=cv2.FILLED
        )

        m3 = cv2.bitwise_or(otsu, m3)

        return m1, m2, m3


    # ----------------------------
    # 8. LIMPIEZA FINAL Y EXTRACCIÓN
    # ----------------------------
    def final_mask(self, mask, original):
        h, w = mask.shape
        flood_mask = np.zeros((h + 2, w + 2), np.uint8)

        filled = mask.copy()
        cv2.floodFill(filled, flood_mask, (0, 0), 255)
        filled_inv = cv2.bitwise_not(filled)

        rellenada = cv2.bitwise_or(mask, filled_inv)

        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5)
        )
        eroded = cv2.erode(rellenada, kernel)

        # Usar skimage para quitar fragmentos pequeños de ruido
        cleaned = remove_small_objects(
            eroded.astype(bool),
            10000
        )
        cleaned = (cleaned * 255).astype(np.uint8)

        dilated = cv2.dilate(cleaned, kernel)

        masked = cv2.bitwise_and(
            original,
            original,
            mask=dilated
        )

        return dilated, masked


    # ----------------------------
    # UTILIDAD BASE64
    # ----------------------------
    @staticmethod
    def to_b64(img):
        _, buffer = cv2.imencode('.png', img)
        return "data:image/png;base64," + base64.b64encode(buffer).decode()


# ----------------------------------
# DJANGO API
# ----------------------------------

class FourierUploadView(APIView):

    def post(self, request):
        image = request.FILES.get("image")

        if not image:
            return Response(
                {"error": "No image received"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 0. Iniciar procesador
            processor = FourierDiagnosticsProcessor(image.read())

            # 1. Denoise espacial
            denoised = processor.denoise()

            # 2. Análisis y Filtrado de Frecuencias (Gaussiano Alto)
            filtered, fourier = processor.fourier_filter(denoised)

            # 3. Retorno al Dominio Espacial
            img_back = processor.inverse_fourier(filtered)

            # 4. Mejora Analítica (Contraste y Morfología)
            clahe, morph = processor.enhance_contrast(img_back)

            # 5. Super Resolución de Bordes
            unsharp, gaussian, super_detail = processor.enhance_details(morph)

            # 6. Detección Base
            otsu, canny = processor.segmentation(super_detail)

            # 7. Unión de Regiones
            m1, m2, m3 = processor.refine(otsu, canny)

            # 8. Máscara Limpia y Extracción Final
            final_mask, masked_img = processor.final_mask(m2, super_detail)

            # 9. Empaquetar resultados
            results = [
                {"step": "original", "url": processor.to_b64(processor.img)},
                {"step": "gray", "url": processor.to_b64(processor.img_gray)},
                {"step": "denoise", "url": processor.to_b64(denoised)},
                {"step": "fourier spectrum", "url": processor.to_b64(fourier)},
                {"step": "inverse fourier", "url": processor.to_b64(img_back)},
                {"step": "clahe", "url": processor.to_b64(clahe)},
                {"step": "morph", "url": processor.to_b64(morph)},
                {"step": "unsharp", "url": processor.to_b64(unsharp)},
                {"step": "gaussian", "url": processor.to_b64(gaussian)},
                {"step": "super detail", "url": processor.to_b64(super_detail)},
                {"step": "otsu", "url": processor.to_b64(otsu)},
                {"step": "canny", "url": processor.to_b64(canny)},
                {"step": "method3", "url": processor.to_b64(m3)},
                {"step": "final mask", "url": processor.to_b64(final_mask)},
                {"step": "masked tumor", "url": processor.to_b64(masked_img)}
            ]

            return Response(results)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
