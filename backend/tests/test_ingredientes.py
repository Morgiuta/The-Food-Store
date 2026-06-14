def test_crear_ingrediente(client):
    payload = {
        "nombre": "Tomate Perita",
        "descripcion": "Tomate fresco para salsas y preparaciones",
        "es_alergeno": False,
        "stock_actual": 25.0,
        "costo_unitario": 120.0,
        "unidad": "kg"
    }
    response = client.post("/api/v1/ingredientes/", json=payload)
    
    print("Ingrediente creado")
    
    assert response.status_code in [200, 201]
    assert response.json()["nombre"] == "Tomate Perita"
    assert float(response.json()["costo_unitario"]) == 120.0

def test_obtener_ingredientes(client):
    response = client.get("/api/v1/ingredientes/")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_ingrediente_por_id(client):
    payload = {
        "nombre": "Queso Mozzarella",
        "descripcion": "Queso mozzarella importado para cocina",
        "stock_actual": 15.0,
        "costo_unitario": 850.0,
        "unidad": "kg"
    }
    creacion = client.post("/api/v1/ingredientes/", json=payload)
    ing_id = creacion.json()["id"]

    response = client.get(f"/api/v1/ingredientes/{ing_id}")
    
    assert response.status_code == 200
    assert response.json()["nombre"] == "Queso Mozzarella"

def test_actualizar_ingrediente(client):
    payload = {
        "nombre": "Cebolla Blanca",
        "descripcion": "Cebolla fresca para cocina",
        "stock_actual": 12.0,
        "costo_unitario": 95.0,
        "unidad": "kg"
    }
    creacion = client.post("/api/v1/ingredientes/", json=payload)
    ing_id = creacion.json()["id"]

    response = client.patch(f"/api/v1/ingredientes/{ing_id}", json={"stock_actual": 18.0})
    
    assert response.status_code == 200
    assert float(response.json()["stock_actual"]) == 18.0

def test_eliminar_ingrediente(client):
    payload = {
        "nombre": "Ajo Fresco",
        "descripcion": "Ajo de cosecha local",
        "unidad": "kg",
        "costo_unitario": 280.0,
        "stock_actual": 5.0
    }
    creacion = client.post("/api/v1/ingredientes/", json=payload)
    ing_id = creacion.json()["id"]

    response = client.delete(f"/api/v1/ingredientes/{ing_id}")
    
    assert response.status_code in [200, 204]

def test_crear_ingrediente_unidad_invalida(client):
    payload = {
        "nombre": "Harina 0000",
        "unidad": "tonelada",
        "costo_unitario": 65.0,
        "stock_actual": 50.0
    }
    response = client.post("/api/v1/ingredientes/", json=payload)
    
    assert response.status_code == 422

def test_actualizar_ingrediente_inexistente(client):
    response = client.patch("/api/v1/ingredientes/99999", json={"nombre": "Sal"})
    
    assert response.status_code == 404