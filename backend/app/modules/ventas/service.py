from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.base_model import utcnow
from app.modules.auth.models import Usuario
from app.modules.producto.models import Producto
from app.modules.ventas.models import (
    DetallePedido,
    EstadoPedido,
    FormaPago,
    HistorialEstadoPedido,
    Pago,
    Pedido,
)
from app.modules.ventas.schemas import (
    DetallePedidoPublic,
    EstadoPedidoPublic,
    FormaPagoPublic,
    HistorialEstadoPedidoPublic,
    PagoCreate,
    PagoPublic,
    PedidoCreate,
    PedidoList,
    PedidoPublic,
)


ESTADOS_SEED = [
    ("PENDIENTE", "Pendiente", 1, False),
    ("CONFIRMADO", "Confirmado", 2, False),
    ("EN_PREP", "En preparacion", 3, False),
    ("EN_CAMINO", "En camino", 4, False),
    ("ENTREGADO", "Entregado", 5, True),
    ("CANCELADO", "Cancelado", 6, True),
]

FORMAS_PAGO_SEED = [
    ("MERCADOPAGO", "Mercado Pago", True),
    ("EFECTIVO", "Efectivo", True),
    ("TRANSFERENCIA", "Transferencia bancaria", True),
]

TRANSICIONES_VALIDAS = {
    "PENDIENTE": {"CONFIRMADO", "CANCELADO"},
    "CONFIRMADO": {"EN_PROCESO", "EN_PREP", "CANCELADO"},
    "EN_PROCESO": {"LISTO", "CANCELADO"},
    "LISTO": {"ENTREGADO"},
    "EN_PREP": {"EN_CAMINO", "CANCELADO"},
    "EN_CAMINO": {"ENTREGADO"},
}

MP_STATUS_TO_ESTADO = {
    "approved": "CONFIRMADO",
    "rejected": "CANCELADO",
    "cancelled": "CANCELADO",
    "refunded": "CANCELADO",
    "charged_back": "CANCELADO",
}


def ensure_ventas_seed_data(session: Session) -> None:
    for codigo, descripcion, habilitado in FORMAS_PAGO_SEED:
        forma_pago = session.get(FormaPago, codigo)
        if forma_pago is None:
            session.add(
                FormaPago(
                    codigo=codigo,
                    descripcion=descripcion,
                    habilitado=habilitado,
                )
            )

    for codigo, descripcion, orden, es_terminal in ESTADOS_SEED:
        estado = session.get(EstadoPedido, codigo)
        if estado is None:
            session.add(
                EstadoPedido(
                    codigo=codigo,
                    descripcion=descripcion,
                    orden=orden,
                    es_terminal=es_terminal,
                )
            )

    session.commit()


