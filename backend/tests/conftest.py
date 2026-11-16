"""
Pytest configuration and shared fixtures for CareerLens backend test suite.
"""
import pytest
import os
import sys

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app


@pytest.fixture
def app():
    """Create Flask application instance configured for testing."""
    test_app = create_app({"TESTING": True})
    return test_app


@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()


@pytest.fixture
def valid_placement_candidate():
    """Realistic high-potential student profile expected to predict Placed."""
    return {
        "CGPA": 8.75,
        "Internships": 2,
        "Projects": 3,
        "Workshops/Certifications": 2,
        "AptitudeTestScore": 88.0,
        "SoftSkillsRating": 4.6,
        "ExtracurricularActivities": "Yes",
        "PlacementTraining": "Yes",
        "SSC_Marks": 84.5,
        "HSC_Marks": 82.0,
        "LeetCode_Problems_Solved": 320,
        "Hackathon_Wins": 2,
        "Publications": 1
    }


@pytest.fixture
def valid_developing_candidate():
    """Realistic developing profile with lower metrics."""
    return {
        "CGPA": 6.8,
        "Internships": 0,
        "Projects": 1,
        "Workshops/Certifications": 0,
        "AptitudeTestScore": 62.0,
        "SoftSkillsRating": 3.2,
        "ExtracurricularActivities": "No",
        "PlacementTraining": "No",
        "SSC_Marks": 58.0,
        "HSC_Marks": 60.0,
        "LeetCode_Problems_Solved": 45,
        "Hackathon_Wins": 0,
        "Publications": 0
    }
