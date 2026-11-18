"""
Student Segmentation (Phase 3) - K-Means clustering of student skill profiles.

Role-aware, explainable, unsupervised clustering using synthetic student profiles.
Cluster labels/descriptions are generated dynamically from learned centroids and
Phase 1 role requirements (not hardcoded by cluster ID).
"""

from .segmentation_routes import segmentation_bp

__all__ = ["segmentation_bp"]
