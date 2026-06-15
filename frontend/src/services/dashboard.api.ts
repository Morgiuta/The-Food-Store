import { api } from './api';

export interface EstadisticasResumen {
  ingresos_totales: number;
  pedidos_completados: number;
  ticket_promedio: number;
}

export interface EstadisticasVentasDia {
  fecha: string;
  ingresos: number;
  pedidos: number;
}

export interface EstadisticasProductoTop {
  producto_id: number;
  nombre: string;
  cantidad_vendida: number;
  ingresos_generados: number;
}

export interface EstadisticasPedidosEstado {
  estado: string;
  cantidad: number;
}

export interface EstadisticasIngresosFormaPago {
  forma_pago: string;
  ingresos: number;
  cantidad_pagos: number;
}

export interface DashboardMetrics {
  resumen: EstadisticasResumen;
  ventasPorDia: EstadisticasVentasDia[];
  productosTop: EstadisticasProductoTop[];
  pedidosPorEstado: EstadisticasPedidosEstado[];
  ingresosPorFormaPago: EstadisticasIngresosFormaPago[];
  productosBajoStock: number;
  pedidosActivos: number;
  ingresosDia: number;
}

interface ProductoItem {
  stock_cantidad: number;
}

interface ProductoListResponse {
  items: ProductoItem[];
  total: number;
}

export const dashboardService = {
  async getMetrics(desde?: string, hasta?: string): Promise<DashboardMetrics> {
    const params = new URLSearchParams();
    if (desde) params.append('desde', desde);
    if (hasta) params.append('hasta', hasta);

    const queryStr = params.toString() ? `?${params.toString()}` : '';

    const [
      resumenRes,
      ventasRes,
      topRes,
      estadosRes,
      formasPagoRes,
      productosRes
    ] = await Promise.all([
      api.get<EstadisticasResumen>(`/estadisticas/resumen${queryStr}`),
      api.get<EstadisticasVentasDia[]>(`/estadisticas/ventas${queryStr}`),
      api.get<EstadisticasProductoTop[]>(`/estadisticas/productos-top${queryStr}`),
      api.get<EstadisticasPedidosEstado[]>(`/estadisticas/pedidos-por-estado${queryStr}`),
      api.get<EstadisticasIngresosFormaPago[]>(`/estadisticas/ingresos${queryStr}`),
      api.get<ProductoListResponse>('/productos/?page=1&size=1000'), // For stock only
    ]);

    const productosBajoStock = (productosRes.data.items || []).filter(
      (p) => Number(p.stock_cantidad) < 10
    ).length;

    // Calculate backward compatible fields for UI that hasn't changed yet
    const pedidosActivos = estadosRes.data
      .filter((e) => e.estado === 'PENDIENTE' || e.estado === 'CONFIRMADO' || e.estado === 'EN_PREP')
      .reduce((acc, curr) => acc + curr.cantidad, 0);

    // Get today's income if it exists in ventas por dia
    const todayStr = new Date().toISOString().split('T')[0];
    const todayVentas = ventasRes.data.find(v => v.fecha === todayStr);
    const ingresosDia = todayVentas ? todayVentas.ingresos : 0;

    return {
      resumen: resumenRes.data,
      ventasPorDia: ventasRes.data,
      productosTop: topRes.data,
      pedidosPorEstado: estadosRes.data,
      ingresosPorFormaPago: formasPagoRes.data,
      productosBajoStock,
      pedidosActivos,
      ingresosDia
    };
  },
};
