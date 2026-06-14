def test_crear_producto_exitoso(client):
    payload = {
        "nombre": "Lomo Completo",
        "descripcion": "Lomo con jamon, queso, huevo, lechuga, tomate y papas fritas",
        "precio_base": 8500.0,
        "stock_cantidad": 10
    }
    
    response = client.post("/api/v1/productos/", json=payload)
    
    print("Producto cargado")
    
    assert response.status_code in [200, 201]
    assert response.json()["nombre"] == "Lomo Completo"
    assert float(response.json()["precio_base"]) == 8500.0

def test_obtener_productos(client):
    response = client.get("/api/v1/productos/?disponible=true&page=1")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_producto_por_id(client):
    payload = {
        "nombre": "Pizza Napolitana",
        "descripcion": "Pizza con queso muzzarella, tomate perita, ajo y oregano",
        "precio_base": 7800.0,
        "stock_cantidad": 25
    }
    creacion = client.post("/api/v1/productos/", json=payload)
    prod_id = creacion.json()["id"]
    
    response = client.get(f"/api/v1/productos/{prod_id}")
    
    assert response.status_code == 200
    assert response.json()["nombre"] == "Pizza Napolitana"

def test_actualizar_producto(client):
    payload = {
        "nombre": "Gaseosa Cola 500ml",
        "descripcion": "Bebida sin alcohol individual para menu",
        "precio_base": 1500.0,
        "stock_cantidad": 30
    }
    creacion = client.post("/api/v1/productos/", json=payload)
    prod_id = creacion.json()["id"]
    
    response = client.patch(f"/api/v1/productos/{prod_id}", json={"precio_base": 1700.0})
    
    assert response.status_code == 200
    assert float(response.json()["precio_base"]) == 1700.0

def test_producto_sin_stock(client):   
    print("Test producto agotado")
    payload = {
        "nombre": "Empanada de Carne",
        "descripcion": "Empanada criolla de carne cortada a cuchillo",
        "precio_base": 900.0,
        "stock_cantidad": 0
    }
    response = client.post("/api/v1/productos/", json=payload)
    
    assert response.status_code in [200, 201]
    assert response.json()["stock_cantidad"] == 0
    
    
def test_crear_producto_falta_nombre(client):
    payload = {
        "descripcion": "Producto de carta sin nombre visible para el cliente",
        "precio_base": 1500.0,
        "stock_cantidad": 5
    }
    response = client.post("/api/v1/productos/", json=payload)
    
    assert response.status_code == 422

def test_crear_producto_precio_negativo(client):
    payload = {
        "nombre": "Hamburguesa Simple",
        "precio_base": -500.0,
        "stock_cantidad": 10
    }
    response = client.post("/api/v1/productos/", json=payload)
    
    assert response.status_code == 422

def test_actualizar_producto_inexistente(client):
    response = client.patch("/api/v1/productos/99999", json={"precio_base": 8500.0})
    
    assert response.status_code == 404
