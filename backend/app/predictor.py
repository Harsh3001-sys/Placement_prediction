"""
Machine learning inference and model inspection service for CareerLens.
Loads the serialized Logistic Regression pipeline and performs deterministic predictions.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

# Canonical evaluation metrics obtained from the project's test evaluation
CANONICAL_EVALUATION = {
    "test_accuracy": 0.8085,
    "precision": 0.7701,
    "recall": 0.7747,
    "f1_score": 0.7724,
    "roc_auc": 0.8840,
    "dataset_total_samples": 10000,
    "train_samples": 8000,
    "test_samples": 2000,
    "split_ratio": "80/20 (Stratified)",
    "algorithm": "Logistic Regression (with StandardScaler)",
    "confusion_matrix": {
        "true_negative": 967,
        "false_positive": 194,
        "false_negative": 189,
        "true_positive": 650,
        "matrix": [
            [967, 194],
            [189, 650],
        ],
        "labels": ["NotPlaced", "Placed"],
    },
    "synthetic_features": [
        "LeetCode_Problems_Solved",
        "Hackathon_Wins",
        "Publications",
    ],
    "synthetic_disclosure": (
        "Three features — LeetCode problems solved, hackathon wins, and research publications — "
        "were synthetically synthesized to enrich the baseline dataset. Evaluation metrics reflect "
        "performance on this designated evaluation set and represent an academic demonstration rather than "
        "guaranteed real-world placement causality."
    ),
}


class ModelLoadingError(Exception):
    """Raised when the serialized model artifact or features schema cannot be loaded."""

    pass


class PlacementPredictor:
    def __init__(self, model_path: Optional[str] = None, features_path: Optional[str] = None):
        self.model_path = str(Path(model_path).resolve()) if model_path else self._resolve_default_path(
            "placement_model.joblib"
        )
        self.features_path = (
            str(Path(features_path).resolve()) if features_path else self._resolve_default_path("features.json")
        )
        self.model = None
        self.features: List[str] = []
        self.features_metadata: Dict[str, Any] = {}
        self.coefficients: Dict[str, float] = {}
        self.intercept: Optional[float] = None
        self.is_loaded = False
        self._load_artifacts()

    @staticmethod
    def _resolve_default_path(filename: str) -> str:
        """Resolve runtime artifact path relative to backend directory (CWD-independent)."""
        backend_dir = Path(__file__).resolve().parents[1]
        workspace_root = Path(__file__).resolve().parents[2]
        candidates = [
            backend_dir / "models" / "placement" / filename,
            backend_dir / "artifacts" / filename,  # legacy fallback
            workspace_root / filename,  # legacy fallback
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return str(candidates[0])

    def _load_artifacts(self):
        """Loads the serialized scikit-learn model and features list."""
        model_path = Path(self.model_path)
        features_path = Path(self.features_path)

        if not model_path.exists():
            logger.error("Model file not found at %s", model_path)
            self.is_loaded = False
            return

        try:
            self.model = joblib.load(model_path)
            self.is_loaded = True
            logger.info("Successfully loaded model from %s", model_path)
        except Exception as e:
            logger.error("Failed to deserialize model at %s: %s", model_path, str(e))
            self.is_loaded = False
            self.model = None
            return

        # Load features schema
        if features_path.exists():
            try:
                with features_path.open("r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                self.features = schema_data.get("features", [])
                self.features_metadata = schema_data.get("feature_metadata", {})
            except Exception as e:
                logger.warning("Could not read features.json (%s), falling back to model attributes", e)

        # Fallback to model's feature_names_in_ if features wasn't read
        if not self.features and hasattr(self.model, "feature_names_in_"):
            self.features = list(self.model.feature_names_in_)

        # Extract logistic regression coefficients if available
        self._extract_coefficients()

    def _extract_coefficients(self):
        if not self.is_loaded or self.model is None:
            return

        try:
            # Check pipeline steps
            lr_estimator = None
            if hasattr(self.model, "named_steps"):
                lr_estimator = self.model.named_steps.get("logisticregression")
            elif hasattr(self.model, "coef_"):
                lr_estimator = self.model

            if lr_estimator is not None and hasattr(lr_estimator, "coef_"):
                coef_array = lr_estimator.coef_[0]
                self.intercept = (
                    float(lr_estimator.intercept_[0]) if hasattr(lr_estimator, "intercept_") else None
                )
                for idx, feat in enumerate(self.features):
                    if idx < len(coef_array):
                        self.coefficients[feat] = round(float(coef_array[idx]), 4)
        except Exception as e:
            logger.warning("Could not extract coefficients: %s", e)

    def predict(self, sanitized_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs deterministic inference on sanitized feature dictionary.
        Returns predicted class and both class probabilities.
        """
        if not self.is_loaded or self.model is None:
            raise ModelLoadingError(
                "Prediction model is not initialized or artifact file is missing. "
                "Ensure placement_model.joblib is present in backend/models/placement/."
            )

        # Build DataFrame with strictly ordered columns
        ordered_data = {feat: [sanitized_data[feat]] for feat in self.features}
        input_df = pd.DataFrame(ordered_data)

        # Run inference
        raw_pred = self.model.predict(input_df)[0]
        raw_proba = self.model.predict_proba(input_df)[0]

        # In binary classification: class 0 = NotPlaced, class 1 = Placed
        classes = getattr(self.model, "classes_", [0, 1])
        class_0_idx = list(classes).index(0) if 0 in classes else 0
        class_1_idx = list(classes).index(1) if 1 in classes else 1

        prob_not_placed = float(raw_proba[class_0_idx])
        prob_placed = float(raw_proba[class_1_idx])

        prediction_label = "Placed" if raw_pred == 1 else "Not Placed"

        return {
            "prediction": prediction_label,
            "placement_probability": round(prob_placed, 4),
            "not_placed_probability": round(prob_not_placed, 4),
            "model": "Logistic Regression",
            "features_analyzed": len(self.features),
            "disclaimer": (
                "Prediction generated by an academic Logistic Regression model. "
                "Model-estimated probabilities are statistical likelihoods, not employment guarantees."
            ),
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Returns model architecture, test metrics, confusion matrix, and feature coefficients."""
        return {
            "model_name": "Logistic Regression",
            "is_loaded": self.is_loaded,
            "n_features": len(self.features),
            "features": self.features,
            "feature_metadata": self.features_metadata,
            "coefficients": self.coefficients,
            "intercept": self.intercept,
            "evaluation": CANONICAL_EVALUATION,
        }
