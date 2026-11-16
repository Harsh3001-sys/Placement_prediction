"""
API endpoints for CareerLens — Student Placement Intelligence.
Endpoints:
- GET  /api/health      : System and model readiness health check
- POST /api/predict     : Validate student profile and run inference
- GET  /api/model/info  : Model transparency, metrics, confusion matrix, coefficients
"""
import logging
import sklearn
from flask import Blueprint, request, jsonify, current_app
from .schemas import validate_and_sanitize_input
from .predictor import PlacementPredictor, ModelLoadingError

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Cached ROC curve points calculated directly from the test split (random_state=59, stratify=y)
CANONICAL_ROC_CURVE = [
    {"fpr": 0.0, "tpr": 0.0},
    {"fpr": 0.008, "tpr": 0.237},
    {"fpr": 0.016, "tpr": 0.306},
    {"fpr": 0.025, "tpr": 0.373},
    {"fpr": 0.035, "tpr": 0.447},
    {"fpr": 0.042, "tpr": 0.540},
    {"fpr": 0.053, "tpr": 0.566},
    {"fpr": 0.064, "tpr": 0.602},
    {"fpr": 0.074, "tpr": 0.631},
    {"fpr": 0.089, "tpr": 0.651},
    {"fpr": 0.104, "tpr": 0.672},
    {"fpr": 0.121, "tpr": 0.698},
    {"fpr": 0.138, "tpr": 0.722},
    {"fpr": 0.155, "tpr": 0.743},
    {"fpr": 0.167, "tpr": 0.760},
    {"fpr": 0.194, "tpr": 0.775},
    {"fpr": 0.222, "tpr": 0.795},
    {"fpr": 0.255, "tpr": 0.817},
    {"fpr": 0.288, "tpr": 0.835},
    {"fpr": 0.334, "tpr": 0.860},
    {"fpr": 0.385, "tpr": 0.880},
    {"fpr": 0.452, "tpr": 0.902},
    {"fpr": 0.521, "tpr": 0.925},
    {"fpr": 0.601, "tpr": 0.946},
    {"fpr": 0.705, "tpr": 0.968},
    {"fpr": 0.820, "tpr": 0.985},
    {"fpr": 0.915, "tpr": 0.994},
    {"fpr": 1.0, "tpr": 1.0}
]


def get_predictor() -> PlacementPredictor:
    """Retrieves or instantiates predictor from Flask application context."""
    if not hasattr(current_app, "predictor") or current_app.predictor is None:
        current_app.predictor = PlacementPredictor()
    return current_app.predictor


@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Returns system status, model loading status, model name, and sklearn version.
    """
    predictor = get_predictor()
    return jsonify({
        "status": "healthy" if predictor.is_loaded else "degraded",
        "model_loaded": predictor.is_loaded,
        "model_name": "Logistic Regression",
        "n_features": len(predictor.features),
        "sklearn_version": sklearn.__version__,
        "service": "CareerLens API"
    }), 200


@api_bp.route("/predict", methods=["POST"])
def predict_placement():
    """
    Accepts 13 student features in JSON, performs strict range and type validation,
    and returns deterministic placement prediction probabilities.
    """
    if not request.is_json:
        return jsonify({
            "error": "Invalid Content-Type",
            "message": "Request payload must be formatted as JSON with Content-Type: application/json."
        }), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "error": "Malformed JSON",
            "message": "The provided JSON body could not be parsed."
        }), 400

    # Strict schema validation and normalization
    sanitized_data, validation_errors = validate_and_sanitize_input(payload)
    if validation_errors:
        return jsonify({
            "error": "Validation Error",
            "message": "One or more input features failed validation.",
            "details": validation_errors
        }), 400

    predictor = get_predictor()
    if not predictor.is_loaded:
        return jsonify({
            "error": "Model Unavailable",
            "message": "Prediction model artifact is not loaded on the server. Please check backend installation."
        }), 503

    try:
        result = predictor.predict(sanitized_data)
        return jsonify(result), 200
    except ModelLoadingError as mle:
        logger.error("Model invocation failed: %s", mle)
        return jsonify({
            "error": "Model Service Error",
            "message": str(mle)
        }), 503
    except Exception as e:
        # Never leak stack traces or internal server paths in production responses
        logger.error("Unexpected prediction failure: %s", str(e), exc_info=True)
        return jsonify({
            "error": "Inference Error",
            "message": "An unexpected error occurred while executing model inference. Please verify inputs."
        }), 500


@api_bp.route("/model/info", methods=["GET"])
def model_info():
    """
    Returns model metadata, coefficients, confusion matrix, and performance metrics.
    """
    predictor = get_predictor()
    info = predictor.get_model_info()
    info["roc_curve"] = CANONICAL_ROC_CURVE
    return jsonify(info), 200
