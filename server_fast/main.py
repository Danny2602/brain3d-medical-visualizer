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

from processing.pipeline import MedicalPipelineBuilder
from processing.pipeline2 import MedicalPipelineBuilder2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Herramienta de traducción de Fotografía a Texto
def image_to_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode('.png', img)
    return "data:image/png;base64," + base64.b64encode(buffer).decode()

# ESTE ES EL CORAZÓN DE TU CONEXIÓN CON REACT
@app.post("/api/process-image-nodos")
async def process_image_nodos(image: UploadFile = File(...), flow_config_json: str = Form(...)):
    # ... (Decodificación de imagen igual) ...
    img_bytes = await image.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    instrucciones = json.loads(flow_config_json)
        
    pipeline = MedicalPipelineBuilder(img_cv)
    # RECIBIMOS las imágenes Y la traza (quién es quién)
    imagenes, traza = pipeline.execute_flow(instrucciones)
    
    respuesta_api = []
    
    # Recorremos la traza para armar la respuesta enriquecida
    for node_id, info in traza.items():
        nodo_res = {
            "id": node_id,
            "filtro": info["filter"],
            "padre": info["parent"],
            "status": info["status"]
        }
        
        # Si fue exitoso y hay imagen, la convertimos a base64
        if info["status"] == "success" and node_id in imagenes:
            nodo_res["url"] = image_to_base64(imagenes[node_id])
        else:
            nodo_res["error"] = info.get("error", "Error desconocido")
            
        respuesta_api.append(nodo_res)
        
    # Devolvemos también la imagen 'original' por si el frontal la necesita
    return {
        "nodos": respuesta_api,
        "original_url": image_to_base64(imagenes['original'])
    }


# ESTE ES EL CORAZÓN DE TU CONEXIÓN CON REACT
@app.post("/api/process-image-lineal")
async def process_image_lineal(
    image: UploadFile = File(...), 
    flow_config_json: str = Form(...) 
):
    """
    1. image: Recibe la foto del tumor.
    2. flow_config_json: Recibe el orden de los filtros como texto JSON.
    """
    
    # Leer la imagen física hacia las matemáticas de Numpy 
    img_bytes = await image.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE) # Leemos directo en escala de grises
    
    # Traducir la lista que mandó React 
    try:
        instrucciones_react = json.loads(flow_config_json)
    except:
        instrucciones_react = []
        
    # Ejecutar LA MAGIA de tu Arquitectura Limpia 
    pipeline = MedicalPipelineBuilder2(img_cv)
    resultados_historial = pipeline.execute_flow(instrucciones_react)
    
    # Empaquetar de regreso a React 
    respuesta_api = []
    for paso_nombre, imagen_procesada in resultados_historial.items():
        respuesta_api.append({

            "nombre_filtro": paso_nombre,
            "url": image_to_base64(imagen_procesada)
        })
        
    return {"historial": respuesta_api}

