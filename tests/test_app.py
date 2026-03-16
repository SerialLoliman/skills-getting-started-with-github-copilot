import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities state between tests
def reset_activities():
    for activity in activities.values():
        activity['participants'].clear()

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Arrange: Reset activities before each test
    reset_activities()
    yield
    reset_activities()


def test_get_activities():
    # Arrange
    # (State is already reset by fixture)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json()["message"].startswith("Signed up")


def test_signup_for_activity_already_signed_up():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    activities[activity]["participants"].append(email)
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_for_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "testuser@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
