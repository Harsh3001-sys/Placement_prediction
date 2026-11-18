"""
Tests for CareerLens Skill Gap Analysis (Phase 1).

Covers dataset loading, algorithm behavior, and API endpoints.
"""

import math

import pytest

from app.skill_gap.dataset_loader import (
    get_metadata,
    get_role_requirements,
    get_roles,
    get_skill_metadata_index,
    role_exists,
)
from app.skill_gap.gap_analyzer import analyze_skill_gap, classify_gap


def test_dataset_loading_roles_and_metadata():
    roles = get_roles()
    assert len(roles) == 6
    role_ids = {r["role_id"] for r in roles}
    assert {
        "software_developer",
        "backend_developer",
        "frontend_developer",
        "full_stack_developer",
        "data_analyst",
        "ml_engineer",
    }.issubset(role_ids)
    for r in roles:
        assert r["skill_count"] >= 12
        assert r["core_skill_count"] >= 1

    meta = get_metadata()
    assert len(meta) >= 33
    assert all(m.get("skill_id") and m.get("description") for m in meta)


def test_role_requirements_weights_normalized_and_valid():
    for role in get_roles():
        req = get_role_requirements(role["role_id"])
        assert req["role_id"] == role["role_id"]
        skills = req["skills"]
        assert 12 <= len(skills) <= 18
        total_w = sum(s["importance_weight"] for s in skills)
        assert math.isclose(total_w, 1.0, rel_tol=0, abs_tol=1e-6)
        for s in skills:
            assert 0 <= s["required_proficiency"] <= 100
            assert s["importance_weight"] > 0
            assert isinstance(s["is_core_skill"], bool)


def test_analyze_valid_role_and_missing_skills_default_to_zero():
    role = get_role_requirements("backend_developer")
    # provide only a subset; missing should be treated as 0
    result = analyze_skill_gap(
        role=role,
        normalized_current_skills={"java": 70.0, "sql": 50.0},
        metadata_index=get_skill_metadata_index(),
    )
    assert result["target_role"] == "backend_developer"
    assert 0 <= result["overall_readiness_score"] <= 100
    # every role skill should be present in comparison
    assert len(result["skill_comparison"]) == role["skill_count"]
    # a skill not provided (e.g. DBMS if omitted) should have current 0
    omitted = next(s for s in result["skill_comparison"] if s["skill_name"] == "DBMS")
    assert omitted["current_proficiency"] == 0.0
    assert omitted["gap"] == omitted["required_proficiency"]


def test_gap_calculation_and_zero_gap_case():
    role = get_role_requirements("data_analyst")
    # Build perfect/above-required input for all skills
    current = {s["skill_name"].strip().lower(): 100.0 for s in role["skills"]}
    result = analyze_skill_gap(role=role, normalized_current_skills=current)
    assert result["overall_readiness_score"] == 100.0
    assert result["summary"]["critical_gaps"] == 0
    assert result["summary"]["moderate_gaps"] == 0
    assert result["summary"]["minor_gaps"] == 0
    assert result["summary"]["strong_skills"] == role["skill_count"]
    for s in result["skill_comparison"]:
        assert s["gap"] == 0.0
        assert s["gap_percentage"] == 0.0
        assert s["priority_classification"] == "Strong"
        assert s["priority_score"] == 0.0
    assert result["skills_requiring_improvement"] == []


def test_no_penalty_when_current_exceeds_required():
    role = get_role_requirements("frontend_developer")
    # exceed requirements for all skills
    current = {s["skill_name"].strip().lower(): 100.0 for s in role["skills"]}
    result = analyze_skill_gap(role=role, normalized_current_skills=current)
    # all gaps should be zero, no penalty
    assert all(s["gap"] == 0.0 for s in result["skill_comparison"])
    # readiness should not be reduced below full coverage baseline; using weighted current gives 100
    assert result["overall_readiness_score"] == 100.0


def test_weighted_readiness_calculation():
    # Construct a small synthetic role payload to verify exact weighted sum
    role = {
        "role_id": "test_role",
        "role_name": "Test Role",
        "skills": [
            {
                "skill_id": "a",
                "skill_name": "Skill A",
                "required_proficiency": 80.0,
                "importance_weight": 0.6,
                "skill_category": "Cat",
                "is_core_skill": True,
            },
            {
                "skill_id": "b",
                "skill_name": "Skill B",
                "required_proficiency": 60.0,
                "importance_weight": 0.4,
                "skill_category": "Cat",
                "is_core_skill": False,
            },
        ],
    }
    result = analyze_skill_gap(
        role=role,
        normalized_current_skills={"skill a": 50.0, "skill b": 100.0},
    )
    # readiness = 50*0.6 + 100*0.4 = 70
    assert result["overall_readiness_score"] == 70.0
    # Skill A: gap 30, priority (30/100)*0.6 = 0.18; Skill B gap 0
    sa = next(s for s in result["skill_comparison"] if s["skill_name"] == "Skill A")
    sb = next(s for s in result["skill_comparison"] if s["skill_name"] == "Skill B")
    assert sa["gap"] == 30.0
    assert math.isclose(sa["priority_score"], 0.18, rel_tol=0, abs_tol=1e-9)
    assert sb["gap"] == 0.0
    assert sb["priority_score"] == 0.0