class VentasService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_formas_pago(self) -> list[FormaPagoPublic]:
        statement = select(FormaPago).order_by(FormaPago.codigo)
        return [FormaPagoPublic.model_validate(item) for item in self.session.exec(statement)]

    def list_estados(self) -> list[EstadoPedidoPublic]:
        statement = select(EstadoPedido).order_by(EstadoPedido.orden)
        return [EstadoPedidoPublic.model_validate(item) for item in self.session.exec(statement)]

    def create_pedido(self, usuario_id: int, data: PedidoCreate) -> PedidoPublic:
        self._assert_usuario_exists(usuario_id)
        forma_pago = self.session.get(FormaPago, data.forma_pago_codigo)
        if forma_pago is None or not forma_pago.habilitado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FormaPago '{data.forma_pago_codigo}' no habilitada o inexistente",
            )

        productos = self._get_productos_for_detalles(data)
        subtotal = self._calculate_subtotal(data, productos)
        total = subtotal - data.descuento + data.costo_envio
        if total < 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El total del pedido no puede ser negativo",
            )

        pedido = Pedido(
            usuario_id=usuario_id,
            direccion_id=data.direccion_id,
            estado_codigo="PENDIENTE",
            forma_pago_codigo=data.forma_pago_codigo,
            subtotal=subtotal,
            descuento=data.descuento,
            costo_envio=data.costo_envio,
            total=total,
            notas=data.notas,
        )
        self.session.add(pedido)
        self.session.flush()

        if pedido.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo crear el pedido",
            )

        for detalle_data in data.detalles:
            producto = productos[detalle_data.producto_id]
            self.session.add(
                DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=producto.id,
                    cantidad=detalle_data.cantidad,
                    nombre_snapshot=producto.nombre,
                    precio_snapshot=producto.precio_base,
                    subtotal_snapshot=producto.precio_base * detalle_data.cantidad,
                    personalizacion=detalle_data.personalizacion,
                )
            )

        self.session.add(
            HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_hacia="PENDIENTE",
                usuario_id=usuario_id,
                motivo="Creacion del pedido",
            )
        )
        self.session.commit()
        return self.get_pedido(pedido.id)

    def list_pedidos(
        self,
        offset: int = 0,
        limit: int = 20,
        usuario_id: int | None = None,
    ) -> PedidoList:
        filters = [Pedido.deleted_at.is_(None)]
        if usuario_id is not None:
            filters.append(Pedido.usuario_id == usuario_id)

        statement = (
            select(Pedido)
            .where(*filters)
            .order_by(Pedido.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = len(self.session.exec(select(Pedido).where(*filters)).all())
        return PedidoList(
            data=[self._to_public(pedido) for pedido in self.session.exec(statement)],
            total=total,
        )

    def get_pedido(
        self,
        pedido_id: int,
        usuario_id: int | None = None,
    ) -> PedidoPublic:
        pedido = self._get_pedido_or_404(pedido_id)
        if usuario_id is not None and pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido con id={pedido_id} no encontrado",
            )
        return self._to_public(pedido)

    def change_estado(
        self,
        pedido_id: int,
        estado_hacia: str,
        usuario_id: int | None,
        motivo: str | None = None,
    ) -> PedidoPublic:
        pedido = self._get_pedido_or_404(pedido_id)
        estado_hacia = estado_hacia.strip().upper()
        self._validate_transition(pedido.estado_codigo, estado_hacia, motivo)
        self._append_estado(pedido, estado_hacia, usuario_id, motivo)
        self.session.commit()
        return self.get_pedido(pedido_id)

    def register_pago(self, pedido_id: int, data: PagoCreate) -> PagoPublic:
        pedido = self._get_pedido_or_404(pedido_id)

        existing = self.session.exec(
            select(Pago).where(Pago.idempotency_key == data.idempotency_key)
        ).first()
        if existing is not None:
            return self._pago_to_public(existing)

        pago = Pago(
            pedido_id=pedido.id,
            mp_payment_id=data.mp_payment_id,
            mp_status=data.mp_status,
            mp_status_detail=data.mp_status_detail,
            external_reference=data.external_reference,
            idempotency_key=data.idempotency_key,
            transaction_amount=data.transaction_amount,
            payment_method=data.payment_method,
        )
        self.session.add(pago)

        next_estado = MP_STATUS_TO_ESTADO.get(data.mp_status)
        if next_estado is not None and pedido.estado_codigo != next_estado:
            try:
                self._validate_transition(pedido.estado_codigo, next_estado, data.mp_status_detail)
                self._append_estado(
                    pedido,
                    next_estado,
                    usuario_id=None,
                    motivo=data.mp_status_detail or f"Pago {data.mp_status}",
                )
            except HTTPException:
                pass

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago ya fue registrado",
            ) from exc

        self.session.refresh(pago)
        return self._pago_to_public(pago)

    def _assert_usuario_exists(self, usuario_id: int) -> None:
        if self.session.get(Usuario, usuario_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={usuario_id} no encontrado",
            )

    def _get_productos_for_detalles(
        self,
        data: PedidoCreate,
    ) -> dict[int, Producto]:
        producto_ids = [detalle.producto_id for detalle in data.detalles]
        if len(producto_ids) != len(set(producto_ids)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="DetallePedido no permite repetir producto_id en el mismo pedido",
            )

        productos = {
            producto.id: producto
            for producto in self.session.exec(
                select(Producto).where(
                    Producto.id.in_(producto_ids),
                    Producto.deleted_at.is_(None),
                )
            ).all()
            if producto.id is not None
        }
        missing_ids = set(producto_ids) - set(productos)
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Productos no encontrados: {sorted(missing_ids)}",
            )
        return productos

    def _calculate_subtotal(
        self,
        data: PedidoCreate,
        productos: dict[int, Producto],
    ) -> Decimal:
        subtotal = Decimal("0.00")
        for detalle in data.detalles:
            subtotal += productos[detalle.producto_id].precio_base * detalle.cantidad
        return subtotal

    def _get_pedido_or_404(self, pedido_id: int) -> Pedido:
        pedido = self.session.get(Pedido, pedido_id)
        if pedido is None or pedido.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido con id={pedido_id} no encontrado",
            )
        return pedido

    def _validate_transition(
        self,
        estado_desde: str,
        estado_hacia: str,
        motivo: str | None,
    ) -> None:
        estado_actual = self.session.get(EstadoPedido, estado_desde)
        estado_destino = self.session.get(EstadoPedido, estado_hacia)
        if estado_actual is None or estado_destino is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="EstadoPedido inexistente",
            )
        if estado_actual.es_terminal:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede cambiar un pedido en estado terminal",
            )
        if estado_hacia not in TRANSICIONES_VALIDAS.get(estado_desde, set()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transicion invalida: {estado_desde} -> {estado_hacia}",
            )
        if estado_hacia == "CANCELADO" and not motivo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El motivo es obligatorio para cancelar un pedido",
            )

    def _append_estado(
        self,
        pedido: Pedido,
        estado_hacia: str,
        usuario_id: int | None,
        motivo: str | None,
    ) -> None:
        estado_desde = pedido.estado_codigo
        pedido.estado_codigo = estado_hacia
        pedido.updated_at = utcnow()
        self.session.add(pedido)
        self.session.add(
            HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_desde,
                estado_hacia=estado_hacia,
                usuario_id=usuario_id,
                motivo=motivo,
            )
        )

    def _to_public(self, pedido: Pedido) -> PedidoPublic:
        detalles = self.session.exec(
            select(DetallePedido)
            .where(DetallePedido.pedido_id == pedido.id)
            .order_by(DetallePedido.created_at)
        ).all()
        pagos = self.session.exec(
            select(Pago).where(Pago.pedido_id == pedido.id).order_by(Pago.created_at)
        ).all()
        historial = self.session.exec(
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido.id)
            .order_by(HistorialEstadoPedido.created_at)
        ).all()
        return PedidoPublic(
            id=pedido.id or 0,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
            estado_codigo=pedido.estado_codigo,
            forma_pago_codigo=pedido.forma_pago_codigo,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            notas=pedido.notas,
            created_at=pedido.created_at,
            updated_at=pedido.updated_at,
            deleted_at=pedido.deleted_at,
            detalles=[
                DetallePedidoPublic.model_validate(detalle) for detalle in detalles
            ],
            pagos=[self._pago_to_public(pago) for pago in pagos],
            historial=[
                HistorialEstadoPedidoPublic.model_validate(item) for item in historial
            ],
        )

    def _pago_to_public(self, pago: Pago) -> PagoPublic:
        return PagoPublic.model_validate(pago)
