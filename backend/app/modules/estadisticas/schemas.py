from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class EstadisticasResumen(BaseModel):
    ingresos_totales: Decimal
    pedidos_completados: int
    ticket_promedio: Decimal

class EstadisticasVentasDia(BaseModel):
    fecha: date
    ingresos: Decimal
    pedidos: int

class EstadisticasProductoTop(BaseModel):
    producto_id: int
    nombre: str
    cantidad_vendida: int
    ingresos_generados: Decimal

class EstadisticasPedidosEstado(BaseModel):
    estado: str
    cantidad: int

class EstadisticasIngresosFormaPago(BaseModel):
    forma_pago: str
    ingresos: Decimal
    cantidad_pagos: int
