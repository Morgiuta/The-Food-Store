from fastapi import UploadFile, HTTPException, status
import cloudinary.uploader
import cloudinary.api

def upload_imagen(file: UploadFile, folder: str = "foodstore/productos") -> dict:
    allowed_formats = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido: {file.content_type}. Solo jpg, png, webp."
        )

    # El tamaño lo podriamos limitar si leemos los bytes, pero lo mejor es usar SpooledTemporaryFile o limitarlo en el web server.
    # Cloudinary tambien valida pero si queremos limitar a 5MB aca:
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen excede el límite de 5MB."
        )

    try:
        response = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="image"
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir imagen a Cloudinary: {str(e)}"
        )

def delete_imagen(public_id: str):
    try:
        response = cloudinary.uploader.destroy(public_id)
        if response.get("result") != "ok":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudo eliminar la imagen: {response.get('result')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar imagen en Cloudinary: {str(e)}"
        )
