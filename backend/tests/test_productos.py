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


def test_actualizar_producto_con_put(client):
    payload = {
        "nombre": "Papas Grandes",
        "descripcion": "Porcion grande de papas fritas",
        "precio_base": 3200.0,
        "stock_cantidad": 15
    }
    creacion = client.post("/api/v1/productos/", json=payload)
    prod_id = creacion.json()["id"]

    response = client.put(f"/api/v1/productos/{prod_id}", json={"precio_base": 3500.0})

    assert response.status_code == 200
    assert float(response.json()["precio_base"]) == 3500.0


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
    assert response.json()["disponible"] is True


def test_stock_no_cambia_disponibilidad_automaticamente(client):
    payload = {
        "nombre": "Sandwich Veggie",
        "descripcion": "Sandwich con vegetales grillados",
        "precio_base": 5200.0,
        "stock_cantidad": 8
    }
    creacion = client.post("/api/v1/productos/", json=payload)
    prod_id = creacion.json()["id"]

    response = client.patch(f"/api/v1/productos/{prod_id}/stock", json={"stock_cantidad": 0})

    assert response.status_code == 200
    assert response.json()["stock_cantidad"] == 0
    assert response.json()["disponible"] is True


def test_producto_ingredientes_endpoints(client):
    producto = client.post("/api/v1/productos/", json={
        "nombre": "Pizza Especial",
        "descripcion": "Pizza con ingredientes editables",
        "precio_base": 9200.0,
        "stock_cantidad": 10
    })
    producto_id = producto.json()["id"]
    ingrediente = client.post("/api/v1/ingredientes/", json={
        "nombre": "Muzzarella",
        "descripcion": "Queso para pizza",
        "stock_actual": 50,
        "costo_unitario": 1200,
        "unidad": "gramos"
    })
    ingrediente_id = ingrediente.json()["id"]

    post_response = client.post(
        f"/api/v1/productos/{producto_id}/ingredientes",
        json=[
            {
                "ingrediente_id": ingrediente_id,
                "es_removible": True,
                "es_opcional": False,
                "cantidad_requerida": 2
            }
        ],
    )
    get_response = client.get(f"/api/v1/productos/{producto_id}/ingredientes")

    assert post_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json()[0]["ingrediente_id"] == ingrediente_id
    assert get_response.json()[0]["es_removible"] is True
    
    
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
