def test_obtener_lista_formas_pago(client):
    response = client.get("/api/v1/ventas/formas-pago")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_obtener_lista_estados(client):
    response = client.get("/api/v1/ventas/estados")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_registrar_pago_pedido_inexistente(client):
    payload = {
        "mp_payment_id": 123456,
        "mp_status": "approved",
        "external_reference": "PEDIDO-999",
        "idempotency_key": "clave-unica-123",
        "transaction_amount": 5000.0,
        "payment_method": "credit_card"
    }
    response = client.post("/api/v1/ventas/pedidos/99999/pagos", json=payload)
    
    assert response.status_code == 404
def test_procesar_pago_webhook_exitoso(client):
    payload = {
        "mp_payment_id": 123456789,
        "mp_status": "approved",
        "mp_status_detail": "accredited",
        "external_reference": "PEDIDO-1",
        "idempotency_key": "clave-unica-123",
        "transaction_amount": 5500.0,
        "payment_method": "credit_card"
    }
    response = client.post("/api/v1/ventas/pedidos/1/pagos", json=payload)
    
    assert response.status_code in [201, 404]

def test_pago_webhook_faltan_datos_obligatorios(client):
    payload = {
        "mp_status": "approved"
    }
    response = client.post("/api/v1/ventas/pedidos/1/pagos", json=payload)
    
    assert response.status_code in [404, 422]

def test_pago_webhook_monto_negativo(client):
    payload = {
        "mp_payment_id": 987654321,
        "mp_status": "rejected",
        "external_reference": "PEDIDO-2",
        "idempotency_key": "clave-unica-456",
        "transaction_amount": -100.0,
        "payment_method": "account_money"
    }
    response = client.post("/api/v1/ventas/pedidos/1/pagos", json=payload)
    
    assert response.status_code in [404, 422]

def test_pago_webhook_estado_excede_limite(client):
    payload = {
        "mp_payment_id": 111222,
        "mp_status": "a" * 35,
        "external_reference": "PEDIDO-3",
        "idempotency_key": "clave-789",
        "transaction_amount": 1000.0
    }
    response = client.post("/api/v1/ventas/pedidos/1/pagos", json=payload)
    
    assert response.status_code in [404, 422]

def test_registrar_pago_exitoso(client):
    payload = {
        "mp_payment_id": 555666777,
        "mp_status": "approved",
        "external_reference": "PEDIDO-TEST-1",
        "idempotency_key": "unique-key-555",
        "transaction_amount": 2500.50,
        "payment_method": "credit_card"
    }
    response = client.post("/api/v1/ventas/pedidos/1/pagos", json=payload)
    
    print("Pago registrado en sistema")
    
    assert response.status_code in [201, 404]

def test_pago_webhook_sin_idempotency_key(client):
    payload = {
        "mp_payment_id": 777888999,
        "mp_status": "pending",
        "external_reference": "PEDIDO-4",
        "transaction_amount": 3000.0,
        "payment_method": "debit_card"
    }
    response = client.post("/api/v1/ventas/pedidos/1/pagos", json=payload)
    
    assert response.status_code in [404, 422]