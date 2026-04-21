import numpy as np
from processing.filters.noise_reduction.nl_means import NlMeansFilter

FILTERS_REGISTRY = {
    "nl_means": NlMeansFilter(),
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
        
        