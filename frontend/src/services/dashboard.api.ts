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
  disponible?: boolean;
  deleted_at?: string | null;
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
      api.get<ProductoListResponse>('/productos/?page=1&size=100&disponible=true'), // For stock only
    ]);

    const productosBajoStock = (productosRes.data.items || []).filter(
      (p) => Number(p.stock_cantidad) < 10 && p.disponible !== false && !p.deleted_at
    ).length;

    // Calculate backward compatible fields for UI that hasn't changed yet
    const pedidosActivos = estadosRes.data
      .filter((e) => e.estado === 'PENDIENTE' || e.estado === 'CONFIRMADO' || e.estado === 'EN_PREP')
      .reduce((acc, curr) => acc + curr.cantidad, 0);

    // Get today's income if it exists in ventas por dia
    const todayStr = new Date().toLocaleDateString('en-CA'); // Gets local YYYY-MM-DD
    const todayVentas = ventasRes.data.find(v => v.fecha === todayStr);
    const ingresosDia = todayVentas ? Number(todayVentas.ingresos) : 0;

    return {
      resumen: {
        ...resumenRes.data,
        ingresos_totales: Number(resumenRes.data.ingresos_totales),
        ticket_promedio: Number(resumenRes.data.ticket_promedio),
      },
      ventasPorDia: ventasRes.data.map(v => ({ ...v, ingresos: Number(v.ingresos) })),
      productosTop: topRes.data.map(p => ({ ...p, ingresos_generados: Number(p.ingresos_generados), cantidad_vendida: Number(p.cantidad_vendida) })),
      pedidosPorEstado: estadosRes.data,
      ingresosPorFormaPago: formasPagoRes.data.map(i => ({ ...i, ingresos: Number(i.ingresos) })),
      productosBajoStock,
      pedidosActivos,
      ingresosDia
    };
  },
};
