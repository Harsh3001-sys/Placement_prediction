"""
CareerLens API Server Entry Point.
Runs the Flask application with proper environment settings.
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    print(f"===========================================================")
    print(f" CareerLens API starting on http://127.0.0.1:{port}")
    print(f" Placement Model Loaded: {app.predictor.is_loaded}")
    print(f" Placement Features configured: {len(app.predictor.features)}")
    print(f" PPO Model Loaded: {getattr(app, 'ppo_predictor', None) and app.ppo_predictor.is_loaded}")
    if getattr(app, 'ppo_predictor', None):
        print(f" PPO Features configured: {len(app.ppo_predictor.features)}")
    print(f"===========================================================")
    app.run(host="0.0.0.0", port=port, debug=debug)
