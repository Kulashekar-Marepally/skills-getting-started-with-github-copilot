"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test."""
    original_state = {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities.items()
    }
    yield
    for name, details in original_state.items():
        activities[name]["participants"] = details["participants"]


client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_chess_club(self):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert "Chess Club" in response.json()


class TestSignupForActivity:
    def test_signup_success(self):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant(self):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert email in activities[activity]["participants"]

    def test_signup_invalid_activity_returns_404(self):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterFromActivity:
    def test_unregister_success(self):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_removes_participant(self):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert email not in activities[activity]["participants"]

    def test_unregister_invalid_activity_returns_404(self):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_400(self):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
