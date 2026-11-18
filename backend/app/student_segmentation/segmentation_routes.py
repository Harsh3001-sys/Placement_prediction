"""
Flask API endpoints for Student Segmentation (Phase 3).

Blueprint: /api/segmentation
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

from app.skill_gap.dataset_loader import (
    SkillDatasetError,
    get_learning_resources,
    get_role_requirements,
    get_roles,
    get_skill_metadata_index,
)
from app.skill_gap.gap_analyzer import analyze_skill_gap
from app.skill_gap.recommendation_engine import recommend_for_analysis

from .cluster_analyzer import analyze_role_clusters
from .model_loader import (
    SEGMENTATION_REPORTS_DIR,
    list_available_segmentation_roles,
    load_json_if_exists,
    load_role_artifacts,
    predict_cluster,
    role_artifact_dir,
)
from .preprocessing import build_feature_vector, load_role_dataset
from .segmentation_schemas import validate_predict_request

logger = logging.getLogger(__name__)

segmentation_bp = Blueprint("segmentation_api", __name__, url_prefix="/api/segmentation")


def _get_cluster_analysis(role_id: str, artifacts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load cluster analysis for a role. Prefer saved analysis; fallback to recompute from dataset+model."""
    # 1) artifact dir
    art_dir = role_artifact_dir(role_id)
    analysis = load_json_if_exists(art_dir / "cluster_analysis.json")
    if analysis:
        return analysis
    # 2) reports dir
    analysis = load_json_if_exists(SEGMENTATION_REPORTS_DIR / role_id / f"{role_id}_cluster_analysis.json")
    if analysis:
        return analysis
    # 3) recompute if artifacts available
    if artifacts is None:
        artifacts = load_role_artifacts(role_id)
    role_data = load_role_dataset(role_id)
    role_cfg = get_role_requirements(role_id)
    X_scaled = artifacts["scaler"].transform(role_data.X)
    labels = artifacts["model"].predict(X_scaled)
    return analyze_role_clusters(
        role_id=role_id,
        role_name=role_cfg.get("role_name", role_id),
        feature_names=role_data.feature_names,
        X_original=role_data.X,
        labels=labels,
        requirements=role_cfg.get("skills", []),
    )


def _cluster_by_id(cluster_analysis: Dict[str, Any], cluster_id: int) -> Optional[Dict[str, Any]]:
    for c in cluster_analysis.get("clusters", []):
        if int(c.get("cluster_id")) == int(cluster_id):
            return c
    return None


def _top_student_skills(
    skills_map: Dict[str, float],
    cluster_means: Dict[str, float],
    n: int = 5,
) -> Dict[str, List[Dict[str, Any]]]:
    rows = []
    for skill, val in skills_map.items():
        c_avg = float(cluster_means.get(skill, 0.0))
        s_val = float(val)
        rows.append(
            {
                "skill_name": skill,
                "student_proficiency": round(s_val, 2),
                "cluster_average": round(c_avg, 2),
                "difference_from_cluster": round(s_val - c_avg, 2),
            }
        )
    strongest = sorted(rows, key=lambda x: (x["student_proficiency"], x["difference_from_cluster"], x["skill_name"].lower()), reverse=True)[:n]
    weakest = sorted(rows, key=lambda x: (x["student_proficiency"], -x["difference_from_cluster"], x["skill_name"].lower()))[:n]
    return {"strongest_skills": strongest, "weakest_skills": weakest}


