import cv2
import numpy as np
import base64
from skimage.morphology import remove_small_objects

# ==========================================
# Si quieres agregar un nuevo filtro, 
# solo creas una clase que herede de ImageFilter sin tocar lo demás.
# Procesamiento de imagenes medicas para segementacion test fourier

class ImageFilter:
    """Clase base para todos los filtros de procesamiento."""
    def apply(self, img, **kwargs):
        raise NotImplementedError("Debe implementar el método apply")


# ==========================================
# MÓDULOS DE PROCESAMIENTO 
# ==========================================

class DenoiseFilter(ImageFilter):
    """Encargado EXCLUSIVAMENTE de limpiar el ruido espacial de origen."""
    def apply(self, img_gray):
        # NlMeans es excelente para ruido de sensor.
        return cv2.fastNlMeansDenoising(img_gray, None, h=10, templateWindowSize=7, searchWindowSize=21)


class FourierHighPassFilter(ImageFilter):
    """Encargado de la transformación y resaltado de frecuencias (Bordes gruesos)."""
    def apply(self, img_gray):
        f = np.fft.fft2(img_gray)
        fshift = np.fft.fftshift(f)

        rows, cols = img_gray.shape
        crow, ccol = rows // 2, cols // 2
        x, y = np.meshgrid(np.arange(cols), np.arange(rows))
        dist_center = np.sqrt((x - ccol)**2 + (y - crow)**2)
        
        # D0 (Frecuencia de corte): Mantiene las estructuras principales.
        D0 = 30.0 
        hpf = 1.0 - np.exp(-(dist_center**2) / (2 * (D0**2)))
        
        high_freq_emphasis = 0.5 + 0.3 * hpf
        filtered = fshift * high_freq_emphasis

        # Regreso al dominio espacial directamente aquí
        f_ishift = np.fft.ifftshift(filtered)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Solo para visualización web
        magnitude = 20 * np.log(np.abs(fshift) + 1)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        return img_back, magnitude


class ContrastEnhancer(ImageFilter):
    """
    Controla CLAHE y Morfología.
    AQUÍ SOLUCIONAMOS EL RUIDO: Reducimos la sensibilidad en zonas planas.
    """
    def apply(self, img):
        # SOLUCIÓN RUIDO CLAHE:
        # clipLimit bajó de 2.5 a 1.2. 
        # ¿Por qué?: Los cerebros tienen mucho líquido/zonas planas planas. Un clipLimit alto 
        # genera ruido granular (arena) en esas zonas. 1.2 o 1.5 es suave y natural para tejidos.
        clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
        clahe_img = clahe.apply(img)

        # SOLUCIÓN RUIDO TOP-HAT:
        # Antes de extraer "detalles luminosos" (Top-Hat), PLANCHAMOS el micro-ruido con un bilateral suave.
        # De esta forma, Top-Hat solo capturará vasos sanguíneos reales y no píxeles corruptos.
        smoothed_for_morph = cv2.bilateralFilter(clahe_img, d=5, sigmaColor=35, sigmaSpace=35)

        # Kernel elíptico (simula formas celulares/orgánicas)
        rows, cols = img.shape
        k_size = max(3, min(rows, cols) // 50) 
        if k_size % 2 == 0: k_size += 1
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
        
        top_hat = cv2.morphologyEx(smoothed_for_morph, cv2.MORPH_TOPHAT, kernel)
        black_hat = cv2.morphologyEx(smoothed_for_morph, cv2.MORPH_BLACKHAT, kernel)

        morph = cv2.add(clahe_img, top_hat)
        morph = cv2.subtract(morph, black_hat)

        return clahe_img, morph


class DetailEnhancer(ImageFilter):
    """Extrae texturas y afina bordes mediante Unsharp y Laplaciano."""
    def apply(self, img):
        # Unsharp Masking Suave: Reducimos la agresividad de 2.0 a 1.5
        gaussian = cv2.GaussianBlur(img, (0, 0), 2)
        unsharp = cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)

        # SOLUCIÓN RUIDO LAPLACIANO:
        # El Laplaciano es un imán de ruido. Si lo aplicamos directo, estalla.
        # Filtramos la imagen SOLO para calcular el Laplaciano, así evitamos derivar el ruido base.
        smooth_for_laplacian = cv2.bilateralFilter(unsharp, d=5, sigmaColor=40, sigmaSpace=40)
        
        laplacian = cv2.Laplacian(smooth_for_laplacian, cv2.CV_64F, ksize=3)
        laplacian_abs = cv2.convertScaleAbs(laplacian)

        # Bajamos la opacidad del laplaciano (ruido) a solo 10% de impacto (antes 15%).
        super_detail = cv2.addWeighted(unsharp, 0.90, laplacian_abs, 0.10, 0)
        
        return unsharp, gaussian, super_detail


class IntelligentSegmenter(ImageFilter):
    """Binarización inteligente combinando Otsu y Canny."""
    def apply(self, img_detail):
        # Planchado masivo de texturas previo a segmentación. 
        # Mantiene bordes afilados para no perder la forma del tumor.
        blur = cv2.bilateralFilter(img_detail, 9, 75, 75)

        _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        canny = cv2.Canny(img_detail, 350, 400) # Canny sí sobre el detalle para no perder perímetro

        return otsu, canny

# class IntelligentSegmenter(ImageFilter):
#     """Binarización inteligente combinando KMeans y Canny dinámico."""
#     def apply(self, img_detail):
#         blur = cv2.bilateralFilter(img_detail, 9, 75, 75)

