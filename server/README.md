# Brain3D Medical Visualizer

## Requisitos

- Python 3.8
- Django 3.2
- Django Rest Framework 3.13.1
- Pillow 9.2.0
- Scikit-Image 0.19.3
- OpenCV 4.6.0

## Desatalles
Este proyecto usa Django Rest Framework, por lo que es necesario tener instalados los siguientes paquetes:

```bash
pip install djangorestframework
pip install django-cors-headers
```

## Finalidad
El objetivo de este proyecto es crear una API REST que permita la visualización de imágenes de diagnóstico de la neurociencia. Esta API será utilizada por una aplicación web que permita a los usuarios realizar análisis de imágenes y visualizar los resultados en una interfaz de usuario.

## Estructura de la aplicación
La aplicación se divide en dos partes principales:

1. El servidor: Este es el componente que se encarga de procesar las imágenes y devolver los resultados en formato JSON.
2. La aplicación web: Esta es la aplicación que se encarga de mostrar los resultados de la API REST y permitir a los usuarios realizar análisis de imágenes.

### Servidor
El servidor se encarga de procesar las imágenes y devolver los resultados en formato JSON. Este proceso se realiza utilizando la librería OpenCV y las funciones de procesamiento de imagen disponibles en la librería Scikit-Image.

### Procesamiento de imágenes
El procesamiento de imágenes se realiza utilizando la librería OpenCV y las funciones de procesamiento de imagen disponibles en la librería Scikit-Image. Estas funciones se utilizan para realizar operaciones como la denoise, la mejora de detalles, la creación de máscaras base, la refinación de segmentación y la transformación de espectro.

### Que Procesos Se Realizan

1. Lectura de la imagen: La imagen se lee desde el servidor y se almacena en una variable de memoria.
2. Denoisa y mejora de detalles: La imagen se denoisea utilizando el filtro Non-Local Means (NLM) y se mejora con el filtro CLAHE (Contrast Limited Adaptive Histogram Equalization).
3. Mejora de detalles: La imagen se mejora con el filtro Laplacian 2D (Diferencia de 2D).
4. Creación de máscaras base: Se crean dos máscaras básicas: una para la detección de bordes puros y otra para la detección de bordes blancos.
5. Refinación de segmentación: Se realizan tres métodos de refinación de segmentación: Método 1, Método 2 y Método 3.
6. Transformación de espectro: Se realiza una transformación de espectro utilizando la función de transformación de espectro de Fourier.
7. Almacenamiento de resultados: Los resultados se almacenan en una lista de diccionarios, donde cada elemento representa una imagen y su URL en Base64.

## API REST
La API REST se encarga de procesar las imágenes y devolver los resultados en formato JSON. Este proceso se realiza utilizando la librería OpenCV y las funciones de procesamiento de imagen disponibles en la librería Scikit-Image.

### Endpoint

- POST /api/image-upload/

### Request

```json
{
    "image": "BASE64_ENCODING_OF_IMAGE"
}
```

### Response

```json
[
    {
        "result": "original",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "grayscale",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "blur Gaussian/NL",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "CLAHE",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "morph",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "unsharp",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "super detail",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "canny",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "otsu",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "metodo 1 (And)",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "metodo 2 (Or+Dilate)",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "metodo 3 (Contours)",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "rellenada",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "eroded",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "Eliminado pequeños objetos",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "dilated final",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "masked",
        "url": "BASE64_ENCODING_OF_IMAGE"
    },
    {
        "result": "Fourier Transform",
        "url": "BASE64_ENCODING_OF_IMAGE"
    }
]
```

