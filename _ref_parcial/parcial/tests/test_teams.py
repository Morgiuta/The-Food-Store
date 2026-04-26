from fastapi.testclient import TestClient

TEAM_PAYLOAD = {"name": "Avengers", "headquarters": "New York"}
TEAM_PAYLOAD_2 = {"name": "X-Men", "headquarters": "Xavier School"}
HERO_PAYLOAD = {"name": "Steve Rogers", "alias": "Captain America", "power_level": 88}


# ── CREATE ────────────────────────────────────────────────────────────────────

def test_create_team_returns_201(client: TestClient):
    response = client.post("/teams/", json=TEAM_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Avengers"
    assert data["is_active"] is True


def test_create_team_duplicate_name_returns_409(client: TestClient):
    client.post("/teams/", json=TEAM_PAYLOAD_2)
    response = client.post("/teams/", json=TEAM_PAYLOAD_2)
    assert response.status_code == 409


# ── READ ──────────────────────────────────────────────────────────────────────

def test_get_team_with_heroes_empty(client: TestClient):
    team = client.post("/teams/", json={"name": "Shield", "headquarters": "Helicarrier"}).json()
    response = client.get(f"/teams/{team['id']}/heroes")
    assert response.status_code == 200
    assert response.json()["heroes"] == []


# ── ASSIGN HERO (cross-module) ────────────────────────────────────────────────

def test_assign_hero_to_team(client: TestClient):
    """
    Caso cross-module: hero y team se modifican en la misma transacción.
    Verifica que el héroe aparece en la respuesta de /teams/{id}/heroes.
    """
    team = client.post("/teams/", json={"name": "Defenders", "headquarters": "NYC"}).json()
    hero = client.post("/heroes/", json=HERO_PAYLOAD).json()

    response = client.post(f"/teams/{team['id']}/heroes/{hero['id']}")
    assert response.status_code == 200

    body = response.json()
    hero_ids = [h["id"] for h in body["heroes"]]
    assert hero["id"] in hero_ids


def test_assign_inactive_hero_returns_422(client: TestClient):
    team = client.post("/teams/", json={"name": "Guardians", "headquarters": "Space"}).json()
    hero = client.post(
        "/heroes/", json={"name": "Wanda M", "alias": "Scarlet Witch", "power_level": 99}
    ).json()
    client.delete(f"/heroes/{hero['id']}")  # soft delete → inactive

    response = client.post(f"/teams/{team['id']}/heroes/{hero['id']}")
    assert response.status_code == 422


# ── UPDATE ────────────────────────────────────────────────────────────────────

def test_patch_team_partial(client: TestClient):
    team = client.post("/teams/", json={"name": "Thunderbolts", "headquarters": "Old HQ"}).json()
    response = client.patch(f"/teams/{team['id']}", json={"headquarters": "New HQ"})
    assert response.status_code == 200
    assert response.json()["headquarters"] == "New HQ"
    assert response.json()["name"] == "Thunderbolts"


# ── SOFT DELETE ───────────────────────────────────────────────────────────────

def test_soft_delete_team(client: TestClient):
    team = client.post("/teams/", json={"name": "Revengers", "headquarters": "Sakaar"}).json()
    response = client.delete(f"/teams/{team['id']}")
    assert response.status_code == 204

    teams = client.get("/teams/").json()["data"]
    ids = [t["id"] for t in teams]
    assert team["id"] not in ids
