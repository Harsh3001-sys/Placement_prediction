"""
Personalized learning roadmap generation (Phase 2).

Builds a 4-stage roadmap using Phase 1 priority/gap information and
Phase 2 recommended resources. Estimated hours are based on actual
resource metadata and are not guaranteed completion times.
"""

from __future__ import annotations

from typing import Any, Dict, List


STAGE_ORDER = [
    ("immediate_focus", "Immediate Focus", "Critical gap skills. Start with foundational resources that address the most important gaps first."),
    ("skill_development", "Skill Development", "Moderate gap skills. Build depth with intermediate tutorials and practical exercises."),
    ("strengthening_skills", "Strengthening Skills", "Minor gaps and near-benchmark skills. Use practice and revision resources to close remaining gaps."),
    ("maintain_strengths", "Maintain Strengths", "Skills already meeting the role benchmark. Use occasional advanced practice or maintenance material to stay sharp."),
]


def _stage_for_classification(classification: str) -> str:
    if classification == "Critical Gap":
        return "immediate_focus"
    if classification == "Moderate Gap":
        return "skill_development"
    if classification == "Minor Gap":
        return "strengthening_skills"
    return "maintain_strengths"


def _resource_brief(resource: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "resource_id": resource.get("resource_id"),
        "resource_title": resource.get("resource_title"),
        "provider": resource.get("provider"),
        "resource_type": resource.get("resource_type"),
        "difficulty_level": resource.get("difficulty_level"),
        "estimated_hours": float(resource.get("estimated_hours", 0.0) or 0.0),
        "is_free": bool(resource.get("is_free")),
        "resource_url": resource.get("resource_url"),
        "recommendation_score": resource.get("recommendation_score"),
        "why_recommended": resource.get("why_recommended", [])[:2],
    }


def generate_learning_roadmap(
    analysis: Dict[str, Any],
    recommended_resources_by_skill: List[Dict[str, Any]],
    maintenance_recommendations_by_skill: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    rec_index = {g["skill_id"]: g for g in (recommended_resources_by_skill or [])}
    for g in (maintenance_recommendations_by_skill or []):
        # Do not override priority-skill recommendations; maintenance fills Strong skills
        rec_index.setdefault(g["skill_id"], g)
    stages: Dict[str, List[Dict[str, Any]]] = {k: [] for k, _, _ in STAGE_ORDER}

    for skill in analysis.get("skill_comparison", []) or []:
        sid = skill.get("skill_id")
        classification = str(skill.get("priority_classification", "Strong"))
        stage_key = _stage_for_classification(classification)
        rec_group = rec_index.get(sid)
        recs = list((rec_group or {}).get("resources") or [])
        recs.sort(key=lambda r: (int(r.get("recommended_rank", 999)), -float(r.get("recommendation_score", 0.0) or 0.0)))
        rec_briefs = [_resource_brief(r) for r in recs]
        stage_hours = round(sum(float(r.get("estimated_hours", 0.0) or 0.0) for r in recs), 2)

        if classification == "Critical Gap":
            reason = f"Critical gap (gap {float(skill.get('gap', 0.0)):.1f}) in a role-relevant skill; prioritize foundational progress first."
        elif classification == "Moderate Gap":
            reason = f"Moderate gap (gap {float(skill.get('gap', 0.0)):.1f}); build capability with targeted learning and practice."
        elif classification == "Minor Gap":
            reason = f"Minor gap (gap {float(skill.get('gap', 0.0)):.1f}); focused practice can help you reach the benchmark."
        else:
            reason = "Current proficiency meets or is close to the benchmark; maintain strength with occasional advanced practice."

        item = {
            "skill_id": sid,
            "skill_name": skill.get("skill_name"),
            "current_proficiency": float(skill.get("current_proficiency", 0.0) or 0.0),
            "required_proficiency": float(skill.get("required_proficiency", 0.0) or 0.0),
            "gap": float(skill.get("gap", 0.0) or 0.0),
            "priority": classification,
            "importance_weight": float(skill.get("importance_weight", 0.0) or 0.0),
            "priority_score": float(skill.get("priority_score", 0.0) or 0.0),
            "recommended_resources": rec_briefs,
            "recommended_sequence": [
                {
                    "step": i + 1,
                    "resource_id": b.get("resource_id"),
                    "resource_title": b.get("resource_title"),
                    "difficulty_level": b.get("difficulty_level"),
                    "resource_type": b.get("resource_type"),
                }
                for i, b in enumerate(rec_briefs)
            ],
            "reason_for_prioritization": reason,
            "estimated_resource_hours": stage_hours,
        }
        stages[stage_key].append(item)

    # Sort items within stages by Phase 1 priority score / gap
    for key in stages:
        reverse = key != "maintain_strengths"
        stages[key].sort(
            key=lambda x: (
                float(x.get("priority_score", 0.0) or 0.0),
                float(x.get("gap", 0.0) or 0.0),
                -float(x.get("current_proficiency", 0.0) or 0.0),
            ),
            reverse=reverse,
        )

    roadmap: List[Dict[str, Any]] = []
    for key, title, desc in STAGE_ORDER:
        items = stages[key]
        roadmap.append({
            "stage": key,
            "title": title,
            "description": desc,
            "skill_count": len(items),
            "estimated_stage_hours": round(sum(float(i.get("estimated_resource_hours", 0.0) or 0.0) for i in items), 2),
            "skills": items,
        })
    return roadmap