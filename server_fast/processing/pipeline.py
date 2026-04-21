import numpy as np
from processing.filters.noise_reduction.nl_means import NlMeansFilter
from processing.filters.noise_reduction.bilateral import BilateralFilter
from processing.filters.noise_reduction.gaussian import GaussianFilter
from processing.filters.mask_extraction.connect_comp import ConnectComponentsFilter
from processing.filters.mask_extraction.morph_connect import MorphConnectFilter
from processing.filters.illumination_contrast.clahe import CLAHEFilter
from processing.filters.illumination_contrast.log_gamma  import LogGammaFilter
from processing.filters.illumination_contrast.min_max import MinMaxFilter
from processing.filters.edge_detection.canny_filter import CannyEdgesFilter
from processing.filters.edge_detection.otsu_threshold import OtsuThresholdFilter
from processing.filters.detail_enhancement.laplacian import LaplacianFilter
from processing.filters.detail_enhancement.unsharp_mask import UnsharpMaskFilter
from processing.filters.detail_enhancement.tophat_morf import TopHatMorfFilter
FILTERS_REGISTRY = {
    #noise_reduction
    "nl_means": NlMeansFilter(),
    "bilateral_filter": BilateralFilter(),
    "gaussian_filter": GaussianFilter(),
    #mask_extraction
    "connect_comp": ConnectComponentsFilter(),
    "morph_connect": MorphConnectFilter(),
    #illumination_contrast
    "clahe": CLAHEFilter(),
    "log_gamma": LogGammaFilter(),
    "min_max": MinMaxFilter(),
    #edge_detection
    "canny_edges": CannyEdgesFilter(),
    "otsu_threshold": OtsuThresholdFilter(),
    #detail_enhancement
    "laplacian": LaplacianFilter(),
    "unsharp_mask": UnsharpMaskFilter(),
    "tophat_morf": TopHatMorfFilter(),
}

class MedicalPipelineBuilder:
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
                self.current_image = filter_instance.apply(self.current_image, **filter_params)
                self.history[filter_name] = self.current_image.copy()
            else:
                print(f"Filter {filter_name} not found")
        
        return self.history
        
        