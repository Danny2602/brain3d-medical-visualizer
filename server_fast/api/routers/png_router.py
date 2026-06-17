from fastapi import APIRouter, UploadFile, File, Form
import json
import cv2
import numpy as np

from processing.png.pipeline_nodes import MedicalPipelineBuilder
from processing.png.pipeline_linear import MedicalPipelineBuilder2
from core.utils import image_to_base64

router = APIRouter()

@router.post("/process-image-nodos")
async def process_image_nodos(image: UploadFile = File(...), flow_config_json: str = Form(...)):
    img_bytes = await image.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    try:
        instrucciones = json.loads(flow_config_json)
    except:
        instrucciones = []
        
    pipeline = MedicalPipelineBuilder(img_cv)
    imagenes, traza = pipeline.execute_flow(instrucciones)
    
    respuesta_api = []
    
    for node_id, info in traza.items():
        nodo_res = {
            "id": node_id,
            "filtro": info["filter"],
            "padre": info["parent"],
            "status": info["status"]
        }
        
        if info["status"] == "success" and node_id in imagenes:
            nodo_res["url"] = image_to_base64(imagenes[node_id])
        else:
            nodo_res["error"] = info.get("error", "Error desconocido")
            
        respuesta_api.append(nodo_res)
        
    return {
        "nodos": respuesta_api,
        "original_url": image_to_base64(imagenes['original'])
    }

@router.post("/process-image-lineal")
async def process_image_lineal(
    image: UploadFile = File(...), 
    flow_config_json: str = Form(...) 
):
    img_bytes = await image.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    try:
        instrucciones_react = json.loads(flow_config_json)
    except:
        instrucciones_react = []
        
    pipeline = MedicalPipelineBuilder2(img_cv)
    resultados_historial = pipeline.execute_flow(instrucciones_react)
    
    respuesta_api = []
    for paso_nombre, imagen_procesada in resultados_historial.items():
        respuesta_api.append({
            "nombre_filtro": paso_nombre,
            "url": image_to_base64(imagen_procesada)
        })
        
    return {"historial": respuesta_api}
