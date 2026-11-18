"""
Rule-based, explainable Skill Gap Analysis engine.

Calculates per-skill gaps, weighted priorities, and overall role readiness
against synthetic illustrative role-skill benchmarks.

Readiness is weighted skill coverage against the selected role's requirements.
It is NOT a placement probability and this module does not use an ML model.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _clamp_proficiency(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def classify_gap(gap: float) -> str:
    """Classify gap (0-100 scale) into priority bands."""
    if gap <= 10:
        return "Strong"
    if gap <= 25:
        return "Minor Gap"
    if gap <= 50:
        return "Moderate Gap"
    return "Critical Gap"


def _improvement_suggestion(skill_name: str, classification: str, is_core: bool) -> str:
    core_note = " This is a core skill for the role." if is_core else ""
    if classification == "Critical Gap":
        return (
            f"Prioritize {skill_name} immediately with focused fundamentals-to-practice learning and regular hands-on exercises.{core_note}"
        )
    if classification == "Moderate Gap":
        return (
            f"Plan structured practice for {skill_name} to close the gap through guided projects and targeted revision.{core_note}"
        )
    if classification == "Minor Gap":
        return f"Strengthen {skill_name} with short practice cycles and apply it in small tasks/projects.{core_note}"
    return f"Maintain {skill_name} through periodic practice and real-world application.{core_note}"


def _roadmap_bucket(classification: str) -> str:
    if classification == "Critical Gap":
        return "immediate_focus"
    if classification == "Moderate Gap":
        return "next_focus"
    # Strong and Minor Gap: maintain/build consistency
    return "maintain_strengths"


def _build_roadmap(skill_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets = {
        "immediate_focus": {
            "title": "Immediate Focus",
            "description": "Critical gaps with meaningful role impact. Address these first to improve role readiness.",
            "skills": [],
        },
        "next_focus": {
            "title": "Next Focus",
            "description": "Moderate gaps to close after immediate priorities for more balanced readiness.",
            "skills": [],
        },
        "maintain_strengths": {
            "title": "Maintain Strengths",
            "description": "Skills that are strong or have minor gaps. Maintain consistency and keep applying them.",
            "skills": [],
        },
    }

    # skill_results expected sorted by priority desc
    for s in skill_results:
        bucket = buckets[_roadmap_bucket(s["priority_classification"])]
        bucket["skills"].append(
            {
                "skill_name": s["skill_name"],
                "gap": s["gap"],
                "importance_weight": s["importance_weight"],
                "priority_classification": s["priority_classification"],
                "reason": (
                    f"{s['skill_name']} has a {s['priority_classification'].lower()} "
                    f"(gap {s['gap']:.1f}, required {s['required_proficiency']:.1f}, "
                    f"importance {s['importance_weight']:.4f})."
                ),
            }
        )

    roadmap = []
    for key in ("immediate_focus", "next_focus", "maintain_strengths"):
        item = buckets[key]
        roadmap.append(
            {
                "phase": key,
                "title": item["title"],
                "description": item["description"],
                "skills": item["skills"],
            }
        )
    return roadmap


def analyze_skill_gap(
    role: Dict[str, Any],
    normalized_current_skills: Dict[str, float],
    metadata_index: Dict[str, Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    Analyze skill gaps for a role.

    Args:
        role: dict with role_id, role_name, skills[] (role requirements)
        normalized_current_skills: mapping of skill_name(lowercase) -> current proficiency (0-100)
        metadata_index: optional metadata indexed by skill_id/skill_name(lowercase)

    Returns:
        API-ready analysis result (JSON serializable)
    """
    requirements: List[Dict[str, Any]] = role.get("skills", [])
    if not requirements:
        raise ValueError("Role requirements are empty")

    metadata_index = metadata_index or {}

    results: List[Dict[str, Any]] = []
    readiness_weighted_sum = 0.0

    for req in requirements:
        skill_name = str(req["skill_name"])
        skill_id = str(req["skill_id"])
        required = _clamp_proficiency(float(req["required_proficiency"]))
        importance = float(req["importance_weight"])
        is_core = bool(req.get("is_core_skill", False))

        current_raw = normalized_current_skills.get(skill_name.strip().lower(), 0.0)
        current = _clamp_proficiency(current_raw)

        # Gap: never negative (do not penalize if current > required)
        gap = max(0.0, required - current)
        gap_percentage = (gap / required * 100.0) if required > 0 else 0.0

        # Weighted skill priority (consistent, documented): higher gap and higher importance => higher priority
        priority_score = (gap / 100.0) * importance

        classification = classify_gap(gap)

        # Overall role readiness (0-100): weighted sum of current proficiencies using normalized role weights.
        # Inputs are clamped to 0-100 and exceeding required proficiency does not penalize.
        readiness_weighted_sum += current * importance

        meta = metadata_index.get(skill_id) or metadata_index.get(skill_name.strip().lower()) or {}
        description = meta.get("description") or (
            f"{skill_name} is relevant for the {role.get('role_name', 'selected')} role."
        )

        results.append(
            {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "skill_category": req.get("skill_category", "General"),
                "is_core_skill": is_core,
                "current_proficiency": round(current, 2),
                "required_proficiency": round(required, 2),
                "gap": round(gap, 2),
                "gap_percentage": round(gap_percentage, 2),
                "importance_weight": round(importance, 6),
                "priority_score": round(priority_score, 6),
                "priority_classification": classification,
                "description": description,
                "why_it_matters": (
                    f"Weighted importance {importance:.4f} for {role.get('role_name', 'this role')}"
                    + (" (core skill)." if is_core else ".")
                ),
                "improvement_suggestion": _improvement_suggestion(skill_name, classification, is_core),
            }
        )

    # Sort by priority desc; tie-break by importance, gap, then name
    results.sort(
        key=lambda x: (
            -x["priority_score"],
            -x["importance_weight"],
            -x["gap"],
            x["skill_name"].lower(),
        )
    )

    readiness_score = round(max(0.0, min(100.0, readiness_weighted_sum)), 2)

    strongest_skills = sorted(
        [r for r in results],
        key=lambda x: (x["gap"], -x["current_proficiency"], -x["importance_weight"], x["skill_name"].lower()),
    )[:5]
    skills_requiring_improvement = [r for r in results if r["gap"] > 0]
    top_priority_skills = results[:5]

    return {
        "target_role": role.get("role_id"),
        "role_name": role.get("role_name"),
        "overall_readiness_score": readiness_score,
        "readiness_score_interpretation": (
            "Weighted skill coverage against the selected role's synthetic benchmark requirements (0-100). "
            "This is not a placement probability."
        ),
        "skill_comparison": results,
        "strongest_skills": strongest_skills,
        "skills_requiring_improvement": skills_requiring_improvement,
        "top_priority_skills": top_priority_skills,
        "improvement_roadmap": _build_roadmap(results),
        "summary": {
            "total_skills": len(results),
            "critical_gaps": sum(1 for r in results if r["priority_classification"] == "Critical Gap"),
            "moderate_gaps": sum(1 for r in results if r["priority_classification"] == "Moderate Gap"),
            "minor_gaps": sum(1 for r in results if r["priority_classification"] == "Minor Gap"),
            "strong_skills": sum(1 for r in results if r["priority_classification"] == "Strong"),
        },
    }
