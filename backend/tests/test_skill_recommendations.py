"""
Tests for CareerLens Phase 2: Personalized Learning Recommendation Engine.

Covers curated resource dataset loading/filtering, recommendation scoring/matching,
roadmap generation, API endpoints, validation, and Phase 1 integration.
"""

from __future__ import annotations

import math

from app.skill_gap.dataset_loader import (
    filter_learning_resources,
    get_learning_resources,
    get_learning_resources_by_skill,
    get_learning_resources_summary,
    get_role_requirements,
    get_skill_metadata_index,
)
from app.skill_gap.gap_analyzer import analyze_skill_gap
from app.skill_gap.recommendation_engine import (
    WEIGHTS,
    difficulty_match_score,
    proficiency_to_level,
    recommend_for_analysis,
)
from app.skill_gap.roadmap_generator import generate_learning_roadmap


def _sample_backend_analysis():
    role = get_role_requirements("backend_developer")
    normalized = {}
    # create a mix of gaps/strengths
    for s in role["skills"]:
        name = s["skill_name"].strip().lower()
        if s["skill_name"] in {"REST APIs", "Node.js", "System Design"}:
            normalized[name] = 20.0
        elif s["skill_name"] in {"Java", "SQL"}:
            normalized[name] = 55.0
        else:
            normalized[name] = 85.0
    return analyze_skill_gap(role=role, normalized_current_skills=normalized, metadata_index=get_skill_metadata_index())


# -------------------- Dataset loading & validation --------------------

def test_learning_resources_dataset_loading_and_coverage():
    resources = get_learning_resources()
    assert 150 <= len(resources) <= 200
    by_skill = get_learning_resources_by_skill()
    # all 33 Phase 1 skills covered
    assert len(by_skill) == 33

    seen_ids = set()
    seen_urls = set()
    valid_types = {
        "Documentation",
        "Video Course",
        "Interactive Tutorial",
        "Practice Platform",
        "Project Tutorial",
        "Course",
        "Book or Reading Material",
    }
    valid_difficulties = {"Beginner", "Intermediate", "Advanced"}

    for r in resources:
        assert r["resource_id"] not in seen_ids
        assert r["resource_url"] not in seen_urls
        seen_ids.add(r["resource_id"])
        seen_urls.add(r["resource_url"])

        assert r["skill_id"] in by_skill
        assert r["skill_name"]
        assert r["resource_title"]
        assert r["provider"]
        assert r["resource_url"].startswith("http")
        assert r["resource_type"] in valid_types
        assert r["difficulty_level"] in valid_difficulties
        assert float(r["estimated_hours"]) > 0
        assert 0 <= int(r["quality_score"]) <= 100
        assert isinstance(r["is_free"], bool)
        assert r["language"]


def test_learning_resources_filtering():
    resources = get_learning_resources()
    # pick a known skill and provider from data
    sql = filter_learning_resources(resources, skill_id="sql")
    assert sql and all(r["skill_id"] == "sql" for r in sql)

    beginner = filter_learning_resources(resources, difficulty="beginner")
    assert beginner and all(r["difficulty_level"] == "Beginner" for r in beginner)

    docs = filter_learning_resources(resources, resource_type="Documentation")
    assert docs and all(r["resource_type"] == "Documentation" for r in docs)

    free = filter_learning_resources(resources, free_only=True)
    assert free and all(r["is_free"] is True for r in free)

    # provider filter case-insensitive
    if resources:
        prov = resources[0]["provider"]
        by_prov = filter_learning_resources(resources, provider=prov.lower())
        assert by_prov and all(r["provider"].lower() == prov.lower() for r in by_prov)


def test_resources_summary():
    summary = get_learning_resources_summary()
    assert summary["total_resources"] >= 150
    assert summary["total_covered_skills"] == 33
    assert set(summary["free_vs_paid"].keys()) == {"free", "paid"}
    assert summary["free_vs_paid"]["free"] + summary["free_vs_paid"]["paid"] == summary["total_resources"]
    assert "resource_counts_by_difficulty" in summary
    assert "resource_counts_by_type" in summary
    assert "provider_distribution" in summary


# -------------------- Difficulty matching & scoring --------------------

