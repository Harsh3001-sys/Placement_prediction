"""
K-Means training and evaluation for Student Segmentation (Phase 3).

- Evaluates candidate K values (2..8 by default, bounded by sample size)
- Computes WCSS/inertia (Elbow), Silhouette, Davies-Bouldin, Calinski-Harabasz
- Selects a defensible K using aggregate metric ranking (not a single metric)
- Trains final role-specific KMeans with reproducible settings
- Prevents data leakage by fitting StandardScaler only on training data used for
  model fitting/evaluation and persisting it with artifacts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from .preprocessing import RoleDataset, validate_role_sample_size

logger = logging.getLogger(__name__)

RANDOM_STATE = 42
N_INIT = 10
MAX_ITER = 300
K_MIN_DEFAULT = 2
K_MAX_DEFAULT = 8


@dataclass
class KSelectionResult:
    selected_k: int
    candidate_metrics: List[Dict[str, Any]]
    selection: Dict[str, Any]


def _safe_float(value: Any) -> float:
    try:
        v = float(value)
        if np.isnan(v) or np.isinf(v):
            return 0.0
        return v
    except Exception:
        return 0.0


def candidate_k_range(n_samples: int, k_min: int = K_MIN_DEFAULT, k_max: int = K_MAX_DEFAULT) -> List[int]:
    # Need k < n_samples for silhouette and meaningful clustering; k >= 2
    upper = min(k_max, max(k_min, n_samples - 1))
    if upper < k_min:
        return []
    return list(range(k_min, upper + 1))


def evaluate_k_candidates(
    X_scaled: np.ndarray,
    k_values: List[int],
    random_state: int = RANDOM_STATE,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    n_samples = int(X_scaled.shape[0])

    for k in k_values:
        if k < 2 or k >= n_samples:
            continue
        km = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=N_INIT,
            max_iter=MAX_ITER,
        )
        labels = km.fit_predict(X_scaled)

        # Metrics on scaled feature space (same space used for clustering)
        inertia = _safe_float(km.inertia_)
        # silhouette requires >1 label and < n_samples unique labels in effect; k>=2 and k<n_samples ensures labels count
        try:
            sil = _safe_float(silhouette_score(X_scaled, labels))
        except Exception:
            sil = float("nan")
        try:
            db = _safe_float(davies_bouldin_score(X_scaled, labels))
        except Exception:
            db = float("nan")
        try:
            ch = _safe_float(calinski_harabasz_score(X_scaled, labels))
        except Exception:
            ch = float("nan")

        results.append(
            {
                "k": int(k),
                "wcss": inertia,
                "inertia": inertia,  # alias
                "silhouette_score": sil,
                "davies_bouldin_score": db,
                "calinski_harabasz_score": ch,
            }
        )
    return results


def _rank_values(values: List[Tuple[int, float]], higher_is_better: bool) -> Dict[int, int]:
    # Returns rank per k (1 = best)
    valid = [(k, v) for k, v in values if not (v is None or np.isnan(v) or np.isinf(v))]
    if not valid:
        return {k: 999 for k, _ in values}
    reverse = higher_is_better
    sorted_vals = sorted(valid, key=lambda x: x[1], reverse=reverse)
    ranks: Dict[int, int] = {}
    for idx, (k, _) in enumerate(sorted_vals, start=1):
        ranks[k] = idx
    # assign worst rank to invalids
    worst = (max(ranks.values()) + 1) if ranks else 999
    for k, v in values:
        if k not in ranks:
            ranks[k] = worst
    return ranks


def select_k(candidate_metrics: List[Dict[str, Any]]) -> KSelectionResult:
    if not candidate_metrics:
        raise ValueError("No candidate K metrics available for selection.")

    ks = [int(m["k"]) for m in candidate_metrics]
    sil_r = _rank_values([(m["k"], float(m.get("silhouette_score", np.nan))) for m in candidate_metrics], True)
    db_r = _rank_values([(m["k"], float(m.get("davies_bouldin_score", np.nan))) for m in candidate_metrics], False)
    ch_r = _rank_values([(m["k"], float(m.get("calinski_harabasz_score", np.nan))) for m in candidate_metrics], True)

    scored = []
    for m in candidate_metrics:
        k = int(m["k"])
        total_rank = sil_r[k] + db_r[k] + ch_r[k]
        sil = float(m.get("silhouette_score", float("nan")))
        # tie-breakers: lower total rank, higher silhouette, smaller K (parsimony)
        scored.append((total_rank, -(sil if not np.isnan(sil) else -1e9), k))

    scored.sort(key=lambda x: (x[0], x[1], x[2]))
    selected_k = int(scored[0][2])

    # Prepare rationale
    selected_metrics = next(m for m in candidate_metrics if int(m["k"]) == selected_k)
    best_sil_k = max(candidate_metrics, key=lambda m: (float(m.get("silhouette_score", -1e9)) if not np.isnan(float(m.get("silhouette_score", np.nan))) else -1e9))["k"]
    best_db_k = min(candidate_metrics, key=lambda m: (float(m.get("davies_bouldin_score", 1e9)) if not np.isnan(float(m.get("davies_bouldin_score", np.nan))) else 1e9))["k"]
    best_ch_k = max(candidate_metrics, key=lambda m: (float(m.get("calinski_harabasz_score", -1e9)) if not np.isnan(float(m.get("calinski_harabasz_score", np.nan))) else -1e9))["k"]

    rationale = (
        f"Selected K={selected_k} using aggregate rank across Silhouette (higher better), "
        f"Davies-Bouldin (lower better), and Calinski-Harabasz (higher better) for K={min(ks)}..{max(ks)}. "
        f"Ties broken by higher Silhouette, then smaller K (parsimony). "
        f"For selected K: Silhouette={selected_metrics.get('silhouette_score')}, "
        f"Davies-Bouldin={selected_metrics.get('davies_bouldin_score')}, "
        f"Calinski-Harabasz={selected_metrics.get('calinski_harabasz_score')}, "
        f"WCSS={selected_metrics.get('wcss')}. "
        f"Metric leaders in evaluated range: best Silhouette K={best_sil_k}, best Davies-Bouldin K={best_db_k}, "
        f"best Calinski-Harabasz K={best_ch_k}. WCSS is reported for elbow analysis; K was not chosen by a single metric."
    )

    selection = {
        "strategy": "aggregate_rank_silhouette_davies_bouldin_calinski_harabasz",
        "rationale": rationale,
        "ranks": {
            "silhouette": sil_r,
            "davies_bouldin": db_r,
            "calinski_harabasz": ch_r,
            "aggregate": {int(m["k"]): int(sil_r[int(m["k"])] + db_r[int(m["k"])] + ch_r[int(m["k"])]) for m in candidate_metrics},
        },
        "metric_leaders": {
            "best_silhouette_k": int(best_sil_k),
            "best_davies_bouldin_k": int(best_db_k),
            "best_calinski_harabasz_k": int(best_ch_k),
        },
    }

    return KSelectionResult(selected_k=selected_k, candidate_metrics=candidate_metrics, selection=selection)


def train_role_segmentation(
    role_data: RoleDataset,
    k_min: int = K_MIN_DEFAULT,
    k_max: int = K_MAX_DEFAULT,
    random_state: int = RANDOM_STATE,
) -> Dict[str, Any]:
    ok, msg = validate_role_sample_size(role_data.role_id, int(role_data.X.shape[0]), k_min=k_min, k_max=k_max)
    if not ok:
        raise ValueError(msg)

    k_values = candidate_k_range(int(role_data.X.shape[0]), k_min=k_min, k_max=k_max)
    if not k_values:
        raise ValueError(f"No valid K candidates for role '{role_data.role_id}' with n={role_data.X.shape[0]}.")

    # Fit scaler only on role training data (no external/user data leakage)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(role_data.X)

    candidates = evaluate_k_candidates(X_scaled, k_values, random_state=random_state)
    selection = select_k(candidates)

    final_km = KMeans(
        n_clusters=selection.selected_k,
        random_state=random_state,
        n_init=N_INIT,
        max_iter=MAX_ITER,
    )
    labels = final_km.fit_predict(X_scaled)

    # Final metrics (on same scaled space)
    final_metrics = {
        "k": int(selection.selected_k),
        "wcss": _safe_float(final_km.inertia_),
        "silhouette_score": _safe_float(silhouette_score(X_scaled, labels)) if selection.selected_k >= 2 else float("nan"),
        "davies_bouldin_score": _safe_float(davies_bouldin_score(X_scaled, labels)) if selection.selected_k >= 2 else float("nan"),
        "calinski_harabasz_score": _safe_float(calinski_harabasz_score(X_scaled, labels)) if selection.selected_k >= 2 else float("nan"),
    }

    training_metadata = {
        "role_id": role_data.role_id,
        "role_name": role_data.role_name,
        "algorithm": "KMeans",
        "random_state": int(random_state),
        "n_init": N_INIT,
        "max_iter": MAX_ITER,
        "n_samples": int(role_data.X.shape[0]),
        "n_features": int(role_data.X.shape[1]),
        "selected_k": int(selection.selected_k),
        "k_range_evaluated": k_values,
        "candidate_metrics": candidates,
        "selection": selection.selection,
        "final_metrics": final_metrics,
        "feature_names": role_data.feature_names,
        "feature_skill_ids": role_data.feature_skill_ids,
        "preprocessing": {
            "scaler": "StandardScaler",
            "scaler_fit": "fit_on_role_training_data_only",
            "feature_selection": "role_relevant_skills_from_phase1_role_skill_requirements",
            "feature_order": "phase1_role_requirement_order",
            "numeric_validation": True,
            "missing_value_handling": "checked; median imputation within role data if encountered (none expected in provided dataset)",
            "duplicate_student_id_check": True,
            "notes": "Clustering and internal evaluation metrics computed on standardized role-specific feature space. Centroid-based interpretation uses original-scale skill values.",
        },
        "data_summary": role_data.summary,
        "disclosure": (
            "Trained on synthetic student skill profiles. Clustering metrics indicate separation/compactness on synthetic data "
            "and do not establish real-world student segmentation quality. Cluster assignment is not a placement prediction."
        ),
    }

    return {
        "model": final_km,
        "scaler": scaler,
        "labels": labels,
        "X_scaled": X_scaled,
        "metadata": training_metadata,
        "feature_config": {
            "role_id": role_data.role_id,
            "role_name": role_data.role_name,
            "feature_names": role_data.feature_names,
            "feature_skill_ids": role_data.feature_skill_ids,
        },
    }
