import numpy as np
from processing.dicom.filters.noise_reduction.bilateral import BilateralFilter
from processing.dicom.filters.noise_reduction.gaussian import GaussianFilter
from processing.dicom.filters.noise_reduction.nl_means import NlMeansFilter
from processing.dicom.filters.mask_extraction.region_fill import RegionFillFilter
from processing.dicom.filters.mask_extraction.morph_erode import MorphErodeFilter
from processing.dicom.filters.mask_extraction.morph_dilate import MorphDilateFilter

FILTERS_REGISTRY = {
    # noise_reduction
    "bilateral_filter": BilateralFilter(),
    "gaussian_filter": GaussianFilter(),
    "nl_means_filter": NlMeansFilter(),
    "morph_erode_filter": MorphErodeFilter(),
    "morph_dilate_filter": MorphDilateFilter(),
    "region_fill_filter": RegionFillFilter(),
}

class MedicalPipelineBuilderDicom:
    def __init__(self, init_image: np.ndarray):
        self.history = { 'original': init_image.copy() }
        self.execution_trace = {} 
    
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

        # 2. Ejecución basada en resolución dinámica de dependencias (Orden Topológico)
        pending = list(flow_config)
        
        while pending:
            node_processed_in_this_round = False
            
            for i, step in enumerate(pending):
                node_id = step.get('id')
                input_id = step.get('input_id', 'original')
                params = step.get('params', {})

                # Conversión de strings numéricos en params
                for key, value in params.items():
                    if isinstance(value, str):
                        try:
                            if '.' in value:
                                params[key] = float(value)
                            else:
                                params[key] = int(value)
                        except ValueError:
                            pass
                
                deps_to_check = [input_id]
                if 'layer_a' in params: deps_to_check.append(params['layer_a'])
                if 'layer_b' in params: deps_to_check.append(params['layer_b'])
                
                # Verificar dependencias
                if all(dep == 'original' or dep in self.history for dep in deps_to_check):
                    filter_name = step.get('filter_name')
                    filter_instance = FILTERS_REGISTRY.get(filter_name)
                    
                    if not filter_instance:
                        self.execution_trace[node_id]["status"] = "error"
                        self.execution_trace[node_id]["error"] = f"Filtro '{filter_name}' no registrado"
                    else:
                        try:
                            source_img = self.history.get(input_id, self.history['original'])
                            result = filter_instance.apply(source_img, history=self.history, **params)
                            self.history[node_id] = result
                            self.execution_trace[node_id]["status"] = "success"
                        except Exception as e:
                            self.execution_trace[node_id]["status"] = "error"
                            self.execution_trace[node_id]["error"] = str(e)
                    
                    pending.pop(i)
                    node_processed_in_this_round = True
                    break
            
            if not node_processed_in_this_round:
                for step in pending:
                    node_id = step.get('id')
                    self.execution_trace[node_id]["status"] = "error"
                    self.execution_trace[node_id]["error"] = "Origen no encontrado o referencia circular"
                break

        return self.history, self.execution_trace
