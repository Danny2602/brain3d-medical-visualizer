import numpy as np

# noise_reduction
from processing.dicom.filters.noise_reduction.bilateral import BilateralFilter
from processing.dicom.filters.noise_reduction.gaussian import GaussianFilter
from processing.dicom.filters.noise_reduction.nl_means import NlMeansFilter

# mask_extraction
from processing.dicom.filters.mask_extraction.mask_clipping import MaskClippingFilter
from processing.dicom.filters.mask_extraction.mass_cleaning import MassCleaningFilter
from processing.dicom.filters.mask_extraction.morph_connect import MorphConnectFilter
from processing.dicom.filters.mask_extraction.morph_dilate import MorphDilateFilter
from processing.dicom.filters.mask_extraction.morph_erode import MorphErodeFilter
from processing.dicom.filters.mask_extraction.morph_gradient import MorphGradientFilter
from processing.dicom.filters.mask_extraction.morph_open import MorphOpenFilter
from processing.dicom.filters.mask_extraction.region_fill import RegionFillFilter

# illumination_contrast
from processing.dicom.filters.illumination_contrast.clahe import CLAHEFilter
from processing.dicom.filters.illumination_contrast.fuzzy_logic import FuzzyLogicFilter
from processing.dicom.filters.illumination_contrast.gamma import GammaFilter
from processing.dicom.filters.illumination_contrast.global_hist_eq import GlobalHistEqFilter
from processing.dicom.filters.illumination_contrast.local_statistical import LocalStatisticalFilter
from processing.dicom.filters.illumination_contrast.logarithmic import LogarithmicFilter
from processing.dicom.filters.illumination_contrast.min_max import MinMaxFilter

# edge_detection
from processing.dicom.filters.edge_detection.canny_filter import CannyEdgesFilter
from processing.dicom.filters.edge_detection.multi_otsu_threshold import MultiOtsuThresholdFilter
from processing.dicom.filters.edge_detection.otsu_threshold import OtsuThresholdFilter

# detail_enhancement
from processing.dicom.filters.detail_enhancement.laplacian import LaplacianFilter
from processing.dicom.filters.detail_enhancement.tophat_morf import TopHatMorfFilter
from processing.dicom.filters.detail_enhancement.unsharp_mask import UnsharpMaskFilter

# advanced_segmentation
from processing.dicom.filters.advanced_segmentation.region_growing import RegionGrowingFilter
from processing.dicom.filters.advanced_segmentation.skull_stripping import SkullStrippingFilter
from processing.dicom.filters.advanced_segmentation.watershed import WatershedFilter

# operations
from processing.dicom.filters.operations.bitwise_and import LogicAndFilter
from processing.dicom.filters.operations.bitwise_or import LogicOrFilter
from processing.dicom.filters.operations.invert_not import InvertNotFilter

FILTERS_REGISTRY = {
    # noise_reduction
    "bilateral_filter": BilateralFilter(),
    "gaussian_filter": GaussianFilter(),
    "nl_means_filter": NlMeansFilter(),

    # mask_extraction
    "mask_clipping_filter": MaskClippingFilter(),
    "mass_cleaning_filter": MassCleaningFilter(),
    "morph_connect_filter": MorphConnectFilter(),
    "morph_dilate_filter": MorphDilateFilter(),
    "morph_erode_filter": MorphErodeFilter(),
    "morph_gradient_filter": MorphGradientFilter(),
    "morph_open_filter": MorphOpenFilter(),
    "region_fill_filter": RegionFillFilter(),

    # illumination_contrast
    "clahe_filter": CLAHEFilter(),
    "fuzzy_logic_filter": FuzzyLogicFilter(),
    "gamma_filter": GammaFilter(),
    "global_hist_eq_filter": GlobalHistEqFilter(),
    "local_statistical_filter": LocalStatisticalFilter(),
    "logarithmic_filter": LogarithmicFilter(),
    "min_max_filter": MinMaxFilter(),

    # edge_detection
    "canny_edges_filter": CannyEdgesFilter(),
    "multi_otsu_threshold_filter": MultiOtsuThresholdFilter(),
    "otsu_threshold_filter": OtsuThresholdFilter(),

    # detail_enhancement
    "laplacian_filter": LaplacianFilter(),
    "tophat_morf_filter": TopHatMorfFilter(),
    "unsharp_mask_filter": UnsharpMaskFilter(),

    # advanced_segmentation
    "region_growing_filter": RegionGrowingFilter(),
    "skull_stripping_filter": SkullStrippingFilter(),
    "watershed_filter": WatershedFilter(),

    # operations
    "logic_and_filter": LogicAndFilter(),
    "logic_or_filter": LogicOrFilter(),
    "invert_not_filter": InvertNotFilter(),
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
