"""
Dataset loading and validation utilities for the Skill Gap Analysis feature.

Loads datasets from backend/datasets:
- role_skill_requirements.csv (synthetic, illustrative)
- skill_metadata.csv (synthetic, illustrative)
- student_skill_profiles.csv (synthetic, illustrative; available for testing/demo)
- learning_resources.csv (curated genuine learning resources; Phase 2)

Skill-gap datasets are synthetic and for demonstration/testing only.
Learning resources are curated genuine resources (not synthetic) with verified URLs.
"""

from __future__ import annotations

import csv
import logging
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATASETS_DIR = Path(__file__).resolve().parents[2] / "datasets"
ROLE_REQUIREMENTS_CSV = DATASETS_DIR / "role_skill_requirements.csv"
SKILL_METADATA_CSV = DATASETS_DIR / "skill_metadata.csv"
STUDENT_PROFILES_CSV = DATASETS_DIR / "student_skill_profiles.csv"
LEARNING_RESOURCES_CSV = DATASETS_DIR / "learning_resources.csv"

VALID_RESOURCE_TYPES = {
    "Documentation",
    "Video Course",
    "Interactive Tutorial",
    "Practice Platform",
    "Project Tutorial",
    "Course",
    "Book or Reading Material",
}
VALID_RESOURCE_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}


class SkillDatasetError(RuntimeError):
    """Raised when skill-gap datasets are missing or invalid."""


