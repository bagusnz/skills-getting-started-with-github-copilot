import asyncio

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


def test_root_redirects_to_static_index():
    response = make_request("GET", "/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_activity_names():
    response = make_request("GET", "/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert "Gym Class" in payload


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"

    response = make_request("POST", "/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_email():
    response = make_request(
        "POST",
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity():
    response = make_request(
        "POST",
        "/activities/Unknown Activity/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
