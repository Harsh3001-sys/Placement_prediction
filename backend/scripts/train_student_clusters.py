"""
Train role-aware K-Means student segmentation models (CareerLens Phase 3).

Loads backend/datasets/student_skill_profiles.csv and Phase 1 role-skill mappings,
performs role-aware preprocessing, evaluates K=2..8 using WCSS/Elbow, Silhouette,
Davies-Bouldin, and Calinski-Harabasz, selects a defensible K, trains reproducible
KMeans models per role, saves artifacts/metadata, and generates evaluation reports/plots.

Usage:
  cd backend
  python scripts/train_student_clusters.py

  # or from repo root
  python backend/scripts/train_student_clusters.py

Outputs:
  backend/models/segmentation/<role_id>/  (kmeans_model.joblib, scaler.joblib, feature_config.json, training_metadata.json)
  backend/reports/segmentation/           (metrics, summaries, plots per role)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Ensure backend root is importable when script is run directly
SCRIPT_PATH = Path(__file__).resolve()
BACKEND_DIR = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[2]
for p in (str(BACKEND_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA

from app.skill_gap.dataset_loader import get_role_requirements, get_roles
from app.student_segmentation.cluster_analyzer import analyze_role_clusters
from app.student_segmentation.clustering import K_MAX_DEFAULT, K_MIN_DEFAULT, train_role_segmentation
from app.student_segmentation.model_loader import (
    SEGMENTATION_REPORTS_DIR,
    ensure_segmentation_dirs,
    role_artifact_dir,
    save_role_artifacts,
)
from app.student_segmentation.preprocessing import load_role_dataset, validate_role_sample_size

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("train_student_clusters")


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(value))


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _plot_metric_lines(role_id: str, role_name: str, candidates: List[Dict[str, Any]], out_dir: Path) -> Dict[str, str]:
    paths: Dict[str, str] = {}
    ks = [int(c["k"]) for c in candidates]
    if not ks:
        return paths

    def plot_one(metric_key: str, ylabel: str, title_suffix: str, filename: str):
        ys = [float(c.get(metric_key, np.nan)) for c in candidates]
        plt.figure(figsize=(7, 4.5))
        plt.plot(ks, ys, marker="o", linewidth=2, color="#3D827C")
        plt.xticks(ks)
        plt.xlabel("K (number of clusters)")
        plt.ylabel(ylabel)
        plt.title(f"{role_name} ({role_id}) - {title_suffix}")
        plt.grid(True, alpha=0.25)
        out = out_dir / filename
        plt.tight_layout()
        plt.savefig(out, dpi=160)
        plt.close()
        paths[metric_key] = str(out)

    plot_one("wcss", "WCSS / Inertia (lower is better for compactness; elbow heuristic)", "Elbow (WCSS by K)", f"{role_id}_elbow_wcss.png")
    plot_one("silhouette_score", "Silhouette Score (higher is better)", "Silhouette Score by K", f"{role_id}_silhouette_by_k.png")
    plot_one("davies_bouldin_score", "Davies-Bouldin Index (lower is better)", "Davies-Bouldin by K", f"{role_id}_davies_bouldin_by_k.png")
    plot_one("calinski_harabasz_score", "Calinski-Harabasz Score (higher is better)", "Calinski-Harabasz by K", f"{role_id}_calinski_harabasz_by_k.png")
    return paths


def _plot_cluster_distribution(role_id: str, role_name: str, cluster_analysis: Dict[str, Any], out_dir: Path) -> str:
    dist = cluster_analysis.get("cluster_distribution", [])
    labels = [f"C{d['cluster_id']}: {d.get('cluster_name', '')}" for d in dist]
    counts = [int(d.get("student_count", 0)) for d in dist]
    # shorten labels for plot readability
    short_labels = [f"C{d['cluster_id']}" for d in dist]
    plt.figure(figsize=(max(7, len(dist) * 1.6), 4.8))
    bars = plt.bar(short_labels, counts, color=["#3D827C", "#C6A66B", "#5A8A9A", "#101C2C", "#7C8A99", "#8C6E3D", "#2F6F68", "#B45309"][: len(dist)])
    plt.xlabel("Cluster")
    plt.ylabel("Number of students")
    plt.title(f"{role_name} ({role_id}) - Cluster Distribution")
    plt.grid(axis="y", alpha=0.25)
    for bar, d in zip(bars, dist):
        pct = d.get("student_percentage", 0)
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{int(bar.get_height())}\n({pct}%)", ha="center", va="bottom", fontsize=8)
    out = out_dir / f"{role_id}_cluster_distribution.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160)
    plt.close()
    return str(out)


def _plot_cluster_profiles(role_id: str, role_name: str, cluster_analysis: Dict[str, Any], feature_names: List[str], out_dir: Path) -> str:
    clusters = cluster_analysis.get("clusters", [])
    if not clusters:
        return ""
    # Heatmap-like profile chart: clusters x skills (average proficiency)
    data = np.array([[c.get("average_proficiency_per_skill", {}).get(f, 0.0) for f in feature_names] for c in clusters], dtype=float)
    plt.figure(figsize=(max(10, len(feature_names) * 0.55), max(4.5, len(clusters) * 0.8 + 1.5)))
    im = plt.imshow(data, aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
    plt.colorbar(im, label="Average proficiency (0-100)")
    plt.yticks(range(len(clusters)), [f"C{c['cluster_id']}" for c in clusters])
    xlabels = [("DSA" if f == "Data Structures and Algorithms" else ("OOP" if f == "Object-Oriented Programming" else f)) for f in feature_names]
    plt.xticks(range(len(feature_names)), xlabels, rotation=45, ha="right", fontsize=8)
    plt.title(f"{role_name} ({role_id}) - Cluster Skill Profiles (Centroid Means, Original Scale)")
    plt.xlabel("Role-relevant skills")
    plt.ylabel("Clusters")
    out = out_dir / f"{role_id}_cluster_profiles.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160)
    plt.close()
    return str(out)


def _plot_pca_clusters(role_id: str, role_name: str, X_scaled: np.ndarray, labels: np.ndarray, out_dir: Path) -> str:
    # PCA is for visualization only (clustering performed in original standardized role feature space)
    if X_scaled.shape[0] < 2 or X_scaled.shape[1] < 2:
        return ""
    n_components = 2 if X_scaled.shape[1] >= 2 else 1
    pca = PCA(n_components=n_components, random_state=42)
    emb = pca.fit_transform(X_scaled)
    plt.figure(figsize=(7.5, 5.5))
    unique = sorted(int(x) for x in np.unique(labels))
    cmap = plt.get_cmap("tab10")
    for i, cid in enumerate(unique):
        mask = labels == cid
        pts = emb[mask]
        plt.scatter(pts[:, 0], pts[:, 1] if n_components > 1 else np.zeros(len(pts)), s=28, alpha=0.75, label=f"Cluster {cid}", color=cmap(i % 10))
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
    if n_components > 1:
        plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
    else:
        plt.ylabel("PC2 (n/a)")
    plt.title(f"{role_name} ({role_id}) - PCA 2D Cluster Visualization (viz only)")
    plt.legend(fontsize=8)
    plt.grid(True, alpha=0.2)
    out = out_dir / f"{role_id}_pca_clusters.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160)
    plt.close()
    return str(out)


def train_for_role(role_id: str) -> Dict[str, Any]:
    role_cfg = get_role_requirements(role_id)
    role_name = role_cfg.get("role_name", role_id)
    logger.info("Processing role: %s (%s)", role_name, role_id)

    role_data = load_role_dataset(role_id)
    ok, msg = validate_role_sample_size(role_data.role_id, int(role_data.X.shape[0]), k_min=K_MIN_DEFAULT, k_max=K_MAX_DEFAULT)
    if not ok:
        logger.warning(msg)
        return {"role_id": role_id, "role_name": role_name, "status": "skipped", "reason": msg}

    result = train_role_segmentation(role_data, k_min=K_MIN_DEFAULT, k_max=K_MAX_DEFAULT)

    # Cluster interpretation (original scale)
    cluster_analysis = analyze_role_clusters(
        role_id=role_id,
        role_name=role_name,
        feature_names=role_data.feature_names,
        X_original=role_data.X,
        labels=result["labels"],
        requirements=role_data.summary.get("skills") or role_cfg.get("skills", []),
    )
    # enrich metadata with interpretation summary
    result["metadata"]["cluster_analysis_summary"] = {
        "cluster_distribution": cluster_analysis.get("cluster_distribution", []),
        "overall_role_average": cluster_analysis.get("overall_role_average"),
        "clusters": [
            {
                "cluster_id": c["cluster_id"],
                "cluster_name": c["cluster_name"],
                "student_count": c["student_count"],
                "student_percentage": c["student_percentage"],
                "average_skill_proficiency": c["average_skill_proficiency"],
            }
            for c in cluster_analysis.get("clusters", [])
        ],
    }

    # Save runtime cluster analysis alongside artifacts for API use
    artifact_paths = save_role_artifacts(
        role_id=role_id,
        model=result["model"],
        scaler=result["scaler"],
        feature_config=result["feature_config"],
        metadata=result["metadata"],
    )
    try:
        (role_artifact_dir(role_id) / "cluster_analysis.json").write_text(
            json.dumps(cluster_analysis, indent=2, default=str), encoding="utf-8"
        )
        artifact_paths["cluster_analysis_path"] = str(role_artifact_dir(role_id) / "cluster_analysis.json")
    except Exception as e:
        logger.warning("Failed to save cluster_analysis.json in artifact dir for %s: %s", role_id, e)

    # Reports/plots
    role_report_dir = SEGMENTATION_REPORTS_DIR / role_id
    role_report_dir.mkdir(parents=True, exist_ok=True)
    candidates = result["metadata"].get("candidate_metrics", [])
    metrics_csv = role_report_dir / f"{role_id}_k_evaluation_metrics.csv"
    pd.DataFrame(candidates).to_csv(metrics_csv, index=False)
    _save_json(role_report_dir / f"{role_id}_training_metadata.json", result["metadata"])
    _save_json(role_report_dir / f"{role_id}_cluster_analysis.json", cluster_analysis)

    plot_paths = {}
    plot_paths.update(_plot_metric_lines(role_id, role_name, candidates, role_report_dir))
    plot_paths["cluster_distribution"] = _plot_cluster_distribution(role_id, role_name, cluster_analysis, role_report_dir)
    plot_paths["cluster_profiles"] = _plot_cluster_profiles(role_id, role_name, cluster_analysis, role_data.feature_names, role_report_dir)
    pca_path = _plot_pca_clusters(role_id, role_name, result["X_scaled"], np.array(result["labels"]), role_report_dir)
    if pca_path:
        plot_paths["pca_clusters"] = pca_path

    # Per-role summary
    role_summary = {
        "role_id": role_id,
        "role_name": role_name,
        "status": "trained",
        "n_students": int(role_data.X.shape[0]),
        "n_features": int(role_data.X.shape[1]),
        "feature_names": role_data.feature_names,
        "selected_k": int(result["metadata"].get("selected_k")),
        "final_metrics": result["metadata"].get("final_metrics", {}),
        "selection": result["metadata"].get("selection", {}),
        "candidate_metrics": candidates,
        "cluster_distribution": cluster_analysis.get("cluster_distribution", []),
        "clusters": [
            {
                "cluster_id": c["cluster_id"],
                "cluster_name": c["cluster_name"],
                "cluster_description": c["cluster_description"],
                "student_count": c["student_count"],
                "student_percentage": c["student_percentage"],
                "average_skill_proficiency": c["average_skill_proficiency"],
                "strongest_skills": c["strongest_skills"],
                "weakest_skills": c["weakest_skills"],
            }
            for c in cluster_analysis.get("clusters", [])
        ],
        "artifacts": artifact_paths,
        "reports": {
            "metrics_csv": str(metrics_csv),
            "metadata_json": str(role_report_dir / f"{role_id}_training_metadata.json"),
            "cluster_analysis_json": str(role_report_dir / f"{role_id}_cluster_analysis.json"),
            "plots": plot_paths,
        },
    }
    _save_json(role_report_dir / f"{role_id}_summary.json", role_summary)
    logger.info(
        "Trained role=%s k=%s silhouette=%s db=%s ch=%s",
        role_id,
        role_summary["selected_k"],
        role_summary["final_metrics"].get("silhouette_score"),
        role_summary["final_metrics"].get("davies_bouldin_score"),
        role_summary["final_metrics"].get("calinski_harabasz_score"),
    )
    return role_summary


def main():
    parser = argparse.ArgumentParser(description="Train role-aware K-Means student segmentation models.")
    parser.add_argument("--roles", nargs="*", default=None, help="Optional subset of role_ids to train")
    args = parser.parse_args()

    ensure_segmentation_dirs()
    roles = get_roles()
    role_ids = [r["role_id"] for r in roles]
    if args.roles:
        wanted = set(args.roles)
        role_ids = [rid for rid in role_ids if rid in wanted]
        missing = [r for r in args.roles if r not in {x["role_id"] for x in roles}]
        if missing:
            raise SystemExit(f"Unknown role_ids requested: {missing}")

    summaries: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for role_id in role_ids:
        try:
            summaries.append(train_for_role(role_id))
        except Exception as e:
            logger.exception("Failed training role %s: %s", role_id, e)
            errors.append({"role_id": role_id, "error": str(e)})
            summaries.append({"role_id": role_id, "status": "error", "reason": str(e)})

    trained = [s for s in summaries if s.get("status") == "trained"]
    overall = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "backend/datasets/student_skill_profiles.csv",
        "role_mappings_source": "backend/datasets/role_skill_requirements.csv (Phase 1)",
        "algorithm": "KMeans (sklearn.cluster.KMeans)",
        "k_range_evaluated": list(range(K_MIN_DEFAULT, K_MAX_DEFAULT + 1)),
        "roles_requested": role_ids,
        "roles_trained": [s["role_id"] for s in trained],
        "roles_skipped_or_failed": [s["role_id"] for s in summaries if s.get("status") != "trained"],
        "errors": errors,
        "role_summaries": summaries,
        "disclosure": {
            "synthetic_profiles": "Student profiles are synthetic (illustrative) and not real student records.",
            "synthetic_labels": "Cluster labels/descriptions are derived from learned centroids on synthetic profiles and Phase 1 synthetic/illustrative role mappings.",
            "metrics_not_real_world": "Clustering metrics indicate structure/separation on the provided synthetic data and do not establish real-world student segmentation quality.",
            "not_placement_prediction": "Cluster assignment is not a placement prediction.",
            "real_data_validation": "Validate on real, representative student data before drawing real-world conclusions.",
        },
    }
    _save_json(SEGMENTATION_REPORTS_DIR / "training_summary.json", overall)

    # Also write a compact markdown summary for quick inspection
    lines = [
        "# Student Segmentation Training Summary",
        "",
        f"Generated (UTC): {overall['generated_at_utc']}",
        "",
        f"- Dataset: `{overall['dataset']}`",
        f"- Roles trained: {', '.join(overall['roles_trained']) if overall['roles_trained'] else '(none)'}",
        f"- K range evaluated: {K_MIN_DEFAULT}..{K_MAX_DEFAULT}",
        "",
        "## Role Results",
        "",
    ]
    for s in summaries:
        if s.get("status") == "trained":
            fm = s.get("final_metrics", {})
            lines.append(f"### {s.get('role_name')} (`{s.get('role_id')}`)")
            lines.append(f"- Students: {s.get('n_students')} | Features: {s.get('n_features')} | Selected K: {s.get('selected_k')}")
            lines.append(f"- Silhouette: {fm.get('silhouette_score')} | Davies-Bouldin: {fm.get('davies_bouldin_score')} | Calinski-Harabasz: {fm.get('calinski_harabasz_score')} | WCSS: {fm.get('wcss')}")
            sel = s.get("selection", {})
            if sel.get("rationale"):
                lines.append(f"- Rationale: {sel.get('rationale')}")
            for c in s.get("clusters", []):
                lines.append(f"  - Cluster {c['cluster_id']} ({c['cluster_name']}): {c['student_count']} students ({c['student_percentage']}%), avg {c['average_skill_proficiency']}")
            lines.append("")
        else:
            lines.append(f"### `{s.get('role_id')}` - {s.get('status')}")
            lines.append(f"- {s.get('reason')}")
            lines.append("")
    (SEGMENTATION_REPORTS_DIR / "training_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "status": "ok" if not errors else "completed_with_errors",
        "roles_trained": overall["roles_trained"],
        "roles_skipped_or_failed": overall["roles_skipped_or_failed"],
        "summary_json": str(SEGMENTATION_REPORTS_DIR / "training_summary.json"),
        "summary_md": str(SEGMENTATION_REPORTS_DIR / "training_summary.md"),
    }, indent=2))
    if errors and not trained:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

