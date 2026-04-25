from sqlmodel import SQLModel, Field
from sqlalchemy import Column, BigInteger, Boolean, ForeignKey


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("productos.id"),
            primary_key=True
        )
    )

    ingrediente_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("ingredientes.id"),
            primary_key=True
        )
    )

    es_removible: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False)
    )