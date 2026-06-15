from datetime import date
from typing import Optional
from decimal import Decimal

from sqlmodel import Session

from app.modules.estadisticas.repository import EstadisticasRepository
from app.modules.estadisticas.schemas import (
    EstadisticasResumen,
    EstadisticasVentasDia,
    EstadisticasProductoTop,
    EstadisticasPedidosEstado,
    EstadisticasIngresosFormaPago
)

class EstadisticasService:
    def __init__(self, session: Session):
        self.repo = EstadisticasRepository(session)

    def get_resumen(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> EstadisticasResumen:
        ingresos, pedidos = self.repo.get_resumen(desde, hasta)
        
        ticket_promedio = Decimal("0.00")
        if pedidos > 0:
            ticket_promedio = Decimal(ingresos) / Decimal(pedidos)
            
        return EstadisticasResumen(
            ingresos_totales=Decimal(ingresos),
            pedidos_completados=pedidos,
            ticket_promedio=ticket_promedio
        )

    def get_ventas_por_dia(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[EstadisticasVentasDia]:
        results = self.repo.get_ventas_por_dia(desde, hasta)
        return [
            EstadisticasVentasDia(
                fecha=row[0],
                ingresos=Decimal(row[1] or 0),
                pedidos=row[2] or 0
            ) for row in results
        ]

    def get_productos_top(self, limite: int = 5, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[EstadisticasProductoTop]:
        results = self.repo.get_productos_top(limite, desde, hasta)
        return [
            EstadisticasProductoTop(
                producto_id=row[0],
                nombre=row[1] or "Desconocido",
                cantidad_vendida=row[2] or 0,
                ingresos_generados=Decimal(row[3] or 0)
            ) for row in results
        ]

    def get_pedidos_por_estado(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[EstadisticasPedidosEstado]:
        results = self.repo.get_pedidos_por_estado(desde, hasta)
        return [
            EstadisticasPedidosEstado(
                estado=row[0],
                cantidad=row[1] or 0
            ) for row in results
        ]

    def get_ingresos_por_forma_pago(self, desde: Optional[date] = None, hasta: Optional[date] = None) -> list[EstadisticasIngresosFormaPago]:
        results = self.repo.get_ingresos_por_forma_pago(desde, hasta)
        return [
            EstadisticasIngresosFormaPago(
                forma_pago=row[0],
                ingresos=Decimal(row[1] or 0),
                cantidad_pagos=row[2] or 0
            ) for row in results
        ]
