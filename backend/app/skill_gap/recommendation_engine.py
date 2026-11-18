"""
Explainable, content-based learning recommendation engine (Phase 2).

Uses Phase 1 gap analysis outputs and curated learning resources to rank and
recommend resources per priority skill. Scores are rule-based ranking signals,
not scientifically validated predictions/probabilities.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

# Ranking weights (initial, configurable, not scientifically validated)
WEIGHTS = {
    "skill_priority": 0.40,
    "difficulty_match": 0.25,
    "resource_quality": 0.20,
    "relevance": 0.10,
    "free_resource": 0.05,
}

DIFFICULTY_LEVEL_ORDER = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}


def proficiency_to_level(proficiency: float) -> str:
    p = float(proficiency)
    if p <= 30:
        return "Beginner"
    if p <= 65:
        return "Intermediate"
    return "Advanced"


def difficulty_match_score(current_proficiency: float, resource_difficulty: str) -> float:
    """
    Returns 0-100 suitability score.
    Mapping: 0-30 Beginner, 31-65 Intermediate, 66-100 Advanced.
    Allows some flexibility (one level above) but avoids advanced for beginners without foundation.
    """
    student_level = proficiency_to_level(current_proficiency)
    res = resource_difficulty
    s = DIFFICULTY_LEVEL_ORDER.get(student_level, 1)
    r = DIFFICULTY_LEVEL_ORDER.get(res, 1)

    if student_level == "Beginner":
        if res == "Beginner":
            return 100.0
        if res == "Intermediate":
            # flexible: one level above, but foundational first
            return 60.0
        return 0.0  # Advanced not recommended for beginners without foundation
    if student_level == "Intermediate":
        if res == "Intermediate":
            return 100.0
        if res == "Beginner":
            return 70.0  # revision/foundation strengthening
        if res == "Advanced":
            return 65.0  # one level above, stretch
        return 0.0
    # Advanced student
    if res == "Advanced":
        return 100.0
    if res == "Intermediate":
        return 70.0
    if res == "Beginner":
        return 40.0
    return 0.0


def _difficulty_preference_filter_score(preference: str, student_level: str, resource_difficulty: str) -> float:
    if preference == "adaptive":
        return 1.0
    pref = preference.title()
    # If user forces a preference, prioritize exact matches but do not fully block close options
    if resource_difficulty == pref:
        return 1.0
    # keep some relevance if adaptive would have allowed it
    if pref in DIFFICULTY_LEVEL_ORDER and resource_difficulty in DIFFICULTY_LEVEL_ORDER:
        diff = abs(DIFFICULTY_LEVEL_ORDER[pref] - DIFFICULTY_LEVEL_ORDER[resource_difficulty])
        return 0.5 if diff == 1 else 0.1
    return 0.5


def _normalize_priority_scores(skills: List[Dict[str, Any]]) -> Dict[str, float]:
    # skill_comparison priority_score is (gap/100)*importance_weight, typically 0..1
    max_p = max((float(s.get("priority_score", 0.0) or 0.0) for s in skills), default=0.0)
    out: Dict[str, float] = {}
    for s in skills:
        raw = float(s.get("priority_score", 0.0) or 0.0)
        if max_p <= 0:
            out[s["skill_id"]] = 0.0
        else:
            out[s["skill_id"]] = (raw / max_p) * 100.0
    return out


def _explanations_for(
    skill: Dict[str, Any],
    resource: Dict[str, Any],
    current_proficiency: float,
    student_level: str,
    preferred_types: List[str],
) -> List[str]:
    reasons: List[str] = []
    gap = float(skill.get("gap", 0.0) or 0.0)
    classification = str(skill.get("priority_classification", ""))
    skill_name = skill.get("skill_name", resource.get("skill_name", "this skill"))

    if classification == "Critical Gap":
        reasons.append(f"Recommended because {skill_name} is a critical skill gap for your selected role.")
    elif classification == "Moderate Gap":
        reasons.append(f"Recommended because improving {skill_name} can significantly strengthen your role readiness.")
    elif classification == "Minor Gap":
        reasons.append(f"Recommended to help close a minor gap in {skill_name} and move closer to the role benchmark.")
    else:
        reasons.append(f"Recommended to strengthen or maintain {skill_name} for your selected role.")

    if resource.get("difficulty_level") == student_level:
        reasons.append(f"This {resource.get('difficulty_level', '').lower()} resource matches your current proficiency ({current_proficiency:.0f}/100).")
    elif DIFFICULTY_LEVEL_ORDER.get(resource.get("difficulty_level", ""), 0) < DIFFICULTY_LEVEL_ORDER.get(student_level, 0):
        reasons.append(f"This {resource.get('difficulty_level', '').lower()} resource can help reinforce fundamentals before advancing in {skill_name}.")
    else:
        reasons.append(f"This {resource.get('difficulty_level', '').lower()} resource provides the next-level challenge after your current {student_level.lower()} proficiency.")

    if preferred_types and resource.get("resource_type") in preferred_types:
        reasons.append(f"Matches your preferred learning format ({resource.get('resource_type')}).")

    if bool(resource.get("is_free")):
        reasons.append("This is a free resource, making it easier to start immediately.")

    # Keep concise and meaningful
    deduped: List[str] = []
    seen = set()
    for r in reasons:
        if r not in seen:
            deduped.append(r)
            seen.add(r)
    return deduped[:4]


def _select_diverse_top(resources_scored: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    # Greedy selection by score with soft preference for type diversity
    selected: List[Dict[str, Any]] = []
    used_types = set()
    remaining = list(resources_scored)
    while remaining and len(selected) < top_n:
        best_idx = 0
        best_val = None
        for idx, item in enumerate(remaining):
            rtype = item["resource"]["resource_type"]
            diversity_bonus = 1.5 if rtype not in used_types else 0.0
            val = item["recommendation_score"] + diversity_bonus
            if best_val is None or val > best_val:
                best_val = val
                best_idx = idx
        chosen = remaining.pop(best_idx)
        selected.append(chosen)
        used_types.add(chosen["resource"]["resource_type"])
    # final sort by actual recommendation score desc
    selected.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return selected


def recommend_for_analysis(
    analysis: Dict[str, Any],
    resources: List[Dict[str, Any]],
    preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    preferences = preferences or {}
    free_only = bool(preferences.get("free_only", False))
    preferred_types = list(preferences.get("preferred_types") or [])
    difficulty_preference = str(preferences.get("difficulty_preference") or "adaptive").lower()

    skill_comparison = analysis.get("skill_comparison", []) or []
    normalized_priority = _normalize_priority_scores(skill_comparison)
    resources_by_skill: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in resources:
        resources_by_skill[r["skill_id"]].append(r)

    recommended_by_skill: List[Dict[str, Any]] = []
    total_recommended = 0
    total_hours = 0.0
    skills_with_recommendations = 0

    def build_recs_for_skill(skill: Dict[str, Any], maintenance_mode: bool = False) -> List[Dict[str, Any]]:
        sid = skill["skill_id"]
        current_prof = float(skill.get("current_proficiency", 0.0) or 0.0)
        student_level = proficiency_to_level(current_prof)
        skill_resources = list(resources_by_skill.get(sid, []))
        if free_only:
            skill_resources = [r for r in skill_resources if bool(r.get("is_free"))]

        scored: List[Dict[str, Any]] = []
        for res in skill_resources:
            diff_score = difficulty_match_score(current_prof, res["difficulty_level"])
            if diff_score <= 0:
                continue
            # In maintenance mode, prefer same-level/advanced practice or projects rather than basic remediation
            if maintenance_mode:
                s_ord = DIFFICULTY_LEVEL_ORDER.get(student_level, 1)
                r_ord = DIFFICULTY_LEVEL_ORDER.get(res["difficulty_level"], 1)
                if r_ord < s_ord and s_ord >= 2:
                    # allow only some revision; de-emphasize easier material
                    diff_score *= 0.6
            pref_mult = _difficulty_preference_filter_score(difficulty_preference, student_level, res["difficulty_level"])
            if pref_mult <= 0:
                continue
            diff_score_adj = diff_score * pref_mult

            quality_score = max(0.0, min(100.0, float(res.get("quality_score", 0) or 0)))
            relevance_score = 100.0 if (not preferred_types or res.get("resource_type") in preferred_types) else 60.0
            if maintenance_mode and res.get("resource_type") in {"Practice Platform", "Project Tutorial", "Documentation"}:
                relevance_score = min(100.0, relevance_score + 10.0)
            free_score = 100.0 if bool(res.get("is_free")) else 0.0
            skill_priority_score = normalized_priority.get(sid, 0.0)

            rec_score = (
                WEIGHTS["skill_priority"] * skill_priority_score
                + WEIGHTS["difficulty_match"] * diff_score_adj
                + WEIGHTS["resource_quality"] * quality_score
                + WEIGHTS["relevance"] * relevance_score
                + WEIGHTS["free_resource"] * free_score
            )
            if maintenance_mode:
                # prioritize quality/difficulty fit over gap priority for already-strong skills
                rec_score = (
                    0.10 * skill_priority_score
                    + 0.35 * diff_score_adj
                    + 0.30 * quality_score
                    + 0.20 * relevance_score
                    + 0.05 * free_score
                )
            rec_score = round(max(0.0, min(100.0, rec_score)), 2)

            explanations = _explanations_for(skill, res, current_prof, student_level, preferred_types)
            if maintenance_mode:
                explanations = [
                    f"{skill.get('skill_name')} is already at or near the benchmark; this resource can help you maintain or deepen strength.",
                    f"This {res.get('difficulty_level', '').lower()} {res.get('resource_type', 'resource').lower()} suits your current proficiency ({current_prof:.0f}/100).",
                ] + ([explanations[-1]] if explanations else [])
            scored.append({
                "resource": res,
                "recommendation_score": rec_score,
                "score_components": {
                    "skill_priority_score": round(skill_priority_score, 2),
                    "difficulty_match_score": round(diff_score_adj, 2),
                    "resource_quality_score": round(quality_score, 2),
                    "relevance_score": round(relevance_score, 2),
                    "free_resource_score": round(free_score, 2),
                },
                "explanations": explanations[:4],
            })

        unique_by_id = {}
        for item in scored:
            rid = item["resource"]["resource_id"]
            if rid not in unique_by_id or item["recommendation_score"] > unique_by_id[rid]["recommendation_score"]:
                unique_by_id[rid] = item
        scored_unique = list(unique_by_id.values())
        scored_unique.sort(key=lambda x: (x["recommendation_score"], float(x["resource"].get("quality_score", 0))), reverse=True)

        if maintenance_mode:
            target_n = 2 if len(scored_unique) >= 2 else len(scored_unique)
            top = _select_diverse_top(scored_unique, top_n=max(1, target_n) if scored_unique else 0)
            top = top[:3]
        else:
            top = _select_diverse_top(scored_unique, top_n=5 if len(scored_unique) >= 5 else (5 if len(scored_unique) >= 3 else len(scored_unique)))
            if len(scored_unique) < 3:
                top = scored_unique

        rec_items = []
        for rank, item in enumerate(top, start=1):
            res = item["resource"]
            rec_items.append({
                "resource_id": res["resource_id"],
                "resource_title": res["resource_title"],
                "skill_id": res["skill_id"],
                "skill_name": res["skill_name"],
                "provider": res["provider"],
                "resource_type": res["resource_type"],
                "difficulty_level": res["difficulty_level"],
                "description": res["description"],
                "resource_url": res["resource_url"],
                "estimated_hours": float(res.get("estimated_hours", 0.0) or 0.0),
                "prerequisites": res.get("prerequisites", ""),
                "is_free": bool(res.get("is_free")),
                "language": res.get("language", "English"),
                "quality_score": int(res.get("quality_score", 0) or 0),
                "tags": res.get("tags", ""),
                "recommendation_score": item["recommendation_score"],
                "score_components": item["score_components"],
                "why_recommended": item["explanations"],
                "recommended_rank": rank,
            })
        return rec_items

    # Recommend for skills that have a meaningful gap (not Strong)
    candidate_skills = [
        s for s in skill_comparison
        if str(s.get("priority_classification")) in {"Critical Gap", "Moderate Gap", "Minor Gap"}
    ]

    for skill in candidate_skills:
        rec_items = build_recs_for_skill(skill, maintenance_mode=False)
        if rec_items:
            sid = skill["skill_id"]
            skills_with_recommendations += 1
            total_recommended += len(rec_items)
            total_hours += sum(float(r["estimated_hours"]) for r in rec_items)
            recommended_by_skill.append({
                "skill_id": sid,
                "skill_name": skill.get("skill_name"),
                "priority_classification": skill.get("priority_classification"),
                "priority_score": float(skill.get("priority_score", 0.0) or 0.0),
                "current_proficiency": float(skill.get("current_proficiency", 0.0) or 0.0),
                "required_proficiency": float(skill.get("required_proficiency", 0.0) or 0.0),
                "gap": float(skill.get("gap", 0.0) or 0.0),
                "resources": rec_items,
            })

    # Maintenance recommendations for Strong skills (Stage 4 support)
    maintenance_recommendations_by_skill: List[Dict[str, Any]] = []
    strong_skills = [s for s in skill_comparison if str(s.get("priority_classification")) == "Strong"]
    for skill in strong_skills:
        rec_items = build_recs_for_skill(skill, maintenance_mode=True)
        if rec_items:
            maintenance_recommendations_by_skill.append({
                "skill_id": skill["skill_id"],
                "skill_name": skill.get("skill_name"),
                "priority_classification": skill.get("priority_classification"),
                "current_proficiency": float(skill.get("current_proficiency", 0.0) or 0.0),
                "required_proficiency": float(skill.get("required_proficiency", 0.0) or 0.0),
                "gap": float(skill.get("gap", 0.0) or 0.0),
                "resources": rec_items,
            })

    # Sort skill groups by Phase 1 priority score desc
    recommended_by_skill.sort(key=lambda x: (x.get("priority_score", 0.0), x.get("gap", 0.0)), reverse=True)

    # Totals for summary include maintenance recs used in roadmap visibility? Keep primary summary focused on priority skills,
    # but also provide maintenance totals separately for UI/roadmap.
    maintenance_total = sum(len(g["resources"]) for g in maintenance_recommendations_by_skill)
    maintenance_hours = sum(float(r["estimated_hours"]) for g in maintenance_recommendations_by_skill for r in g["resources"])
    maintenance_free = sum(1 for g in maintenance_recommendations_by_skill for r in g["resources"] if r["is_free"])

    return {
        "recommended_resources_by_skill": recommended_by_skill,
        "maintenance_recommendations_by_skill": maintenance_recommendations_by_skill,
        "recommendation_summary": {
            "priority_skills_covered": skills_with_recommendations,
            "total_recommended_resources": total_recommended,
            "free_resources_recommended": sum(1 for g in recommended_by_skill for r in g["resources"] if r["is_free"]),
            "estimated_total_learning_hours": round(total_hours, 2),
            "maintenance_resources_count": maintenance_total,
            "maintenance_estimated_hours": round(maintenance_hours, 2),
            "maintenance_free_resources": maintenance_free,
            "top_skill_to_focus": (
                recommended_by_skill[0]["skill_name"] if recommended_by_skill else
                (analysis.get("top_priority_skills", [{}])[0].get("skill_name") if analysis.get("top_priority_skills") else None)
            ),
        },
        "ranking": {
            "formula": "Recommendation Score = 0.40*SkillPriority + 0.25*DifficultyMatch + 0.20*ResourceQuality + 0.10*Relevance + 0.05*FreeResource",
            "weights": WEIGHTS,
            "normalization": "All component scores are normalized to 0-100 before weighting. Maintenance recommendations for strong skills emphasize difficulty fit, quality, and relevance.",
            "disclosure": "Weights are initial configurable ranking weights and are not scientifically validated.",
        },
    }