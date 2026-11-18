"""
Request validation helpers for Skill Recommendation APIs (Phase 2).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .dataset_loader import VALID_RESOURCE_DIFFICULTIES, VALID_RESOURCE_TYPES
from .skill_schemas import validate_and_normalize_analyze_request


VALID_DIFFICULTY_PREFERENCES = {"adaptive", "beginner", "intermediate", "advanced"}


def validate_resource_filters(args: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    filters: Dict[str, Any] = {}

    skill_id = args.get("skill_id")
    if skill_id is not None and str(skill_id).strip() != "":
        if not isinstance(skill_id, str):
            errors.append("skill_id must be a string")
        else:
            filters["skill_id"] = skill_id.strip().lower()

    difficulty = args.get("difficulty")
    if difficulty is not None and str(difficulty).strip() != "":
        if not isinstance(difficulty, str):
            errors.append("difficulty must be a string")
        else:
            d = difficulty.strip().title()
            if d not in VALID_RESOURCE_DIFFICULTIES:
                errors.append(f"difficulty must be one of: {sorted(VALID_RESOURCE_DIFFICULTIES)}")
            else:
                filters["difficulty"] = d

    resource_type = args.get("resource_type")
    if resource_type is not None and str(resource_type).strip() != "":
        if not isinstance(resource_type, str):
            errors.append("resource_type must be a string")
        else:
            rt = resource_type.strip()
            allowed_lower = {v.lower(): v for v in VALID_RESOURCE_TYPES}
            if rt.lower() not in allowed_lower:
                errors.append(f"resource_type must be one of: {sorted(VALID_RESOURCE_TYPES)}")
            else:
                filters["resource_type"] = allowed_lower[rt.lower()]

    provider = args.get("provider")
    if provider is not None and str(provider).strip() != "":
        if not isinstance(provider, str):
            errors.append("provider must be a string")
        else:
            filters["provider"] = provider.strip()

    free_only = args.get("free_only")
    if free_only is not None and str(free_only).strip() != "":
        if isinstance(free_only, bool):
            filters["free_only"] = free_only
        else:
            val = str(free_only).strip().lower()
            if val in {"true", "1", "yes"}:
                filters["free_only"] = True
            elif val in {"false", "0", "no"}:
                filters["free_only"] = False
            else:
                errors.append("free_only must be a boolean (true/false)")

    return filters, errors


def _validate_preferences(preferences: Any) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    normalized = {
        "free_only": False,
        "preferred_types": [],
        "difficulty_preference": "adaptive",
    }
    if preferences is None:
        return normalized, errors
    if not isinstance(preferences, dict):
        errors.append("'preferences' must be an object when provided")
        return normalized, errors

    if "free_only" in preferences:
        fo = preferences.get("free_only")
        if not isinstance(fo, bool):
            errors.append("preferences.free_only must be a boolean")
        else:
            normalized["free_only"] = fo

    if "preferred_types" in preferences:
        pts = preferences.get("preferred_types")
        if pts is None:
            normalized["preferred_types"] = []
        elif not isinstance(pts, list) or any(not isinstance(x, str) for x in pts):
            errors.append("preferences.preferred_types must be a list of strings")
        else:
            allowed_lower = {v.lower(): v for v in VALID_RESOURCE_TYPES}
            mapped = []
            seen = set()
            for x in pts:
                key = x.strip().lower()
                if not key:
                    continue
                if key not in allowed_lower:
                    errors.append(
                        f"preferences.preferred_types contains invalid value '{x}'. Allowed: {sorted(VALID_RESOURCE_TYPES)}"
                    )
                else:
                    val = allowed_lower[key]
                    if val not in seen:
                        mapped.append(val)
                        seen.add(val)
            normalized["preferred_types"] = mapped

    if "difficulty_preference" in preferences:
        dp = preferences.get("difficulty_preference")
        if dp is None or str(dp).strip() == "":
            normalized["difficulty_preference"] = "adaptive"
        elif not isinstance(dp, str):
            errors.append("preferences.difficulty_preference must be a string")
        else:
            val = dp.strip().lower()
            if val not in VALID_DIFFICULTY_PREFERENCES:
                errors.append(
                    f"preferences.difficulty_preference must be one of: {sorted(VALID_DIFFICULTY_PREFERENCES)}"
                )
            else:
                normalized["difficulty_preference"] = val

    return normalized, errors


def validate_and_normalize_recommend_request(payload: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, List[str]]:
    if not isinstance(payload, dict):
        return None, ["Request body must be a JSON object"]

    normalized_analysis, errors = validate_and_normalize_analyze_request(payload)
    if normalized_analysis is None:
        return None, errors

    preferences, pref_errors = _validate_preferences(payload.get("preferences"))
    errors.extend(pref_errors)
    if errors:
        return None, errors

    return {
        **normalized_analysis,
        "preferences": preferences,
    }, []