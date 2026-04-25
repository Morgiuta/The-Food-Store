from typing import Optional, List
from pydantic import BaseModel


# CREATE
class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagen_url: Optional[str] = None
    stock_cantidad: int = 0


#  UPDATE
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagen_url: Optional[str] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None


#  READ
class ProductoRead(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio_base: float
    imagen_url: Optional[str]
    stock_cantidad: int
    disponible: bool

    class Config:
        from_attributes = True