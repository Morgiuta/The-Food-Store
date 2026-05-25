from sqlalchemy import func
from sqlmodel import Session, select

from app.modules.auth.models import Usuario, UsuarioRol
from app.modules.producto.models import Producto
from app.modules.ventas.models import (
    DetallePedido,
    EstadoPedido,
    FormaPago,
    HistorialEstadoPedido,
    Pago,
    Pedido,
)


class PedidoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, pedido_id: int) -> Pedido | None:
        pedido = self.session.get(Pedido, pedido_id)
        if pedido is None or pedido.deleted_at is not None:
            return None
        return pedido

    def get_all(self, offset: int = 0, limit: int = 20, solo_hoy: bool = False) -> list[Pedido]:
        stmt = select(Pedido).where(Pedido.deleted_at.is_(None))
        if solo_hoy:
            from datetime import datetime, time
            start_of_day = datetime.combine(datetime.now().date(), time.min)
            stmt = stmt.where(Pedido.updated_at >= start_of_day)
            
        return list(
            self.session.exec(
                stmt.order_by(Pedido.created_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_all(self, solo_hoy: bool = False) -> int:
        stmt = select(func.count(Pedido.id)).where(Pedido.deleted_at.is_(None))
        if solo_hoy:
            from datetime import datetime, time
            start_of_day = datetime.combine(datetime.now().date(), time.min)
            stmt = stmt.where(Pedido.updated_at >= start_of_day)
            
        return int(self.session.exec(stmt).one())

    def get_by_usuario(
        self,
        usuario_id: int,
        offset: int = 0,
        limit: int = 20,
        solo_hoy: bool = False,
    ) -> list[Pedido]:
        stmt = select(Pedido).where(
            Pedido.deleted_at.is_(None),
            Pedido.usuario_id == usuario_id,
        )
        if solo_hoy:
            from datetime import datetime, time
            start_of_day = datetime.combine(datetime.now().date(), time.min)
            stmt = stmt.where(Pedido.updated_at >= start_of_day)
            
        return list(
            self.session.exec(
                stmt.order_by(Pedido.created_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_by_usuario(self, usuario_id: int, solo_hoy: bool = False) -> int:
        stmt = select(func.count(Pedido.id)).where(
            Pedido.deleted_at.is_(None),
            Pedido.usuario_id == usuario_id,
        )
        if solo_hoy:
            from datetime import datetime, time
            start_of_day = datetime.combine(datetime.now().date(), time.min)
            stmt = stmt.where(Pedido.updated_at >= start_of_day)
            
        return int(self.session.exec(stmt).one())

    def create(self, pedido: Pedido) -> Pedido:
        self.session.add(pedido)
        self.session.flush()
        self.session.refresh(pedido)
        return pedido

    def update_estado(
        self,
        pedido: Pedido,
        estado_hacia: str,
        usuario_id: int | None,
        motivo: str | None = None,
    ) -> HistorialEstadoPedido:
        estado_desde = pedido.estado_codigo
        pedido.estado_codigo = estado_hacia
        self.session.add(pedido)
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id or 0,
            estado_desde=estado_desde,
            estado_hacia=estado_hacia,
            usuario_id=usuario_id,
            motivo=motivo,
        )
        self.session.add(historial)
        self.session.flush()
        return historial

    def add_detalle(self, detalle: DetallePedido) -> DetallePedido:
        self.session.add(detalle)
        self.session.flush()
        return detalle

    def add_historial(self, historial: HistorialEstadoPedido) -> HistorialEstadoPedido:
        self.session.add(historial)
        self.session.flush()
        return historial

    def get_forma_pago(self, codigo: str) -> FormaPago | None:
        return self.session.get(FormaPago, codigo)

    def get_estado(self, codigo: str) -> EstadoPedido | None:
        return self.session.get(EstadoPedido, codigo)

    def get_productos_by_ids(self, producto_ids: list[int]) -> list[Producto]:
        if not producto_ids:
            return []
        return list(
            self.session.exec(
                select(Producto).where(
                    Producto.id.in_(producto_ids),
                    Producto.deleted_at.is_(None),
                )
            ).all()
        )

    def save_producto(self, producto: Producto) -> Producto:
        self.session.add(producto)
        self.session.flush()
        return producto

    def list_detalles(self, pedido_id: int) -> list[DetallePedido]:
        return list(
            self.session.exec(
                select(DetallePedido)
                .where(DetallePedido.pedido_id == pedido_id)
                .order_by(DetallePedido.created_at)
            ).all()
        )

    def list_pagos(self, pedido_id: int) -> list[Pago]:
        return list(
            self.session.exec(
                select(Pago).where(Pago.pedido_id == pedido_id).order_by(Pago.created_at)
            ).all()
        )

    def list_historial(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        return list(
            self.session.exec(
                select(HistorialEstadoPedido)
                .where(HistorialEstadoPedido.pedido_id == pedido_id)
                .order_by(HistorialEstadoPedido.created_at)
            ).all()
        )

    def get_pago_by_idempotency_key(self, idempotency_key: str) -> Pago | None:
        return self.session.exec(
            select(Pago).where(Pago.idempotency_key == idempotency_key)
        ).first()

    def add_pago(self, pago: Pago) -> Pago:
        self.session.add(pago)
        self.session.flush()
        self.session.refresh(pago)
        return pago

    def get_role_codes(self, usuario_id: int) -> list[str]:
        return list(
            self.session.exec(
                select(UsuarioRol.rol_codigo).where(
                    UsuarioRol.usuario_id == usuario_id,
                    UsuarioRol.deleted_at.is_(None),
                )
            ).all()
        )

    def usuario_exists(self, usuario_id: int) -> bool:
        return self.session.get(Usuario, usuario_id) is not None
