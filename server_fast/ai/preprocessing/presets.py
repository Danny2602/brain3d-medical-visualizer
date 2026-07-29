"""
Estrategias y Pipelines predeterminados para imágenes médicas cerebrales en formato DICOM.
Basado en estándares radiológicos de contraste (Unidades Hounsfield / MRI).
"""

BRAIN_PRESETS = {
    "brain_soft_tissue": {
        "name": "Tejido Cerebral Blando",
        "description": "Optimizado para la diferenciación de Sustancia Gris, Sustancia Blanca y LCR.",
        "recommended_pipeline": [
            {
                "id": "node_1",
                "filter_name": "gaussian_filter",
                "input_id": "original",
                "params": {"kernel_size": 3}
            },
            {
                "id": "node_2",
                "filter_name": "clahe_filter",
                "input_id": "node_1",
                "params": {"clipLimit": 2.0, "tileGridSize": "8,8"}
            },
            {
                "id": "node_3",
                "filter_name": "skull_stripping_filter",
                "input_id": "node_2",
                "params": {}
            }
        ]
    },
    
    "tumor_enhancement": {
        "name": "Detección / Realce de Tumores",
        "description": "Preserva bordes de lesiones y realza el contraste de regiones hiperdensas o con contraste.",
        "recommended_pipeline": [
            {
                "id": "node_1",
                "filter_name": "bilateral_filter",
                "input_id": "original",
                "params": {"diameter": 7, "sigma_color": 0.05, "sigma_space": 5.0}
            },
            {
                "id": "node_2",
                "filter_name": "fuzzy_logic_filter",
                "input_id": "node_1",
                "params": {"mode": "triangular", "sigma": 0.15}
            },
            {
                "id": "node_3",
                "filter_name": "unsharp_mask_filter",
                "input_id": "node_2",
                "params": {"radius": 1.5, "amount": 1.2}
            }
        ]
    },
    
    "skull_isolation": {
        "name": "Aislamiento de Cráneo y Hueso",
        "description": "Segmenta las estructuras óseas de alta densidad en tomografías cerebrales.",
        "recommended_pipeline": [
            {
                "id": "node_1",
                "filter_name": "min_max_filter",
                "input_id": "original",
                "params": {"alpha": 0.0, "beta": 1.0}
            },
            {
                "id": "node_2",
                "filter_name": "otsu_threshold_filter",
                "input_id": "node_1",
                "params": {}
            }
        ]
    }
}