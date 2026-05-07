"""
Tests for the FastAPI activities management API.

Uses pytest with FastAPI TestClient and AAA (Arrange-Act-Assert) pattern.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app, follow_redirects=False)

# Store original activities for reset
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities():
    """Test GET /activities returns all activities with correct structure."""
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # 9 activities defined
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_root_redirect():
    """Test GET / redirects to static homepage."""
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_signup_valid():
    """Test POST /activities/{activity_name}/signup with valid data."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    # Verify participant was added
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity_name]["participants"]


def test_signup_duplicate_email():
    """Test POST /activities/{activity_name}/signup with duplicate email."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_signup_nonexistent_activity():
    """Test POST /activities/{activity_name}/signup for non-existent activity."""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_valid():
    """Test DELETE /activities/{activity_name}/signup with valid data."""
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already signed up

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    # Verify participant was removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity_name]["participants"]


def test_unregister_not_signed_up():
    """Test DELETE /activities/{activity_name}/signup when student not signed up."""
    # Arrange
    activity_name = "Programming Class"
    email = "notsignedup@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up for this activity"}


def test_unregister_nonexistent_activity():
    """Test DELETE /activities/{activity_name}/signup for non-existent activity."""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}