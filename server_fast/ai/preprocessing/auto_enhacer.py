"""
Motor de optimización inteligente con Optuna, Memoria Persistente SQLite 
y Verificación Dinámica de Calidad (Quality Guardrail) por corte.
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

# Número fijo de iteraciones de exploración - la IA se auto-gestiona
N_TRIALS_FIXED = 20

# Base de Datos de Memoria Persistente (Se crea automáticamente si no existe)
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "optuna_memory.db")
STORAGE_URL = f"sqlite:///{DB_PATH}"

# Caché inteligente en memoria RAM
PIPELINE_CACHE = {}


def _auto_series_uid(img: np.ndarray) -> str:
    """Genera un ID de serie automático basado en las estadísticas de la imagen."""
    stats = f"{img.shape}_{float(np.mean(img)):.2f}_{float(np.std(img)):.2f}"
    return hashlib.md5(stats.encode()).hexdigest()[:12]


class AutoDicomEnhancer:
    def __init__(self, quality_threshold: float = 0.80):
        """
        :param quality_threshold: Si la calidad del resultado cae por debajo de este porcentaje del score esperado,
                                  la IA re-optimiza automáticamente con nuevas combinaciones de filtros.
        """
        self.quality_threshold = quality_threshold


    def get_or_optimize_pipeline(self, dicom_img: np.ndarray, series_uid: str = None) -> dict:
        """Aplica aprendizaje continuo + verificación dinámica de calidad por corte."""
        # Si no se provee un ID de serie, generarlo automáticamente
        if series_uid is None:
            series_uid = _auto_series_uid(dicom_img)


        # ⚡ 1. VERIFICACIÓN CON CACHÉ + EVALUACIÓN DE CALIDAD EN TIEMPO REAL
        if series_uid in PIPELINE_CACHE:
            cached_flow = PIPELINE_CACHE[series_uid]["optimal_flow"]
            expected_score = PIPELINE_CACHE[series_uid]["best_quality_score"]

            # Probar el pipeline guardado en la nueva corte
            builder = MedicalPipelineBuilderDicom(dicom_img)
            history, trace = builder.execute_flow(cached_flow)
            
            final_node_id = cached_flow[-1]["id"] if cached_flow else "original"
            test_img = history.get(final_node_id, history.get("original"))
            current_score = compute_composite_quality_score(test_img)

            #  Si la calidad se mantiene dentro del rango tolerable, USAR CACHÉ (Milisegundos)
            if current_score >= (expected_score * self.quality_threshold):
                return {
                    "optimal_flow": cached_flow,
                    "best_quality_score": round(current_score, 4),
                    "from_cache": True,
                    "reoptimized": False,
                    "note": "Calidad verificada y aprobada desde memoria"
                }

        # 🧠 2. SI ES UNA SERIE NUEVA O LA CALIDAD CAYÓ: APRENDER / RE-OPTIMIZAR CON OPTUNA
        if not HAS_OPTUNA:
            return self._heuristic_fallback()

        def objective(trial: optuna.Trial) -> float:
            flow_config = []
            node_idx = 1
            last_node_id = "original"

            # ETAPA 1: REDUCCIÓN DE RUIDO (opcional)
            noise_filter = trial.suggest_categorical(
                "noise_filter", ["bilateral_filter", "gaussian_filter", "nl_means_filter", "none"]
            )
            if noise_filter != "none":
                node_id = f"node_{node_idx}"
                params = {}
                if noise_filter == "bilateral_filter":
                    params = {
                        "diameter": trial.suggest_int("bilateral_diameter", 3, 9, step=2),
                        "sigma_color": trial.suggest_float("bilateral_sigma_color", 0.01, 0.1, step=0.02),
                        "sigma_space": trial.suggest_float("bilateral_sigma_space", 1.0, 9.0, step=2.0)
                    }
                elif noise_filter == "gaussian_filter":
                    params = {"kernel_size": trial.suggest_int("gaussian_kernel", 3, 7, step=2)}
                elif noise_filter == "nl_means_filter":
                    params = {"h": trial.suggest_float("nl_h", 0.05, 0.25, step=0.05), "patch_size": 7, "patch_distance": 11}
                
                flow_config.append({"id": node_id, "filter_name": noise_filter, "input_id": last_node_id, "params": params})
                last_node_id = node_id
                node_idx += 1

            # ETAPA 2: CONTRASTE (obligatoria - siempre se aplica al menos uno)
            contrast_filter = trial.suggest_categorical(
                "contrast_filter", ["clahe_filter", "fuzzy_logic_filter", "local_statistical_filter", "gamma_filter", "logarithmic_filter"]
            )
            node_id = f"node_{node_idx}"
            params = {}
            if contrast_filter == "clahe_filter":
                params = {"clipLimit": trial.suggest_float("clahe_clip", 1.0, 4.0, step=0.5), "tileGridSize": "8,8"}
            elif contrast_filter == "fuzzy_logic_filter":
                params = {"mode": trial.suggest_categorical("fuzzy_mode", ["triangular", "campana", "sigmoide"]), "sigma": trial.suggest_float("fuzzy_sigma", 0.1, 0.3, step=0.05)}
            elif contrast_filter == "local_statistical_filter":
                params = {"kernel_size": trial.suggest_int("stat_kernel", 9, 21, step=4), "k_factor": trial.suggest_float("stat_k", 1.0, 3.0, step=0.5)}
            elif contrast_filter == "gamma_filter":
                params = {"gamma": trial.suggest_float("gamma_val", 0.5, 1.8, step=0.2)}
            elif contrast_filter == "logarithmic_filter":
                params = {"gain": trial.suggest_float("log_gain", 0.8, 2.0, step=0.2)}
            flow_config.append({"id": node_id, "filter_name": contrast_filter, "input_id": last_node_id, "params": params})
            last_node_id = node_id
            node_idx += 1

            # ETAPA 3: MEJORA DE DETALLES (opcional)
            detail_filter = trial.suggest_categorical("detail_filter", ["unsharp_mask_filter", "none"])
            if detail_filter != "none":
                node_id = f"node_{node_idx}"
                params = {"radius": trial.suggest_float("unsharp_radius", 0.5, 2.0, step=0.5), "amount": trial.suggest_float("unsharp_amount", 0.5, 1.5, step=0.25)}
                flow_config.append({"id": node_id, "filter_name": detail_filter, "input_id": last_node_id, "params": params})
                last_node_id = node_id

            builder = MedicalPipelineBuilderDicom(dicom_img)
            history, trace = builder.execute_flow(flow_config)
            final_img = history.get(last_node_id, history.get("original"))
            
            score = compute_composite_quality_score(final_img)
            trial.set_user_attr("flow_config", flow_config)
            return score

        # Crear o cargar estudio persistente en SQLite (aprendizaje acumulativo)
        # v2: Métricas recalibradas con Entropía + Nitidez priorizadas sobre SNR
        study = optuna.create_study(
            study_name="brain_dicom_enhancement_v2",
            storage=STORAGE_URL,
            load_if_exists=True,
            direction="maximize"
        )
        study.optimize(objective, n_trials=N_TRIALS_FIXED)

        best_flow = study.best_trial.user_attrs.get("flow_config", [])
        best_score = round(study.best_value, 4)

        # Actualizar caché de la serie con el nuevo conocimiento
        PIPELINE_CACHE[series_uid] = {
            "optimal_flow": best_flow,
            "best_quality_score": best_score
        }

        return {
            "optimal_flow": best_flow,
            "best_quality_score": best_score,
            "from_cache": False,
            "reoptimized": True,
            "note": "Re-optimizado con éxito y guardado en la base de datos SQLite de la IA"
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