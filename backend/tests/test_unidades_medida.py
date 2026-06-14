def test_crear_unidad_medida_exitosa(client):
    payload = {
        "codigo": "KG",
        "nombre": "Kilogramo",
        "simbolo": "kg"
    }
    response = client.post("/api/v1/unidades-medida/", json=payload)
    
    print("Unidad de medida creada")
    
    assert response.status_code in [200, 201]
    assert response.json()["simbolo"] == "kg"

def test_obtener_lista_unidades(client):
    response = client.get("/api/v1/unidades-medida/")
    
    assert response.status_code == 200
    assert "items" in response.json()

def test_obtener_unidad_por_id(client):
    payload = {
        "codigo": "L",
        "nombre": "Litro",
        "simbolo": "l"
    }
    creacion = client.post("/api/v1/unidades-medida/", json=payload)
    
    if creacion.status_code in [200, 201]:
        unidad_id = creacion.json()["id"]
        response = client.get(f"/api/v1/unidades-medida/{unidad_id}")
        
        assert response.status_code == 200
        assert response.json()["nombre"] == "Litro"
    else:
        assert creacion.status_code in [200, 201, 409]

def test_actualizar_unidad_medida(client):
    payload = {
        "codigo": "GR",
        "nombre": "Gramos",
        "simbolo": "gr"
    }
    creacion = client.post("/api/v1/unidades-medida/", json=payload)
    
    if creacion.status_code in [200, 201]:
        unidad_id = creacion.json()["id"]
        response = client.patch(f"/api/v1/unidades-medida/{unidad_id}", json={"simbolo": "g"})
        
        assert response.status_code == 200
        assert response.json()["simbolo"] == "g"
    else:
        assert creacion.status_code in [200, 201, 409]

def test_eliminar_unidad_medida(client):
    payload = {
        "codigo": "ML",
        "nombre": "Mililitro",
        "simbolo": "ml"
    }
    creacion = client.post("/api/v1/unidades-medida/", json=payload)
    
    if creacion.status_code in [200, 201]:
        unidad_id = creacion.json()["id"]
        response = client.delete(f"/api/v1/unidades-medida/{unidad_id}")
        
        assert response.status_code in [200, 204]
    else:
        assert creacion.status_code in [200, 201, 409]

def test_crear_unidad_medida_falta_dato(client):
    payload = {
        "nombre": "Porcion"
    }
    response = client.post("/api/v1/unidades-medida/", json=payload)
    
    assert response.status_code == 422