def test_proficiency_to_level_and_difficulty_match():
    assert proficiency_to_level(0) == "Beginner"
    assert proficiency_to_level(30) == "Beginner"
    assert proficiency_to_level(31) == "Intermediate"
    assert proficiency_to_level(65) == "Intermediate"
    assert proficiency_to_level(66) == "Advanced"

    # Beginner: no advanced without foundation
    assert difficulty_match_score(20, "Beginner") == 100.0
    assert difficulty_match_score(20, "Intermediate") == 60.0
    assert difficulty_match_score(20, "Advanced") == 0.0

    # Intermediate: flexible around level
    assert difficulty_match_score(50, "Intermediate") == 100.0
    assert difficulty_match_score(50, "Beginner") == 70.0
    assert difficulty_match_score(50, "Advanced") == 65.0

    # Advanced
    assert difficulty_match_score(85, "Advanced") == 100.0
    assert difficulty_match_score(85, "Intermediate") == 70.0
    assert difficulty_match_score(85, "Beginner") == 40.0


def test_recommendation_ranking_scoring_and_explanations():
    analysis = _sample_backend_analysis()
    resources = get_learning_resources()
    rec = recommend_for_analysis(analysis, resources, preferences={"free_only": False, "preferred_types": ["Documentation"], "difficulty_preference": "adaptive"})

    assert "recommended_resources_by_skill" in rec
    assert "recommendation_summary" in rec
    assert rec["ranking"]["weights"] == WEIGHTS

    groups = rec["recommended_resources_by_skill"]
    assert groups, "Expected recommendations for a profile with gaps"

    # groups sorted by priority/gap desc
    prios = [(g.get("priority_score", 0), g.get("gap", 0)) for g in groups]
    assert prios == sorted(prios, reverse=True)

    for g in groups:
        assert 1 <= len(g["resources"]) <= 5
        scores = [r["recommendation_score"] for r in g["resources"]]
        assert scores == sorted(scores, reverse=True)
        ids = [r["resource_id"] for r in g["resources"]]
        assert len(ids) == len(set(ids)), "Duplicate recommendations within a skill group"
        for r in g["resources"]:
            assert 0 <= r["recommendation_score"] <= 100
            comps = r["score_components"]
            # all components normalized 0-100
            for k in ["skill_priority_score", "difficulty_match_score", "resource_quality_score", "relevance_score", "free_resource_score"]:
                assert 0 <= comps[k] <= 100
            assert isinstance(r["why_recommended"], list) and len(r["why_recommended"]) >= 1
            # explanations should be meaningful strings
            assert all(isinstance(x, str) and x.strip() for x in r["why_recommended"])


def test_free_only_preference_and_no_advanced_for_beginners():
    analysis = _sample_backend_analysis()
    resources = get_learning_resources()
    rec = recommend_for_analysis(analysis, resources, preferences={"free_only": True, "preferred_types": [], "difficulty_preference": "adaptive"})
    for g in rec["recommended_resources_by_skill"]:
        for r in g["resources"]:
            assert r["is_free"] is True
    # Beginner-level current proficiency (20) should not get Advanced resources
    beginner_groups = [g for g in rec["recommended_resources_by_skill"] if g["current_proficiency"] <= 30]
    for g in beginner_groups:
        assert all(r["difficulty_level"] != "Advanced" for r in g["resources"])


def test_duplicate_recommendation_prevention_across_ranking():
    # craft resources with duplicate id possibility? engine dedupes by resource_id; ensure no dups in output
    analysis = _sample_backend_analysis()
    resources = get_learning_resources()
    rec = recommend_for_analysis(analysis, resources, preferences={"free_only": False})
    all_ids = [r["resource_id"] for g in rec["recommended_resources_by_skill"] for r in g["resources"]]
    # same resource could appear for different skills only if mapped so, but our dataset maps 1:1 skill_id
    # ensure per-skill uniqueness
    for g in rec["recommended_resources_by_skill"]:
        ids = [r["resource_id"] for r in g["resources"]]
        assert len(ids) == len(set(ids))


def test_missing_resource_handling_for_skill_with_no_resources():
    analysis = _sample_backend_analysis()
    # remove all resources for one gap skill
    resources = [r for r in get_learning_resources() if r["skill_id"] != "system_design"]
    rec = recommend_for_analysis(analysis, resources, preferences={"free_only": False})
    # should not crash; system_design may have no rec group
    sys_groups = [g for g in rec["recommended_resources_by_skill"] if g["skill_id"] == "system_design"]
    assert sys_groups == [] or len(sys_groups[0]["resources"]) == 0


# -------------------- Roadmap generation --------------------

