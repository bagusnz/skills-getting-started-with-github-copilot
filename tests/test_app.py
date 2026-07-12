import asyncio

import pytest
import httpx

from src.app import app, activities


def make_request(method, path, **kwargs):
    async def _request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_request())


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
    response = make_request(
        "DELETE",
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"


def test_unregister_participant_returns_404_for_unknown_activity():
    response = make_request(
        "DELETE",
        "/activities/Unknown Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
