def test_crear_producto_exitoso(client):
    payload = {
        "nombre": "Churrasco con Papas",
        "descripcion": "Churrasco a la parrilla con papas fritas y ensalada fresca",
        "precio_base": 8500.0,
        "stock_cantidad": 10
    }
    
    response = client.post("/api/v1/productos/", json=payload)
    
    print("Producto cargado")
    
    assert response.status_code in [200, 201]
    assert response.json()["nombre"] == "Churrasco con Papas"
    assert float(response.json()["precio_base"]) == 8500.0

def test_obtener_productos(client):
    response = client.get("/api/v1/productos/?disponible=true&page=1")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_producto_por_id(client):
    payload = {
        "nombre": "Milanesa Napolitana",
        "descripcion": "Milanesa de ternera con queso y tomate",
        "precio_base": 7200.0,
        "stock_cantidad": 25
    }
    creacion = client.post("/api/v1/productos/", json=payload)
    prod_id = creacion.json()["id"]
    
    response = client.get(f"/api/v1/productos/{prod_id}")
    
    assert response.status_code == 200
    assert response.json()["nombre"] == "Milanesa Napolitana"

def test_actualizar_producto(client):
    payload = {
        "nombre": "Jugo Natural Naranja",
        "descripcion": "Jugo fresco recién exprimido",
        "precio_base": 1800.0,
        "stock_cantidad": 30
    }
    creacion = client.post("/api/v1/productos/", json=payload)
    prod_id = creacion.json()["id"]
    
    response = client.patch(f"/api/v1/productos/{prod_id}", json={"precio_base": 2000.0})
    
    assert response.status_code == 200
    assert float(response.json()["precio_base"]) == 2000.0

def test_producto_sin_stock(client):   
    print("Test producto agotado")
    payload = {
        "nombre": "Torta de Chocolate Selva Negra",
        "descripcion": "Torta clasica con cobertura de chocolate",
        "precio_base": 4500.0,
        "stock_cantidad": 0
    }
    response = client.post("/api/v1/productos/", json=payload)
    
    assert response.status_code in [200, 201]
    assert response.json()["stock_cantidad"] == 0
    
    
def test_crear_producto_falta_nombre(client):
    payload = {
        "descripcion": "Un producto sin nombre",
        "precio_base": 1000.0,
        "stock_cantidad": 5
    }
    response = client.post("/api/v1/productos/", json=payload)
    
    assert response.status_code == 422

def test_crear_producto_precio_negativo(client):
    payload = {
        "nombre": "Producto Invalido",
        "precio_base": -500.0,
        "stock_cantidad": 10
    }
    response = client.post("/api/v1/productos/", json=payload)
    
    assert response.status_code == 422

def test_actualizar_producto_inexistente(client):
    response = client.patch("/api/v1/productos/99999", json={"precio_base": 1000.0})
    
    assert response.status_code == 404