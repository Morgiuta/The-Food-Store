import { api } from './api';
import type { PedidosResponse } from '../types/pedido';

export interface DashboardMetrics {
  pedidosActivos: number;
  ingresosDia: number;
  productosBajoStock: number;
}

interface ProductoItem {
  stock_cantidad: number;
}

interface ProductoListResponse {
  items: ProductoItem[];
  total: number;
}

function isToday(value: string): boolean {
  const date = new Date(value);
  const today = new Date();

  return (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  );
}

function wasDeliveredToday(pedido: PedidosResponse['items'][number]): boolean {
  const deliveredEntry = pedido.historial.find(
    (entry) => entry.estado_hacia === 'ENTREGADO',
  );

  return isToday(deliveredEntry?.created_at ?? pedido.updated_at);
}

export const dashboardService = {
  async getMetrics(): Promise<DashboardMetrics> {
    const [pedidosRes, productosRes] = await Promise.all([
      api.get<PedidosResponse>('/pedidos?page=1&limit=100'),
      api.get<ProductoListResponse>('/productos?page=1&limit=100'),
    ]);

    const pedidos = pedidosRes.data.items || [];

    const pedidosActivos = pedidos.filter(
      (pedido) => pedido.estado_codigo === 'PENDIENTE' || pedido.estado_codigo === 'CONFIRMADO',
    ).length;

    const ingresosDia = pedidos
      .filter((pedido) => pedido.estado_codigo === 'ENTREGADO' && wasDeliveredToday(pedido))
      .reduce((acc, pedido) => acc + Number(pedido.total), 0);

    const productos = productosRes.data.items || [];
    const productosBajoStock = productos.filter(
      (producto) => Number(producto.stock_cantidad) < 10,
    ).length;

    return {
      pedidosActivos,
      ingresosDia,
      productosBajoStock,
    };
  },
};
