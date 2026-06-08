from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.base_model import utcnow
from app.modules.pedidos.repository import PedidoRepository
from app.modules.pedidos.schemas import PedidoList
from app.modules.pedidos.unit_of_work import PedidosUnitOfWork
from app.modules.producto.models import Producto
from app.modules.ventas.models import DetallePedido, HistorialEstadoPedido, Pago, Pedido
from app.modules.ventas.schemas import (
    DetallePedidoPublic,
    HistorialEstadoPedidoPublic,
    PagoCreate,
    PagoPublic,
    PedidoCreate,
    PedidoPublic,
)

TRANSICIONES_VALIDAS = {
    "PENDIENTE": {"CONFIRMADO", "CANCELADO"},
    "CONFIRMADO": {"EN_PREP", "CANCELADO"},
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


AVANCE_ESTADOS_VALIDOS = {
    "PENDIENTE": "CONFIRMADO",
    "CONFIRMADO": "EN_PREP",
    "EN_PREP": "EN_CAMINO",
    "EN_CAMINO": "ENTREGADO",
}

ESTADOS_CANCELABLES = {"PENDIENTE", "CONFIRMADO"}

EVENTOS_WS = {
    "PENDIENTE": "NUEVO_PEDIDO",
    "CONFIRMADO": "PEDIDO_CONFIRMADO",
    "EN_PREP": "PEDIDO_EN_PREPARACION",
    "EN_CAMINO": "PEDIDO_EN_CAMINO",
    "ENTREGADO": "PEDIDO_ENTREGADO",
    "CANCELADO": "PEDIDO_CANCELADO",
}

ROLES_POR_ESTADO = {
    "PENDIENTE": ["PEDIDOS", "STOCK", "ADMIN"],
    "CONFIRMADO": ["PEDIDOS", "STOCK", "ADMIN"],
    "EN_PREP": ["STOCK", "PEDIDOS", "ADMIN"],
    "EN_CAMINO": ["PEDIDOS", "STOCK", "ADMIN"],
    "ENTREGADO": ["PEDIDOS", "ADMIN"],
    "CANCELADO": ["PEDIDOS", "STOCK", "ADMIN"],
}


class PedidosService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.pedidos = PedidoRepository(session)

    def list_pedidos_for_user(
        self,
        current_user_id: int,
        page: int = 1,
        limit: int = 10,
    ) -> PedidoList:
        offset = (page - 1) * limit
        if self.can_view_all(current_user_id):
            pedidos = self.pedidos.get_all(offset=offset, limit=limit)
            total = self.pedidos.count_all()
        else:
            pedidos = self.pedidos.get_by_usuario(
                current_user_id,
                offset=offset,
                limit=limit,
            )
            total = self.pedidos.count_by_usuario(current_user_id)

        return PedidoList(
            items=[self._to_public(pedido) for pedido in pedidos],
            total=total,
            page=page,
            limit=limit,
        )

    def can_view_all(self, usuario_id: int) -> bool:
        return self._has_any_role(usuario_id, {"ADMIN", "PEDIDOS"})

    def is_admin(self, usuario_id: int) -> bool:
        return self._has_any_role(usuario_id, {"ADMIN"})

    async def create_pedido(self, usuario_id: int, data: PedidoCreate) -> PedidoPublic:
        pedido_id: int

        with PedidosUnitOfWork(self.session) as uow:
            self._assert_usuario_exists(usuario_id, uow.pedidos)
            forma_pago = uow.pedidos.get_forma_pago(data.forma_pago_codigo)
            if forma_pago is None or not forma_pago.habilitado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"FormaPago '{data.forma_pago_codigo}' no habilitada o inexistente",
                )

            productos = self._get_productos_for_detalles(data, uow.pedidos)
            self._validate_productos_disponibles(data, productos)
            self._validate_stock_suficiente(data, productos)
            subtotal = self._calculate_subtotal(data, productos)
            total = subtotal - data.descuento + data.costo_envio
            if total < 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El total del pedido no puede ser negativo",
                )

            for detalle_data in data.detalles:
                producto = productos[detalle_data.producto_id]
                producto.stock_cantidad -= detalle_data.cantidad
                if producto.stock_cantidad == 0:
                    producto.disponible = False
                producto.updated_at = utcnow()
                uow.pedidos.save_producto(producto)

            pedido = uow.pedidos.create(
                Pedido(
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
            )

            if pedido.id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo crear el pedido",
                )

            for detalle_data in data.detalles:
                producto = productos[detalle_data.producto_id]
                uow.pedidos.add_detalle(
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

            uow.pedidos.add_historial(
                HistorialEstadoPedido(
                    pedido_id=pedido.id,
                    estado_desde=None,
                    estado_hacia="PENDIENTE",
                    usuario_id=usuario_id,
                    motivo="Creacion del pedido",
                )
            )
            pedido_id = pedido.id

        result = self.get_pedido(pedido_id)
        await self._emit_ws_events(result)
        return result

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

    async def change_estado(
        self,
        pedido_id: int,
        estado_hacia: str,
        usuario_id: int | None,
        motivo: str | None = None,
    ) -> PedidoPublic:
        with PedidosUnitOfWork(self.session) as uow:
            pedido = self._get_pedido_or_404(pedido_id, uow.pedidos)
            estado_hacia = estado_hacia.strip().upper()
            self._validate_transition(pedido.estado_codigo, estado_hacia, motivo, uow.pedidos)
            pedido.updated_at = utcnow()
            uow.pedidos.update_estado(pedido, estado_hacia, usuario_id, motivo)

        result = self.get_pedido(pedido_id)
        await self._emit_ws_events(result)
        return result

    async def avanzar_estado(
        self,
        pedido_id: int,
        nuevo_estado: str,
        usuario_id: int | None,
    ) -> PedidoPublic:
        with PedidosUnitOfWork(self.session) as uow:
            pedido = self._get_pedido_or_404(pedido_id, uow.pedidos)
            nuevo_estado = nuevo_estado.strip().upper()
            esperado = AVANCE_ESTADOS_VALIDOS.get(pedido.estado_codigo)

            if esperado != nuevo_estado:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "Transicion invalida: "
                        f"{pedido.estado_codigo} -> {nuevo_estado}"
                    ),
                )

            pedido.updated_at = utcnow()
            uow.pedidos.update_estado(
                pedido=pedido,
                estado_hacia=nuevo_estado,
                usuario_id=usuario_id,
                motivo=None,
            )

        result = self.get_pedido(pedido_id)
        await self._emit_ws_events(result)
        return result

    async def cancelar_pedido(
        self,
        pedido_id: int,
        usuario_id: int,
    ) -> PedidoPublic:
        with PedidosUnitOfWork(self.session) as uow:
            pedido = self._get_pedido_or_404(pedido_id, uow.pedidos)

            if not self.is_admin(usuario_id) and pedido.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puede cancelar un pedido de otro usuario",
                )

            if pedido.estado_codigo not in ESTADOS_CANCELABLES:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "Solo se puede cancelar un pedido en estado "
                        "PENDIENTE o CONFIRMADO"
                    ),
                )

            pedido.updated_at = utcnow()
            uow.pedidos.update_estado(
                pedido=pedido,
                estado_hacia="CANCELADO",
                usuario_id=usuario_id,
                motivo="Cancelacion del pedido",
            )

        result = self.get_pedido(pedido_id)
        await self._emit_ws_events(result)
        return result

    async def register_pago(self, pedido_id: int, data: PagoCreate) -> PagoPublic:
        estado_actualizado = False
        try:
            with PedidosUnitOfWork(self.session) as uow:
                pedido = self._get_pedido_or_404(pedido_id, uow.pedidos)

                existing = uow.pedidos.get_pago_by_idempotency_key(data.idempotency_key)
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
                uow.pedidos.add_pago(pago)

                next_estado = MP_STATUS_TO_ESTADO.get(data.mp_status)
                if next_estado is not None and pedido.estado_codigo != next_estado:
                    try:
                        self._validate_transition(
                            pedido.estado_codigo,
                            next_estado,
                            data.mp_status_detail,
                            uow.pedidos,
                        )
                        pedido.updated_at = utcnow()
                        uow.pedidos.update_estado(
                            pedido,
                            next_estado,
                            usuario_id=None,
                            motivo=data.mp_status_detail or f"Pago {data.mp_status}",
                        )
                        estado_actualizado = True
                    except HTTPException:
                        pass

        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago ya fue registrado",
            ) from exc

        self.session.refresh(pago)
        result = self._pago_to_public(pago)
        if estado_actualizado:
            await self._emit_ws_events(self.get_pedido(pedido_id))
        return result

    async def _emit_ws_events(self, pedido: PedidoPublic) -> None:
        event_type = EVENTOS_WS.get(pedido.estado_codigo)
        if not event_type:
            return

        from app.core.websocket import manager

        roles = ROLES_POR_ESTADO.get(pedido.estado_codigo, [])
        await manager.broadcast_to_order_and_roles(
            order_id=pedido.id,
            roles=roles,
            event_type=event_type,
            data=pedido.model_dump(mode="json"),
        )

    def _has_any_role(self, usuario_id: int, roles: set[str]) -> bool:
        current_roles = set(self.pedidos.get_role_codes(usuario_id))
        return bool(current_roles.intersection(roles))

    def _assert_usuario_exists(
        self,
        usuario_id: int,
        repo: PedidoRepository | None = None,
    ) -> None:
        repo = repo or self.pedidos
        if not repo.usuario_exists(usuario_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={usuario_id} no encontrado",
            )

    def _get_productos_for_detalles(
        self,
        data: PedidoCreate,
        repo: PedidoRepository | None = None,
    ) -> dict[int, Producto]:
        repo = repo or self.pedidos
        producto_ids = [detalle.producto_id for detalle in data.detalles]
        if len(producto_ids) != len(set(producto_ids)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="DetallePedido no permite repetir producto_id en el mismo pedido",
            )

        productos = {
            producto.id: producto
            for producto in repo.get_productos_by_ids(producto_ids)
            if producto.id is not None
        }
        missing_ids = set(producto_ids) - set(productos)
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Productos no encontrados: {sorted(missing_ids)}",
            )
        return productos

    def _validate_productos_disponibles(
        self,
        data: PedidoCreate,
        productos: dict[int, Producto],
    ) -> None:
        unavailable = [
            detalle.producto_id
            for detalle in data.detalles
            if not productos[detalle.producto_id].disponible
        ]
        if unavailable:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Productos no disponibles: {sorted(unavailable)}",
            )

    def _validate_stock_suficiente(
        self,
        data: PedidoCreate,
        productos: dict[int, Producto],
    ) -> None:
        insufficient = [
            {
                "producto_id": detalle.producto_id,
                "stock_disponible": productos[detalle.producto_id].stock_cantidad,
                "cantidad_pedida": detalle.cantidad,
            }
            for detalle in data.detalles
            if productos[detalle.producto_id].stock_cantidad < detalle.cantidad
        ]
        if insufficient:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "mensaje": "Stock insuficiente para uno o mas productos",
                    "productos": insufficient,
                },
            )

    def _calculate_subtotal(
        self,
        data: PedidoCreate,
        productos: dict[int, Producto],
    ) -> Decimal:
        subtotal = Decimal("0.00")
        for detalle in data.detalles:
            subtotal += productos[detalle.producto_id].precio_base * detalle.cantidad
        return subtotal

    def _get_pedido_or_404(
        self,
        pedido_id: int,
        repo: PedidoRepository | None = None,
    ) -> Pedido:
        repo = repo or self.pedidos
        pedido = repo.get_by_id(pedido_id)
        if pedido is None:
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
        repo: PedidoRepository | None = None,
    ) -> None:
        repo = repo or self.pedidos
        estado_actual = repo.get_estado(estado_desde)
        estado_destino = repo.get_estado(estado_hacia)
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

    def _to_public(self, pedido: Pedido) -> PedidoPublic:
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
                DetallePedidoPublic.model_validate(detalle)
                for detalle in self.pedidos.list_detalles(pedido.id or 0)
            ],
            pagos=[
                self._pago_to_public(pago)
                for pago in self.pedidos.list_pagos(pedido.id or 0)
            ],
            historial=[
                HistorialEstadoPedidoPublic.model_validate(item)
                for item in self.pedidos.list_historial(pedido.id or 0)
            ],
        )

    def _pago_to_public(self, pago: Pago) -> PagoPublic:
        return PagoPublic.model_validate(pago)
