from fastapi.testclient import TestClient


def test_create_producto_ingrediente_returns_201(client: TestClient):
    ingrediente = client.post("/ingredientes/", json={"nombre": "Jamon"}).json()
    producto = client.post(
        "/productos/",
        json={"nombre": "Tostado", "precio_base": "4500.00", "stock_cantidad": 8},
    ).json()

    response = client.post(
        "/producto-ingredientes/",
        json={
            "producto_id": producto["id"],
            "ingrediente_id": ingrediente["id"],
            "es_removible": True,
            "es_opcional": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["es_opcional"] is True


def test_update_producto_ingrediente_returns_200(client: TestClient):
    ingrediente = client.post("/ingredientes/", json={"nombre": "Aceitunas"}).json()
    producto = client.post(
        "/productos/",
        json={"nombre": "Fugazzeta", "precio_base": "11000.00", "stock_cantidad": 3},
    ).json()
    client.post(
        "/producto-ingredientes/",
        json={
            "producto_id": producto["id"],
            "ingrediente_id": ingrediente["id"],
            "es_removible": False,
            "es_opcional": False,
        },
    )

    response = client.patch(
        f"/producto-ingredientes/{producto['id']}/{ingrediente['id']}",
        json={"es_removible": True, "es_opcional": True},
    )
    assert response.status_code == 200
    assert response.json()["es_removible"] is True
