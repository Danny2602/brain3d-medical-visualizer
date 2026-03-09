from django.shortcuts import render

from networkx import edges
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import cv2
import numpy as np
import io
from skimage.morphology import remove_small_objects

class ImageUploadView(APIView):
    def post(self, request):
        import base64
        image = request.FILES.get('image')
        try:
            if image:
                file_bytes = np.frombuffer(image.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR) #Imagen en RGB original 
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #Imagen en escala de grises
                FIL = cv2.GaussianBlur(img_gray, (5, 5), 0) #Imagen en escala de grises con blur
                img_cany = cv2.Canny(FIL, 10, 50) #Imagen con bordes detectados


                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))#Kernel para dilatacion
                DIL = cv2.dilate(img_cany,kernel,iterations=2)#Imagen dilatada

                #Fourier Transform
                # Aplicar FFT 2D
                f = np.fft.fft2(img_gray)

                # Mover frecuencias bajas al centro
                fshift = np.fft.fftshift(f)

                # Magnitud para visualizar
                magnitude = 20 * np.log(np.abs(fshift) + 1)



                #Relleno de hueco
                h, w = DIL.shape #Obtener alto y ancho de la imagen
                mask = np.zeros((h+2, w+2), np.uint8) #Crear mascara para floodFill (debe ser 2 pixeles mas grande que la imagen)
                filled = DIL.copy()#Crear copia de la imagen
                cv2.floodFill(filled, mask, (0,0), 255)#Rellenar la mascara con el color 255 (blanco)
                filled_inv = cv2.bitwise_not(filled)#Invertir la imagen rellenada para obtener solo los objetos rellenos
                rellenada = cv2.bitwise_or(DIL, filled_inv)#Combinar la imagen dilatada con la imagen invertida para obtener la imagen con los objetos rellenos

                #erosion
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))#Kernel para erosion
                eroded = cv2.erode(rellenada,kernel)#

                #eliminacion de objetos pequeños
                P = remove_small_objects(eroded.astype(bool), 10000)
                P = (P * 255).astype(np.uint8)  # Convierte de bool a uint8 para imencode

                
                #diltacion final
                DIL2 = cv2.dilate(P.astype("uint8"),kernel)
                #imagen con mascara
                img_masked = cv2.bitwise_and(img_gray,img_gray,mask=DIL2)

                # Convierte a base64 y formato data URI para fácil uso en frontend
                b64_orig = self.convert_base64_to_image(img)
                b64_gray = self.convert_base64_to_image(img_gray)
                b64_blur = self.convert_base64_to_image(FIL)
                b64_cany = self.convert_base64_to_image(img_cany)
                b64_dil = self.convert_base64_to_image(DIL)
                b64_rellenada = self.convert_base64_to_image(rellenada) 
                b64_eroded = self.convert_base64_to_image(eroded)
                b64_p = self.convert_base64_to_image(P)
                b64_dil2 = self.convert_base64_to_image(DIL2)
                b64_masked = self.convert_base64_to_image(img_masked)
                b64_Fourier = self.convert_base64_to_image(magnitude)

                # Formato data URI para fácil uso en frontend
                data = [
                    {'result':'original','url': f'data:image/png;base64,{b64_orig}'},
                    {'result':'grayscale','url': f'data:image/png;base64,{b64_gray}'},
                    {'result':'blur Gaussian','url': f'data:image/png;base64,{b64_blur}'},
                    {'result':'canny','url': f'data:image/png;base64,{b64_cany}'},
                    {'result':'dilated','url': f'data:image/png;base64,{b64_dil}'},
                    {'result':'rellenada','url': f'data:image/png;base64,{b64_rellenada}'},
                    {'result':'eroded','url': f'data:image/png;base64,{b64_eroded}'},
                    {'result':'Eliminado pequeños objetos','url': f'data:image/png;base64,{b64_p}'},
                    {'result':'dilated final','url': f'data:image/png;base64,{b64_dil2}'},
                    {'result':'masked','url': f'data:image/png;base64,{b64_masked}'},
                    {'result':'Fourier Transform','url': f'data:image/png;base64,{b64_Fourier}'},
                ]
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No se recibió ninguna imagen'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
   

   
    def convert_base64_to_image(self, img): # Convierte a base64 y formato data URI para fácil uso en frontend
        import base64
        _, buffer_orig = cv2.imencode('.png', img)
        img_base64 = base64.b64encode(buffer_orig).decode('utf-8')
        return img_base64



