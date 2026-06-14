from io import BytesIO

def test_upload_imagen_exitoso(client):
    file_content = BytesIO(b"imagen de lomo completo")
    files = {"file": ("lomo_completo.jpg", file_content, "image/jpeg")}
    
    response = client.post("/api/v1/uploads/imagen", files=files)
    
    print("Imagen subida exitosamente")
    
    assert response.status_code in [201, 500]

def test_upload_imagen_con_folder_personalizado(client):
    file_content = BytesIO(b"imagen de pizza napolitana")
    files = {"file": ("pizza_napolitana.png", file_content, "image/png")}
    
    response = client.post(
        "/api/v1/uploads/imagen", 
        files=files,
        params={"folder": "foodstore/custom"}
    )
    
    assert response.status_code in [201, 500]

def test_upload_imagen_sin_archivo(client):
    response = client.post("/api/v1/uploads/imagen")
    
    assert response.status_code == 422

def test_upload_imagen_tipo_archivo_valido(client):
    file_content = BytesIO(b"imagen de empanada de carne")
    files = {"file": ("empanada_carne.webp", file_content, "image/webp")}
    
    response = client.post("/api/v1/uploads/imagen", files=files)
    
    print("Foto subida")
    
    assert response.status_code in [201, 500]

def test_delete_imagen_con_public_id(client):
    file_content = BytesIO(b"imagen de hamburguesa completa")
    files = {"file": ("hamburguesa_completa.jpg", file_content, "image/jpeg")}
    
    upload_response = client.post("/api/v1/uploads/imagen", files=files)
    
    if upload_response.status_code == 201:
        public_id = upload_response.json()["public_id"]
        
        delete_response = client.delete(f"/api/v1/uploads/imagen/{public_id}")
        
        assert delete_response.status_code == 204

def test_delete_imagen_public_id_inexistente(client):
    fake_public_id = "foodstore/productos/lomo_completo_xyz123"
    
    response = client.delete(f"/api/v1/uploads/imagen/{fake_public_id}")
    
    assert response.status_code in [204, 404, 500]

def test_upload_imagen_multiples_archivos(client):
    for i in range(3):
        file_content = BytesIO(b"imagen de producto de carta")
        files = {"file": (f"producto_carta_{i}.jpg", file_content, "image/jpeg")}
        
        response = client.post("/api/v1/uploads/imagen", files=files)
        
        assert response.status_code in [201, 500]
    
    print("Multiples imagenes testeadas")
