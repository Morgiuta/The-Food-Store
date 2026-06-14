def test_crear_pedido(client):
    payload_dir = {
        "calle": "Av Las Heras",
        "numero": "1550",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": True
    }
    res_dir = client.post("/api/v1/direcciones/", json=payload_dir)
    dir_id = res_dir.json().get("id")

    payload_prod = {
        "nombre": "Pizza Cuatro Quesos",
        "descripcion": "Pizza con mozzarella, queso azul, parmesano y ricota",
        "precio_base": 8200.0,
        "stock_cantidad": 15
    }
    res_prod = client.post("/api/v1/productos/", json=payload_prod)
    prod_id = res_prod.json().get("id")

    payload_pedido = {
        "direccion_id": dir_id,
        "forma_pago_codigo": "EFECTIVO",
        "descuento": "0.00",
        "costo_envio": "600.00",
        "notas": "Extra oregano en la pizza",
        "detalles": [
            {"producto_id": prod_id, "cantidad": 1}
        ]
    }
    response = client.post("/api/v1/pedidos/", json=payload_pedido)
    
    assert response.status_code == 201
    assert response.json().get("estado_codigo") == "PENDIENTE"

def test_listar_pedidos(client):
    response = client.get("/api/v1/pedidos/")
    
    assert response.status_code == 200

def test_cancelar_pedido(client):
    payload_dir = {
        "calle": "Avenida Colon",
        "numero": "2100",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": True
    }
    res_dir = client.post("/api/v1/direcciones/", json=payload_dir)
    dir_id = res_dir.json().get("id")

    payload_prod = {
        "nombre": "Empanadas Fritas",
        "descripcion": "Empanadas caseras de carne fritas",
        "precio_base": 850.0,
        "stock_cantidad": 60
    }
    res_prod = client.post("/api/v1/productos/", json=payload_prod)
    prod_id = res_prod.json().get("id")

    payload_pedido = {
        "direccion_id": dir_id,
        "forma_pago_codigo": "EFECTIVO",
        "descuento": "0.00",
        "costo_envio": "500.00",
        "notas": "Retiro en local",
        "detalles": [
            {"producto_id": prod_id, "cantidad": 12}
        ]
    }
    res_pedido = client.post("/api/v1/pedidos/", json=payload_pedido)
    pedido_id = res_pedido.json().get("id")

    response = client.patch(f"/api/v1/pedidos/{pedido_id}/cancelar")
    
    assert response.status_code in [200, 422]

def test_actualizar_estado_pedido_admin(client):
    payload_dir = {
        "calle": "Avenida Mitre",
        "numero": "2200",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": True
    }
    res_dir = client.post("/api/v1/direcciones/", json=payload_dir)
    dir_id = res_dir.json().get("id")

    payload_prod = {
        "nombre": "Lomo Completo",
        "descripcion": "Lomo a la parrilla con chimichurri casero",
        "precio_base": 10500.0,
        "stock_cantidad": 20
    }
    res_prod = client.post("/api/v1/productos/", json=payload_prod)
    prod_id = res_prod.json().get("id")

    payload_pedido = {
        "direccion_id": dir_id,
        "forma_pago_codigo": "EFECTIVO",
        "descuento": "0.00",
        "costo_envio": "300.00",
        "notas": "",
        "detalles": [
            {"producto_id": prod_id, "cantidad": 1}
        ]
    }
    res_pedido = client.post("/api/v1/pedidos/", json=payload_pedido)
    pedido_id = res_pedido.json().get("id")

    response = client.patch(
        f"/api/v1/pedidos/{pedido_id}/estado",
        json={"nuevo_estado": "CONFIRMADO"}
    )
    
    assert response.status_code == 200
    assert response.json().get("estado_codigo") == "CONFIRMADO"

def test_obtener_pedido_por_id_inexistente(client):
    response = client.get("/api/v1/pedidos/99999")
    
    assert response.status_code == 404
    
def test_crear_pedido_sin_detalles(client):
    payload_dir = {
        "calle": "Avenida San Martin",
        "numero": "1900",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": True
    }
    res_dir = client.post("/api/v1/direcciones/", json=payload_dir)
    dir_id = res_dir.json().get("id")

    payload_pedido = {
        "direccion_id": dir_id,
        "forma_pago_codigo": "EFECTIVO",
        "descuento": "0.00",
        "costo_envio": "500.00",
        "notas": "Test sin productos",
        "detalles": []
    }
    response = client.post("/api/v1/pedidos/", json=payload_pedido)
    
    assert response.status_code in [400, 422]

def test_cancelar_pedido_inexistente(client):
    response = client.patch("/api/v1/pedidos/99999/cancelar")
    
    assert response.status_code == 404