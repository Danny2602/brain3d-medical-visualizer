import numpy as np
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
    "logarithmic": LogarithmicFilter(),
    "gamma": GammaFilter(),
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

class MedicalPipelineBuilder2:
    def __init__(self,init_image: np.ndarray):
        self.current_image = init_image #La imagen que se va a procesar
        self.history={}
    
    def execute_flow(self, flow_config: list)-> dict:
        self.history['original'] = self.current_image.copy()

        for step in flow_config:
            filter_name = step.get('filter_name')
            filter_params = step.get('params',{})
            filter_instance = FILTERS_REGISTRY.get(filter_name)
            if filter_instance:
                self.current_image = filter_instance.apply(self.current_image, history=self.history, **filter_params)
                self.history[filter_name] = self.current_image.copy()
            else:
                print(f"Filter {filter_name} not found")
        
        return self.history
        
        