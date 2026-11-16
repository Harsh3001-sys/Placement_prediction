"""
CareerLens Flask Application Factory.
Configures explicit CORS origins, blueprints, and global error handlers.
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from .routes import api_bp
from .ppo_routes import ppo_bp
from .predictor import PlacementPredictor
from .ppo_predictor import PPOPredictor

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)


def create_app(test_config=None) -> Flask:
    app = Flask(__name__)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-careerlens-key-academic-only"),
        TESTING=False
    )

    if test_config:
        app.config.update(test_config)

    # CORS configuration with explicit origins (no wildcard * in production)
    allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
    if allowed_origins_env:
        origins = []
        for origin in allowed_origins_env.split(","):
            normalized = origin.strip().rstrip("/")
            if normalized:
                origins.append(normalized)
    else:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]

    CORS(
        app,
        resources={r"/api/*": {"origins": origins}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )

    # Pre-initialize predictors on startup (unless in a custom test setup)
    model_override = app.config.get("MODEL_PATH")
    features_override = app.config.get("FEATURES_PATH")
    app.predictor = PlacementPredictor(
        model_path=model_override,
        features_path=features_override
    )

    # Independent PPO predictor (separate artifacts, features, and logic)
    app.ppo_predictor = PPOPredictor(
        model_path=app.config.get("PPO_MODEL_PATH"),
        features_path=app.config.get("PPO_FEATURES_PATH"),
        metadata_path=app.config.get("PPO_METADATA_PATH"),
    )

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(ppo_bp)

    # Global Error Handlers (return JSON, never HTML or stack traces)
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "Not Found",
            "message": "The requested API endpoint does not exist."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "error": "Method Not Allowed",
            "message": "The HTTP method is not supported for this endpoint."
        }), 405

    @app.errorhandler(500)
    def internal_error(e):
        logging.error("Internal Server Error: %s", str(e))
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected server error occurred."
        }), 500

    return app
