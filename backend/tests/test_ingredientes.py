def test_crear_ingrediente(client):
    payload = {
        "nombre": "Tomate Perita",
        "descripcion": "Tomate fresco para salsas y preparaciones",
        "es_alergeno": False,
        "stock_cantidad": 25.0,
        "costo_unitario": 1800.0,
        "unidad_medida_id": 1
    }
    response = client.post("/api/v1/ingredientes/", json=payload)
    
    print("Ingrediente creado")
    
    assert response.status_code in [200, 201]
    assert response.json()["nombre"] == "Tomate Perita"
    assert float(response.json()["costo_unitario"]) == 1800.0

def test_obtener_ingredientes(client):
    response = client.get("/api/v1/ingredientes/")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_ingrediente_por_id(client):
    payload = {
        "nombre": "Queso Muzzarella",
        "descripcion": "Queso muzzarella para pizzas y lomos",
        "stock_cantidad": 15.0,
        "costo_unitario": 5200.0,
        "unidad_medida_id": 1
    }
    creacion = client.post("/api/v1/ingredientes/", json=payload)
    ing_id = creacion.json()["id"]

    response = client.get(f"/api/v1/ingredientes/{ing_id}")
    
    assert response.status_code == 200
    assert response.json()["nombre"] == "Queso Muzzarella"

def test_actualizar_ingrediente(client):
    payload = {
        "nombre": "Lechuga Criolla",
        "descripcion": "Lechuga fresca para lomos y hamburguesas",
        "stock_cantidad": 12.0,
        "costo_unitario": 1300.0,
        "unidad_medida_id": 1
    }
    creacion = client.post("/api/v1/ingredientes/", json=payload)
    ing_id = creacion.json()["id"]

    response = client.patch(f"/api/v1/ingredientes/{ing_id}", json={"stock_cantidad": 18.0})
    
    assert response.status_code == 200
    assert float(response.json()["stock_cantidad"]) == 18.0

def test_eliminar_ingrediente(client):
    payload = {
        "nombre": "Jamon Cocido",
        "descripcion": "Jamon cocido feteado para lomos y pizzas",
        "unidad_medida_id": 1,
        "costo_unitario": 4800.0,
        "stock_cantidad": 5.0
    }
    creacion = client.post("/api/v1/ingredientes/", json=payload)
    ing_id = creacion.json()["id"]

    response = client.delete(f"/api/v1/ingredientes/{ing_id}")
    
    assert response.status_code in [200, 204]

def test_actualizar_ingrediente_inexistente(client):
    response = client.patch("/api/v1/ingredientes/99999", json={"nombre": "Sal Fina"})
    
    assert response.status_code == 404
