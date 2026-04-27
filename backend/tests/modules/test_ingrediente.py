from fastapi.testclient import TestClient


def test_create_ingrediente_returns_201(client: TestClient):
    response = client.post(
        "/ingredientes/",
        json={"nombre": "Tomate", "descripcion": "Natural", "es_alergeno": False},
    )
    assert response.status_code == 201
    assert response.json()["nombre"] == "Tomate"


def test_update_ingrediente_returns_200(client: TestClient):
    ingrediente = client.post("/ingredientes/", json={"nombre": "Harina"}).json()
    response = client.patch(
        f"/ingredientes/{ingrediente['id']}",
        json={"descripcion": "000"},
    )
    assert response.status_code == 200
    assert response.json()["descripcion"] == "000"
