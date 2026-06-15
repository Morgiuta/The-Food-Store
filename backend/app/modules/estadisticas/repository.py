from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, select, desc
from sqlmodel import Session

from app.modules.ventas.models import Pedido, DetallePedido, Pago

class EstadisticasRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_resumen(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> tuple:
        query = select(
            func.sum(Pedido.total).label("ingresos_totales"),
            func.count(Pedido.id).label("pedidos_completados")
        ).where(Pedido.estado_codigo != "CANCELADO")
        
        if desde:
            query = query.where(func.date(Pedido.created_at) >= desde)
        if hasta:
            query = query.where(func.date(Pedido.created_at) <= hasta)
            
        result = self.session.execute(query).first()
        ingresos = result[0] or 0
        pedidos = result[1] or 0
        return ingresos, pedidos

    def get_ventas_por_dia(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[tuple]:
        query = select(
            func.date(Pedido.created_at).label("fecha"),
            func.sum(Pedido.total).label("ingresos"),
            func.count(Pedido.id).label("pedidos")
        ).where(Pedido.estado_codigo != "CANCELADO")
        
        if desde:
            query = query.where(func.date(Pedido.created_at) >= desde)
        if hasta:
            query = query.where(func.date(Pedido.created_at) <= hasta)
            
        query = query.group_by(func.date(Pedido.created_at)).order_by(func.date(Pedido.created_at))
        return self.session.execute(query).all()

    def get_productos_top(self, limite: int = 5, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[tuple]:
        query = select(
            DetallePedido.producto_id,
            func.max(DetallePedido.nombre_snapshot).label("nombre"),
            func.sum(DetallePedido.cantidad).label("cantidad_vendida"),
            func.sum(DetallePedido.subtotal_snapshot).label("ingresos_generados")
        ).join(Pedido, DetallePedido.pedido_id == Pedido.id) \
         .where(Pedido.estado_codigo != "CANCELADO")
         
        if desde:
            query = query.where(func.date(Pedido.created_at) >= desde)
        if hasta:
            query = query.where(func.date(Pedido.created_at) <= hasta)
            
        query = query.group_by(DetallePedido.producto_id) \
                     .order_by(desc("cantidad_vendida")) \
                     .limit(limite)
                     
        return self.session.execute(query).all()

    def get_pedidos_por_estado(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[tuple]:
        query = select(
            Pedido.estado_codigo,
            func.count(Pedido.id).label("cantidad")
        )
        
        if desde:
            query = query.where(func.date(Pedido.created_at) >= desde)
        if hasta:
            query = query.where(func.date(Pedido.created_at) <= hasta)
            
        query = query.group_by(Pedido.estado_codigo)
        return self.session.execute(query).all()

    def get_ingresos_por_forma_pago(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[tuple]:
        query = select(
            Pedido.forma_pago_codigo,
            func.sum(Pedido.total).label("ingresos"),
            func.count(Pedido.id).label("cantidad_pagos")
        ).where(Pedido.estado_codigo != "CANCELADO")
        
        if desde:
            query = query.where(func.date(Pedido.created_at) >= desde)
        if hasta:
            query = query.where(func.date(Pedido.created_at) <= hasta)
            
        query = query.group_by(Pedido.forma_pago_codigo)
        return self.session.execute(query).all()
