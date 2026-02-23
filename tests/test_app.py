from urllib.parse import quote
import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

# preserve original state so each test can start fresh
ORIGINAL = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # clear and repopulate the dict
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL))
    yield


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    # make sure some known key is present
    assert "Chess Club" in data


def test_signup_success():
    email = "new@school.edu"
    r = client.post(
        f"/activities/{quote('Chess Club')}/signup",
        params={"email": email},
    )
    assert r.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    existing = activities["Chess Club"]["participants"][0]
    r = client.post(
        f"/activities/{quote('Chess Club')}/signup",
        params={"email": existing},
    )
    assert r.status_code == 400


def test_signup_nonexistent_activity():
    r = client.post("/activities/NotThere/signup", params={"email": "a@b.c"})
    assert r.status_code == 404


def test_remove_participant_success():
    email = activities["Chess Club"]["participants"][0]
    r = client.delete(
        f"/activities/{quote('Chess Club')}/participants/{quote(email)}"
    )
    assert r.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant():
    r = client.delete(
        f"/activities/{quote('Chess Club')}/participants/{quote('nope@x')}"
    )
    assert r.status_code == 404


def test_remove_from_nonexistent_activity():
    r = client.delete("/activities/NoSuch/participants/foo")
    assert r.status_code == 404
