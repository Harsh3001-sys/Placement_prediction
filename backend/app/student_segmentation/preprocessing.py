"""
Role-aware preprocessing for Student Segmentation (Phase 3).

Uses existing synthetic student profiles and Phase 1 role-skill mappings.
Preprocessing is deterministic and documented:
- Role-aware feature selection (only skills relevant to selected role)
- Consistent feature ordering per role (Phase 1 role requirement order)
- Numeric validation and coercion checks
- Missing-value checks/handling (dataset is expected complete; missing numeric
  values would be imputed with role feature median if encountered)
- Duplicate student_id checks
- StandardScaler fit only on provided training data and persisted with artifacts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from functools import lru_cache

from app.skill_gap.dataset_loader import STUDENT_PROFILES_CSV, get_role_requirements

logger = logging.getLogger(__name__)


@dataclass
class RoleDataset:
    role_id: str
    role_name: str
    feature_names: List[str]          # ordered skill names (role-relevant)
    feature_skill_ids: List[str]      # aligned skill_ids
    X: np.ndarray                     # shape (n_samples, n_features), float64
    df: pd.DataFrame                  # filtered role dataframe (original scale)
    student_ids: List[str]
    summary: Dict[str, Any]


def get_role_feature_config(role_id: str) -> Dict[str, Any]:
    """Return ordered feature configuration for a role from Phase 1 mappings."""
    role = get_role_requirements(role_id)
    skills = role.get("skills", [])
    feature_names = [str(s["skill_name"]) for s in skills]
    feature_skill_ids = [str(s["skill_id"]) for s in skills]
    return {
        "role_id": role.get("role_id"),
        "role_name": role.get("role_name"),
        "feature_names": feature_names,
        "feature_skill_ids": feature_skill_ids,
        "n_features": len(feature_names),
        "skills": skills,
    }


def validate_role_sample_size(role_id: str, n_samples: int, k_min: int = 2, k_max: int = 8) -> Tuple[bool, str]:
    """Return (ok, message). Need enough samples to evaluate/train meaningful clusters."""
    # For silhouette and stable KMeans fits, require n_samples > k_max and at least 2*k_min.
    min_required = max(k_max + 1, k_min * 2, 10)
    if n_samples < min_required:
        return (
            False,
            f"Role '{role_id}' has insufficient student samples for meaningful clustering "
            f"(n={n_samples}, minimum required={min_required} for K={k_min}..{k_max}).",
        )
    return True, ""


@lru_cache(maxsize=1)
def _load_student_profiles_df() -> pd.DataFrame:
    if not STUDENT_PROFILES_CSV.exists():
        raise ValueError(f"Required dataset not found: {STUDENT_PROFILES_CSV}")
    df = pd.read_csv(STUDENT_PROFILES_CSV, encoding="utf-8-sig")
    if df.empty:
        raise ValueError(f"Dataset is empty: {STUDENT_PROFILES_CSV}")
    return df


def load_role_dataset(role_id: str) -> RoleDataset:
    """Load, validate, and extract role-aware feature matrix for a target role."""
    role_cfg = get_role_feature_config(role_id)
    role_name = role_cfg["role_name"]
    feature_names = role_cfg["feature_names"]
    feature_skill_ids = role_cfg["feature_skill_ids"]

    if not feature_names:
        raise ValueError(f"No relevant skills found for role '{role_id}'.")

    profiles_df = _load_student_profiles_df().copy()
    if "target_role" not in profiles_df.columns:
        raise ValueError("student_skill_profiles.csv is missing required column 'target_role'.")
    if "student_id" not in profiles_df.columns:
        raise ValueError("student_skill_profiles.csv is missing required column 'student_id'.")

    role_df = profiles_df[profiles_df["target_role"].astype(str) == str(role_id)].copy()
    n_samples = len(role_df)
    if n_samples == 0:
        raise ValueError(f"No student profiles found for role '{role_id}'.")

    # Duplicate student_id checks
    dup_ids = int(role_df["student_id"].astype(str).duplicated().sum())
    if dup_ids > 0:
        raise ValueError(f"Duplicate student_id values found for role '{role_id}' (count={dup_ids}).")

    # Ensure all required role features exist
    missing_cols = [c for c in feature_names if c not in role_df.columns]
    if missing_cols:
        raise ValueError(
            f"Student profiles are missing required role feature columns for '{role_id}': {missing_cols}"
        )

    # Numeric validation and missing-value handling
    X_df = role_df[feature_names].copy()
    # Coerce to numeric; non-numeric become NaN and are reported
    for col in feature_names:
        X_df[col] = pd.to_numeric(X_df[col], errors="coerce")

    non_numeric_cells = int(X_df.isna().sum().sum())
    if non_numeric_cells > 0:
        # Defensive handling: impute missing/non-numeric with feature median (fit on role data only)
        medians = X_df.median(numeric_only=True)
        X_df = X_df.fillna(medians)
        logger.warning(
            "Role %s: encountered %s missing/non-numeric skill values; imputed with role feature medians.",
            role_id,
            non_numeric_cells,
        )

    # Range validation/clamping (skill proficiencies expected 0-100)
    out_of_range = int(((X_df < 0) | (X_df > 100)).to_numpy().sum())
    if out_of_range > 0:
        logger.warning("Role %s: clamped %s out-of-range skill values to [0, 100].", role_id, out_of_range)
        X_df = X_df.clip(lower=0.0, upper=100.0)

    X = X_df.to_numpy(dtype=np.float64)
    if X.ndim != 2 or X.shape[1] != len(feature_names):
        raise ValueError(f"Invalid feature matrix shape for role '{role_id}': {X.shape}")

    summary = {
        "role_id": role_id,
        "role_name": role_name,
        "n_samples": int(n_samples),
        "n_features": int(len(feature_names)),
        "duplicate_student_ids": dup_ids,
        "missing_or_non_numeric_cells_imputed": non_numeric_cells,
        "out_of_range_cells_clamped": out_of_range,
        "feature_means": {name: float(X_df[name].mean()) for name in feature_names},
        "feature_stds": {name: float(X_df[name].std(ddof=0)) for name in feature_names},
        "feature_mins": {name: float(X_df[name].min()) for name in feature_names},
        "feature_maxs": {name: float(X_df[name].max()) for name in feature_names},
    }

    return RoleDataset(
        role_id=str(role_id),
        role_name=str(role_name),
        feature_names=feature_names,
        feature_skill_ids=feature_skill_ids,
        X=X,
        df=role_df.reset_index(drop=True),
        student_ids=role_df["student_id"].astype(str).tolist(),
        summary=summary,
    )


def build_feature_vector(
    normalized_skills: Dict[str, float],
    feature_names: List[str],
) -> np.ndarray:
    """Build ordered feature vector (1, n_features) from normalized lowercase skill map."""
    values = []
    for name in feature_names:
        key = str(name).strip().lower()
        val = float(normalized_skills.get(key, 0.0))
        if val < 0:
            val = 0.0
        elif val > 100:
            val = 100.0
        values.append(val)
    return np.array([values], dtype=np.float64)


