"""
Motor de optimización inteligente con Optuna v5:
Construye pipelines multicapa completos (3 a 4 etapas consecutivas de procesamiento)
evaluados con métricas anatómicas de alta precisión en ROI y mezcla suave de fondo.
"""

import numpy as np
import os
import hashlib
from processing.dicom.pipeline_nodes import MedicalPipelineBuilderDicom, FILTERS_REGISTRY
from ai.preprocessing.metrics import compute_composite_quality_score

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False

N_TRIALS_FIXED = 30

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "optuna_memory.db")
STORAGE_URL = f"sqlite:///{DB_PATH}"

PIPELINE_CACHE = {}


def _auto_series_uid(img: np.ndarray) -> str:
    stats = f"{img.shape}_{float(np.mean(img)):.2f}_{float(np.std(img)):.2f}"
    return hashlib.md5(stats.encode()).hexdigest()[:12]


class AutoDicomEnhancer:
    def __init__(self, quality_threshold: float = 0.80):
        self.quality_threshold = quality_threshold

    def get_or_optimize_pipeline(self, dicom_img: np.ndarray, series_uid: str = None) -> dict:
        if series_uid is None:
            series_uid = _auto_series_uid(dicom_img)

        if series_uid in PIPELINE_CACHE:
            cached_flow = PIPELINE_CACHE[series_uid]["optimal_flow"]
            expected_score = PIPELINE_CACHE[series_uid]["best_quality_score"]

            builder = MedicalPipelineBuilderDicom(dicom_img)
            history, trace = builder.execute_flow(cached_flow)
            
            final_node_id = cached_flow[-1]["id"] if cached_flow else "original"
            test_img = history.get(final_node_id, history.get("original"))
            current_score = compute_composite_quality_score(test_img, dicom_img)

            if current_score >= (expected_score * self.quality_threshold):
                return {
                    "optimal_flow": cached_flow,
                    "best_quality_score": round(current_score, 4),
                    "from_cache": True,
                    "reoptimized": False,
                    "note": "Calidad verificada y aprobada desde memoria"
                }

        if not HAS_OPTUNA:
            return self._heuristic_fallback()

        def objective(trial: optuna.Trial) -> float:
            flow_config = []
            node_idx = 1
            last_node_id = "original"

            # ETAPA 1: REDUCCIÓN DE RUIDO Y PRE-FILTRADO (Obligatoria para máxima calidad)
            noise_filter = trial.suggest_categorical(
                "noise_filter", ["gaussian_filter", "bilateral_filter", "nl_means_filter"]
            )
            node_id = f"node_{node_idx}"
            params = {}
            if noise_filter == "bilateral_filter":
                params = {
                    "diameter": trial.suggest_int("bilateral_diameter", 3, 7, step=2),
                    "sigma_color": trial.suggest_float("bilateral_sigma_color", 0.01, 0.09, step=0.02),
                    "sigma_space": trial.suggest_float("bilateral_sigma_space", 1.0, 7.0, step=2.0)
                }
            elif noise_filter == "gaussian_filter":
                params = {"kernel_size": trial.suggest_int("gaussian_kernel", 3, 5, step=2)}
            elif noise_filter == "nl_means_filter":
                params = {"h": trial.suggest_float("nl_h", 0.03, 0.15, step=0.03), "patch_size": 5, "patch_distance": 9}

            flow_config.append({"id": node_id, "filter_name": noise_filter, "input_id": last_node_id, "params": params})
            last_node_id = node_id
            node_idx += 1

            # ETAPA 2: CONTRASTE ADAPTATIVO CLAHE (Obligatoria para ecualización local)
            node_id = f"node_{node_idx}"
            params = {"clipLimit": trial.suggest_float("clahe_clip", 1.2, 3.6, step=0.4), "tileGridSize": "8,8"}
            flow_config.append({"id": node_id, "filter_name": "clahe_filter", "input_id": last_node_id, "params": params})
            last_node_id = node_id
            node_idx += 1

            # ETAPA 3: AJUSTE FINO DE TONO LOCAL (Obligatoria)
            tone_filter = trial.suggest_categorical(
                "tone_filter", ["local_statistical_filter", "gamma_filter", "logarithmic_filter", "fuzzy_logic_filter"]
            )
            node_id = f"node_{node_idx}"
            params = {}
            if tone_filter == "local_statistical_filter":
                params = {"kernel_size": trial.suggest_int("stat_kernel", 9, 17, step=4), "k_factor": trial.suggest_float("stat_k", 1.0, 2.2, step=0.4)}
            elif tone_filter == "gamma_filter":
                params = {"gamma": trial.suggest_float("gamma_val", 0.8, 1.4, step=0.1)}
            elif tone_filter == "logarithmic_filter":
                params = {"gain": trial.suggest_float("log_gain", 0.9, 1.5, step=0.1)}
            elif tone_filter == "fuzzy_logic_filter":
                params = {"mode": trial.suggest_categorical("fuzzy_mode", ["triangular", "campana", "sigmoide"]), "sigma": trial.suggest_float("fuzzy_sigma", 0.1, 0.3, step=0.05)}

            flow_config.append({"id": node_id, "filter_name": tone_filter, "input_id": last_node_id, "params": params})
            last_node_id = node_id
            node_idx += 1

            # ETAPA 4: REALCE MORFOLÓGICO DE BORDES Y DETALLES (Obligatoria)
            detail_filter = trial.suggest_categorical("detail_filter", ["unsharp_mask_filter", "tophat_morf_filter"])
            node_id = f"node_{node_idx}"
            params = {}
            if detail_filter == "unsharp_mask_filter":
                params = {
                    "radius": trial.suggest_float("unsharp_radius", 0.5, 2.0, step=0.5),
                    "amount": trial.suggest_float("unsharp_amount", 0.5, 1.5, step=0.25)
                }
            elif detail_filter == "tophat_morf_filter":
                params = {"kernel_size": trial.suggest_int("tophat_kernel", 3, 7, step=2)}

            flow_config.append({"id": node_id, "filter_name": detail_filter, "input_id": last_node_id, "params": params})
            last_node_id = node_id
            node_idx += 1

            builder = MedicalPipelineBuilderDicom(dicom_img)
            history, trace = builder.execute_flow(flow_config)
            final_img = history.get(last_node_id, history.get("original"))
            
            score = compute_composite_quality_score(final_img, dicom_img)
            trial.set_user_attr("flow_config", flow_config)
            return score

        # v5: Multicapa 4-Etapas Completo con Mezcla Suave Continuous Smoothstep
        study = optuna.create_study(
            study_name="brain_dicom_enhancement_v5",
            storage=STORAGE_URL,
            load_if_exists=True,
            direction="maximize"
        )
        study.optimize(objective, n_trials=N_TRIALS_FIXED)

        best_flow = study.best_trial.user_attrs.get("flow_config", [])
        best_score = round(study.best_value, 4)

        PIPELINE_CACHE[series_uid] = {
            "optimal_flow": best_flow,
            "best_quality_score": best_score
        }

        return {
            "optimal_flow": best_flow,
            "best_quality_score": best_score,
            "from_cache": False,
            "reoptimized": True,
            "note": "Optimizado con exito usando pipeline completo de 4 etapas v5"
        }

    def _heuristic_fallback(self) -> dict:
        from ai.preprocessing.presets import BRAIN_PRESETS
        preset = BRAIN_PRESETS["brain_soft_tissue"]
        return {
            "optimal_flow": preset["recommended_pipeline"],
            "best_quality_score": 1.0,
            "from_cache": False,
            "reoptimized": False,
            "note": "Optuna no disponible, se aplico preset heuristico por defecto"
        }