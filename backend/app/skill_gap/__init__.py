"""
Skill Gap Analysis module (Phase 1) for CareerLens.

Rule-based, explainable engine using synthetic illustrative role-skill benchmarks.
No trained ML model is used for this feature.
"""

from .skill_routes import skill_gap_bp

__all__ = ["skill_gap_bp"]
