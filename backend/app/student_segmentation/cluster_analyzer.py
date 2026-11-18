"""
Cluster interpretation and dynamic labeling for Student Segmentation (Phase 3).

Generates human-readable cluster names/descriptions and per-cluster statistics
from learned KMeans assignments and centroids (interpreted in original skill
scale) together with Phase 1 role requirements. Labels are NOT hardcoded by
cluster ID.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def _round(v: Any, nd: int = 2) -> float:
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return 0.0
        return round(f, nd)
    except Exception:
        return 0.0


def _safe_mean(arr: np.ndarray) -> float:
    if arr.size == 0:
        return 0.0
    v = float(np.mean(arr))
    return 0.0 if (math.isnan(v) or math.isinf(v)) else v


def _top_bottom_skills(
    cluster_means: Dict[str, float],
    overall_means: Dict[str, float],
    n: int = 3,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    deltas = []
    for skill, c_mean in cluster_means.items():
        o_mean = float(overall_means.get(skill, 0.0))
        deltas.append((skill, float(c_mean), o_mean, float(c_mean) - o_mean))

    # Strongest: highest absolute cluster mean, tie-break by positive delta
    strongest_sorted = sorted(deltas, key=lambda x: (x[1], x[3], x[0].lower()), reverse=True)
    weakest_sorted = sorted(deltas, key=lambda x: (x[1], -x[3], x[0].lower()))

    strongest = [
        {
            "skill_name": s,
            "cluster_average": _round(c, 2),
            "overall_average": _round(o, 2),
            "difference_from_overall": _round(d, 2),
        }
        for s, c, o, d in strongest_sorted[:n]
    ]
    weakest = [
        {
            "skill_name": s,
            "cluster_average": _round(c, 2),
            "overall_average": _round(o, 2),
            "difference_from_overall": _round(d, 2),
        }
        for s, c, o, d in weakest_sorted[:n]
    ]
    return strongest, weakest


def _category_profile(
    cluster_means: Dict[str, float],
    overall_means: Dict[str, float],
    requirements: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    cat_vals: Dict[str, List[float]] = defaultdict(list)
    cat_overall: Dict[str, List[float]] = defaultdict(list)
    cat_req: Dict[str, List[float]] = defaultdict(list)
    skill_to_cat = {}
    for req in requirements:
        name = str(req.get("skill_name"))
        cat = str(req.get("skill_category", "General"))
        skill_to_cat[name] = cat
        cat_req[cat].append(float(req.get("required_proficiency", 0.0) or 0.0))
    for skill, val in cluster_means.items():
        cat = skill_to_cat.get(skill, "General")
        cat_vals[cat].append(float(val))
        cat_overall[cat].append(float(overall_means.get(skill, 0.0)))

    profiles = []
    for cat in sorted(cat_vals.keys()):
        c_avg = _safe_mean(np.array(cat_vals[cat], dtype=float))
        o_avg = _safe_mean(np.array(cat_overall[cat], dtype=float))
        r_avg = _safe_mean(np.array(cat_req.get(cat, []), dtype=float)) if cat_req.get(cat) else 0.0
        profiles.append(
            {
                "category": cat,
                "cluster_average": _round(c_avg, 2),
                "overall_average": _round(o_avg, 2),
                "required_average": _round(r_avg, 2),
                "difference_from_overall": _round(c_avg - o_avg, 2),
            }
        )
    profiles.sort(key=lambda x: x["difference_from_overall"], reverse=True)
    return profiles


def _generate_cluster_name_and_description(
    cluster_id: int,
    cluster_means: Dict[str, float],
    overall_means: Dict[str, float],
    requirements: List[Dict[str, Any]],
    cluster_avg: float,
    overall_role_avg: float,
) -> Tuple[str, str]:
    # Compare cluster to overall role averages and role requirements
    deltas = []
    req_map = {str(r.get("skill_name")): r for r in requirements}
    for skill, c_mean in cluster_means.items():
        o_mean = float(overall_means.get(skill, 0.0))
        req = float(req_map.get(skill, {}).get("required_proficiency", 0.0) or 0.0)
        deltas.append(
            {
                "skill_name": skill,
                "cluster_average": float(c_mean),
                "overall_average": o_mean,
                "delta_overall": float(c_mean) - o_mean,
                "required_proficiency": req,
                "delta_required": float(c_mean) - req,
                "category": str(req_map.get(skill, {}).get("skill_category", "General")),
                "is_core": bool(req_map.get(skill, {}).get("is_core_skill", False)),
            }
        )

    # Identify notable strengths/weaknesses relative to overall role cohort
    pos = sorted([d for d in deltas if d["delta_overall"] >= 3.0], key=lambda x: (x["delta_overall"], x["cluster_average"]), reverse=True)
    neg = sorted([d for d in deltas if d["delta_overall"] <= -3.0], key=lambda x: (x["delta_overall"], -x["cluster_average"]))

    # Category-level tendencies
    cat_profiles = _category_profile(cluster_means, overall_means, requirements)
    strong_cats = [c["category"] for c in cat_profiles if c["difference_from_overall"] >= 3.0][:2]
    weak_cats = [c["category"] for c in sorted(cat_profiles, key=lambda x: x["difference_from_overall"]) if c["difference_from_overall"] <= -3.0][:2]

    overall_delta = cluster_avg - overall_role_avg
    if overall_delta >= 6.0:
        level_label = "Above-Average Proficiency"
    elif overall_delta <= -6.0:
        level_label = "Foundational Proficiency"
    else:
        level_label = "Balanced Proficiency"

    def short_skill_label(items: List[Dict[str, Any]], fallback_cat: List[str]) -> Optional[str]:
        if items:
            names = [i["skill_name"] for i in items[:2]]
            # shorten very long compound names for label readability
            short = []
            for n in names:
                if n == "Data Structures and Algorithms":
                    short.append("DSA")
                elif n == "Object-Oriented Programming":
                    short.append("OOP")
                elif n == "Git and GitHub":
                    short.append("Git/GitHub")
                elif n == "Data Visualization":
                    short.append("Data Viz")
                else:
                    short.append(n)
            return " & ".join(short)
        if fallback_cat:
            return " & ".join(fallback_cat[:2])
        return None

    strong_label = short_skill_label(pos, strong_cats)
    weak_label = short_skill_label(list(reversed(neg)), weak_cats) if neg else short_skill_label(list(neg), weak_cats)

    # Compose dynamic name
    if strong_label and weak_label and abs(overall_delta) < 10:
        name = f"Stronger {strong_label}, Developing {weak_label}"
    elif strong_label and not weak_label:
        name = f"Strong {strong_label} Profile"
    elif weak_label and not strong_label:
        name = f"Developing {weak_label} Profile"
    elif strong_label and weak_label:
        name = f"{level_label}: Strong {strong_label}, Developing {weak_label}"
    else:
        name = f"{level_label} Profile"

    # Description with concrete evidence
    above_req = [d for d in deltas if d["delta_required"] >= 0]
    below_req = [d for d in deltas if d["delta_required"] < 0]
    top_strengths = sorted(deltas, key=lambda x: (x["delta_overall"], x["cluster_average"]), reverse=True)[:3]
    top_needs = sorted(deltas, key=lambda x: (x["delta_overall"], -x["cluster_average"]))[:3]

    strengths_text = ", ".join(
        f"{d['skill_name']} ({_round(d['cluster_average'])} avg, {_round(d['delta_overall'], 1):+} vs role avg)"
        for d in top_strengths
    )
    needs_text = ", ".join(
        f"{d['skill_name']} ({_round(d['cluster_average'])} avg, {_round(d['delta_overall'], 1):+} vs role avg)"
        for d in top_needs
    )
    cat_text_parts = []
    if strong_cats:
        cat_text_parts.append(f"relatively stronger in {', '.join(strong_cats)}")
    if weak_cats:
        cat_text_parts.append(f"relatively lower in {', '.join(weak_cats)}")
    cat_sentence = (" This group is " + " and ".join(cat_text_parts) + " compared to other students in the same role.") if cat_text_parts else ""

    description = (
        f"Cluster {cluster_id} ({name}) includes students whose role-relevant skill profile averages "
        f"{_round(cluster_avg, 1)} across selected skills ({_round(overall_delta, 1):+} points vs overall role average {_round(overall_role_avg, 1)}). "
        f"Compared with the role cohort, notable strengths appear in {strengths_text}. "
        f"Lower relative areas include {needs_text}. "
        f"Against role benchmark requirements, this cluster is at/above requirement in {len(above_req)} skills and below requirement in {len(below_req)} skills." 
        f"{cat_sentence} "
        f"This description is derived from learned cluster centroids and Phase 1 role requirements (synthetic-profile analysis)."
    )
    return name, description


def analyze_role_clusters(
    role_id: str,
    role_name: str,
    feature_names: List[str],
    X_original: np.ndarray,
    labels: np.ndarray,
    requirements: List[Dict[str, Any]],
) -> Dict[str, Any]:
    n_samples = int(X_original.shape[0])
    if n_samples == 0:
        raise ValueError("Cannot analyze clusters for empty dataset.")

    labels = np.asarray(labels).astype(int)
    unique_clusters = sorted(int(x) for x in np.unique(labels))
    overall_means_arr = X_original.mean(axis=0)
    overall_means = {name: float(overall_means_arr[i]) for i, name in enumerate(feature_names)}
    overall_role_avg = float(np.mean(overall_means_arr))

    clusters: List[Dict[str, Any]] = []
    for cid in unique_clusters:
        mask = labels == cid
        cluster_X = X_original[mask]
        count = int(cluster_X.shape[0])
        pct = (count / n_samples * 100.0) if n_samples else 0.0

        means_arr = cluster_X.mean(axis=0) if count else np.zeros(len(feature_names), dtype=float)
        cluster_means = {name: float(means_arr[i]) for i, name in enumerate(feature_names)}
        cluster_avg = float(np.mean(means_arr)) if count else 0.0

        strongest, weakest = _top_bottom_skills(cluster_means, overall_means, n=3)
        cat_profiles = _category_profile(cluster_means, overall_means, requirements)
        name, description = _generate_cluster_name_and_description(
            cluster_id=cid,
            cluster_means=cluster_means,
            overall_means=overall_means,
            requirements=requirements,
            cluster_avg=cluster_avg,
            overall_role_avg=overall_role_avg,
        )

        # role-specific skill patterns vs requirements
        req_comparison = []
        req_map = {str(r.get("skill_name")): r for r in requirements}
        for skill in feature_names:
            req = req_map.get(skill, {})
            req_val = float(req.get("required_proficiency", 0.0) or 0.0)
            c_val = float(cluster_means.get(skill, 0.0))
            req_comparison.append(
                {
                    "skill_id": req.get("skill_id"),
                    "skill_name": skill,
                    "skill_category": req.get("skill_category", "General"),
                    "is_core_skill": bool(req.get("is_core_skill", False)),
                    "cluster_average": _round(c_val, 2),
                    "required_proficiency": _round(req_val, 2),
                    "overall_average": _round(overall_means.get(skill, 0.0), 2),
                    "difference_from_required": _round(c_val - req_val, 2),
                    "difference_from_overall": _round(c_val - overall_means.get(skill, 0.0), 2),
                }
            )
        req_comparison.sort(key=lambda x: (x["difference_from_overall"], x["cluster_average"]), reverse=True)

        clusters.append(
            {
                "cluster_id": cid,
                "cluster_name": name,
                "cluster_description": description,
                "student_count": count,
                "student_percentage": _round(pct, 2),
                "average_skill_proficiency": _round(cluster_avg, 2),
                "difference_from_overall_role_average": _round(cluster_avg - overall_role_avg, 2),
                "average_proficiency_per_skill": {k: _round(v, 2) for k, v in cluster_means.items()},
                "skill_profile_vs_requirements": req_comparison,
                "strongest_skills": strongest,
                "weakest_skills": weakest,
                "category_profile": cat_profiles,
            }
        )

    clusters.sort(key=lambda x: int(x["cluster_id"]))

    distribution = [
        {
            "cluster_id": c["cluster_id"],
            "cluster_name": c["cluster_name"],
            "student_count": c["student_count"],
            "student_percentage": c["student_percentage"],
        }
        for c in clusters
    ]

    return {
        "role_id": role_id,
        "role_name": role_name,
        "n_students": n_samples,
        "overall_role_average": _round(overall_role_avg, 2),
        "overall_average_per_skill": {k: _round(v, 2) for k, v in overall_means.items()},
        "clusters": clusters,
        "cluster_distribution": distribution,
    }
