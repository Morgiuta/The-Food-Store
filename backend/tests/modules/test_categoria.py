from fastapi.testclient import TestClient


def test_create_categoria_returns_201(client: TestClient):
    response = client.post(
        "/categorias/",
        json={"nombre": "Bebidas", "descripcion": "Frias", "orden_display": 2},
    )
    assert response.status_code == 201
    assert response.json()["nombre"] == "Bebidas"


def test_categoria_duplicate_name_returns_409(client: TestClient):
    client.post("/categorias/", json={"nombre": "Postres", "orden_display": 1})
    response = client.post("/categorias/", json={"nombre": "Postres", "orden_display": 2})
    assert response.status_code == 409


def test_soft_delete_categoria_hides_from_list(client: TestClient):
    categoria = client.post("/categorias/", json={"nombre": "Pastas", "orden_display": 3}).json()
    response = client.delete(f"/categorias/{categoria['id']}")
    assert response.status_code == 204
    categorias = client.get("/categorias/").json()["data"]
    assert categoria["id"] not in [item["id"] for item in categorias]
