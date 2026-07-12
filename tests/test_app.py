import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = {}
    for name, details in activities.items():
        original[name] = {
            **details,
            "participants": list(details["participants"]),
        }

    yield

    activities.clear()
    activities.update(original)


def test_unregister_participant_removes_the_student():
    client = TestClient(app)

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"


def test_unregister_participant_returns_404_for_unknown_activity():
    client = TestClient(app)

    response = client.delete(
        "/activities/Unknown Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
