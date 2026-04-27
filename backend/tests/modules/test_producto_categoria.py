from fastapi.testclient import TestClient


def test_create_producto_categoria_returns_201(client: TestClient):
    categoria = client.post("/categorias/", json={"nombre": "Sandwiches", "orden_display": 1}).json()
    producto = client.post(
        "/productos/",
        json={"nombre": "Hamburguesa", "precio_base": "7000.00", "stock_cantidad": 4},
    ).json()

    response = client.post(
        "/producto-categorias/",
        json={"producto_id": producto["id"], "categoria_id": categoria["id"], "es_principal": True},
    )
    assert response.status_code == 201
    assert response.json()["es_principal"] is True


def test_only_one_categoria_principal_per_producto(client: TestClient):
    categoria_1 = client.post("/categorias/", json={"nombre": "Menu Ejecutivo", "orden_display": 1}).json()
    categoria_2 = client.post("/categorias/", json={"nombre": "Promos", "orden_display": 2}).json()
    producto = client.post(
        "/productos/",
        json={"nombre": "Ravioles", "precio_base": "10000.00", "stock_cantidad": 6},
    ).json()

    client.post(
        "/producto-categorias/",
        json={"producto_id": producto["id"], "categoria_id": categoria_1["id"], "es_principal": True},
    )
    response = client.post(
        "/producto-categorias/",
        json={"producto_id": producto["id"], "categoria_id": categoria_2["id"], "es_principal": True},
    )
    assert response.status_code == 409
