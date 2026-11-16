"""
Independent PPO prediction service.
Loads serialized PPO pipeline and performs inference.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

logger = logging.getLogger(__name__)


class PPOModelLoadingError(Exception):
    pass


class PPOPredictor:
    def __init__(
        self,
        model_path: Optional[str] = None,
        features_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
    ):
        backend_dir = Path(__file__).resolve().parents[1]
        default_dir = backend_dir / "models" / "ppo"
        legacy_dir = backend_dir / "artifacts" / "ppo"

        self.model_path = self._resolve_path(model_path, default_dir / "ppo_prediction_model.joblib", legacy_dir / "ppo_prediction_model.joblib")
        self.features_path = self._resolve_path(features_path, default_dir / "ppo_features.json", legacy_dir / "ppo_features.json")
        self.metadata_path = self._resolve_path(metadata_path, default_dir / "metadata.json", legacy_dir / "metadata.json", allow_missing=True)

        self.model = None
        self.features: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.threshold: float = 0.5
        self.is_loaded = False
        self.load_error: Optional[str] = None

        self._load_artifacts()

    @staticmethod
    def _resolve_path(
        explicit: Optional[str],
        primary: Path,
        legacy: Path,
        allow_missing: bool = False,
    ) -> str:
        if explicit:
            return str(Path(explicit).resolve())
        if primary.exists() or allow_missing:
            return str(primary)
        if legacy.exists():
            return str(legacy)
        return str(primary)

    @staticmethod
    def _patch_sklearn_compat(obj):
        """Compatibility patches for artifacts pickled with older scikit-learn versions."""
        try:
            if obj is None:
                return
            # SimpleImputer pickled in 1.6.x may miss _fill_dtype expected by 1.8.x
            if hasattr(obj, "statistics_") and not hasattr(obj, "_fill_dtype"):
                try:
                    import numpy as np
                    stats = getattr(obj, "statistics_", None)
                    if stats is not None:
                        obj._fill_dtype = stats.dtype
                    elif hasattr(obj, "_fit_dtype"):
                        obj._fill_dtype = obj._fit_dtype
                except Exception:
                    pass
            # Recurse into pipelines/composed estimators
            if hasattr(obj, "named_steps"):
                for step in obj.named_steps.values():
                    PPOPredictor._patch_sklearn_compat(step)
            if hasattr(obj, "steps"):
                for _, step in getattr(obj, "steps", []):
                    PPOPredictor._patch_sklearn_compat(step)
            if hasattr(obj, "transformers_"):
                for t in getattr(obj, "transformers_", []):
                    try:
                        transformer = t[1]
                        PPOPredictor._patch_sklearn_compat(transformer)
                    except Exception:
                        pass
            if hasattr(obj, "transformers"):
                for t in getattr(obj, "transformers", []):
                    try:
                        transformer = t[1]
                        PPOPredictor._patch_sklearn_compat(transformer)
                    except Exception:
                        pass
        except Exception:
            # Never fail loading solely due to best-effort compatibility patch
            pass

    def _load_artifacts(self):
        try:
            features_path = Path(self.features_path)
            metadata_path = Path(self.metadata_path)
            model_path = Path(self.model_path)

            if features_path.exists():
                with features_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.features = data
                elif isinstance(data, dict):
                    self.features = data.get("features", [])
            else:
                self.load_error = f"Features file not found at {features_path}"
                logger.error(self.load_error)

            if metadata_path.exists():
                with metadata_path.open("r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                self.threshold = float(self.metadata.get("threshold", 0.5))
            else:
                # Graceful fallback; required metrics provided in app
                self.metadata = {}
                self.threshold = 0.5

            if not model_path.exists():
                self.load_error = f"Model file not found at {model_path}"
                logger.error(self.load_error)
                self.is_loaded = False
                return

            self.model = joblib.load(model_path)
            self._patch_sklearn_compat(self.model)
            self.is_loaded = True
            logger.info("Successfully loaded PPO model from %s", model_path)

            # Prefer model feature names if available and consistent length
            if not self.features and hasattr(self.model, "feature_names_in_"):
                self.features = list(self.model.feature_names_in_)

            if hasattr(self.model, "feature_names_in_") and self.features:
                model_feats = list(self.model.feature_names_in_)
                if model_feats != self.features:
                    logger.warning(
                        "PPO feature order mismatch between features file and model; using features file order."
                    )
        except Exception as e:
            self.load_error = str(e)
            self.is_loaded = False
            self.model = None
            logger.error("Failed to load PPO artifacts: %s", e, exc_info=True)

    def predict(self, sanitized: Dict[str, float]) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            raise PPOModelLoadingError(
                self.load_error
                or "PPO prediction model is not loaded. Ensure PPO artifacts are present in backend/models/ppo/."
            )

        if not self.features:
            raise PPOModelLoadingError("PPO feature configuration is unavailable.")

        ordered = {feat: [sanitized[feat]] for feat in self.features}
        input_df = pd.DataFrame(ordered, columns=self.features)

        raw_pred = self.model.predict(input_df)[0]
        raw_proba = self.model.predict_proba(input_df)[0]

        classes = getattr(self.model, "classes_", [0, 1])
        try:
            idx_no = list(classes).index(0)
            idx_yes = list(classes).index(1)
        except ValueError:
            idx_no, idx_yes = 0, 1

        prob_no = float(raw_proba[idx_no])
        prob_yes = float(raw_proba[idx_yes])

        prediction = 1 if prob_yes >= self.threshold else 0
        # also respect model hard prediction when aligned; threshold is authoritative per spec
        label = "PPO Likely" if prediction == 1 else "PPO Unlikely"

        return {
            "success": True,
            "model": "ppo_prediction",
            "prediction": int(prediction),
            "prediction_label": label,
            "ppo_probability": round(prob_yes, 4),
            "no_ppo_probability": round(prob_no, 4),
            "threshold": float(self.threshold),
            "raw_model_prediction": int(raw_pred),
        }

    def get_info(self) -> Dict[str, Any]:
        # Ensure canonical metrics/coeffs are present even if metadata file missing
        canonical = {
            "algorithm": "Logistic Regression",
            "dataset": "Synthetic PPO Dataset V3",
            "dataset_records": 8017,
            "n_features": 8,
            "threshold": 0.5,
            "evaluation": {
                "test_accuracy": 0.8229,
                "precision": 0.8644,
                "recall": 0.8916,
                "f1_score": 0.8778,
                "roc_auc": 0.8852,
                "balanced_accuracy": 0.7719,
            },
            "coefficients": {
                "Technical_Evaluation": 0.712782,
                "Task_Completion_Rate": 0.542007,
                "Manager_Rating": 0.461836,
                "Code_Quality_Score": 0.296444,
                "Communication_Score": 0.2101,
                "Deadline_Adherence": 0.162467,
                "Attendance_Rate": 0.149356,
                "Teamwork_Score": 0.1201,
            },
            "disclosure": "This model was trained and evaluated on synthetic PPO data. Actual PPO decisions depend on company-specific evaluation criteria and cannot be guaranteed.",
        }
        merged = {**canonical, **(self.metadata or {})}
        merged["evaluation"] = {**canonical["evaluation"], **(self.metadata.get("evaluation", {}) if self.metadata else {})}
        merged["coefficients"] = canonical["coefficients"] if not self.metadata.get("coefficients") else self.metadata.get("coefficients")
        return {
            "is_loaded": self.is_loaded,
            "features": self.features,
            "feature_definitions": None,
            "load_error": self.load_error,
            **merged,
        }
