from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from core.utils import read_dicom_image, image_to_base64
from processing.dicom.pipeline_nodes import MedicalPipelineBuilderDicom
from ai.preprocessing.auto_enhacer import AutoDicomEnhancer
from ai.preprocessing.presets import BRAIN_PRESETS

router = APIRouter(prefix="/ai/dicom", tags=["AI DICOM Medical"])

@router.get("/presets")
async def get_brain_presets():
    """
    Retorna la lista de presets y estrategias predeterminadas para tejidos cerebrales.
    """
    return {"presets": BRAIN_PRESETS}


@router.post("/auto-enhance")
async def auto_enhance_brain_dicom(
    image: UploadFile = File(...),
    series_uid: Optional[str] = Form("default_series"),
    n_trials: Optional[int] = Form(10)
):
    """
    Pre-procesamiento con IA y Memoria Persistente/Caché:
    - Optimiza los filtros usando Optuna sólo en la primera corte de la serie.
    - Aplica la receta óptima aprendida instantáneamente (en ms) al resto de cortes.
    - Almacena el historial en base de datos SQLite para aprendizaje acumulativo.
    """
    img_bytes = await image.read()
    try:
        img_cv = read_dicom_image(img_bytes)
    except Exception as e:
        return {"error": f"No se pudo procesar la imagen DICOM: {str(e)}"}

    # 1. Obtener o calcular la mejor receta usando IA + Caché por Serie
    enhancer = AutoDicomEnhancer(n_trials=n_trials)
    optimization_result = enhancer.get_or_optimize_pipeline(img_cv, series_uid=series_uid)
    
    optimal_flow = optimization_result["optimal_flow"]
    
    # 2. Ejecutar el pipeline óptimo sobre la imagen en milisegundos
    pipeline_builder = MedicalPipelineBuilderDicom(img_cv)
    imagenes, traza = pipeline_builder.execute_flow(optimal_flow)
    
    # 3. Formatear la respuesta con traza y previews
    respuesta_nodos = []
    for node_id, info in traza.items():
        nodo_res = {
            "id": node_id,
            "filtro": info["filter"],
            "parent": info["parent"],
            "status": info["status"]
        }
        if info["status"] == "success" and node_id in imagenes:
            nodo_res["url"] = image_to_base64(imagenes[node_id])
        else:
            nodo_res["error"] = info.get("error", "Error desconocido")
            
        respuesta_nodos.append(nodo_res)
        
    final_node_id = optimal_flow[-1]["id"] if optimal_flow else "original"
    enhanced_url = image_to_base64(imagenes.get(final_node_id, imagenes["original"]))

    return {
        "enhanced_url": enhanced_url,
        "original_url": image_to_base64(imagenes["original"]),
        "quality_score": optimization_result.get("best_quality_score"),
        "from_cache": optimization_result.get("from_cache", False),
        "optimal_flow": optimal_flow,
        "nodos": respuesta_nodos
    }