def _comparison_with_cluster(
    skills_map: Dict[str, float],
    cluster_means: Dict[str, float],
    overall_means: Dict[str, float],
    requirements: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    req_map = {str(r.get("skill_name")): r for r in requirements}
    out = []
    for skill, s_val in skills_map.items():
        req = req_map.get(skill, {})
        c_avg = float(cluster_means.get(skill, 0.0))
        o_avg = float(overall_means.get(skill, 0.0))
        sv = float(s_val)
        out.append(
            {
                "skill_id": req.get("skill_id"),
                "skill_name": skill,
                "skill_category": req.get("skill_category", "General"),
                "is_core_skill": bool(req.get("is_core_skill", False)),
                "student_proficiency": round(sv, 2),
                "cluster_average": round(c_avg, 2),
                "overall_role_average": round(o_avg, 2),
                "required_proficiency": round(float(req.get("required_proficiency", 0.0) or 0.0), 2),
                "difference_from_cluster": round(sv - c_avg, 2),
                "difference_from_overall": round(sv - o_avg, 2),
            }
        )
    out.sort(key=lambda x: (x["difference_from_cluster"], x["student_proficiency"]))
    return out


def _resources_for_cluster_weaknesses(
    cluster: Dict[str, Any],
    role_id: str,
    limit: int = 6,
) -> Dict[str, Any]:
    """Return curated resources aligned to cluster-level weak skills (reuses Phase 2 dataset)."""
    try:
        resources = get_learning_resources()
    except Exception:
        return {"cluster_weak_skills": [], "suggested_resources": []}

    weak = cluster.get("weakest_skills", []) or []
    weak_names = [w.get("skill_name") for w in weak if w.get("skill_name")]
    # pick bottom skills by cluster average as well
    avg_map = cluster.get("average_proficiency_per_skill", {}) or {}
    sorted_low = sorted(avg_map.items(), key=lambda x: (float(x[1]), str(x[0]).lower()))
    for name, _ in sorted_low:
        if name not in weak_names:
            weak_names.append(name)
        if len(weak_names) >= 3:
            break

    by_skill: Dict[str, List[Dict[str, Any]]] = {}
    for r in resources:
        by_skill.setdefault(str(r.get("skill_name")), []).append(r)

    suggested = []
    used_ids = set()
    for skill_name in weak_names[:3]:
        candidates = list(by_skill.get(skill_name, []))
        # prioritize beginner/intermediate, higher quality, free
        candidates.sort(key=lambda x: (0 if x.get("is_free") else 1, {"Beginner": 0, "Intermediate": 1, "Advanced": 2}.get(x.get("difficulty_level"), 9), -int(x.get("quality_score", 0) or 0)))
        for r in candidates[:2]:
            rid = r.get("resource_id")
            if rid in used_ids:
                continue
            used_ids.add(rid)
            suggested.append({
                "skill_name": skill_name,
                "resource_id": r.get("resource_id"),
                "resource_title": r.get("resource_title"),
                "provider": r.get("provider"),
                "resource_type": r.get("resource_type"),
                "difficulty_level": r.get("difficulty_level"),
                "resource_url": r.get("resource_url"),
                "is_free": bool(r.get("is_free")),
                "estimated_hours": float(r.get("estimated_hours", 0.0) or 0.0),
                "quality_score": int(r.get("quality_score", 0) or 0),
            })
            if len(suggested) >= limit:
                break
        if len(suggested) >= limit:
            break

    return {"cluster_weak_skills": weak_names[:3], "suggested_resources": suggested}


@segmentation_bp.route("/roles", methods=["GET"])
def get_segmentation_roles():
    try:
        available = set(list_available_segmentation_roles())
        phase1_roles = get_roles()
        roles = []
        for r in phase1_roles:
            rid = r["role_id"]
            if rid in available:
                # enrich with model metadata if possible
                meta = {}
                try:
                    art = load_role_artifacts(rid)
                    m = art.get("metadata", {})
                    meta = {
                        "selected_k": m.get("selected_k"),
                        "n_samples_trained": m.get("n_samples"),
                        "n_features": m.get("n_features"),
                        "algorithm": m.get("algorithm", "KMeans"),
                    }
                except Exception:
                    meta = {}
                roles.append({
                    "role_id": rid,
                    "role_name": r.get("role_name"),
                    "available": True,
                    **meta,
                })
        return jsonify({
            "roles": roles,
            "count": len(roles),
            "disclosure": "Segmentation models are trained on synthetic student skill profiles (demonstration only). Cluster assignments are not placement predictions.",
        }), 200
    except SkillDatasetError as e:
        return jsonify({"error": "Dataset Error", "message": str(e)}), 500
    except Exception as e:
        logger.exception("Failed to list segmentation roles: %s", e)
        return jsonify({"error": "Internal Server Error", "message": "Failed to retrieve segmentation roles."}), 500


@segmentation_bp.route("/overview/<role_id>", methods=["GET"])
def get_overview(role_id: str):
    try:
        rid = str(role_id).strip()
        if not rid:
            return jsonify({"error": "Validation Error", "message": "role_id is required."}), 400
        # ensure role exists in Phase 1 mappings
        try:
            role_cfg = get_role_requirements(rid)
        except Exception:
            return jsonify({"error": "Not Found", "message": f"Role '{rid}' is not a supported target role."}), 404
        if rid not in set(list_available_segmentation_roles()):
            return jsonify({
                "error": "Not Found",
                "message": f"No trained segmentation model available for role '{rid}'.",
                "hint": "Run backend/scripts/train_student_clusters.py to generate segmentation artifacts.",
            }), 404

        artifacts = load_role_artifacts(rid)
        metadata = artifacts.get("metadata", {})
        analysis = _get_cluster_analysis(rid, artifacts=artifacts)
        final_metrics = metadata.get("final_metrics", {}) or {}

        return jsonify({
            "role_id": rid,
            "role_name": role_cfg.get("role_name", rid),
            "n_clusters": int(metadata.get("selected_k") or len(analysis.get("clusters", [])) or 0),
            "students_analyzed": int(metadata.get("n_samples") or analysis.get("n_students") or 0),
            "cluster_distribution": analysis.get("cluster_distribution", []),
            "selected_k": int(metadata.get("selected_k") or 0),
            "clustering_evaluation_metrics": {
                "silhouette_score": final_metrics.get("silhouette_score"),
                "davies_bouldin_score": final_metrics.get("davies_bouldin_score"),
                "calinski_harabasz_score": final_metrics.get("calinski_harabasz_score"),
                "wcss": final_metrics.get("wcss"),
            },
            "candidate_k_metrics": metadata.get("candidate_metrics", []),
            "k_selection": metadata.get("selection", {}),
            "overall_clustering_summary": {
                "overall_role_average": analysis.get("overall_role_average"),
                "n_features": int(metadata.get("n_features") or len(metadata.get("feature_names", []) or [])),
                "feature_names": metadata.get("feature_names", []),
                "cluster_count": len(analysis.get("clusters", [])),
            },
            "disclosure": metadata.get("disclosure"),
        }), 200
    except FileNotFoundError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404
    except SkillDatasetError as e:
        return jsonify({"error": "Dataset Error", "message": str(e)}), 500
    except Exception as e:
        logger.exception("Failed to get segmentation overview for role %s: %s", role_id, e)
        return jsonify({"error": "Internal Server Error", "message": "Failed to retrieve segmentation overview."}), 500


@segmentation_bp.route("/clusters/<role_id>", methods=["GET"])
def get_clusters(role_id: str):
    try:
        rid = str(role_id).strip()
        try:
            role_cfg = get_role_requirements(rid)
        except Exception:
            return jsonify({"error": "Not Found", "message": f"Role '{rid}' is not a supported target role."}), 404
        if rid not in set(list_available_segmentation_roles()):
            return jsonify({
                "error": "Not Found",
                "message": f"No trained segmentation model available for role '{rid}'.",
            }), 404
        artifacts = load_role_artifacts(rid)
        analysis = _get_cluster_analysis(rid, artifacts=artifacts)
        return jsonify({
            "role_id": rid,
            "role_name": role_cfg.get("role_name", rid),
            "selected_k": int((artifacts.get("metadata") or {}).get("selected_k") or len(analysis.get("clusters", [])) or 0),
            "students_analyzed": int(analysis.get("n_students") or 0),
            "clusters": analysis.get("clusters", []),
            "disclosure": (artifacts.get("metadata") or {}).get("disclosure"),
        }), 200
    except FileNotFoundError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404
    except SkillDatasetError as e:
        return jsonify({"error": "Dataset Error", "message": str(e)}), 500
    except Exception as e:
        logger.exception("Failed to get clusters for role %s: %s", role_id, e)
        return jsonify({"error": "Internal Server Error", "message": "Failed to retrieve cluster details."}), 500


@segmentation_bp.route("/model-info/<role_id>", methods=["GET"])
def get_model_info(role_id: str):
    try:
        rid = str(role_id).strip()
        try:
            role_cfg = get_role_requirements(rid)
        except Exception:
            return jsonify({"error": "Not Found", "message": f"Role '{rid}' is not a supported target role."}), 404
        if rid not in set(list_available_segmentation_roles()):
            return jsonify({"error": "Not Found", "message": f"No trained segmentation model available for role '{rid}'."}), 404
        artifacts = load_role_artifacts(rid)
        metadata = artifacts.get("metadata", {})
        return jsonify({
            "role_id": rid,
            "role_name": role_cfg.get("role_name", rid),
            "model_type": "KMeans",
            "selected_k": metadata.get("selected_k"),
            "training_sample_count": metadata.get("n_samples"),
            "feature_count": metadata.get("n_features"),
            "feature_names": metadata.get("feature_names", []),
            "training_metadata": {
                "algorithm": metadata.get("algorithm"),
                "random_state": metadata.get("random_state"),
                "n_init": metadata.get("n_init"),
                "max_iter": metadata.get("max_iter"),
                "k_range_evaluated": metadata.get("k_range_evaluated"),
                "selection": metadata.get("selection"),
                "preprocessing": metadata.get("preprocessing"),
            },
            "evaluation_metrics": metadata.get("final_metrics", {}),
            "candidate_k_metrics": metadata.get("candidate_metrics", []),
            "disclosure": metadata.get("disclosure"),
        }), 200
    except FileNotFoundError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404
    except Exception as e:
        logger.exception("Failed to get segmentation model info for role %s: %s", role_id, e)
        return jsonify({"error": "Internal Server Error", "message": "Failed to retrieve segmentation model information."}), 500


@segmentation_bp.route("/predict", methods=["POST"])
def predict_segment():
    try:
        payload = request.get_json(silent=True)
        normalized, errors = validate_predict_request(payload)
        if errors:
            return jsonify({"error": "Validation Error", "message": "Invalid segmentation request.", "details": errors}), 400

        role_id = normalized["target_role"]
        role_name = normalized["role_name"]
        requirements = normalized["requirements"]
        skills_norm = normalized["skills_normalized"]

        if role_id not in set(list_available_segmentation_roles()):
            return jsonify({
                "error": "Not Found",
                "message": f"No trained segmentation model available for role '{role_id}'.",
                "hint": "Train segmentation models or choose a role with available artifacts.",
            }), 404

        artifacts = load_role_artifacts(role_id)
        feature_names = artifacts.get("feature_config", {}).get("feature_names") or [r["skill_name"] for r in requirements]
        if not feature_names:
            return jsonify({"error": "Internal Server Error", "message": "Model feature configuration is unavailable."}), 500

        # Build feature vector in consistent order
        X_vec = build_feature_vector(skills_norm, feature_names)
        pred = predict_cluster(artifacts["model"], artifacts["scaler"], X_vec)
        cluster_id = int(pred["cluster_id"])

        analysis = _get_cluster_analysis(role_id, artifacts=artifacts)
        cluster = _cluster_by_id(analysis, cluster_id)
        if cluster is None:
            return jsonify({"error": "Internal Server Error", "message": "Predicted cluster details could not be resolved."}), 500

        # student skills map in display order
        student_skill_map = {name: float(skills_norm.get(str(name).strip().lower(), 0.0)) for name in feature_names}
        cluster_means = {k: float(v) for k, v in (cluster.get("average_proficiency_per_skill") or {}).items()}
        overall_means = {k: float(v) for k, v in (analysis.get("overall_average_per_skill") or {}).items()}
        extremes = _top_student_skills(student_skill_map, cluster_means, n=5)
        comparison = _comparison_with_cluster(student_skill_map, cluster_means, overall_means, requirements)

        # Personal skill gaps (Phase 1 reuse)
        personal_analysis = analyze_skill_gap(
            role={"role_id": role_id, "role_name": role_name, "skills": requirements},
            normalized_current_skills=skills_norm,
            metadata_index=get_skill_metadata_index(),
        )
        # Recommendations based on individual gaps and cluster patterns (Phase 2 reuse)
        personal_recommendations = None
        cluster_recommendations = None
        cluster_gap_analysis = None
        try:
            all_resources = get_learning_resources()
            personal_recommendations = recommend_for_analysis(personal_analysis, all_resources, preferences={"difficulty_preference": "adaptive"})
            # Cluster-level analysis/recommendations by treating cluster averages as representative profile
            cluster_norm = {str(name).strip().lower(): float(cluster_means.get(name, 0.0)) for name in feature_names}
            cluster_gap_analysis = analyze_skill_gap(
                role={"role_id": role_id, "role_name": role_name, "skills": requirements},
                normalized_current_skills=cluster_norm,
                metadata_index=get_skill_metadata_index(),
            )
            cluster_recommendations = recommend_for_analysis(cluster_gap_analysis, all_resources, preferences={"difficulty_preference": "adaptive"})
        except Exception as e:
            logger.warning("Recommendation integration unavailable for segmentation predict: %s", e)

        cluster_resource_hints = _resources_for_cluster_weaknesses(cluster, role_id)

        # Cluster characteristics summary
        cluster_characteristics = {
            "student_count": cluster.get("student_count"),
            "student_percentage": cluster.get("student_percentage"),
            "average_skill_proficiency": cluster.get("average_skill_proficiency"),
            "difference_from_overall_role_average": cluster.get("difference_from_overall_role_average"),
            "strongest_skills": cluster.get("strongest_skills", []),
            "weakest_skills": cluster.get("weakest_skills", []),
            "category_profile": cluster.get("category_profile", []),
        }

        # Recommended areas of improvement (personal + cluster context)
        personal_priority = (personal_analysis.get("top_priority_skills") or [])[:5]
        recommended_improvements = [
            {
                "skill_name": s.get("skill_name"),
                "gap": s.get("gap"),
                "priority_classification": s.get("priority_classification"),
                "reason": f"Personal gap vs role benchmark (gap {s.get('gap')}, required {s.get('required_proficiency')}).",
            }
            for s in personal_priority if float(s.get("gap", 0) or 0) > 0
        ]

        # Why student belongs to this cluster (explainable comparison)
        diffs = sorted(comparison, key=lambda x: abs(float(x.get("difference_from_cluster", 0))), reverse=True)
        closest = sorted(comparison, key=lambda x: abs(float(x.get("difference_from_cluster", 0))))[:3]
        farthest = diffs[:3]
        why_reasons = []
        why_reasons.append(
            f"Predicted using the trained K-Means model for {role_name} on role-relevant standardized features; your profile is closest to Cluster {cluster_id} ({cluster.get('cluster_name')}) in that feature space."
        )
        if closest:
            why_reasons.append(
                "Skills closest to this cluster's average: "
                + ", ".join([f"{x['skill_name']} (you {x['student_proficiency']}, cluster {x['cluster_average']})" for x in closest])
                + "."
            )
        if farthest:
            why_reasons.append(
                "Largest differences from this cluster's average: "
                + ", ".join([f"{x['skill_name']} ({x['difference_from_cluster']:+.1f})" for x in farthest])
                + "."
            )

        personal_recs_payload = None
        if personal_recommendations:
            try:
                from app.skill_gap.roadmap_generator import generate_learning_roadmap
                personal_roadmap = generate_learning_roadmap(
                    personal_analysis,
                    personal_recommendations.get("recommended_resources_by_skill", []),
                    personal_recommendations.get("maintenance_recommendations_by_skill", []),
                )
            except Exception:
                personal_roadmap = []
            personal_recs_payload = {
                "recommended_resources_by_skill": personal_recommendations.get("recommended_resources_by_skill", []),
                "learning_roadmap": personal_roadmap,
                "recommendation_summary": personal_recommendations.get("recommendation_summary", {}),
                "ranking": personal_recommendations.get("ranking", {}),
            }

        if cluster_recommendations and cluster_gap_analysis is not None:
            cluster_recs_payload = {
                "representative_cluster_profile_gaps": {
                    "overall_readiness_score": cluster_gap_analysis.get("overall_readiness_score"),
                    "top_priority_skills": (cluster_gap_analysis.get("top_priority_skills", []) or [])[:5],
                },
                "recommended_resources_by_skill": cluster_recommendations.get("recommended_resources_by_skill", []),
                "recommendation_summary": cluster_recommendations.get("recommendation_summary", {}),
                "resource_suggestions_for_cluster_weaknesses": cluster_resource_hints,
                "ranking": cluster_recommendations.get("ranking", {}),
            }
        else:
            cluster_recs_payload = {"resource_suggestions_for_cluster_weaknesses": cluster_resource_hints}

        return jsonify({
            "target_role": role_id,
            "role_name": role_name,
            "predicted_cluster_id": cluster_id,
            "cluster_name": cluster.get("cluster_name"),
            "cluster_description": cluster.get("cluster_description"),
            "cluster_characteristics": cluster_characteristics,
            "student_strongest_skills": extremes["strongest_skills"],
            "student_weakest_skills": extremes["weakest_skills"],
            "comparison_with_cluster": comparison,
            "recommended_areas_of_improvement": recommended_improvements,
            "why_this_cluster": why_reasons,
            "personal_skill_gaps": {
                "overall_readiness_score": personal_analysis.get("overall_readiness_score"),
                "summary": personal_analysis.get("summary"),
                "top_priority_skills": personal_priority,
                "skills_requiring_improvement": personal_analysis.get("skills_requiring_improvement", [])[:10],
            },
            "cluster_level_weaknesses": {
                "weakest_skills": cluster.get("weakest_skills", []),
                "category_profile": cluster.get("category_profile", []),
                "difference_from_overall_role_average": cluster.get("difference_from_overall_role_average"),
            },
            "recommendations_based_on_individual_gaps": personal_recs_payload,
            "recommendations_based_on_cluster_patterns": cluster_recs_payload,
            "integration_notes": {
                "phase1": "Personal and cluster-level gap analysis reuse Phase 1 role mappings/requirements and the rule-based gap analyzer.",
                "phase2": "Personal and cluster-pattern recommendations reuse the existing Phase 2 recommendation engine and curated learning resources dataset (no duplicate resource dataset or duplicate recommendation logic).",
                "distinction": "Personal insights are computed from the submitted student skill profile; cluster insights are computed from the learned cluster centroid profile for the predicted segment.",
            },
            "disclosure": (artifacts.get("metadata") or {}).get("disclosure"),
        }), 200

    except FileNotFoundError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404
    except SkillDatasetError as e:
        return jsonify({"error": "Dataset Error", "message": str(e)}), 500
    except Exception as e:
        logger.exception("Segmentation prediction failed: %s", e)
        return jsonify({"error": "Internal Server Error", "message": "Failed to predict student segment."}), 500