def test_priority_sorting_and_classification():
    assert classify_gap(0) == "Strong"
    assert classify_gap(10) == "Strong"
    assert classify_gap(11) == "Minor Gap"
    assert classify_gap(25) == "Minor Gap"
    assert classify_gap(26) == "Moderate Gap"
    assert classify_gap(50) == "Moderate Gap"
    assert classify_gap(51) == "Critical Gap"

    role = {
        "role_id": "test_role",
        "role_name": "Test Role",
        "skills": [
            {"skill_id": "a", "skill_name": "A", "required_proficiency": 80, "importance_weight": 0.5, "skill_category": "X", "is_core_skill": True},
            {"skill_id": "b", "skill_name": "B", "required_proficiency": 80, "importance_weight": 0.3, "skill_category": "X", "is_core_skill": True},
            {"skill_id": "c", "skill_name": "C", "required_proficiency": 80, "importance_weight": 0.2, "skill_category": "X", "is_core_skill": False},
        ],
    }
    # A gap 60 -> priority 0.30, B gap 40 -> 0.12, C gap 70 -> 0.14 => order A, C, B
    result = analyze_skill_gap(role=role, normalized_current_skills={"a": 20, "b": 40, "c": 10})
    names = [s["skill_name"] for s in result["skill_comparison"]]
    assert names == ["A", "C", "B"]


# -------------------- API tests --------------------

def test_api_get_roles(client):
    resp = client.get("/api/skills/roles")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "roles" in data
    assert data["count"] == len(data["roles"]) >= 6
    assert any(r["role_id"] == "backend_developer" for r in data["roles"])


def test_api_get_requirements_valid_and_invalid_role(client):
    ok = client.get("/api/skills/requirements/backend_developer")
    assert ok.status_code == 200
    data = ok.get_json()
    assert data["role_id"] == "backend_developer"
    assert data["skill_count"] == len(data["skills"]) >= 12
    assert "importance_weight" in data["skills"][0]

    bad = client.get("/api/skills/requirements/not_a_real_role")
    assert bad.status_code == 404
    err = bad.get_json()
    assert err["error"] == "Not Found"


def test_api_get_metadata(client):
    resp = client.get("/api/skills/metadata")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 33
    assert any(s["skill_name"] == "SQL" for s in data["skills"])


def test_api_analyze_success_with_missing_skill_values(client):
    payload = {
        "target_role": "backend_developer",
        "skills": {
            "Java": 75,
            "Python": 60,
            "SQL": 50,
            # other role skills omitted intentionally -> should default to 0
        },
    }
    resp = client.post("/api/skills/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["target_role"] == "backend_developer"
    assert "overall_readiness_score" in data
    assert 0 <= data["overall_readiness_score"] <= 100
    assert isinstance(data["skill_comparison"], list) and len(data["skill_comparison"]) > 0
    assert isinstance(data["top_priority_skills"], list)
    assert len(data["top_priority_skills"]) <= 5
    assert "improvement_roadmap" in data and len(data["improvement_roadmap"]) == 3
    # verify missing skill handled as 0
    dbms = next(s for s in data["skill_comparison"] if s["skill_name"] == "DBMS")
    assert dbms["current_proficiency"] == 0.0


def test_api_analyze_invalid_role(client):
    resp = client.post("/api/skills/analyze", json={"target_role": "unknown_role", "skills": {"Java": 50}})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Validation Error"
    assert any("target_role" in d.lower() or "invalid target_role" in d.lower() for d in data.get("details", []))


def test_api_analyze_proficiency_out_of_range(client):
    low = client.post("/api/skills/analyze", json={"target_role": "backend_developer", "skills": {"Java": -1}})
    high = client.post("/api/skills/analyze", json={"target_role": "backend_developer", "skills": {"Java": 101}})
    assert low.status_code == 400
    assert high.status_code == 400
    assert "details" in low.get_json()
    assert "details" in high.get_json()


def test_api_analyze_malformed_or_missing_body(client):
    no_json = client.post("/api/skills/analyze", data="not json", content_type="text/plain")
    assert no_json.status_code == 400
    missing = client.post("/api/skills/analyze", json={"skills": {"Java": 50}})
    assert missing.status_code == 400
    missing_skills = client.post("/api/skills/analyze", json={"target_role": "backend_developer"})
    assert missing_skills.status_code == 400
