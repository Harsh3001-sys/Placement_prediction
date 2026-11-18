"""
Tests for CareerLens Student Segmentation (Phase 3).

Covers dataset loading, role feature selection, preprocessing/scaling,
K evaluation and selection, cluster interpretation/assignment, prediction,
invalid inputs/missing models, API success/failure, and Phase 1/2 integration.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.student_segmentation.cluster_analyzer import analyze_role_clusters
from app.student_segmentation.clustering import evaluate_k_candidates, select_k, train_role_segmentation
from app.student_segmentation.preprocessing import (
    build_feature_vector,
    get_role_feature_config,
    load_role_dataset,
    validate_role_sample_size,
)


def _all_role_ids() -> list[str]:
    return [
        "software_developer",
        "backend_developer",
        "frontend_developer",
        "full_stack_developer",
        "data_analyst",
        "ml_engineer",
    ]


def test_dataset_loading_and_role_feature_selection():
    for role_id in _all_role_ids():
        cfg = get_role_feature_config(role_id)
        assert cfg["role_id"] == role_id
        assert cfg["n_features"] == len(cfg["feature_names"])
        assert cfg["n_features"] >= 10
        assert len(cfg["feature_skill_ids"]) == len(cfg["feature_names"])

        data = load_role_dataset(role_id)
        assert data.role_id == role_id
        assert data.X.shape[0] > 0
        assert data.X.shape[1] == len(data.feature_names)
        assert data.feature_names == cfg["feature_names"]
        assert data.feature_skill_ids == cfg["feature_skill_ids"]
        assert data.summary["duplicate_student_ids"] == 0
        assert data.summary["missing_or_non_numeric_cells_imputed"] == 0

    # student profiles dataset should include 1000 rows across roles
    total = sum(load_role_dataset(r).X.shape[0] for r in _all_role_ids())
    assert total == 1000


def test_preprocessing_scaling_and_feature_vector():
    data = load_role_dataset("frontend_developer")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data.X)
    assert X_scaled.shape == data.X.shape
    # standardized features should have ~0 mean and ~1 std
    assert np.allclose(X_scaled.mean(axis=0), 0.0, atol=1e-7)
    assert np.allclose(X_scaled.std(axis=0), 1.0, atol=1e-7)

    # build ordered feature vector from partial normalized skills
    partial = {
        data.feature_names[0].strip().lower(): 75.0,
        data.feature_names[1].strip().lower(): 40.0,
    }
    vec = build_feature_vector(partial, data.feature_names)
    assert vec.shape == (1, len(data.feature_names))
    assert float(vec[0, 0]) == 75.0
    assert float(vec[0, 1]) == 40.0
    # missing skills default to 0
    assert float(vec[0, 2]) == 0.0


def test_k_evaluation_and_defensible_selection():
    data = load_role_dataset("frontend_developer")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data.X)
    candidates = evaluate_k_candidates(X_scaled, list(range(2, 6)), random_state=42)
    assert len(candidates) == 4
    for c in candidates:
        assert "k" in c and "wcss" in c
        assert "silhouette_score" in c and "davies_bouldin_score" in c and "calinski_harabasz_score" in c
        assert c["wcss"] > 0

    sel = select_k(candidates)
    assert sel.selected_k in [2, 3, 4, 5]
    assert sel.selection["strategy"]
    assert "rationale" in sel.selection
    assert sel.selection["metric_leaders"]["best_silhouette_k"] in [2, 3, 4, 5]


def test_train_role_segmentation_cluster_analysis_and_predict(tmp_path):
    data = load_role_dataset("frontend_developer")
    ok, msg = validate_role_sample_size(data.role_id, int(data.X.shape[0]), k_min=2, k_max=8)
    assert ok, msg

    result = train_role_segmentation(data, k_min=2, k_max=8, random_state=42)
    model = result["model"]
    scaler = result["scaler"]
    labels = result["labels"]
    meta = result["metadata"]

    assert isinstance(model, KMeans)
    assert isinstance(scaler, StandardScaler)
    assert len(labels) == data.X.shape[0]
    assert meta["selected_k"] == int(model.n_clusters)
    assert meta["random_state"] == 42
    assert meta["n_init"] == 10
    assert meta["n_features"] == len(data.feature_names)
    assert "final_metrics" in meta and "candidate_metrics" in meta

    # interpretation is dynamic from centroids/requirements
    role_cfg = get_role_feature_config("frontend_developer")
    analysis = analyze_role_clusters(
        role_id="frontend_developer",
        role_name=role_cfg["role_name"],
        feature_names=data.feature_names,
        X_original=data.X,
        labels=np.array(labels),
        requirements=role_cfg["skills"],
    )
    assert analysis["n_students"] == data.X.shape[0]
    assert len(analysis["clusters"]) == meta["selected_k"]
    total_pct = sum(c["student_percentage"] for c in analysis["clusters"])
    assert abs(total_pct - 100.0) < 0.5
    for c in analysis["clusters"]:
        assert c["cluster_name"]
        assert c["cluster_description"]
        assert isinstance(c["average_proficiency_per_skill"], dict)
        assert len(c["average_proficiency_per_skill"]) == len(data.feature_names)
        assert len(c["strongest_skills"]) >= 1
        assert len(c["weakest_skills"]) >= 1

    # prediction uses persisted artifacts (no retraining)
    model_path = tmp_path / "model.joblib"
    scaler_path = tmp_path / "scaler.joblib"
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    loaded_model = joblib.load(model_path)
    loaded_scaler = joblib.load(scaler_path)

    sample = {name.strip().lower(): float(val) for name, val in zip(data.feature_names, data.X[0])}
    vec = build_feature_vector(sample, data.feature_names)
    pred = loaded_model.predict(loaded_scaler.transform(vec))
    assert int(pred[0]) in set(int(x) for x in labels)


def test_segmentation_api_endpoints_success(client):
    # roles
    resp = client.get("/api/segmentation/roles")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] >= 1
    role_ids = {r["role_id"] for r in body["roles"]}
    assert "frontend_developer" in role_ids

    role_id = "frontend_developer"

    ov = client.get(f"/api/segmentation/overview/{role_id}")
    assert ov.status_code == 200
    ovb = ov.get_json()
    assert ovb["role_id"] == role_id
    assert ovb["students_analyzed"] > 0
    assert ovb["n_clusters"] >= 2
    assert "clustering_evaluation_metrics" in ovb
    assert len(ovb.get("cluster_distribution", [])) == ovb["n_clusters"]

    cl = client.get(f"/api/segmentation/clusters/{role_id}")
    assert cl.status_code == 200
    clb = cl.get_json()
    assert clb["role_id"] == role_id
    assert len(clb["clusters"]) == clb["selected_k"]
    for c in clb["clusters"]:
        assert c["cluster_name"]
        assert c["cluster_description"]
        assert "average_proficiency_per_skill" in c

    mi = client.get(f"/api/segmentation/model-info/{role_id}")
    assert mi.status_code == 200
    mib = mi.get_json()
    assert mib["model_type"] == "KMeans"
    assert mib["feature_count"] == len(mib.get("feature_names", []))
    assert "evaluation_metrics" in mib


def test_segmentation_predict_and_phase1_phase2_integration(client):
    role_id = "frontend_developer"
    req_resp = client.get(f"/api/skills/requirements/{role_id}")
    assert req_resp.status_code == 200
    skills = req_resp.get_json()["skills"]
    # Build a valid payload with role-relevant skills
    payload_skills = {}
    for s in skills:
        payload_skills[s["skill_name"]] = max(0, min(100, int(s["required_proficiency"]) - 10))

    resp = client.post(
        "/api/segmentation/predict",
        data=json.dumps({"target_role": role_id, "skills": payload_skills}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["target_role"] == role_id
    assert "predicted_cluster_id" in body
    assert body["cluster_name"]
    assert body["cluster_description"]
    assert isinstance(body.get("comparison_with_cluster"), list)
    assert len(body["comparison_with_cluster"]) == len(skills)

    # Phase 1 integration (personal gaps)
    psg = body.get("personal_skill_gaps") or {}
    assert "overall_readiness_score" in psg
    assert "top_priority_skills" in psg

    # Phase 2 integration (recommendation engine/dataset reuse, separated insights)
    assert "recommendations_based_on_individual_gaps" in body
    assert "recommendations_based_on_cluster_patterns" in body
    notes = body.get("integration_notes") or {}
    assert "Phase 1" in notes.get("phase1", "") or "phase 1" in notes.get("phase1", "").lower()
    assert "Phase 2" in notes.get("phase2", "") or "phase 2" in notes.get("phase2", "").lower()
    assert "personal" in notes.get("distinction", "").lower()
    assert "cluster" in notes.get("distinction", "").lower()


def test_segmentation_predict_validation_and_missing_artifacts(client, app):
    # invalid role
    resp = client.post(
        "/api/segmentation/predict",
        data=json.dumps({"target_role": "not_a_role", "skills": {"Python": 50}}),
        content_type="application/json",
    )
    assert resp.status_code in (400, 404)

    # missing skills field
    resp = client.post(
        "/api/segmentation/predict",
        data=json.dumps({"target_role": "frontend_developer"}),
        content_type="application/json",
    )
    assert resp.status_code == 400

    # unknown skill for role
    resp = client.post(
        "/api/segmentation/predict",
        data=json.dumps({"target_role": "frontend_developer", "skills": {"Underwater Basket Weaving": 50}}),
        content_type="application/json",
    )
    assert resp.status_code == 400

    # out-of-range skill value
    valid_req = client.get("/api/skills/requirements/frontend_developer").get_json()["skills"][0]["skill_name"]
    resp = client.post(
        "/api/segmentation/predict",
        data=json.dumps({"target_role": "frontend_developer", "skills": {valid_req: 150}}),
        content_type="application/json",
    )
    assert resp.status_code == 400

    # simulate missing artifacts by temporarily hiding a role artifact directory
    from app.student_segmentation import model_loader

    role_id = "ml_engineer"
    art_dir = Path(model_loader.role_artifact_dir(role_id))
    temp_dir = art_dir.parent / f"_{role_id}_hidden_for_test"
    moved = False
    if art_dir.exists():
        art_dir.rename(temp_dir)
        moved = True
    try:
        resp = client.get(f"/api/segmentation/overview/{role_id}")
        assert resp.status_code == 404
        resp = client.post(
            "/api/segmentation/predict",
            data=json.dumps({"target_role": role_id, "skills": {s["skill_name"]: 50 for s in client.get(f"/api/skills/requirements/{role_id}").get_json()["skills"]}}),
            content_type="application/json",
        )
        assert resp.status_code == 404
    finally:
        if moved and temp_dir.exists():
            temp_dir.rename(art_dir)
