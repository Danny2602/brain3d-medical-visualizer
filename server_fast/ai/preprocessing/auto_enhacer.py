"""
Motor de optimización por árbol de exploración (Optuna v6):
Explora combinaciones dinámicas de 3 a 5 filtros en cascada sobre el registro completo de filtros DICOM.
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

N_TRIALS_FIXED = 35

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "optuna_memory.db")
STORAGE_URL = f"sqlite:///{DB_PATH}"

# Limpiar caché de RAM al iniciar
PIPELINE_CACHE = {}


def _auto_series_uid(img: np.ndarray) -> str:
    stats = f"{img.shape}_{float(np.mean(img)):.2f}_{float(np.std(img)):.2f}_{float(np.var(img)):.2f}"
    return hashlib.md5(stats.encode()).hexdigest()[:12]


# Categorías de filtros médicos para exploración en árbol
NOISE_FILTERS = ["bilateral_filter", "gaussian_filter", "nl_means_filter"]
CONTRASTE_FILTERS = ["clahe_filter", "fuzzy_logic_filter", "local_statistical_filter", "gamma_filter", "logarithmic_filter"]
DETAIL_FILTERS = ["unsharp_mask_filter", "tophat_morf_filter"]
SECONDARY_CONTRAST_FILTERS = ["min_max_filter", "gamma_filter", "local_statistical_filter", "none"]


class AutoDicomEnhancer:
    def __init__(self, quality_threshold: float = 0.85):
        self.quality_threshold = quality_threshold

    def get_or_optimize_pipeline(self, dicom_img: np.ndarray, series_uid: str = None) -> dict:
        if series_uid is None:
            series_uid = _auto_series_uid(dicom_img)

        # Si ya está en caché y es la misma serie, verificar score
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
                    "note": "Calidad aprobada desde memoria de IA"
                }

        if not HAS_OPTUNA:
            return self._heuristic_fallback()

        def objective(trial: optuna.Trial) -> float:
            flow_config = []
            node_idx = 1
            last_node_id = "original"

            # 🌲 ÁRBOL DE EXPLORACIÓN DE 3 A 4 ETAPAS COMPLEMENTARIAS
            
            # ETAPA 1: Reducción de Ruido
            noise_name = trial.suggest_categorical("step1_noise", NOISE_FILTERS)
            p1 = {}
            if noise_name == "bilateral_filter":
                p1 = {
                    "diameter": trial.suggest_int("s1_bilateral_d", 3, 7, step=2),
                    "sigma_color": trial.suggest_float("s1_bilateral_sc", 0.01, 0.09, step=0.02),
                    "sigma_space": trial.suggest_float("s1_bilateral_ss", 1.0, 7.0, step=2.0)
                }
            elif noise_name == "gaussian_filter":
                p1 = {"kernel_size": trial.suggest_int("s1_gauss_k", 3, 5, step=2)}
            elif noise_name == "nl_means_filter":
                p1 = {"h": trial.suggest_float("s1_nlm_h", 0.03, 0.15, step=0.03), "patch_size": 5, "patch_distance": 9}

            flow_config.append({"id": f"node_{node_idx}", "filter_name": noise_name, "input_id": last_node_id, "params": p1})
            last_node_id = f"node_{node_idx}"
            node_idx += 1

            # ETAPA 2: Ecualización Adaptable Principal (CLAHE)
            clahe_clip = trial.suggest_float("s2_clahe_clip", 1.2, 3.6, step=0.4)
            flow_config.append({
                "id": f"node_{node_idx}",
                "filter_name": "clahe_filter",
                "input_id": last_node_id,
                "params": {"clipLimit": clahe_clip, "tileGridSize": "8,8"}
            })
            last_node_id = f"node_{node_idx}"
            node_idx += 1

            # ETAPA 3: Modulación Fina de Tono Local
            tone_name = trial.suggest_categorical("step3_tone", CONTRASTE_FILTERS)
            p3 = {}
            if tone_name == "local_statistical_filter":
                p3 = {"kernel_size": trial.suggest_int("s3_stat_k", 9, 17, step=4), "k_factor": trial.suggest_float("s3_stat_factor", 1.0, 2.2, step=0.4)}
            elif tone_name == "gamma_filter":
                p3 = {"gamma": trial.suggest_float("s3_gamma_val", 0.8, 1.4, step=0.1)}
            elif tone_name == "logarithmic_filter":
                p3 = {"gain": trial.suggest_float("s3_log_gain", 0.9, 1.5, step=0.1)}
            elif tone_name == "fuzzy_logic_filter":
                p3 = {"mode": trial.suggest_categorical("s3_fuzzy_mode", ["triangular", "campana", "sigmoide"]), "sigma": trial.suggest_float("s3_fuzzy_sigma", 0.1, 0.3, step=0.05)}
            elif tone_name == "clahe_filter":
                p3 = {"clipLimit": 1.5, "tileGridSize": "8,8"}

            flow_config.append({"id": f"node_{node_idx}", "filter_name": tone_name, "input_id": last_node_id, "params": p3})
            last_node_id = f"node_{node_idx}"
            node_idx += 1

            # ETAPA 4: Realce Morfológico y Bordes Anatómicos
            detail_name = trial.suggest_categorical("step4_detail", DETAIL_FILTERS)
            p4 = {}
            if detail_name == "unsharp_mask_filter":
                p4 = {
                    "radius": trial.suggest_float("s4_unsharp_r", 0.5, 2.0, step=0.5),
                    "amount": trial.suggest_float("s4_unsharp_a", 0.5, 1.5, step=0.25)
                }
            elif detail_name == "tophat_morf_filter":
                p4 = {"kernel_size": trial.suggest_int("s4_tophat_k", 3, 7, step=2)}

            flow_config.append({"id": f"node_{node_idx}", "filter_name": detail_name, "input_id": last_node_id, "params": p4})
            last_node_id = f"node_{node_idx}"
            node_idx += 1

            builder = MedicalPipelineBuilderDicom(dicom_img)
            history, trace = builder.execute_flow(flow_config)
            final_img = history.get(last_node_id, history.get("original"))
            
            score = compute_composite_quality_score(final_img, dicom_img)
            trial.set_user_attr("flow_config", flow_config)
            return score

        # v6: Árbol de Exploración Optuna Completo de 4 Filtros
        study = optuna.create_study(
            study_name="brain_dicom_enhancement_v6",
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
            "note": "Árbol de exploración Optuna v6 completado con éxito"
        }

    def _heuristic_fallback(self) -> dict:
        from ai.preprocessing.presets import BRAIN_PRESETS
        preset = BRAIN_PRESETS["brain_soft_tissue"]
        return {
            "optimal_flow": preset["recommended_pipeline"],
            "best_quality_score": 1.0,
            "from_cache": False,
            "reoptimized": False,
            "note": "Optuna no disponible, se aplicó preset heurístico por defecto"
        }