from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that GET / redirects to the static index page."""
    # Arrange
    # (no setup needed)
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert "Mergington High School Activities" in response.text


def test_get_activities():
    """Test GET /activities returns all activities."""
    # Arrange
    # (activities data is pre-loaded in the app)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity}" in data["message"]
    
    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistent Activity"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate():
    """Test signup when already signed up."""
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Programming Class"
    
    # First signup - sign up the user
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act - attempt to sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity."""
    # Arrange
    email = "unregister@mergington.edu"
    activity = "Gym Class"
    
    # Sign up first
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity}" in data["message"]
    
    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity]["participants"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistent Activity"
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_participant_not_found():
    """Test unregister when participant is not signed up."""
    # Arrange
    email = "notsignedup@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]


def test_activities_data_integrity():
    """Test that activities data remains consistent."""
    # Arrange
    email_to_add = "integrity@mergington.edu"
    email_to_remove = "isabella@mergington.edu"
    activity = "Art Club"
    
    response = client.get("/activities")
    initial_data = response.json()
    
    # Act
    # Add a new participant
    client.post(f"/activities/{activity}/signup?email={email_to_add}")
    # Remove an existing participant
    client.delete(f"/activities/{activity}/signup?email={email_to_remove}")
    
    # Assert
    response = client.get("/activities")
    final_data = response.json()
    
    # Verify the changes
    assert email_to_add in final_data[activity]["participants"]
    assert email_to_remove not in final_data[activity]["participants"]
    
    # Verify other activities are unchanged
    for activity_name in initial_data:
        if activity_name != activity:
            assert initial_data[activity_name]["participants"] == final_data[activity_name]["participants"]
