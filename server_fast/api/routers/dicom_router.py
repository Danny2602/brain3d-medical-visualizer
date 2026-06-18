from fastapi import APIRouter, UploadFile, File, Form
import json

from processing.dicom.pipeline_nodes import MedicalPipelineBuilderDicom

from core.utils import read_dicom_image, image_to_base64

router = APIRouter()

@router.post("/preview-dicom")
async def preview_dicom(
    image: UploadFile = File(...)
):
    img_bytes = await image.read()
    try:
        img_cv = read_dicom_image(img_bytes)
        return {"preview_url": image_to_base64(img_cv)}
    except Exception as e:
        return {"error": f"No se pudo leer el archivo DICOM: {str(e)}"}

@router.post("/process-dicom-nodos")
async def process_dicom_nodos(
    image: UploadFile = File(...), 
    flow_config_json: str = Form(...)
):
    img_bytes = await image.read()
    
    try:
        img_cv = read_dicom_image(img_bytes)
    except Exception as e:
        return {"error": f"No se pudo leer el archivo DICOM: {str(e)}"}

    try:
        instrucciones = json.loads(flow_config_json)
    except:
        instrucciones = []
        
    pipeline = MedicalPipelineBuilderDicom(img_cv)
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
