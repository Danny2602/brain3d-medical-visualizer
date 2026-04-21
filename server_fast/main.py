# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import cv2
import numpy as np
import base64

# Importamos TU orquestador
from processing.pipeline import MedicalPipelineBuilder

app = FastAPI()

# Permiso mágico para que React no tenga el famoso y doloroso "Error de CORS"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiarlo por la URL de tu React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Herramienta de traducción de Fotografía a Texto
def image_to_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode('.png', img)
    return "data:image/png;base64," + base64.b64encode(buffer).decode()

# ESTE ES EL CORAZÓN DE TU CONEXIÓN CON REACT
@app.post("/process-image")
async def process_image(
    image: UploadFile = File(...), 
    flow_config_json: str = Form(...) 
):
    """
    1. image: Recibe la foto del tumor.
    2. flow_config_json: Recibe el orden de los filtros como texto JSON.
    """
    
    # --- PASO 1: Leer la imagen física hacia las matemáticas de Numpy ---
    img_bytes = await image.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE) # Leemos directo en escala de grises
    
    # --- PASO 2: Traducir la lista que mandó React ---
    try:
        instrucciones_react = json.loads(flow_config_json)
    except:
        instrucciones_react = []
        
    # --- PASO 3: Ejecutar LA MAGIA de tu Arquitectura Limpia ---
    pipeline = MedicalPipelineBuilder(img_cv)
    resultados_historial = pipeline.execute_flow(instrucciones_react)
    
    # --- PASO 4: Empaquetar de regreso a React ---
    respuesta_api = []
    for paso_nombre, imagen_procesada in resultados_historial.items():
        respuesta_api.append({
            "nombre_filtro": paso_nombre,
            "url": image_to_base64(imagen_procesada)
        })
        
    return {"historial": respuesta_api}

