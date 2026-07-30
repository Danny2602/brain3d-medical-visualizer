from fastapi import APIRouter, UploadFile, File

from core.utils import read_dicom_image, image_to_base64
from processing.dicom.pipeline_nodes import MedicalPipelineBuilderDicom
from ai.preprocessing.auto_enhacer import AutoDicomEnhancer
from ai.preprocessing.presets import BRAIN_PRESETS

router = APIRouter(prefix="/ai/dicom", tags=["AI DICOM Medical"])

# Instancia global del optimizador (mantiene la caché en RAM durante la sesión del servidor)
_enhancer = AutoDicomEnhancer()

@router.get("/presets")
async def get_brain_presets():
    """Retorna las estrategias radiológicas predeterminadas para tejidos cerebrales."""
    return {"presets": BRAIN_PRESETS}


@router.post("/auto-enhance")
async def auto_enhance_brain_dicom(image: UploadFile = File(...)):
    """
    Pre-procesamiento automático con IA:
    - La IA detecta automáticamente el tipo de imagen y genera el ID de serie.
    - Explora 20 combinaciones de filtros con Optuna la primera vez.
    - Para imágenes del mismo estudio, aplica el resultado en milisegundos desde caché.
    - Re-optimiza automáticamente si la calidad baja en algún corte.
    """
    img_bytes = await image.read()
    try:
        img_cv = read_dicom_image(img_bytes)
    except Exception as e:
        return {"error": f"No se pudo procesar la imagen DICOM: {str(e)}"}

    # La IA gestiona todo internamente (serie, caché, re-optimización)
    optimization_result = _enhancer.get_or_optimize_pipeline(img_cv)
    optimal_flow = optimization_result["optimal_flow"]

    if not optimal_flow:
        return {"error": "La IA no pudo generar un pipeline de mejora."}

    # Ejecutar el pipeline óptimo sobre la imagen
    pipeline_builder = MedicalPipelineBuilderDicom(img_cv)
    imagenes, traza = pipeline_builder.execute_flow(optimal_flow)

    # Formatear la respuesta con traza y previews por nodo
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

    final_node_id = optimal_flow[-1]["id"]
    enhanced_url = image_to_base64(imagenes.get(final_node_id, imagenes["original"]))

    return {
        "enhanced_url": enhanced_url,
        "original_url": image_to_base64(imagenes["original"]),
        "quality_score": optimization_result.get("best_quality_score"),
        "from_cache": optimization_result.get("from_cache", False),
        "optimal_flow": optimal_flow,
        "nodos": respuesta_nodos
    }