# class ImageUploadView(APIView):
#     def post(self, request):
#         image = request.FILES.get('image')
#         try:
#             if not image:
#                 return Response({'error': 'No se recibió ninguna imagen'}, status=status.HTTP_400_BAD_REQUEST)

#             file_bytes = np.frombuffer(image.read(), np.uint8)
#             img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#             if img is None:
#                 return Response({'error': 'Imagen inválida o corrupta'}, status=status.HTTP_400_BAD_REQUEST)

#             # ---------------------------------------------------------
#             # 1. Escala de grises (Base)
#             # ---------------------------------------------------------
#             img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#             # ---------------------------------------------------------
#             # 2. Eliminación de Ruido Cuántico (Non-Local Means)
#             # Mucho más poderoso que Gaussian. Limpia la "estática" de
#             # rayos X e IRM borrosas pero preserva intacta la anatomía.
#             # ---------------------------------------------------------
#             img_denoised = cv2.fastNlMeansDenoising(img_gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

#             # ---------------------------------------------------------
#             # 3. Ecualización Adaptativa Paramétrica (CLAHE)
#             # Nivelamos las luces. Evita que partes del cerebro queden oscuras.
#             # ---------------------------------------------------------
#             clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
#             img_clahe = clahe.apply(img_denoised)

#             # ---------------------------------------------------------
#             # 4. Extracción de Micro-Estructuras (Top-Hat & Black-Hat)
#             # LA MAGIA PARA IMÁGENES BORROSAS. 
#             # Top-Hat: Resalta vasos sanguíneos/tejido denso minúsculo.
#             # Black-Hat: Profundiza los surcos y fisuras cerebrales.
#             # Fórmula: Imagen Original + TopHat - BlackHat
#             # ---------------------------------------------------------
#             kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
#             top_hat = cv2.morphologyEx(img_clahe, cv2.MORPH_TOPHAT, kernel_morph)
#             black_hat = cv2.morphologyEx(img_clahe, cv2.MORPH_BLACKHAT, kernel_morph)
            
#             # Combinamos la extracción estructural
#             img_morph_enhanced = cv2.add(img_clahe, top_hat)
#             img_morph_enhanced = cv2.subtract(img_morph_enhanced, black_hat)

#             # ---------------------------------------------------------
#             # 5. Máscara de Desenfoque (Unsharp Masking - Re-enfoque HD)
#             # Si el escáner del cerebro quedó borroso o movido, 
#             # forzamos el aislamiento de bordes ocultos y los afilamos x2.
#             # ---------------------------------------------------------
#             gaussian_blur = cv2.GaussianBlur(img_morph_enhanced, (0, 0), 3.0)
#             img_unsharp = cv2.addWeighted(img_morph_enhanced, 2.0, gaussian_blur, -1.0, 0)

#             # ---------------------------------------------------------
#             # 6. Definición Hiper-Fina (Laplaciano de 2da Derivada)
#             # Detectamos las fronteras moleculares más finas del tejido y
#             # las inyectamos suavemente (15%) al tejido ya enfocado (85%).
#             # ---------------------------------------------------------
#             laplacian = cv2.Laplacian(img_unsharp, cv2.CV_64F, ksize=3)
#             laplacian_abs = cv2.convertScaleAbs(laplacian)
#             img_super_detail = cv2.addWeighted(img_unsharp, 0.85, laplacian_abs, 0.15, 0)

