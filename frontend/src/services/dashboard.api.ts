import { api } from './api';
import type { PedidosResponse } from '../types/pedido';

export interface DashboardMetrics {
  pedidosActivos: number;
  totalProductos: number;
  totalCategorias: number;
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

interface CategoriaListResponse {
  items: unknown[];
  total?: number;
}

export const dashboardService = {
  async getMetrics(): Promise<DashboardMetrics> {
    const [pedidosRes, productosRes, categoriasRes] = await Promise.all([
      // Pedidos de hoy: el endpoint de pedidos acepta offset/limit, no page
      api.get<PedidosResponse>('/pedidos?offset=0&limit=100&solo_hoy=true'),
      // Productos: el endpoint acepta page/limit con max 100
      api.get<ProductoListResponse>('/productos?page=1&limit=100'),
      // Categorias
      api.get<CategoriaListResponse>('/categorias'),
    ]);

    const pedidos = pedidosRes.data.items || [];

    // Pedidos activos hoy: PENDIENTE y CONFIRMADO
    const pedidosActivos = pedidos.filter(
      (p) => p.estado_codigo === 'PENDIENTE' || p.estado_codigo === 'CONFIRMADO'
    ).length;

    // Ingresos del día: solo pedidos ENTREGADOS hoy
    const ingresosDia = pedidos
      .filter((p) => p.estado_codigo === 'ENTREGADO')
      .reduce((acc, curr) => acc + Number(curr.total), 0);

    // Total productos (usa el campo total de la respuesta paginada)
    const totalProductos = productosRes.data.total ?? 0;

    // Total categorías
    const totalCategorias =
      (categoriasRes.data as { total?: number }).total ??
      categoriasRes.data.items?.length ??
      0;

    // Productos bajo stock: los que tienen stock_cantidad < 10
    const productos = productosRes.data.items || [];
    const productosBajoStock = productos.filter(
      (p) => Number(p.stock_cantidad) < 10
    ).length;

    return {
      pedidosActivos,
      totalProductos,
      totalCategorias,
      ingresosDia,
      productosBajoStock,
    };
  },
};
