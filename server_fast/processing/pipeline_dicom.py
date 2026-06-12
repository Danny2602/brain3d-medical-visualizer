class MedicalPipelineBuilderDicom:
    def __init__(self, init_image: np.ndarray):
        self.history = { 'original': init_image.copy() }
        self.execution_trace = {} 
    