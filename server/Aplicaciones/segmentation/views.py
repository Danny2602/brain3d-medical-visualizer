from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import cv2
import numpy as np
import io

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
                # Codifica ambas imágenes a PNG en memoria
                _, buffer_orig = cv2.imencode('.png', img)
                _, buffer_gray = cv2.imencode('.png', img_gray)
                _, buffer_blur = cv2.imencode('.png', FIL)

                # Convierte a base64
                b64_orig = base64.b64encode(buffer_orig).decode('utf-8')
                b64_gray = base64.b64encode(buffer_gray).decode('utf-8')
                b64_blur = base64.b64encode(buffer_blur).decode('utf-8')

                # Formato data URI para fácil uso en frontend
                data = [
                    {'result':'original','url': f'data:image/png;base64,{b64_orig}'},
                    {'result':'grayscale','url': f'data:image/png;base64,{b64_gray}'},
                    {'result':'blur Gaussian','url': f'data:image/png;base64,{b64_blur}'},
                ]
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No se recibió ninguna imagen'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
