"""
Request/response validation helpers for Skill Gap Analysis APIs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .dataset_loader import get_role_requirements


def normalize_target_role(payload: Dict[str, Any]) -> Tuple[str | None, List[str]]:
    errors: List[str] = []
    role = payload.get("target_role")
    if role is None or str(role).strip() == "":
        errors.append("Missing required field: target_role")
        return None, errors
    if not isinstance(role, str):
        errors.append("target_role must be a string (role_id)")
        return None, errors
    return role.strip(), errors


def validate_and_normalize_analyze_request(payload: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, List[str]]:
    """
    Validate POST /api/skills/analyze payload and normalize skill inputs.

    Accepts skill keys by skill name or skill_id (case-insensitive for names/ids).
    Missing skills for the selected role default to 0.0 (handled consistently).
    Unknown skills are rejected with a validation error.
    """
    errors: List[str] = []
    if not isinstance(payload, dict):
        return None, ["Request body must be a JSON object."]

    target_role, role_errors = normalize_target_role(payload)
    errors.extend(role_errors)

    skills_input = payload.get("skills")
    if skills_input is None:
        errors.append("Missing required field: skills")
    elif not isinstance(skills_input, dict):
        errors.append("skills must be an object mapping skill names/ids to proficiency values (0-100)")
        skills_input = {}

    if errors:
        return None, errors

    try:
        role = get_role_requirements(target_role)  # type: ignore[arg-type]
    except KeyError:
        return None, [f"Invalid target_role: '{target_role}'. Use /api/skills/roles to view valid role_id values."]
    except Exception as e:
        return None, [f"Failed to load role requirements: {str(e)}"]

    # Build lookup maps for accepted keys
    name_to_name: Dict[str, str] = {}
    id_to_name: Dict[str, str] = {}
    for s in role["skills"]:
        name_to_name[s["skill_name"].strip().lower()] = s["skill_name"]
        id_to_name[s["skill_id"].strip().lower()] = s["skill_name"]

    normalized: Dict[str, float] = {}
    unknown_keys: List[str] = []

    for raw_key, raw_val in (skills_input or {}).items():
        key = str(raw_key).strip()
        key_l = key.lower()
        canonical_name = name_to_name.get(key_l) or id_to_name.get(key_l)
        if canonical_name is None:
            unknown_keys.append(str(raw_key))
            continue

        # Validate numeric proficiency
        if isinstance(raw_val, bool):
            errors.append(f"Skill '{canonical_name}' must be a numeric proficiency between 0 and 100, not a boolean.")
            continue
        try:
            val = float(raw_val)
        except Exception:
            errors.append(f"Skill '{canonical_name}' must be a numeric proficiency between 0 and 100.")
            continue
        if val != val or val in (float("inf"), float("-inf")):  # NaN/inf
            errors.append(f"Skill '{canonical_name}' must be a finite numeric proficiency between 0 and 100.")
            continue
        if val < 0 or val > 100:
            errors.append(f"Skill '{canonical_name}' proficiency must be between 0 and 100.")
            continue

        normalized[canonical_name.strip().lower()] = float(val)

    if unknown_keys:
        # keep message useful but not too noisy
        sample = ", ".join(unknown_keys[:8])
        suffix = " ..." if len(unknown_keys) > 8 else ""
        errors.append(
            f"Unknown skill(s) for role '{role['role_id']}': {sample}{suffix}. "
            "Use /api/skills/requirements/<role_id> for valid skills."
        )

    if errors:
        return None, errors

    # Missing role skills default to 0.0 consistently
    for s in role["skills"]:
        lname = s["skill_name"].strip().lower()
        normalized.setdefault(lname, 0.0)

    return {
        "role": role,
        "normalized_current_skills": normalized,
    }, []
