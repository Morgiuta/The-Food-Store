def test_registro_usuario_exitoso(client):
    payload = {
        "nombre": "Cliente",
        "apellido": "Mostrador",
        "email": "cliente@test.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201

def test_registro_faltan_datos(client):
    payload = {
        "nombre": "Cliente",
        "email": "cliente_sin_apellido@test.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422

def test_login_exitoso(client):
    payload_reg = {
        "nombre": "Cliente",
        "apellido": "Delivery",
        "email": "cliente_delivery@test.com",
        "password": "Password123!"
    }
    client.post("/api/v1/auth/register", json=payload_reg)

    payload_login = {
        "username": "cliente_delivery@test.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/token", data=payload_login)
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_credenciales_invalidas(client):
    payload_login = {
        "username": "no_existe@test.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/token", data=payload_login)
    
    assert response.status_code in [400, 401]

def test_login_falta_form_data(client):
    response = client.post("/api/v1/auth/token", json={"email": "cliente@test.com"})
    
    assert response.status_code == 422
    
def test_registro_email_vacio(client):
    payload = {
        "nombre": "Cliente",
        "apellido": "Sin Email",
        "email": "",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422

def test_registro_password_vacia(client):
    payload = {
        "nombre": "Cliente",
        "apellido": "Sin Password",
        "email": "cliente_sin_password@test.com",
        "password": ""
    }
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422

def test_registro_nombre_vacio(client):
    payload = {
        "nombre": "",
        "apellido": "Sin Nombre",
        "email": "cliente_sin_nombre@test.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422

def test_login_formato_invalido(client):
    payload = {
        "username": "us",
        "password": ""
    }
    response = client.post("/api/v1/auth/token", data=payload)
    
    assert response.status_code in [400, 401, 422]
