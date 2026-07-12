import pytest

from src.app import activities


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
