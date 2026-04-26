from fastapi.testclient import TestClient


def test_create_producto_with_stock_sets_disponible_true(client: TestClient):
    response = client.post(
        "/productos/",
        json={
            "nombre": "Empanada",
            "precio_base": "2500.00",
            "stock_cantidad": 5,
            "tiempo_prep_min": 15,
        },
    )
    assert response.status_code == 201
    assert response.json()["disponible"] is True


def test_update_producto_zero_stock_sets_disponible_false(client: TestClient):
    producto = client.post(
        "/productos/",
        json={"nombre": "Lomito", "precio_base": "8500.00", "stock_cantidad": 3},
    ).json()
    response = client.patch(
        f"/productos/{producto['id']}",
        json={"stock_cantidad": 0},
    )
    assert response.status_code == 200
    assert response.json()["disponible"] is False


def test_soft_delete_producto_hides_from_list(client: TestClient):
    producto = client.post(
        "/productos/",
        json={"nombre": "Milanesa", "precio_base": "9000.00", "stock_cantidad": 2},
    ).json()
    response = client.delete(f"/productos/{producto['id']}")
    assert response.status_code == 204
    productos = client.get("/productos/").json()["data"]
    assert producto["id"] not in [item["id"] for item in productos]
