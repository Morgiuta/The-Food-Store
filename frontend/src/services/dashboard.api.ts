import { api } from './api';
import type { PedidosResponse } from '../types/pedido';

export interface DashboardMetrics {
  pedidosActivos: number;
  totalProductos: number;
  totalCategorias: number;
  ingresosDia: number;
}

export const dashboardService = {
  async getMetrics(): Promise<DashboardMetrics> {
    const [pedidosRes, productosRes, categoriasRes] = await Promise.all([
      api.get<PedidosResponse>('/pedidos?solo_hoy=true&limit=100'),
      api.get('/productos?limit=1'),
      api.get('/categorias'),
    ]);

    const pedidos = pedidosRes.data.items || [];
    
    // Activos de hoy: PENDIENTE y CONFIRMADO
    const pedidosActivos = pedidos.filter(
      (p) => p.estado_codigo === 'PENDIENTE' || p.estado_codigo === 'CONFIRMADO'
    ).length;

    // Ingresos del día: El backend ya filtra por el día de hoy, solo filtramos ENTREGADO
    const ingresosDia = pedidos
      .filter((p) => p.estado_codigo === 'ENTREGADO')
      .reduce((acc, curr) => acc + curr.total, 0);

    // Total productos
    const totalProductos = productosRes.data.total || 0;

    // Total categorías
    const totalCategorias = categoriasRes.data.total || categoriasRes.data.items?.length || 0;

    return {
      pedidosActivos,
      totalProductos,
      totalCategorias,
      ingresosDia,
    };
  },
};
