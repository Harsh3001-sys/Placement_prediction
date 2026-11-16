"""
Tests for CareerLens Health Check and Model Information endpoints.
"""
import pytest


def test_health_endpoint_healthy(client):
    """Ensure GET /api/health returns 200 with model status and metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()

    assert data["status"] in ("healthy", "degraded")
    assert "model_loaded" in data
    assert data["model_loaded"] is True
    assert data["model_name"] == "Logistic Regression"
    assert data["n_features"] == 13
    assert "sklearn_version" in data
    assert data["service"] == "CareerLens API"


def test_model_info_endpoint(client):
    """Ensure GET /api/model/info returns full model transparency metadata."""
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.get_json()

    assert data["model_name"] == "Logistic Regression"
    assert data["is_loaded"] is True
    assert len(data["features"]) == 13
    assert "coefficients" in data
    assert "intercept" in data
    assert "evaluation" in data

    # Verify canonical evaluation metrics
    eval_data = data["evaluation"]
    assert eval_data["test_accuracy"] == 0.8085
    assert eval_data["precision"] == 0.7701
    assert eval_data["recall"] == 0.7747
    assert eval_data["f1_score"] == 0.7724
    assert eval_data["roc_auc"] == 0.8840

    # Verify confusion matrix
    cm = eval_data["confusion_matrix"]
    assert cm["true_negative"] == 967
    assert cm["false_positive"] == 194
    assert cm["false_negative"] == 189
    assert cm["true_positive"] == 650

    # Verify synthetic features disclosure
    assert "synthetic_features" in eval_data
    assert len(eval_data["synthetic_features"]) == 3
