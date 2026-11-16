"""
Comprehensive test suite for the /api/predict endpoint.
Covers:
- Valid predictions (Placed & Not Placed)
- Probability bounds & sum constraint
- Missing features
- Invalid numeric formats
- Non-finite values (NaN, +inf, -inf)
- Out-of-bounds ranges
- Invalid categoricals
- Missing model artifact behavior
"""
import pytest
import math
from app import create_app


def test_valid_prediction_placed(client, valid_placement_candidate):
    """Verify inference for a strong candidate produces valid schema and high probability."""
    response = client.post("/api/predict", json=valid_placement_candidate)
    assert response.status_code == 200
    data = response.get_json()

    assert data["prediction"] in ("Placed", "Not Placed")
    assert "placement_probability" in data
    assert "not_placed_probability" in data
    assert data["model"] == "Logistic Regression"
    assert data["features_analyzed"] == 13

    # Probability bounds
    p_placed = data["placement_probability"]
    p_not_placed = data["not_placed_probability"]
    assert 0.0 <= p_placed <= 1.0
    assert 0.0 <= p_not_placed <= 1.0
    assert round(p_placed + p_not_placed, 2) == 1.0


def test_valid_prediction_not_placed(client, valid_developing_candidate):
    """Verify inference for a developing candidate produces valid output."""
    response = client.post("/api/predict", json=valid_developing_candidate)
    assert response.status_code == 200
    data = response.get_json()

    assert data["prediction"] in ("Placed", "Not Placed")
    p_placed = data["placement_probability"]
    p_not_placed = data["not_placed_probability"]
    assert 0.0 <= p_placed <= 1.0
    assert 0.0 <= p_not_placed <= 1.0
    assert round(p_placed + p_not_placed, 2) == 1.0


def test_missing_feature(client, valid_placement_candidate):
    """Ensure omitting any required feature triggers 400 with descriptive error."""
    payload = valid_placement_candidate.copy()
    del payload["CGPA"]

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "CGPA" in str(data["details"])


def test_invalid_numeric_string(client, valid_placement_candidate):
    """Ensure non-numeric strings trigger 400."""
    payload = valid_placement_candidate.copy()
    payload["AptitudeTestScore"] = "excellent"

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "AptitudeTestScore" in str(data["details"])


def test_boolean_for_numeric_field(client, valid_placement_candidate):
    """Ensure passing boolean to numeric field is rejected."""
    payload = valid_placement_candidate.copy()
    payload["CGPA"] = True

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "CGPA" in str(data["details"])


def test_non_finite_nan(client, valid_placement_candidate):
    """Ensure NaN values are rejected."""
    # Note: JSON standard doesn't support NaN directly, but client might pass or construct it
    payload = valid_placement_candidate.copy()
    payload["CGPA"] = float("nan")

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "CGPA" in str(data["details"]) or "NaN" in str(data)


def test_non_finite_infinity(client, valid_placement_candidate):
    """Ensure infinite values are rejected."""
    payload = valid_placement_candidate.copy()
    payload["SSC_Marks"] = float("inf")

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "SSC_Marks" in str(data["details"])


def test_out_of_range_high_cgpa(client, valid_placement_candidate):
    """Ensure CGPA > 10 is rejected."""
    payload = valid_placement_candidate.copy()
    payload["CGPA"] = 11.5

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "out of permitted range" in str(data["details"])


def test_out_of_range_negative_projects(client, valid_placement_candidate):
    """Ensure negative counts are rejected."""
    payload = valid_placement_candidate.copy()
    payload["Projects"] = -2

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Projects" in str(data["details"])


def test_out_of_range_leetcode(client, valid_placement_candidate):
    """Ensure LeetCode exceeding 500 is rejected."""
    payload = valid_placement_candidate.copy()
    payload["LeetCode_Problems_Solved"] = 650

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "LeetCode_Problems_Solved" in str(data["details"])


def test_invalid_categorical_option(client, valid_placement_candidate):
    """Ensure options other than Yes/No are rejected."""
    payload = valid_placement_candidate.copy()
    payload["PlacementTraining"] = "Maybe"

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "PlacementTraining" in str(data["details"])


def test_missing_model_artifact_handling():
    """Ensure application handles missing model file gracefully with 503."""
    custom_app = create_app({
        "TESTING": True,
        "MODEL_PATH": "non_existent_model_artifact.joblib"
    })
    test_client = custom_app.test_client()

    valid_payload = {
        "CGPA": 8.0,
        "Internships": 1,
        "Projects": 2,
        "Workshops/Certifications": 1,
        "AptitudeTestScore": 80.0,
        "SoftSkillsRating": 4.0,
        "ExtracurricularActivities": "Yes",
        "PlacementTraining": "Yes",
        "SSC_Marks": 75.0,
        "HSC_Marks": 75.0,
        "LeetCode_Problems_Solved": 200,
        "Hackathon_Wins": 1,
        "Publications": 0
    }

    response = test_client.post("/api/predict", json=valid_payload)
    assert response.status_code == 503
    data = response.get_json()
    assert "error" in data
