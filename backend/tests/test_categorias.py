def test_crear_categoria_exitosa(client):
    payload = {
        "nombre": "Bebidas Sin Alcohol",
        "orden_display": 1
    }
    response = client.post("/api/v1/categorias/", json=payload)
    
    print("Categoria cargada en base de datos")
    
    assert response.status_code in [200, 201]
    assert response.json()["nombre"] == "Bebidas Sin Alcohol"

def test_obtener_lista_categorias(client):
    response = client.get("/api/v1/categorias/")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_categoria_por_id(client):
    payload = {
        "nombre": "Platos Principales",
        "orden_display": 1
    }
    creacion = client.post("/api/v1/categorias/", json=payload)
    cat_id = creacion.json()["id"]

    response = client.get(f"/api/v1/categorias/{cat_id}")
    
    assert response.status_code == 200
    assert response.json()["nombre"] == "Platos Principales"

def test_actualizar_categoria(client):
    payload = {
        "nombre": "Platos Principales"
    }
    creacion = client.post("/api/v1/categorias/", json=payload)
    cat_id = creacion.json()["id"]

    response = client.patch(f"/api/v1/categorias/{cat_id}", json={"orden_display": 5})
    
    assert response.status_code == 200
    assert response.json()["orden_display"] == 5

def test_eliminar_categoria(client):
    payload = {
        "nombre": "Entradas"
    }
    creacion = client.post("/api/v1/categorias/", json=payload)
    cat_id = creacion.json()["id"]

    response = client.delete(f"/api/v1/categorias/{cat_id}")
    
    assert response.status_code in [200, 204]

def test_crear_categoria_falta_nombre(client):
    response = client.post("/api/v1/categorias/", json={"orden_display": 1})
    
    assert response.status_code == 422

def test_obtener_categoria_inexistente(client):
    response = client.get("/api/v1/categorias/99999")
    
    assert response.status_code == 404
