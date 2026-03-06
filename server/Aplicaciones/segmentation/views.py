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
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))#Kernel para dilatacion
                DIL = cv2.dilate(img_cany,kernel,iterations=2)#Imagen dilatada

                #Relleno de hueco
                h, w = DIL.shape #Obtener alto y ancho de la imagen
                mask = np.zeros((h+2, w+2), np.uint8) #Crear mascara para floodFill (debe ser 2 pixeles mas grande que la imagen)
                filled = DIL.copy()#Crear copia de la imagen
                cv2.floodFill(filled, mask, (0,0), 255)#Rellenar la mascara con el color 255 (blanco)
                filled_inv = cv2.bitwise_not(filled)#Invertir la imagen rellenada para obtener solo los objetos rellenos
                rellenada = cv2.bitwise_or(DIL, filled_inv)#Combinar la imagen dilatada con la imagen invertida para obtener la imagen con los objetos rellenos

                #erosion
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))#Kernel para erosion
                eroded = cv2.erode(rellenada,kernel)#

                #eliminacion de objetos pequeños
                P = remove_small_objects(eroded.astype(bool), 10000)
                P = (P * 255).astype(np.uint8)  # Convierte de bool a uint8 para imencode

                #diltacion final
                DIL2 = cv2.dilate(P.astype("uint8"),kernel)
                #imagen con mascara
                img_masked = cv2.bitwise_and(img,img,mask=DIL2)

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
                ]
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No se recibió ninguna imagen'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def convert_base64_to_image(self, img):
        import base64
        _, buffer_orig = cv2.imencode('.png', img)
        img_base64 = base64.b64encode(buffer_orig).decode('utf-8')
        return img_base64