#             # ---------------------------------------------------------
#             # 7. Segmentación del Cráneo / Fondo (Ostracismo de Ruido Exterior)
#             # Ahora que el cerebro es súper nítido, cortamos matemáticamente
#             # el cráneo exterior o el fondo negro usando el Método de Otsu.
#             # ---------------------------------------------------------
#             mask_blur = cv2.GaussianBlur(img_denoised, (11, 11), 0)
#             _, mask_otsu = cv2.threshold(mask_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
#             # Limpiamos orificios residuales en la máscara
#             kernel_mask = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
#             mask_clean = cv2.morphologyEx(mask_otsu, cv2.MORPH_OPEN, kernel_mask, iterations=2)
#             mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_mask, iterations=3)
            
#             # Recortamos el tejido perfecto (Cerebro HD levitando sobre negro absoluto)
#             img_final_isolated = cv2.bitwise_and(img_super_detail, img_super_detail, mask=mask_clean)

#             # ---------------------------------------------------------
#             # 8. Transformada Rápida de Fourier (Diagnóstico de Frecuencias)
#             # Convertimos la información espacial en dominios de frecuencia para análisis.
#             # ---------------------------------------------------------
#             f = np.fft.fft2(img_super_detail)
#             fshift = np.fft.fftshift(f)
#             magnitude = 20 * np.log(np.abs(fshift) + 1)
#             magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

#             # ---------------------------------------------------------
#             # 9. Mapas de Densidad Tisular (Radiología en Falso Color)
#             # Traduce variaciones minúsculas de grises a colores espectrales
#             # donde el ojo humano puede diferenciar tumores o anomalías con facilidad.
#             # ---------------------------------------------------------
#             # INFERNO: Excelente para neuroimagen (resalta la actividad térmica/densidad)
#             img_heatmap = cv2.applyColorMap(img_final_isolated, cv2.COLORMAP_INFERNO)
#             # BONE: El estándar clínico para Resonancia/Rayos X, imita película radiográfica mejorada
#             img_bone = cv2.applyColorMap(img_final_isolated, cv2.COLORMAP_BONE)

#             # ---------------------------------------------------------
#             # 10. Ensamblaje y Exportación para el Frontend
#             # ---------------------------------------------------------
#             resultados_generados = [
#                 {'result': 'Original', 'image': img},
#                 {'result': 'Limpieza Anti-Estática (NL Means)', 'image': img_denoised},
#                 {'result': 'Nivelación de Sombras (CLAHE)', 'image': img_clahe},
#                 {'result': 'Revelado de Fisuras (Top-Hat/Black-Hat)', 'image': img_morph_enhanced},
#                 {'result': 'Re-Enfoque HD (Unsharp Mask)', 'image': img_unsharp},
#                 {'result': 'Micro-Texturas (Blend Laplaciano)', 'image': img_super_detail},
#                 {'result': 'Extracción Pura (Aislado + Otsu)', 'image': img_final_isolated},
#                 {'result': 'Densidad Neurológica (Mapa Inferno)', 'image': img_heatmap},
#                 {'result': 'Film Clínico Mejorado (Filtro Bone)', 'image': img_bone},
#                 {'result': 'Diagnóstico Espectral (Transformada Fourier)', 'image': magnitude},
#             ]

#             data = []
#             for item in resultados_generados:
#                 b64_str = self.convert_base64_to_image(item['image'])
#                 data.append({
#                     'result': item['result'],
#                     'url': f'data:image/png;base64,{b64_str}'
#                 })

#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#     # ---------------------------------------------------------
#     # FUNCIÓN INTACTA: Retenemos y respetamos tu codificador Base64
#     # ---------------------------------------------------------
#     def convert_base64_to_image(self, img):
#         import base64
#         _, buffer_orig = cv2.imencode('.png', img)
#         img_base64 = base64.b64encode(buffer_orig).decode('utf-8')
#         return img_base64