def _read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise SkillDatasetError(f"Required dataset not found: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise SkillDatasetError(f"Dataset has no header: {path}")
            rows = [dict(row) for row in reader]
    except SkillDatasetError:
        raise
    except Exception as e:
        raise SkillDatasetError(f"Failed to read dataset {path}: {e}") from e
    if not rows:
        raise SkillDatasetError(f"Dataset is empty: {path}")
    return rows


def _to_bool(value: Any) -> bool:
    s = str(value).strip().lower()
    return s in {"1", "true", "yes", "y"}


def _validate_role_requirement_rows(rows: List[Dict[str, str]]) -> None:
    required_cols = {
        "role_id",
        "role_name",
        "skill_id",
        "skill_name",
        "required_proficiency",
        "importance_weight",
        "skill_category",
        "is_core_skill",
    }
    seen = set()
    sums: Dict[str, float] = {}
    for i, row in enumerate(rows, start=2):
        missing = [c for c in required_cols if c not in row or str(row.get(c, "")).strip() == ""]
        if missing:
            raise SkillDatasetError(f"role_skill_requirements.csv row {i} missing values: {missing}")
        key = (row["role_id"].strip(), row["skill_id"].strip())
        if key in seen:
            raise SkillDatasetError(f"Duplicate role-skill mapping in role_skill_requirements.csv: {key}")
        seen.add(key)
        try:
            req = float(row["required_proficiency"])
            weight = float(row["importance_weight"])
        except Exception as e:
            raise SkillDatasetError(f"Invalid numeric value in role_skill_requirements.csv row {i}: {e}") from e
        if not (0.0 <= req <= 100.0):
            raise SkillDatasetError(f"required_proficiency out of range in row {i}: {req}")
        if weight <= 0:
            raise SkillDatasetError(f"importance_weight must be positive in row {i}: {weight}")
        role_id = row["role_id"].strip()
        sums[role_id] = sums.get(role_id, 0.0) + weight
    for role_id, total in sums.items():
        if abs(total - 1.0) > 1e-6:
            raise SkillDatasetError(f"Importance weights for role '{role_id}' must sum to 1.0 (got {total})")


def _validate_metadata_rows(rows: List[Dict[str, str]]) -> None:
    required_cols = {
        "skill_id",
        "skill_name",
        "skill_category",
        "description",
        "beginner_description",
        "intermediate_description",
        "advanced_description",
    }
    seen = set()
    for i, row in enumerate(rows, start=2):
        missing = [c for c in required_cols if c not in row or str(row.get(c, "")).strip() == ""]
        if missing:
            raise SkillDatasetError(f"skill_metadata.csv row {i} missing values: {missing}")
        sid = row["skill_id"].strip()
        if sid in seen:
            raise SkillDatasetError(f"Duplicate skill_id in skill_metadata.csv: {sid}")
        seen.add(sid)


@lru_cache(maxsize=1)
def load_role_requirements() -> List[Dict[str, Any]]:
    rows = _read_csv(ROLE_REQUIREMENTS_CSV)
    _validate_role_requirement_rows(rows)
    parsed: List[Dict[str, Any]] = []
    for row in rows:
        parsed.append(
            {
                "role_id": row["role_id"].strip(),
                "role_name": row["role_name"].strip(),
                "skill_id": row["skill_id"].strip(),
                "skill_name": row["skill_name"].strip(),
                "required_proficiency": float(row["required_proficiency"]),
                "importance_weight": float(row["importance_weight"]),
                "skill_category": row["skill_category"].strip(),
                "is_core_skill": _to_bool(row["is_core_skill"]),
            }
        )
    return parsed


@lru_cache(maxsize=1)
def load_skill_metadata() -> List[Dict[str, Any]]:
    rows = _read_csv(SKILL_METADATA_CSV)
    _validate_metadata_rows(rows)
    return [{k: str(v).strip() for k, v in row.items()} for row in rows]


def clear_cache() -> None:
    load_role_requirements.cache_clear()
    load_skill_metadata.cache_clear()


def get_roles() -> List[Dict[str, Any]]:
    reqs = load_role_requirements()
    roles: Dict[str, Dict[str, Any]] = {}
    for r in reqs:
        rid = r["role_id"]
        if rid not in roles:
            roles[rid] = {
                "role_id": rid,
                "role_name": r["role_name"],
                "skill_count": 0,
                "core_skill_count": 0,
            }
        roles[rid]["skill_count"] += 1
        if r["is_core_skill"]:
            roles[rid]["core_skill_count"] += 1

    # stable order by role_name for UI
    return sorted(roles.values(), key=lambda x: x["role_name"])


def role_exists(role_id: str) -> bool:
    rid = str(role_id or "").strip()
    return any(r["role_id"] == rid for r in get_roles())


def get_role_requirements(role_id: str) -> Dict[str, Any]:
    rid = str(role_id or "").strip()
    reqs = [r for r in load_role_requirements() if r["role_id"] == rid]
    if not reqs:
        raise KeyError(f"Unknown target role: {role_id}")

    role_name = reqs[0]["role_name"]
    skills = sorted(
        [
            {
                "skill_id": r["skill_id"],
                "skill_name": r["skill_name"],
                "required_proficiency": round(float(r["required_proficiency"]), 2),
                "importance_weight": round(float(r["importance_weight"]), 6),
                "skill_category": r["skill_category"],
                "is_core_skill": bool(r["is_core_skill"]),
            }
            for r in reqs
        ],
        key=lambda x: (-x["importance_weight"], -x["required_proficiency"], x["skill_name"]),
    )

    return {
        "role_id": rid,
        "role_name": role_name,
        "skill_count": len(skills),
        "skills": skills,
    }


def get_metadata() -> List[Dict[str, Any]]:
    return load_skill_metadata()


def get_skill_metadata_index() -> Dict[str, Dict[str, Any]]:
    """Index metadata by skill_id and lowercased skill_name for easy lookup."""
    index: Dict[str, Dict[str, Any]] = {}
    for item in load_skill_metadata():
        index[item["skill_id"]] = item
        index[item["skill_name"].strip().lower()] = item
    return index


def try_load_student_profiles_count() -> Optional[int]:
    """Best-effort count for validation/reporting; profiles are not required by APIs."""
    try:
        rows = _read_csv(STUDENT_PROFILES_CSV)
        return len(rows)
    except Exception:
        return None

# -------------------- Learning resources (Phase 2) --------------------


def _to_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes"}


@lru_cache(maxsize=1)
def _load_learning_resources_cached():
    rows = _read_csv(LEARNING_RESOURCES_CSV)
    required = {
        "resource_id",
        "resource_title",
        "skill_id",
        "skill_name",
        "provider",
        "resource_type",
        "difficulty_level",
        "description",
        "resource_url",
        "estimated_hours",
        "prerequisites",
        "is_free",
        "language",
        "quality_score",
        "tags",
    }
    if not rows:
        raise SkillDatasetError(f"Learning resources dataset is empty: {LEARNING_RESOURCES_CSV.name}")
    if not required.issubset(rows[0].keys()):
        raise SkillDatasetError(
            f"Learning resources dataset missing required columns: {sorted(required - set(rows[0].keys()))}"
        )

    valid_skill_ids = set(get_skill_metadata_index().keys())
    seen_ids = set()
    seen_urls = set()
    out = []

    for idx, row in enumerate(rows, start=2):
        rid = str(row.get("resource_id", "")).strip()
        sid = str(row.get("skill_id", "")).strip()
        url = str(row.get("resource_url", "")).strip()
        rtype = str(row.get("resource_type", "")).strip()
        diff = str(row.get("difficulty_level", "")).strip()
        if not rid:
            raise SkillDatasetError(f"Learning resources row {idx} missing resource_id")
        if rid in seen_ids:
            raise SkillDatasetError(f"Duplicate resource_id in learning resources: {rid}")
        if url in seen_urls:
            raise SkillDatasetError(f"Duplicate resource_url in learning resources: {url}")
        if sid not in valid_skill_ids:
            raise SkillDatasetError(f"Learning resource {rid} has invalid skill_id: {sid}")
        if rtype not in VALID_RESOURCE_TYPES:
            raise SkillDatasetError(f"Learning resource {rid} has invalid resource_type: {rtype}")
        if diff not in VALID_RESOURCE_DIFFICULTIES:
            raise SkillDatasetError(f"Learning resource {rid} has invalid difficulty_level: {diff}")
        try:
            hours = float(row.get("estimated_hours", ""))
            if hours <= 0:
                raise ValueError
        except Exception as exc:
            raise SkillDatasetError(f"Learning resource {rid} has invalid estimated_hours") from exc
        try:
            quality = int(float(row.get("quality_score", "")))
            if quality < 0 or quality > 100:
                raise ValueError
        except Exception as exc:
            raise SkillDatasetError(f"Learning resource {rid} has invalid quality_score") from exc

        skill_meta = get_skill_metadata_index().get(sid, {})
        rec = {
            "resource_id": rid,
            "resource_title": str(row.get("resource_title", "")).strip(),
            "skill_id": sid,
            "skill_name": str(row.get("skill_name", "")).strip() or skill_meta.get("skill_name", ""),
            "provider": str(row.get("provider", "")).strip(),
            "resource_type": rtype,
            "difficulty_level": diff,
            "description": str(row.get("description", "")).strip(),
            "resource_url": url,
            "estimated_hours": float(hours),
            "prerequisites": str(row.get("prerequisites", "")).strip(),
            "is_free": _to_bool(row.get("is_free")),
            "language": str(row.get("language", "")).strip() or "English",
            "quality_score": quality,
            "tags": str(row.get("tags", "")).strip(),
        }
        if not rec["resource_title"] or not rec["resource_url"] or not rec["provider"]:
            raise SkillDatasetError(f"Learning resource {rid} missing title/url/provider")
        out.append(rec)
        seen_ids.add(rid)
        seen_urls.add(url)

    logger.info("Loaded %d curated learning resources from %s", len(out), LEARNING_RESOURCES_CSV.name)
    return out


def get_learning_resources():
    """Return all curated learning resources (copies)."""
    return [dict(r) for r in _load_learning_resources_cached()]


def get_learning_resources_by_skill():
    """Return learning resources grouped by skill_id."""
    grouped = {}
    for rec in _load_learning_resources_cached():
        grouped.setdefault(rec["skill_id"], []).append(dict(rec))
    return grouped


def filter_learning_resources(
    resources,
    *,
    skill_id=None,
    difficulty=None,
    resource_type=None,
    provider=None,
    free_only=None,
):
    out = list(resources)
    if skill_id:
        sid = str(skill_id).strip().lower()
        out = [r for r in out if str(r.get("skill_id", "")).strip().lower() == sid]
    if difficulty:
        d = str(difficulty).strip().title()
        out = [r for r in out if str(r.get("difficulty_level", "")).strip() == d]
    if resource_type:
        rt = str(resource_type).strip().lower()
        out = [r for r in out if str(r.get("resource_type", "")).strip().lower() == rt]
    if provider:
        p = str(provider).strip().lower()
        out = [r for r in out if str(r.get("provider", "")).strip().lower() == p]
    if free_only:
        out = [r for r in out if bool(r.get("is_free"))]
    return out


def get_learning_resources_summary():
    resources = _load_learning_resources_cached()
    by_skill = Counter(r["skill_id"] for r in resources)
    by_difficulty = Counter(r["difficulty_level"] for r in resources)
    by_type = Counter(r["resource_type"] for r in resources)
    by_provider = Counter(r["provider"] for r in resources)
    free_count = sum(1 for r in resources if r.get("is_free"))
    paid_count = len(resources) - free_count
    return {
        "total_resources": len(resources),
        "total_covered_skills": len(by_skill),
        "resource_counts_by_difficulty": dict(by_difficulty),
        "resource_counts_by_type": dict(by_type),
        "free_vs_paid": {"free": free_count, "paid": paid_count},
        "provider_distribution": dict(by_provider),
        "disclosure": (
            "Learning resources are curated genuine resources with verified URLs at generation time. "
            "Availability, pricing, and content may change over time."
        ),
    }
