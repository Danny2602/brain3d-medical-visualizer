from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import cv2
import numpy as np
import base64
from skimage.morphology import remove_small_objects

class BrainDiagnosticsProcessor:
    """
    Clase dedicada exclusivamente a manipular los tensores y extraer info de la imagen.
    Mantiene cada 'etapa' de la transformación en funciones separadas.
    
    """
    def __init__(self, image_bytes):
        # 1. Lectura e inicialización
        self.img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        self.img = cv2.convertScaleAbs(self.img, alpha=1, beta=0)
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
    def denoise_and_enhance(self):
        # Filtro Non-Local Means (mejora ruido sin perder bordes a diferencia de Gaussian)
        denoised = cv2.fastNlMeansDenoising(self.img_gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Ecualización adaptativa (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        clahe_img = clahe.apply(denoised)
        
        # Top-Hat y Black-Hat (Resalta micro-estructuras)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        top_hat = cv2.morphologyEx(clahe_img, cv2.MORPH_TOPHAT, kernel)
        black_hat = cv2.morphologyEx(clahe_img, cv2.MORPH_BLACKHAT, kernel)
        
        morph_img = cv2.add(clahe_img, top_hat)
        morph_img = cv2.subtract(morph_img, black_hat)
        
        return denoised, clahe_img, morph_img
        
    def enhance_details(self, morph_img):
        # Unsharp (Re-enfoque)
        gaussian = cv2.GaussianBlur(morph_img, (0, 0), 3.0)
        unsharp = cv2.addWeighted(morph_img, 2.0, gaussian, -1.0, 0)
        
        # Laplaciano 2da derivada (Definición hiper fina)
        laplacian = cv2.Laplacian(unsharp, cv2.CV_64F, ksize=3)
        laplacian_abs = cv2.convertScaleAbs(laplacian)
        super_detail = cv2.addWeighted(unsharp, 0.85, laplacian_abs, 0.15, 0)
        return unsharp, super_detail
        
    def create_base_masks(self, denoised_img):
        # Otsu (Masa principal)
        mask_blur = cv2.GaussianBlur(denoised_img, (11, 11), 0)
        _, otsu = cv2.threshold(mask_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Canny (Bordes puros)
        canny = cv2.Canny(denoised_img, 20, 60)
        return otsu, canny
        
    def get_refinement_methods(self, otsu, canny):
        # Método 1 (Intersección estricta Canny + Otsu)
        m1 = cv2.bitwise_and(otsu, canny)
        
        # Método 2 (Or de Otsu con Bordes Canny Dilatados)
        kernel4 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        canny_dilated = cv2.dilate(canny, kernel4, iterations=2)
        m2 = cv2.bitwise_or(otsu, canny_dilated)
        
        # Método 3 (Relleno externo de silueta Otsu)
        contours, _ = cv2.findContours(otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        m3 = np.zeros_like(otsu)
        cv2.drawContours(m3, contours, -1, 255, thickness=cv2.FILLED)
        m3 = cv2.bitwise_or(otsu, m3)
        
        return m1, m2, m3
        
    def execute_final_segmentation(self, chosen_method,super_detail):
        """Toma el método refinado elegido y lo perfecciona tapando hoyos pequeños"""
        # FloodFill (El relleno de huecos del usuario)
        h, w = chosen_method.shape
        mask = np.zeros((h+2, w+2), np.uint8)
        filled = chosen_method.copy()
        cv2.floodFill(filled, mask, (0,0), 255)
        filled_inv = cv2.bitwise_not(filled)
        
        # ¡CORRECCIÓN!: bitwise_or es necesario para rellenar vacíos (sumamos interior blanco a la masa inicial)
        rellenada = cv2.bitwise_or(chosen_method, filled_inv)
        
        # Erosión
        kernel5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        eroded = cv2.erode(rellenada, kernel5)
        
        # Eliminación de artefactos y manchas pequeñas perdidas
        cleaned = remove_small_objects(eroded.astype(bool), 10000)
        cleaned_uint8 = (cleaned * 255).astype(np.uint8)
        
        # Dilatación de corrección final y aplicar máscara al original
        dilated_final = cv2.dilate(cleaned_uint8, kernel5)
        masked_img = cv2.bitwise_and(super_detail, super_detail, mask=dilated_final)
        
        return rellenada, eroded, cleaned_uint8, dilated_final, masked_img
        
    def calculate_fourier(self):
        f = np.fft.fft2(self.img_gray)
        fshift = np.fft.fftshift(f)
        magnitude = 20 * np.log(np.abs(fshift) + 1)
        return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    @staticmethod
    def to_b64(img):
        """Helper para empaquetar en protocolo Data URI rápido para React/Vue"""
        _, buffer = cv2.imencode('.png', img)
        return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"


class ImageUploadView(APIView):
    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No se recibió ninguna imagen'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 1. Inicializamos clase con lo recibido
            processor = BrainDiagnosticsProcessor(image.read())
            
            # 2. Empezamos el pipeline (Paso a paso, súper legible)
            denoised, clahe, morph = processor.denoise_and_enhance()
            unsharp, super_detail = processor.enhance_details(morph)
            otsu, canny = processor.create_base_masks(denoised)
            
            # 3. Aplicar las matemáticas de intersección que pediste
            m1, m2, m3 = processor.get_refinement_methods(otsu, canny)
            
            # 4. Elegimos el M3 como segmentación principal y generamos la foto recortada real
            rellenada, eroded, cleaned, dilated_final, masked_img = processor.execute_final_segmentation(m3,super_detail)
            
            # 5. Transformada de espectro
            fourier = processor.calculate_fourier()

            # Empaquetamos todo directamente a Base64 sin llenar la vista de lógica
            resultados = [
                {'result': 'original', 'url': processor.to_b64(processor.img)},
                {'result': 'grayscale', 'url': processor.to_b64(processor.img_gray)},
                {'result': 'blur Gaussian/NL', 'url': processor.to_b64(denoised)},
                {'result': 'CLAHE', 'url': processor.to_b64(clahe)},
                {'result': 'morph', 'url': processor.to_b64(morph)},
                {'result': 'unsharp', 'url': processor.to_b64(unsharp)},
                {'result': 'super detail', 'url': processor.to_b64(super_detail)},
                {'result': 'canny', 'url': processor.to_b64(canny)},
                {'result': 'otsu', 'url': processor.to_b64(otsu)},
                {'result': 'metodo 1 (And)', 'url': processor.to_b64(m1)},
                {'result': 'metodo 2 (Or+Dilate)', 'url': processor.to_b64(m2)},
                {'result': 'metodo 3 (Contours)', 'url': processor.to_b64(m3)},
                {'result': 'rellenada', 'url': processor.to_b64(rellenada)},
                {'result': 'eroded', 'url': processor.to_b64(eroded)},
                {'result': 'Eliminado pequeños objetos', 'url': processor.to_b64(cleaned)},
                {'result': 'dilated final', 'url': processor.to_b64(dilated_final)},
                {'result': 'masked', 'url': processor.to_b64(masked_img)},
                {'result': 'Fourier Transform', 'url': processor.to_b64(fourier)},
            ]

            return Response(resultados, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