#         # 1. K-MEANS CLUSTERING EN LUGAR DE OTSU
#         # Buscamos 4 grupos (Fondo, Tejido Oscuro, Tejido Intermedio, Tumor/Hueso brillante)
#         Z = blur.reshape((-1, 1))
#         Z = np.float32(Z)
#         criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
#         K = 4
#         _, label, centers = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
#         # Recuperar la imagen segmentada en niveles
#         centers = np.uint8(centers)
#         res = centers[label.flatten()]
#         segmented_img = res.reshape((img_detail.shape))
        
#         # Aislar únicamente el clúster más brillante (Tumor/Cráneo)
#         max_intensity = np.max(centers)
#         _, optimal_mask = cv2.threshold(segmented_img, max_intensity - 1, 255, cv2.THRESH_BINARY)

#         # 2. CANNY DINÁMICO (Mejora el punto 2)
#         v = np.median(img_detail)
#         lower = int(max(0, (1.0 - 0.33) * v))
#         upper = int(min(255, (1.0 + 0.33) * v))
#         canny = cv2.Canny(img_detail, lower, upper)

#         # Retornamos kmeans en lugar de otsu
#         return optimal_mask, canny



class MaskConnectivityRefiner(ImageFilter):
    """
    Restaura fracturas y limpia ruido aislando LA MÁSCARA BINARIA de acuerdo 
    al modelo de conectividades (4-vecinos y 8-vecinos).
    """
    def apply(self, otsu, canny):
        m1_or = cv2.bitwise_or(otsu, canny)
        
        # Conectividad 4 (Mínima): Borra granitos de arena aislados.
        kernel_4 = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        opened = cv2.morphologyEx(m1_or, cv2.MORPH_OPEN, kernel_4)
        
        # Conectividad 8 (Evolucionada 5x5): Rellena las grietas entre tumores fragmentados.
        kernel_8_thick = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_8_thick)
        
        # Relleno de agujeros internos
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        m3_filled = np.zeros_like(otsu)
        cv2.drawContours(m3_filled, contours, -1, 255, thickness=cv2.FILLED)

        final_m3 = cv2.bitwise_or(closed, m3_filled)
        return m1_or, closed, final_m3




class TissueExtractor(ImageFilter):
    """Procesa el recorte final mediante proporciones dinámicas."""
    def apply(self, mask, original_img):
        # Evaluar el tamaño por el % de la imagen total
        h, w = mask.shape
        total_pixels = h * w
        
        # Umbral: Eliminar todo lo que sea menor al 1.5% del área total de la imagen
        min_size = int(total_pixels * 0.015) 
        
        cleaned_mask = remove_small_objects(mask.astype(bool), min_size)
        cleaned_mask = (cleaned_mask * 255).astype(np.uint8)

        masked_tumor = cv2.bitwise_and(original_img, original_img, mask=cleaned_mask)
        return cleaned_mask, masked_tumor

# ==========================================
# PIPELINE ORQUESTADOR 
# ==========================================

class MedicalDiagnosticPipeline:
    """
    Orquesta los filtros paso a paso. Cumple Inversión de Dependencias y 
    Responsabilidad única, ya que solo delega, no calcula.
    """
    def __init__(self, image_bytes):
        self.img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        self.img = cv2.convertScaleAbs(self.img, alpha=1, beta=0)
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Instanciar submódulos
        self.denoise_filter = DenoiseFilter()
        self.fourier_filter = FourierHighPassFilter()
        self.enhancer = ContrastEnhancer()
        self.detailer = DetailEnhancer()
        self.segmenter = IntelligentSegmenter()
        self.refiner = MaskConnectivityRefiner()
        self.extractor = TissueExtractor()

    def process_all(self):
        """Ejecuta el pipeline de procesamiento fotograma a fotograma."""
        denoised = self.denoise_filter.apply(self.img_gray)
        img_back, fourier_mag = self.fourier_filter.apply(denoised)
        
        clahe, morph = self.enhancer.apply(img_back)
        unsharp, gaussian, super_detail = self.detailer.apply(morph)
        
        otsu, canny = self.segmenter.apply(super_detail)
        m1, m2_closed, m3_filled = self.refiner.apply(otsu, canny)
        
        final_mask, masked_img = self.extractor.apply(m3_filled, super_detail)

        return {
            "original": self.img,
            "gray": self.img_gray,
            "denoise": denoised,
            "fourier spectrum": fourier_mag,
            "inverse fourier": img_back,
            "clahe": clahe,
            "top/black-hat": morph,
            "unsharp": unsharp,
            "gaussian": gaussian,
            "super detail": super_detail,
            "otsu": otsu,
            "canny": canny,
            "m1_or": m1,
            "m2_closed": m2_closed,
            "method3_filled": m3_filled,
            "final cleaned mask": final_mask,
            "masked tumor": masked_img
        }

    @staticmethod
    def to_b64(img):
        """Herramienta de conversión aislada."""
        _, buffer = cv2.imencode('.png', img)
        return "data:image/png;base64," + base64.b64encode(buffer).decode()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class FourierUploadView(APIView):

    def post(self, request):
        image = request.FILES.get("image")

        if not image:
            return Response({"error": "No image received"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Nuestro pipeline ahora es limpio y orientado a objetos
            pipeline = MedicalDiagnosticPipeline(image.read())
            results_dict = pipeline.process_all()

            # Mapeo a respuesta API iterando de manera robusta
            api_response = [
                {"result": name, "url": MedicalDiagnosticPipeline.to_b64(img)}
                for name, img in results_dict.items()
            ]

            return Response(api_response)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )