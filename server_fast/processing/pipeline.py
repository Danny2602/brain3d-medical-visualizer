import numpy as np
import traceback
from processing.filters.noise_reduction.nl_means import NlMeansFilter
from processing.filters.noise_reduction.bilateral import BilateralFilter
from processing.filters.noise_reduction.gaussian import GaussianFilter
from processing.filters.mask_extraction.mass_cleaning import MassCleaningFilter
from processing.filters.mask_extraction.mask_clipping import MaskClippingFilter
from processing.filters.mask_extraction.morph_connect import MorphConnectFilter
from processing.filters.illumination_contrast.clahe import CLAHEFilter
from processing.filters.illumination_contrast.gamma import GammaFilter
from processing.filters.illumination_contrast.logarithmic import LogarithmicFilter
from processing.filters.illumination_contrast.min_max import MinMaxFilter
from processing.filters.illumination_contrast.fuzzy_logic import FuzzyLogicFilter
from processing.filters.illumination_contrast.local_statistical import LocalStatisticalFilter
from processing.filters.illumination_contrast.global_hist_eq import GlobalHistEqFilter
from processing.filters.edge_detection.canny_filter import CannyEdgesFilter
from processing.filters.edge_detection.otsu_threshold import OtsuThresholdFilter
from processing.filters.detail_enhancement.laplacian import LaplacianFilter
from processing.filters.detail_enhancement.unsharp_mask import UnsharpMaskFilter
from processing.filters.detail_enhancement.tophat_morf import TopHatMorfFilter
from processing.filters.operations.bitwise_and import LogicAndFilter
from processing.filters.operations.bitwise_or import LogicOrFilter
FILTERS_REGISTRY = {
    #noise_reduction
    "nl_means": NlMeansFilter(),
    "bilateral_filter": BilateralFilter(),
    "gaussian_filter": GaussianFilter(),
    #mask_extraction
    "mass_cleaning": MassCleaningFilter(),
    "mask_clipping": MaskClippingFilter(),
    "morph_connect": MorphConnectFilter(),
    #illumination_contrast
    "clahe": CLAHEFilter(),
    "gamma": GammaFilter(),
    "logarithmic": LogarithmicFilter(),
    "min_max": MinMaxFilter(),
    "fuzzy_logic": FuzzyLogicFilter(),
    "local_statistical": LocalStatisticalFilter(),
    "global_hist_eq": GlobalHistEqFilter(),
    #edge_detection
    "canny_edges": CannyEdgesFilter(),
    "otsu_threshold": OtsuThresholdFilter(),
    #detail_enhancement
    "laplacian": LaplacianFilter(),
    "unsharp_mask": UnsharpMaskFilter(),
    "tophat_morf": TopHatMorfFilter(),
    #operations
    "logic_and": LogicAndFilter(),
    "logic_or": LogicOrFilter(),
}


class MedicalPipelineBuilder:
    def __init__(self, init_image: np.ndarray):
        self.history = { 'original': init_image.copy() }
        self.execution_trace = {} # <-- NUEVO: Para guardar qué hizo cada nodo
    def execute_flow(self, flow_config: list) -> tuple: # <-- CAMBIO: Ahora devuelve una tupla
        # print(f"\n--- INICIANDO PIPELINE DE NODOS ({len(flow_config)} pasos) ---")
        
        for step in flow_config:
            node_id = step.get('id', f"node_{flow_config.index(step)}")
            filter_name = step.get('filter_name')
            input_id = step.get('input_id', 'original')
            params = step.get('params', {})
            # Registro inicial en la traza
            self.execution_trace[node_id] = {
                "filter": filter_name,
                "parent": input_id,
                "status": "pending"
            }
            filter_instance = FILTERS_REGISTRY.get(filter_name)
            
            if not filter_instance or input_id not in self.history:
                self.execution_trace[node_id]["status"] = "error"
                self.execution_trace[node_id]["error"] = "Origen no encontrado o filtro inválido"
                continue
            try:
                source_img = self.history[input_id]
                result = filter_instance.apply(source_img, history=self.history, **params)
                self.history[node_id] = result
                self.execution_trace[node_id]["status"] = "success"
                # print(f"ÉXITO en '{node_id}'")
            except Exception as e:
                self.execution_trace[node_id]["status"] = "error"
                self.execution_trace[node_id]["error"] = str(e)
                # print(f"ERROR en '{node_id}': {str(e)}")
        # print("--- PIPELINE FINALIZADO ---\n")
        return self.history, self.execution_trace # <-- DEVOLVEMOS AMBOS
