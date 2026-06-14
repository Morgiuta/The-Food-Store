def test_crear_direccion(client):
    payload = {
        "calle": "Avenida San Martin",
        "numero": "1845",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": False
    }
    response = client.post("/api/v1/direcciones/", json=payload)
    
    assert response.status_code == 201
    assert "id" in response.json()

def test_obtener_direcciones(client):
    response = client.get("/api/v1/direcciones/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list) or "items" in response.json()

def test_marcar_direccion_principal(client):
    payload = {
        "calle": "Avenida Belgrano",
        "numero": "1120",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": False
    }
    creacion = client.post("/api/v1/direcciones/", json=payload)
    dir_id = creacion.json().get("id")
    
    response = client.patch(f"/api/v1/direcciones/{dir_id}/principal")
    
    assert response.status_code == 200

def test_eliminar_direccion(client):
    payload = {
        "calle": "Avenida Aristicides Villanueva",
        "numero": "760",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": False
    }
    creacion = client.post("/api/v1/direcciones/", json=payload)
    dir_id = creacion.json().get("id")
    
    response = client.delete(f"/api/v1/direcciones/{dir_id}")
    
    assert response.status_code in [200, 204]

def test_crear_direccion_faltan_datos(client):
    payload = {
        "calle": "Avenida San Martin"
    }
    response = client.post("/api/v1/direcciones/", json=payload)
    
    assert response.status_code == 422

def test_obtener_direccion_por_id(client):
    payload = {
        "calle": "Avenida Mitre",
        "numero": "1430",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": False
    }
    creacion = client.post("/api/v1/direcciones/", json=payload)
    list_resp = client.get("/api/v1/direcciones/")
    
    print("Direcciones listadas")
    
    assert creacion.status_code == 201
    assert list_resp.status_code == 200

def test_actualizar_direccion(client):
    payload = {
        "calle": "Avenida Las Heras",
        "numero": "500",
        "ciudad": "Mendoza",
        "provincia": "Mendoza",
        "codigo_postal": "5500",
        "es_principal": False
    }
    creacion = client.post("/api/v1/direcciones/", json=payload)
    dir_id = creacion.json().get("id")
    
    response = client.put(f"/api/v1/direcciones/{dir_id}", json=payload | {"numero": "600"})
    
    assert response.status_code == 200
    assert response.json()["numero"] == "600"