def test_roadmap_generation_four_stages():
    analysis = _sample_backend_analysis()
    resources = get_learning_resources()
    rec = recommend_for_analysis(analysis, resources, preferences={"free_only": False})
    roadmap = generate_learning_roadmap(
        analysis,
        rec.get("recommended_resources_by_skill", []),
        rec.get("maintenance_recommendations_by_skill", []),
    )
    assert [s["stage"] for s in roadmap] == [
        "immediate_focus",
        "skill_development",
        "strengthening_skills",
        "maintain_strengths",
    ]
    all_role_skill_ids = {s["skill_id"] for s in analysis["skill_comparison"]}
    roadmap_skill_ids = {item["skill_id"] for stage in roadmap for item in stage["skills"]}
    assert roadmap_skill_ids == all_role_skill_ids
    for stage in roadmap:
        assert "title" in stage and "description" in stage
        assert stage["skill_count"] == len(stage["skills"])
        assert stage["estimated_stage_hours"] >= 0
        for item in stage["skills"]:
            assert item["reason_for_prioritization"]
            assert isinstance(item["recommended_sequence"], list)
            # hours based on actual resource metadata
            calc_hours = round(sum(float(r.get("estimated_hours", 0.0)) for r in item.get("recommended_resources", [])), 2)
            assert math.isclose(float(item["estimated_resource_hours"]), calc_hours, rel_tol=0, abs_tol=1e-6)


# -------------------- API endpoints & validation --------------------

def test_api_resources_filters_and_summary(client):
    resp = client.get("/api/skills/resources")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == len(data["resources"]) >= 150

    filt = client.get("/api/skills/resources?skill_id=sql&difficulty=Beginner&free_only=true")
    assert filt.status_code == 200
    fdata = filt.get_json()
    assert all(r["skill_id"] == "sql" for r in fdata["resources"])
    assert all(r["difficulty_level"] == "Beginner" for r in fdata["resources"])
    assert all(r["is_free"] is True for r in fdata["resources"])

    bad = client.get("/api/skills/resources?difficulty=Expert")
    assert bad.status_code == 400
    assert bad.get_json()["error"] == "Validation Error"

    summary = client.get("/api/skills/resources/summary")
    assert summary.status_code == 200
    sdata = summary.get_json()
    assert sdata["total_covered_skills"] == 33
    assert sdata["total_resources"] >= 150


def test_api_recommend_success_and_phase1_integration(client):
    payload = {
        "target_role": "backend_developer",
        "skills": {
            "Java": 75,
            "Python": 60,
            "DSA": 45,
            "SQL": 50,
            "DBMS": 55,
            "Node.js": 30,
            "System Design": 25,
        },
        "preferences": {
            "free_only": True,
            "preferred_types": ["Documentation", "Interactive Tutorial", "Practice Platform"],
            "difficulty_preference": "adaptive",
        },
    }
    resp = client.post("/api/skills/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()

    # integrates/reuses Phase 1 results
    assert data["target_role"] == "backend_developer"
    assert 0 <= data["overall_readiness_score"] <= 100
    assert isinstance(data.get("priority_skills"), list)
    assert isinstance(data.get("recommended_resources_by_skill"), list)
    assert isinstance(data.get("learning_roadmap"), list) and len(data["learning_roadmap"]) == 4
    assert [s["stage"] for s in data["learning_roadmap"]] == [
        "immediate_focus",
        "skill_development",
        "strengthening_skills",
        "maintain_strengths",
    ]
    rs = data.get("recommendation_summary", {})
    assert "priority_skills_covered" in rs
    assert "total_recommended_resources" in rs
    assert "free_resources_recommended" in rs
    assert "estimated_total_learning_hours" in rs
    assert "top_skill_to_focus" in rs
    assert "dataset_disclosure" in data
    assert "learning_resources" in data["dataset_disclosure"]
    assert "recommendation_scores" in data["dataset_disclosure"]

    # free_only respected
    for g in data["recommended_resources_by_skill"]:
        assert all(r["is_free"] is True for r in g["resources"])


def test_api_recommend_invalid_requests(client):
    bad_role = client.post("/api/skills/recommend", json={"target_role": "unknown_role", "skills": {"Java": 50}})
    assert bad_role.status_code == 400

    bad_skill = client.post("/api/skills/recommend", json={"target_role": "backend_developer", "skills": {"Java": 101}})
    assert bad_skill.status_code == 400

    bad_pref = client.post(
        "/api/skills/recommend",
        json={
            "target_role": "backend_developer",
            "skills": {"Java": 50},
            "preferences": {"preferred_types": ["NotARealType"]},
        },
    )
    assert bad_pref.status_code == 400

    malformed = client.post("/api/skills/recommend", data="not json", content_type="text/plain")
    assert malformed.status_code == 400

    missing_body = client.post("/api/skills/recommend", json={"skills": {"Java": 50}})
    assert missing_body.status_code == 400
