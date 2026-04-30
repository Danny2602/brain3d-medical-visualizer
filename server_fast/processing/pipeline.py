import numpy as np
import traceback
from processing.filters.noise_reduction.nl_means import NlMeansFilter
from processing.filters.noise_reduction.bilateral import BilateralFilter
from processing.filters.noise_reduction.gaussian import GaussianFilter
from processing.filters.mask_extraction.mass_cleaning import MassCleaningFilter
from processing.filters.mask_extraction.mask_clipping import MaskClippingFilter
from processing.filters.mask_extraction.morph_connect import MorphConnectFilter
from processing.filters.mask_extraction.morph_open import MorphOpenFilter
from processing.filters.illumination_contrast.clahe import CLAHEFilter
from processing.filters.illumination_contrast.gamma import GammaFilter
from processing.filters.illumination_contrast.logarithmic import LogarithmicFilter
from processing.filters.illumination_contrast.min_max import MinMaxFilter
from processing.filters.illumination_contrast.fuzzy_logic import FuzzyLogicFilter
from processing.filters.illumination_contrast.local_statistical import LocalStatisticalFilter
from processing.filters.illumination_contrast.global_hist_eq import GlobalHistEqFilter
from processing.filters.edge_detection.canny_filter import CannyEdgesFilter
from processing.filters.edge_detection.otsu_threshold import OtsuThresholdFilter
from processing.filters.edge_detection.multi_otsu_threshold import MultiOtsuThresholdFilter
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
    "morph_open": MorphOpenFilter(),
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
    "multi_otsu_threshold": MultiOtsuThresholdFilter(),
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
    def execute_flow(self, flow_config: list) -> tuple:
        # 1. Registro inicial de todos los nodos en la traza como pendientes
        for step in flow_config:
            node_id = step.get('id')
            filter_name = step.get('filter_name')
            input_id = step.get('input_id', 'original')
            self.execution_trace[node_id] = {
                "filter": filter_name,
                "parent": input_id,
                "status": "pending"
            }

        # 2. Ejecución basada en resolución de dependencias (Orden Topológico Dinámico)
        pending = list(flow_config)
        
        while pending:
            node_processed_in_this_round = False
            
            for i, step in enumerate(pending):
                node_id = step.get('id')
                input_id = step.get('input_id', 'original')
                params = step.get('params', {})

                
                for key, value in params.items():
                    if isinstance(value, str):
                        try:
                            # Si es un número con decimal (ej. "10.5"), lo pasamos a float
                            if '.' in value:
                                params[key] = float(value)
                            # Si es un número entero (ej. "10"), lo pasamos a int
                            else:
                                params[key] = int(value)
                        except ValueError:
                            # Si no se puede convertir, lo dejamos como string (ej. "gray")
                            pass
                
                deps_to_check = [input_id]
                if 'layer_a' in params: deps_to_check.append(params['layer_a'])
                if 'layer_b' in params: deps_to_check.append(params['layer_b'])
                
                # ¿Están todas las dependencias listas en el historial?
                if all(dep == 'original' or dep in self.history for dep in deps_to_check):
                    filter_name = step.get('filter_name')
                    filter_instance = FILTERS_REGISTRY.get(filter_name)
                    
                    if not filter_instance:
                        self.execution_trace[node_id]["status"] = "error"
                        self.execution_trace[node_id]["error"] = f"Filtro '{filter_name}' no registrado"
                    else:
                        try:
                            # Obtener imagen de origen (principal)
                            source_img = self.history.get(input_id, self.history['original'])
                            
                            # Aplicar el filtro inyectando el historial completo para que pueda buscar sus capas
                            result = filter_instance.apply(source_img, history=self.history, **params)
                            
                            # Guardar resultado y marcar éxito
                            self.history[node_id] = result
                            self.execution_trace[node_id]["status"] = "success"
                        except Exception as e:
                            self.execution_trace[node_id]["status"] = "error"
                            self.execution_trace[node_id]["error"] = str(e)
                            # traceback.print_exc() # Útil para depuración en consola
                    
                    # Remover de pendientes y marcar que avanzamos
                    pending.pop(i)
                    node_processed_in_this_round = True
                    break # Reiniciamos el loop de pendientes para verificar nuevos nodos desbloqueados
            
            # Si en una vuelta entera no pudimos procesar nada pero hay pendientes, hay un problema
            if not node_processed_in_this_round:
                for step in pending:
                    node_id = step.get('id')
                    self.execution_trace[node_id]["status"] = "error"
                    self.execution_trace[node_id]["error"] = "Origen no encontrado o referencia circular"
                break

        return self.history, self.execution_trace
