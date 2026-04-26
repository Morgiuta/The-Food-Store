from fastapi.testclient import TestClient


def test_catalogo_productos_flow(client: TestClient):
    categoria = client.post(
        "/categorias/",
        json={"nombre": "Pizzas", "descripcion": "Categoria principal", "orden_display": 1},
    )
    assert categoria.status_code == 201
    categoria_id = categoria.json()["id"]

    producto = client.post(
        "/productos/",
        json={
            "nombre": "Muzzarella",
            "descripcion": "Pizza clasica",
            "precio_base": "12000.50",
            "stock_cantidad": 10,
            "tiempo_prep_min": 20,
            "imagenes_url": ["https://ejemplo.com/pizza.jpg"],
        },
    )
    assert producto.status_code == 201
    producto_id = producto.json()["id"]
    assert producto.json()["disponible"] is True

    ingrediente = client.post(
        "/ingredientes/",
        json={"nombre": "Queso", "descripcion": "Mozzarella", "es_alergeno": True},
    )
    assert ingrediente.status_code == 201
    ingrediente_id = ingrediente.json()["id"]

    relacion_categoria = client.post(
        "/producto-categorias/",
        json={"producto_id": producto_id, "categoria_id": categoria_id, "es_principal": True},
    )
    assert relacion_categoria.status_code == 201

    relacion_ingrediente = client.post(
        "/producto-ingredientes/",
        json={
            "producto_id": producto_id,
            "ingrediente_id": ingrediente_id,
            "es_removible": True,
            "es_opcional": False,
        },
    )
    assert relacion_ingrediente.status_code == 201
