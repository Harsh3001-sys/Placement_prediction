"""
Artifact persistence and runtime loading for Student Segmentation (Phase 3).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
SEGMENTATION_MODELS_DIR = BACKEND_DIR / "models" / "segmentation"
SEGMENTATION_REPORTS_DIR = BACKEND_DIR / "reports" / "segmentation"

MODEL_FILENAME = "kmeans_model.joblib"
SCALER_FILENAME = "scaler.joblib"
FEATURE_CONFIG_FILENAME = "feature_config.json"
METADATA_FILENAME = "training_metadata.json"


def ensure_segmentation_dirs() -> None:
    SEGMENTATION_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    SEGMENTATION_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def role_artifact_dir(role_id: str) -> Path:
    return SEGMENTATION_MODELS_DIR / str(role_id)


def save_role_artifacts(
    role_id: str,
    model: Any,
    scaler: Any,
    feature_config: Dict[str, Any],
    metadata: Dict[str, Any],
) -> Dict[str, str]:
    out_dir = role_artifact_dir(role_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    model_path = out_dir / MODEL_FILENAME
    scaler_path = out_dir / SCALER_FILENAME
    feature_path = out_dir / FEATURE_CONFIG_FILENAME
    meta_path = out_dir / METADATA_FILENAME

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    feature_path.write_text(json.dumps(feature_config, indent=2), encoding="utf-8")
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return {
        "role_id": str(role_id),
        "model_path": str(model_path),
        "scaler_path": str(scaler_path),
        "feature_config_path": str(feature_path),
        "metadata_path": str(meta_path),
    }


def load_role_artifacts(role_id: str) -> Dict[str, Any]:
    d = role_artifact_dir(role_id)
    model_path = d / MODEL_FILENAME
    scaler_path = d / SCALER_FILENAME
    feature_path = d / FEATURE_CONFIG_FILENAME
    meta_path = d / METADATA_FILENAME

    missing = [str(p) for p in [model_path, scaler_path, feature_path, meta_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(
            f"Segmentation artifacts missing for role '{role_id}'. Missing: {missing}. "
            "Train models using backend/scripts/train_student_clusters.py."
        )

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_config = json.loads(feature_path.read_text(encoding="utf-8"))
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))

    return {
        "role_id": str(role_id),
        "model": model,
        "scaler": scaler,
        "feature_config": feature_config,
        "metadata": metadata,
        "artifact_dir": str(d),
    }


def list_available_segmentation_roles() -> List[str]:
    if not SEGMENTATION_MODELS_DIR.exists():
        return []
    roles = []
    for child in SEGMENTATION_MODELS_DIR.iterdir():
        if not child.is_dir():
            continue
        required = [
            child / MODEL_FILENAME,
            child / SCALER_FILENAME,
            child / FEATURE_CONFIG_FILENAME,
            child / METADATA_FILENAME,
        ]
        if all(p.exists() for p in required):
            roles.append(child.name)
    roles.sort()
    return roles


def role_has_artifacts(role_id: str) -> bool:
    d = role_artifact_dir(role_id)
    required = [d / MODEL_FILENAME, d / SCALER_FILENAME, d / FEATURE_CONFIG_FILENAME, d / METADATA_FILENAME]
    return all(p.exists() for p in required)


def predict_cluster(model: Any, scaler: Any, X_original: np.ndarray) -> Dict[str, Any]:
    """Predict cluster for feature vector(s) in original scale using persisted scaler/model."""
    X_scaled = scaler.transform(X_original)
    labels = model.predict(X_scaled)
    # Distances to centroids in scaled space (explainability/supporting info)
    if hasattr(model, "transform"):
        distances = model.transform(X_scaled)
    else:
        # Euclidean distances to cluster_centers_
        centers = getattr(model, "cluster_centers_", None)
        if centers is None:
            distances = None
        else:
            diff = X_scaled[:, None, :] - centers[None, :, :]
            distances = np.sqrt(np.sum(diff ** 2, axis=2))
    label = int(labels[0]) if len(labels) else -1
    dist_row = distances[0].tolist() if distances is not None and len(distances) else None
    return {
        "cluster_id": label,
        "labels": [int(x) for x in labels.tolist()],
        "distances_to_centroids_scaled": dist_row,
    }


def load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
