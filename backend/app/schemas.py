"""
Schema validation and data sanitization for Student Placement Prediction.
Provides strict checking for missing fields, non-numeric values, non-finite values (NaN/inf),
and domain-specific boundary constraints.
"""
from typing import Dict, Any, Tuple, List
import math

FEATURE_DEFINITIONS = {
    "CGPA": {
        "type": "float",
        "min": 0.0,
        "max": 10.0,
        "label": "CGPA",
        "description": "Cumulative Grade Point Average (0.0 to 10.0)"
    },
    "Internships": {
        "type": "int",
        "min": 0,
        "max": 10,
        "label": "Internships",
        "description": "Number of completed internships (0 to 10)"
    },
    "Projects": {
        "type": "int",
        "min": 0,
        "max": 15,
        "label": "Projects",
        "description": "Number of completed academic or personal projects (0 to 15)"
    },
    "Workshops/Certifications": {
        "type": "int",
        "min": 0,
        "max": 15,
        "label": "Workshops / Certifications",
        "description": "Number of workshops and certifications earned (0 to 15)"
    },
    "AptitudeTestScore": {
        "type": "float",
        "min": 0.0,
        "max": 100.0,
        "label": "Aptitude Test Score",
        "description": "General aptitude evaluation score (0.0 to 100.0)"
    },
    "SoftSkillsRating": {
        "type": "float",
        "min": 0.0,
        "max": 5.0,
        "label": "Soft Skills Rating",
        "description": "Behavioral and soft skills evaluation rating (0.0 to 5.0)"
    },
    "ExtracurricularActivities": {
        "type": "boolean_str",
        "allowed": ["Yes", "No"],
        "label": "Extracurricular Activities",
        "description": "Active participation in clubs, sports, or cultural bodies ('Yes' or 'No')"
    },
    "PlacementTraining": {
        "type": "boolean_str",
        "allowed": ["Yes", "No"],
        "label": "Placement Training",
        "description": "Enrolled in structured campus placement preparation ('Yes' or 'No')"
    },
    "SSC_Marks": {
        "type": "float",
        "min": 0.0,
        "max": 100.0,
        "label": "SSC Marks (10th Standard)",
        "description": "Secondary school percentage (0.0 to 100.0)"
    },
    "HSC_Marks": {
        "type": "float",
        "min": 0.0,
        "max": 100.0,
        "label": "HSC Marks (12th Standard)",
        "description": "Higher secondary percentage (0.0 to 100.0)"
    },
    "LeetCode_Problems_Solved": {
        "type": "int",
        "min": 0,
        "max": 500,
        "label": "LeetCode Problems Solved",
        "description": "Competitive programming problems solved (0 to 500)"
    },
    "Hackathon_Wins": {
        "type": "int",
        "min": 0,
        "max": 5,
        "label": "Hackathon Wins",
        "description": "Podium placements in competitive hackathons (0 to 5)"
    },
    "Publications": {
        "type": "int",
        "min": 0,
        "max": 4,
        "label": "Research Publications",
        "description": "Peer-reviewed conference or journal papers (0 to 4)"
    }
}

REQUIRED_FEATURES = list(FEATURE_DEFINITIONS.keys())


class ValidationError(Exception):
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or [message]


def validate_and_sanitize_input(data: Any) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validates input dictionary against exact required features and ranges.
    Returns:
        (sanitized_data, errors_list)
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return {}, ["Request body must be a valid JSON object."]

    # Check for missing features
    missing_features = [f for f in REQUIRED_FEATURES if f not in data]
    if missing_features:
        errors.append(f"Missing required features: {', '.join(missing_features)}")
        return {}, errors

    sanitized: Dict[str, Any] = {}

    for feature_name, rules in FEATURE_DEFINITIONS.items():
        val = data.get(feature_name)

        if val is None:
            errors.append(f"Feature '{feature_name}' cannot be null or empty.")
            continue

        f_type = rules["type"]

        if f_type == "boolean_str":
            if isinstance(val, bool):
                val_str = "Yes" if val else "No"
            elif isinstance(val, (int, float)):
                if val == 1:
                    val_str = "Yes"
                elif val == 0:
                    val_str = "No"
                else:
                    errors.append(
                        f"Feature '{feature_name}' must be 'Yes' or 'No' (or 1/0)."
                    )
                    continue
            elif isinstance(val, str):
                val_str = val.strip().capitalize()
            else:
                errors.append(f"Feature '{feature_name}' must be 'Yes' or 'No'.")
                continue

            if val_str not in rules["allowed"]:
                errors.append(
                    f"Feature '{feature_name}' must be one of: {', '.join(rules['allowed'])}. Received: '{val}'"
                )
                continue

            # Model expects 1 for Yes, 0 for No
            sanitized[feature_name] = 1 if val_str == "Yes" else 0

        elif f_type in ("float", "int"):
            # Check for non-numeric types (e.g. booleans are ints in Python, so exclude bool)
            if isinstance(val, bool):
                errors.append(f"Feature '{feature_name}' must be a number, not a boolean.")
                continue

            try:
                numeric_val = float(val)
            except (ValueError, TypeError):
                errors.append(f"Feature '{feature_name}' must be a valid numeric value.")
                continue

            # Non-finite check (NaN, +inf, -inf)
            if not math.isfinite(numeric_val):
                errors.append(f"Feature '{feature_name}' must be a finite number (received NaN or Infinity).")
                continue

            min_val = rules["min"]
            max_val = rules["max"]

            if numeric_val < min_val or numeric_val > max_val:
                errors.append(
                    f"Feature '{feature_name}' value {numeric_val} is out of permitted range [{min_val}, {max_val}]."
                )
                continue

            if f_type == "int":
                # Ensure it represents an integer (or allow minor float like 2.0)
                if not float(numeric_val).is_integer():
                    errors.append(f"Feature '{feature_name}' must be a whole non-negative integer.")
                    continue
                sanitized[feature_name] = int(numeric_val)
            else:
                sanitized[feature_name] = round(float(numeric_val), 4)

    return sanitized, errors
