import pytest
from fastapi.testclient import TestClient


# ── Fixtures de datos ─────────────────────────────────────────────────────────

HERO_PAYLOAD = {"name": "Peter Parker", "alias": "Spider-Man", "power_level": 85}
HERO_PAYLOAD_2 = {"name": "Tony Stark", "alias": "Iron Man", "power_level": 95}


# ── CREATE ────────────────────────────────────────────────────────────────────

def test_create_hero_returns_201(client: TestClient):
    response = client.post("/heroes/", json=HERO_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["alias"] == "Spider-Man"
    assert data["is_active"] is True
    assert "id" in data


def test_create_hero_duplicate_alias_returns_409(client: TestClient):
    client.post("/heroes/", json=HERO_PAYLOAD)
    response = client.post("/heroes/", json=HERO_PAYLOAD)
    assert response.status_code == 409
    assert "alias" in response.json()["detail"]


def test_create_hero_invalid_power_level_returns_422(client: TestClient):
    bad = {**HERO_PAYLOAD, "alias": "other-alias", "power_level": 200}
    response = client.post("/heroes/", json=bad)
    assert response.status_code == 422


# ── READ ──────────────────────────────────────────────────────────────────────

def test_get_hero_by_id(client: TestClient):
    created = client.post("/heroes/", json=HERO_PAYLOAD_2).json()
    response = client.get(f"/heroes/{created['id']}")
    assert response.status_code == 200
    assert response.json()["alias"] == "Iron Man"


def test_get_hero_not_found_returns_404(client: TestClient):
    response = client.get("/heroes/99999")
    assert response.status_code == 404


def test_list_heroes_returns_data_and_total(client: TestClient):
    response = client.get("/heroes/")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "total" in body


# ── UPDATE ────────────────────────────────────────────────────────────────────

def test_patch_hero_partial_update(client: TestClient):
    hero = client.post(
        "/heroes/", json={"name": "Bruce Banner", "alias": "Hulk", "power_level": 90}
    ).json()
    response = client.patch(f"/heroes/{hero['id']}", json={"power_level": 99})
    assert response.status_code == 200
    assert response.json()["power_level"] == 99
    assert response.json()["alias"] == "Hulk"  # campo no tocado


# ── SOFT DELETE ───────────────────────────────────────────────────────────────

def test_soft_delete_hero_returns_204(client: TestClient):
    hero = client.post(
        "/heroes/", json={"name": "Natasha R", "alias": "Black Widow", "power_level": 80}
    ).json()
    response = client.delete(f"/heroes/{hero['id']}")
    assert response.status_code == 204


def test_soft_deleted_hero_not_in_list(client: TestClient):
    hero = client.post(
        "/heroes/", json={"name": "Clint B", "alias": "Hawkeye", "power_level": 70}
    ).json()
    client.delete(f"/heroes/{hero['id']}")
    heroes = client.get("/heroes/").json()["data"]
    ids = [h["id"] for h in heroes]
    assert hero["id"] not in ids
