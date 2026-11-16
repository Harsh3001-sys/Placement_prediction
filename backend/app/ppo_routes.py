"""
Independent PPO API endpoints.
"""
import logging
from flask import Blueprint, current_app, jsonify, request

from .ppo_predictor import PPOPredictor, PPOModelLoadingError
from .ppo_schemas import validate_and_sanitize_ppo_input, PPO_FEATURE_DEFINITIONS

logger = logging.getLogger(__name__)

ppo_bp = Blueprint("ppo_api", __name__, url_prefix="/api/ppo")


def get_ppo_predictor() -> PPOPredictor:
    if not hasattr(current_app, "ppo_predictor") or current_app.ppo_predictor is None:
        current_app.ppo_predictor = PPOPredictor()
    return current_app.ppo_predictor


@ppo_bp.route("/health", methods=["GET"])
def ppo_health():
    predictor = get_ppo_predictor()
    return jsonify({
        "status": "healthy" if predictor.is_loaded else "degraded",
        "model_loaded": predictor.is_loaded,
        "model": "ppo_prediction",
        "n_features": len(predictor.features),
        "threshold": predictor.threshold,
        "load_error": predictor.load_error if not predictor.is_loaded else None,
    }), 200


@ppo_bp.route("/predict", methods=["POST"])
def ppo_predict():
    if not request.is_json:
        return jsonify({
            "error": "Invalid Content-Type",
            "message": "Request payload must be formatted as JSON with Content-Type: application/json.",
        }), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "error": "Malformed JSON",
            "message": "The provided JSON body could not be parsed.",
        }), 400

    sanitized, errors = validate_and_sanitize_ppo_input(payload)
    if errors:
        return jsonify({
            "error": "Validation Error",
            "message": "One or more input features failed validation.",
            "details": errors,
        }), 400

    predictor = get_ppo_predictor()
    if not predictor.is_loaded:
        return jsonify({
            "error": "Model Unavailable",
            "message": "PPO prediction model is not loaded on the server. Please check backend artifacts.",
        }), 503

    try:
        result = predictor.predict(sanitized)
        return jsonify(result), 200
    except PPOModelLoadingError as e:
        logger.error("PPO model invocation failed: %s", e)
        return jsonify({
            "error": "Model Service Error",
            "message": str(e),
        }), 503
    except Exception as e:
        logger.error("Unexpected PPO prediction failure: %s", e, exc_info=True)
        return jsonify({
            "error": "Inference Error",
            "message": "An unexpected error occurred while executing PPO model inference. Please verify inputs.",
        }), 500


@ppo_bp.route("/info", methods=["GET"])
def ppo_info():
    predictor = get_ppo_predictor()
    info = predictor.get_info()
    info["feature_definitions"] = PPO_FEATURE_DEFINITIONS
    return jsonify(info), 200
