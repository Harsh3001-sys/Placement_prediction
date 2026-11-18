"""
Validation helpers for Student Segmentation APIs (Phase 3).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.skill_gap.dataset_loader import get_role_requirements
from app.skill_gap.skill_schemas import normalize_target_role


def normalize_segmentation_role(role_id: str) -> str:
    return str(role_id).strip()


def validate_predict_request(payload: Any) -> Tuple[Dict[str, Any] | None, List[str]]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return None, ["Request body must be a JSON object."]

    target_role, role_errors = normalize_target_role(payload)
    errors.extend(role_errors)
    if target_role is None:
        return None, errors

    # Validate role exists in Phase 1 mappings
    try:
        role = get_role_requirements(target_role)
    except Exception:
        errors.append(f"Invalid target_role '{target_role}'. Use a valid role_id from Phase 1 role mappings.")
        return None, errors

    skills_input = payload.get("skills")
    if skills_input is None:
        errors.append("Missing required field: skills")
        return None, errors
    if not isinstance(skills_input, dict):
        errors.append("'skills' must be an object mapping skill names/ids to proficiency values (0-100)")
        return None, errors

    # Build lookup for role-relevant skills (names and ids)
    requirements = role.get("skills", [])
    by_name = {str(s["skill_name"]).strip().lower(): s for s in requirements}
    by_id = {str(s["skill_id"]).strip().lower(): s for s in requirements}

    normalized: Dict[str, float] = {}
    for key, value in skills_input.items():
        if not isinstance(key, str) or not key.strip():
            errors.append("Skill keys must be non-empty strings")
            continue
        k = key.strip().lower()
        match = by_name.get(k) or by_id.get(k)
        if match is None:
            errors.append(
                f"Unknown skill '{key}' for role '{role.get('role_name', target_role)}'. "
                "Provide only skills relevant to the selected role."
            )
            continue
        if isinstance(value, bool) or value is None:
            errors.append(f"Skill '{match['skill_name']}' must be a numeric value between 0 and 100")
            continue
        try:
            num = float(value)
        except (TypeError, ValueError):
            errors.append(f"Skill '{match['skill_name']}' must be a numeric value between 0 and 100")
            continue
        if num < 0 or num > 100:
            errors.append(f"Skill '{match['skill_name']}' must be between 0 and 100 (received {value})")
            continue
        # If duplicates provided via name/id, keep last but values must be valid; prefer canonical name key
        normalized[str(match["skill_name"]).strip().lower()] = float(num)

    if errors:
        return None, errors

    # Fill missing role-relevant skills with 0.0 for a complete feature vector
    for req in requirements:
        lname = str(req["skill_name"]).strip().lower()
        normalized.setdefault(lname, 0.0)

    return {
        "target_role": str(role.get("role_id")),
        "role_name": str(role.get("role_name")),
        "skills_normalized": normalized,
        "requirements": requirements,
    }, []
