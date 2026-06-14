from sqlmodel import Field, SQLModel

from app.modules.ventas.schemas import PagoPublic

__all__ = ["CrearPagoRequest", "CrearPagoResponse", "WebhookResponse", "PagoPublic"]


class CrearPagoRequest(SQLModel):
    pedido_id: int = Field(gt=0)


class CrearPagoResponse(SQLModel):
    pedido_id: int
    preference_id: str
    init_point: str
    sandbox_init_point: str | None = None
    public_key: str


class WebhookResponse(SQLModel):
    status: str = "ok"
