from fastapi import APIRouter, Depends, UploadFile, File, status
from typing import Annotated
from urllib.parse import unquote

from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import Usuario
from app.modules.uploads.schemas import CloudinaryResponse
from app.modules.uploads import service as uploads_service

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("/imagen", response_model=CloudinaryResponse, status_code=status.HTTP_201_CREATED)
def upload_imagen(
    file: UploadFile = File(...),
    folder: str = "foodstore/productos",
    _current_user=Depends(require_permission("upload", "manage"))
):
    """
    Sube una imagen a Cloudinary. Recibe multipart/form-data.
    Devuelve secure_url y public_id.
    """
    response = uploads_service.upload_imagen(file, folder)
    return CloudinaryResponse(
        secure_url=response.get("secure_url"),
        public_id=response.get("public_id"),
        width=response.get("width"),
        height=response.get("height"),
        format=response.get("format"),
        resource_type=response.get("resource_type")
    )

@router.delete("/imagen/{public_id:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_imagen(
    public_id: str,
    _current_user=Depends(require_permission("upload", "manage"))
):
    """
    Elimina una imagen de Cloudinary por su public_id.
    """
    decoded_public_id = unquote(public_id)
    uploads_service.delete_imagen(decoded_public_id)
