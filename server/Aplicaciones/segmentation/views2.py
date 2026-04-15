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
    """
    --- FILTRO ANULADO ---
    Generaba exceso de afilado compitiendo con DetailEnhancer.
    Conceptualmente redundante en este pipeline.
    ----------------------
    """
    def apply(self, img_gray):
        # f = np.fft.fft2(img_gray)
        # fshift = np.fft.fftshift(f)

        # rows, cols = img_gray.shape
        # crow, ccol = rows // 2, cols // 2
        # x, y = np.meshgrid(np.arange(cols), np.arange(rows))
        # dist_center = np.sqrt((x - ccol)**2 + (y - crow)**2)
        
        # # D0 (Frecuencia de corte): Mantiene las estructuras principales.
        # D0 = 30.0 
        # hpf = 1.0 - np.exp(-(dist_center**2) / (2 * (D0**2)))
        
        # high_freq_emphasis = 0.5 + 0.3 * hpf
        # filtered = fshift * high_freq_emphasis

        # # Regreso al dominio espacial directamente aquí
        # f_ishift = np.fft.ifftshift(filtered)
        # img_back = np.fft.ifft2(f_ishift)
        # img_back = np.abs(img_back)
        # img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # # Solo para visualización web
        # magnitude = 20 * np.log(np.abs(fshift) + 1)
        # magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # return img_back, magnitude
        pass


class IlluminationCorrector(ImageFilter):
    """
    Controla el balance de luz global mediante transformaciones matemáticas.
    """
    def apply(self, img_gray, mode="gamma", factor=1.2):
        # Convertimos la imagen de [0 a 255] a rango flotante [0.0 a 1.0] 
        # para que las matemáticas exponenciales no den errores de desbordamiento.
        img_float = img_gray.astype(np.float32) / 255.0

        if mode == "log":
            # TRANSFORMACIÓN LOGARÍTMICA: s = c * log(1 + r)
            # Expande drásticamente las zonas negras revelando detalles ocultos en las sombras.
            c = 1.0 / np.log(1.0 + np.max(img_float))
            transformed = c * np.log(1.0 + img_float)

        elif mode == "gamma" or mode == "exp":
            # TRANSFORMACIÓN EXPONENCIAL (Gamma): s = c * r^gamma
            # factor > 1: Efecto "apagar la luz", oscurece todo excepto lo más brillante.
            # factor < 1: Actúa parecido al logaritmo, aclarando la imagen.
            transformed = np.power(img_float, factor)

        else:
            transformed = img_float

        # Regresamos la imagen a escala OpenCV (0 a 255 en uint8)
        return (transformed * 255).astype(np.uint8)


class HistogramStretcher(ImageFilter):
    """
    Mejora: Expansión de Contraste Lineal (Min-Max Normalization).
    Estira los valores de los píxeles (del más oscuro al más claro) para que ocupen todo el rango [0, 255].
    Garantiza que el contraste base sea ancho antes de pasarlo al ecualizador local adaptativo.
    """
    def apply(self, img_gray):
        # cv2.normalize realiza la expansión de contraste lineal matemática:
        stretched = cv2.normalize(img_gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return stretched


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
        _, otsu = cv2.threshold(img_detail, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        canny = cv2.Canny(img_detail, 350, 400) # Canny sí sobre el detalle para no perder perímetro

        return otsu, canny


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
    """Procesa el recorte final mediante análisis de Componentes Conexas."""
    def apply(self, mask, original_img):
        # Ejecutar el Algoritmo de Componentes Conexas
        # connectivity=8 evalúa píxeles vecinos en todas las direcciones (diagonales incluidas)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
        
        # Si la imagen está completamente en negro (solo hay fondo/label 0), retornamos
        if num_labels <= 1:
            return mask, cv2.bitwise_and(original_img, original_img, mask=mask)

        # Definir el tamaño mínimo aceptado (1.5% de la imagen)
        h, w = mask.shape
        min_size = int((h * w) * 0.015) 
        
        # Matriz vacía donde dibujaremos solo los componentes válidos
        cleaned_mask = np.zeros_like(mask)
        
        # Iterar sobre todos los componentes encontrados
        # Empezamos el bucle en 1 para ignorar el índice 0 (que siempre es el fondo negro)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]  # Extraer el área en píxeles del componente actual
            
            # Si supera el umbral, "encendemos" todos los píxeles de ese componente
            if area >= min_size:
                cleaned_mask[labels == i] = 255
                
        # ==============================================================================
        # EN caso de necesidad, puedes extraer el componente más grande: (Tener en cuenta esto para pruebas)
        # Si en algún momento necesitas extraer ESTRICTAMENTE el tumor principal y
        # borrar cualquier otra mancha flotante sin importar su tamaño, borras el  
        # bucle "for" de arriba e insertas esto para extraer el componente más grande:
        #
        # largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        # cleaned_mask[labels == largest_label] = 255
        # ==============================================================================

        # 4. Aislar el tejido en la imagen original
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
        self.illumination = IlluminationCorrector()
        self.stretcher = HistogramStretcher()

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
        #El factor 1.5 es para corregir la iluminación, se puede ajustar si es necesario para que la imagen se vea mas clara o mas oscura
        illum_fixed = self.illumination.apply(denoised, mode="gamma", factor=1.5)
        
        # ---> MEJORA ANTES DE CLAHE <---
        # Aseguramos que el contraste base ocupe todo el rango 0-255 con una expansión asimétrica.
        stretched = self.stretcher.apply(illum_fixed)
        
        # --- FILTRO DE FOURIER ANULADO POR REDUNDANCIA ---
        # img_back, fourier_mag = self.fourier_filter.apply(stretched)
        
        # Pasa la imagen con expansión de contraste al potenciador adaptativo
        clahe, morph = self.enhancer.apply(stretched) 
        unsharp, gaussian, super_detail = self.detailer.apply(morph)
        
        otsu, canny = self.segmenter.apply(super_detail)
        m1, m2_closed, m3_filled = self.refiner.apply(otsu, canny)
        
        final_mask, masked_img = self.extractor.apply(m3_filled, super_detail)

        return {
            "original": self.img,
            "gray": self.img_gray,
            "denoise": denoised,
            "illumination fixed": illum_fixed,
            "contrast stretched": stretched,
            # "fourier spectrum": fourier_mag,      # ANULADO
            # "inverse fourier": img_back,          # ANULADO
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