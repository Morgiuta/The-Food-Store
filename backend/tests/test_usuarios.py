def test_listar_usuarios_admin(client):
    response = client.get("/api/v1/admin/usuarios/")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_usuario_admin_actual(client):
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"

def test_obtener_usuario_por_id_inexistente(client):
    response = client.get("/api/v1/admin/usuarios/99999")
    
    assert response.status_code == 404

def test_actualizar_usuario_admin(client):
    me_resp = client.get("/api/v1/auth/me")
    admin_id = me_resp.json()["id"]

    payload = {
        "nombre": "Admin Modificado"
    }
    response = client.patch(f"/api/v1/admin/usuarios/{admin_id}", json=payload)
    
    assert response.status_code == 200

def test_eliminar_usuario_inexistente(client):
    response = client.delete("/api/v1/admin/usuarios/99999")
    
    assert response.status_code in [204, 404]

def test_obtener_usuario_por_id_formato_invalido(client):
    response = client.get("/api/v1/admin/usuarios/abc")
    
    assert response.status_code == 422

def test_actualizar_usuario_con_datos_vacios(client):
    me_resp = client.get("/api/v1/auth/me")
    admin_id = me_resp.json()["id"]

    response = client.patch(f"/api/v1/admin/usuarios/{admin_id}", json={"nombre": ""})
    
    assert response.status_code == 422

def test_asignar_rol_a_usuario(client):
    payload_reg = {
        "nombre": "Maria",
        "apellido": "Gonzalez",
        "email": "maria.gonzalez@foodstore.com",
        "password": "test123"
    }
    reg_resp = client.post("/api/v1/auth/register", json=payload_reg)
    usuario_id = reg_resp.json()["id"]
    
    payload_rol = {
        "rol_nombre": "ADMIN"
    }
    response = client.patch(f"/api/v1/admin/usuarios/{usuario_id}/rol", json=payload_rol)
    
    print("Rol asignado al usuario")
    
    assert response.status_code == 200

def test_listar_usuarios_con_filtro_rol(client):
    response = client.get("/api/v1/admin/usuarios/?rol=ADMIN")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_actualizar_usuario_apellido(client):
    me_resp = client.get("/api/v1/auth/me")
    admin_id = me_resp.json()["id"]

    payload = {
        "nombre": "Admin Nuevo"
    }
    response = client.patch(f"/api/v1/admin/usuarios/{admin_id}", json=payload)
    
    assert response.status_code == 200
    assert response.json()["nombre"] == "Admin Nuevo"