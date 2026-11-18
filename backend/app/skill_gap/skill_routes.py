"""
API endpoints for CareerLens Skill Gap Analysis (Phase 1) and
Personalized Learning Recommendations (Phase 2).

Rule-based, explainable features:
- Phase 1 uses synthetic illustrative role-skill benchmarks (no trained ML model).
- Phase 2 uses curated genuine learning resources with explainable ranking.
Readiness/recommendation scores are not placement probabilities.
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from .dataset_loader import (
    SkillDatasetError,
    filter_learning_resources,
    get_learning_resources,
    get_learning_resources_summary,
    get_metadata,
    get_role_requirements,
    get_roles,
    get_skill_metadata_index,
)
from .gap_analyzer import analyze_skill_gap
from .recommendation_engine import recommend_for_analysis
from .recommendation_schemas import (
    validate_and_normalize_recommend_request,
    validate_resource_filters,
)
from .roadmap_generator import generate_learning_roadmap
from .skill_schemas import validate_and_normalize_analyze_request

logger = logging.getLogger(__name__)

skill_gap_bp = Blueprint("skill_gap_api", __name__, url_prefix="/api/skills")


@skill_gap_bp.route("/roles", methods=["GET"])
def list_roles():
    try:
        roles = get_roles()
        return (
            jsonify(
                {
                    "roles": roles,
                    "count": len(roles),
                    "disclaimer": (
                        "Role-skill benchmarks are synthetic, illustrative data for demonstration. "
                        "They are not verified industry-wide hiring standards."
                    ),
                }
            ),
            200,
        )
    except SkillDatasetError as exc:
        logger.error("Skill dataset error (roles): %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Skill datasets are unavailable or invalid.",
                }
            ),
            503,
        )


@skill_gap_bp.route("/requirements/<string:role_id>", methods=["GET"])
def role_requirements(role_id: str):
    try:
        role = get_role_requirements(role_id)
        return (
            jsonify(
                {
                    **role,
                    "disclaimer": (
                        "Skill requirements are synthetic, illustrative benchmarks for demonstration only."
                    ),
                }
            ),
            200,
        )
    except (SkillDatasetError, KeyError, ValueError) as exc:
        if (
            isinstance(exc, KeyError)
            or "Unknown target role" in str(exc)
            or "not found" in str(exc).lower()
        ):
            return (
                jsonify(
                    {
                        "error": "Not Found",
                        "message": f"Role '{role_id}' was not found.",
                    }
                ),
                404,
            )
        logger.error("Skill dataset error (requirements): %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Skill datasets are unavailable or invalid.",
                }
            ),
            503,
        )


@skill_gap_bp.route("/metadata", methods=["GET"])
def skill_metadata():
    try:
        meta = get_metadata()
        return jsonify({"skills": meta, "count": len(meta)}), 200
    except SkillDatasetError as exc:
        logger.error("Skill dataset error (metadata): %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Skill metadata dataset is unavailable or invalid.",
                }
            ),
            503,
        )


@skill_gap_bp.route("/analyze", methods=["POST"])
def analyze():
    if not request.is_json:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Content-Type must be application/json",
                }
            ),
            400,
        )

    payload = request.get_json(silent=True)
    if payload is None:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Malformed JSON in request body",
                }
            ),
            400,
        )

    normalized, errors = validate_and_normalize_analyze_request(payload)
    if errors or normalized is None:
        return (
            jsonify(
                {
                    "error": "Validation Error",
                    "message": "Skill gap analysis request failed validation",
                    "details": errors,
                }
            ),
            400,
        )

    try:
        role = normalized["role"]
        result = analyze_skill_gap(
            role=role,
            normalized_current_skills=normalized["normalized_current_skills"],
            metadata_index=get_skill_metadata_index(),
        )
        result["disclaimer"] = (
            "This Skill Gap Analysis uses synthetic, illustrative role-skill benchmarks and a "
            "rule-based, explainable calculation (no trained ML model). The readiness score reflects "
            "weighted skill coverage for the selected role and is not a placement probability."
        )
        return jsonify(result), 200
    except SkillDatasetError as exc:
        logger.error("Skill dataset error during analysis: %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Skill datasets are unavailable or invalid.",
                }
            ),
            503,
        )
    except Exception as exc:
        logger.exception("Unexpected skill analysis error: %s", exc)
        return (
            jsonify(
                {
                    "error": "Analysis Error",
                    "message": "An unexpected error occurred during skill gap analysis.",
                }
            ),
            500,
        )


# -------------------- Phase 2: Learning Recommendations --------------------


@skill_gap_bp.route("/resources", methods=["GET"])
def list_resources():
    try:
        filters, errors = validate_resource_filters(request.args.to_dict(flat=True))
        if errors:
            return (
                jsonify(
                    {
                        "error": "Validation Error",
                        "message": "Invalid resource filter parameters",
                        "details": errors,
                    }
                ),
                400,
            )
        resources = filter_learning_resources(get_learning_resources(), **filters)
        return (
            jsonify(
                {
                    "resources": resources,
                    "count": len(resources),
                    "filters_applied": filters,
                    "disclosure": (
                        "Learning resources are curated genuine resources (not synthetic) with URLs verified at dataset generation time. "
                        "Availability, pricing, and external content may change."
                    ),
                }
            ),
            200,
        )
    except SkillDatasetError as exc:
        logger.error("Learning resources dataset error: %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Learning resources dataset is unavailable or invalid.",
                }
            ),
            503,
        )
    except Exception as exc:
        logger.exception("Unexpected error listing learning resources: %s", exc)
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred while retrieving learning resources.",
                }
            ),
            500,
        )


@skill_gap_bp.route("/resources/summary", methods=["GET"])
def resources_summary():
    try:
        summary = get_learning_resources_summary()
        return jsonify(summary), 200
    except SkillDatasetError as exc:
        logger.error("Learning resources dataset error: %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Learning resources dataset is unavailable or invalid.",
                }
            ),
            503,
        )
    except Exception as exc:
        logger.exception("Unexpected error building resources summary: %s", exc)
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred while summarizing learning resources.",
                }
            ),
            500,
        )


@skill_gap_bp.route("/recommend", methods=["POST"])
def recommend():
    if not request.is_json:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Content-Type must be application/json",
                }
            ),
            400,
        )

    payload = request.get_json(silent=True)
    if payload is None:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Malformed JSON in request body",
                }
            ),
            400,
        )

    normalized, errors = validate_and_normalize_recommend_request(payload)
    if errors or normalized is None:
        return (
            jsonify(
                {
                    "error": "Validation Error",
                    "message": "Recommendation request failed validation",
                    "details": errors,
                }
            ),
            400,
        )

    try:
        role = normalized["role"]
        analysis = analyze_skill_gap(
            role=role,
            normalized_current_skills=normalized["normalized_current_skills"],
            metadata_index=get_skill_metadata_index(),
        )
        analysis["disclaimer"] = (
            "This Skill Gap Analysis uses synthetic, illustrative role-skill benchmarks and a "
            "rule-based, explainable calculation (no trained ML model). The readiness score reflects "
            "weighted skill coverage for the selected role and is not a placement probability."
        )

        preferences = normalized.get("preferences") or {}
        resources = get_learning_resources()
        if preferences.get("free_only"):
            resources = [r for r in resources if r.get("is_free")]

        rec = recommend_for_analysis(analysis, resources, preferences)
        roadmap = generate_learning_roadmap(
            analysis,
            rec.get("recommended_resources_by_skill", []),
            rec.get("maintenance_recommendations_by_skill", []),
        )

        response = {
            "target_role": analysis.get("target_role"),
            "role_name": analysis.get("role_name"),
            "overall_readiness_score": analysis.get("overall_readiness_score"),
            "readiness_score_interpretation": analysis.get("readiness_score_interpretation"),
            "priority_skills": analysis.get("top_priority_skills", []),
            "recommended_resources_by_skill": rec.get("recommended_resources_by_skill", []),
            "recommendation_ranking": rec.get("ranking", {}),
            "learning_roadmap": roadmap,
            "recommendation_summary": rec.get("recommendation_summary", {}),
            "preferences_applied": preferences,
            "analysis_summary": analysis.get("summary", {}),
            "dataset_disclosure": {
                "role_requirements_and_profiles": (
                    "Synthetic, illustrative role-skill benchmarks and student profile structures used for demonstration/testing. "
                    "Not verified industry-wide hiring standards or real student records."
                ),
                "learning_resources": (
                    "Curated genuine learning resources with URLs verified at dataset generation time. "
                    "External availability, pricing, and content may change."
                ),
                "recommendation_scores": (
                    "Rule-based, explainable ranking scores (not scientifically validated probabilities or guarantees). "
                    "They do not predict placement outcomes."
                ),
            },
        }
        return jsonify(response), 200
    except SkillDatasetError as exc:
        logger.error("Skill/recommendation dataset error: %s", exc)
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Skill or learning resources datasets are unavailable or invalid.",
                }
            ),
            503,
        )
    except Exception as exc:
        logger.exception("Unexpected recommendation error: %s", exc)
        return (
            jsonify(
                {
                    "error": "Recommendation Error",
                    "message": "An unexpected error occurred while generating recommendations.",
                }
            ),
            500,
        )