"""
Schema validation for PPO Prediction inputs.
Independent from placement schemas.
"""
from typing import Any, Dict, List, Tuple
import math

PPO_FEATURE_DEFINITIONS = {
    "Technical_Evaluation": {
        "type": "float",
        "min": 1.0,
        "max": 10.0,
        "label": "Technical Evaluation",
        "description": "Technical evaluation score (1.0 to 10.0)",
    },
    "Task_Completion_Rate": {
        "type": "float",
        "min": 20.0,
        "max": 100.0,
        "label": "Task Completion Rate",
        "description": "Percentage of assigned tasks completed (20.0 to 100.0)",
    },
    "Attendance_Rate": {
        "type": "float",
        "min": 51.5,
        "max": 100.0,
        "label": "Attendance Rate",
        "description": "Internship attendance percentage (51.5 to 100.0)",
    },
    "Communication_Score": {
        "type": "float",
        "min": 3.6,
        "max": 10.0,
        "label": "Communication Score",
        "description": "Communication effectiveness score (3.6 to 10.0)",
    },
    "Manager_Rating": {
        "type": "float",
        "min": 1.4,
        "max": 10.0,
        "label": "Manager Rating",
        "description": "Manager performance rating (1.4 to 10.0)",
    },
    "Code_Quality_Score": {
        "type": "float",
        "min": 1.0,
        "max": 10.0,
        "label": "Code Quality Score",
        "description": "Code quality assessment score (1.0 to 10.0)",
    },
    "Teamwork_Score": {
        "type": "float",
        "min": 3.5,
        "max": 10.0,
        "label": "Teamwork Score",
        "description": "Team collaboration score (3.5 to 10.0)",
    },
    "Deadline_Adherence": {
        "type": "float",
        "min": 20.0,
        "max": 100.0,
        "label": "Deadline Adherence",
        "description": "Percentage of deadlines met (20.0 to 100.0)",
    },
}

PPO_REQUIRED_FEATURES = list(PPO_FEATURE_DEFINITIONS.keys())


def validate_and_sanitize_ppo_input(data: Any) -> Tuple[Dict[str, float], List[str]]:
    """Validate PPO request payload. Returns (sanitized, errors)."""
    errors: List[str] = []

    if not isinstance(data, dict):
        return {}, ["Request body must be a valid JSON object."]

    missing = [f for f in PPO_REQUIRED_FEATURES if f not in data]
    if missing:
        errors.append(f"Missing required features: {', '.join(missing)}")
        return {}, errors

    sanitized: Dict[str, float] = {}

    for name, rules in PPO_FEATURE_DEFINITIONS.items():
        val = data.get(name)

        if val is None:
            errors.append(f"Feature '{name}' cannot be null or empty.")
            continue

        if isinstance(val, bool):
            errors.append(f"Feature '{name}' must be a number, not a boolean.")
            continue

        try:
            numeric = float(val)
        except (ValueError, TypeError):
            errors.append(f"Feature '{name}' must be a valid numeric value.")
            continue

        if not math.isfinite(numeric):
            errors.append(f"Feature '{name}' must be a finite number (received NaN or Infinity).")
            continue

        min_v = float(rules["min"])
        max_v = float(rules["max"])
        if numeric < min_v or numeric > max_v:
            errors.append(
                f"Feature '{name}' value {numeric} is out of permitted range [{min_v}, {max_v}]."
            )
            continue

        sanitized[name] = round(float(numeric), 4)

    return sanitized, errors
