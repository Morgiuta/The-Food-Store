import type { Pedido, PedidoPersonalizacion, PedidosResponse } from '../types/pedido';
import { api } from './api';

export interface PedidoCreateInput {
  direccion_id: number | null;
  forma_pago_codigo: string;
  descuento: number;
  costo_envio: number;
  notas: string | null;
  detalles: Array<{
    producto_id: number;
    cantidad: number;
    personalizacion: PedidoPersonalizacion | null;
  }>;
}

export const pedidosService = {
  async getAll(page: number = 1, size: number = 50): Promise<PedidosResponse> {
    const { data } = await api.get<PedidosResponse>(`/pedidos/?page=${page}&size=${size}`);
    return data;
  },

  async getById(id: number): Promise<Pedido> {
    const { data } = await api.get<Pedido>(`/pedidos/${id}`);
    return data;
  },

  async create(input: PedidoCreateInput): Promise<Pedido> {
    const { data } = await api.post<Pedido>('/pedidos/', input);
    return data;
  },

  async avanzarEstado(id: number, nuevoEstado: string): Promise<Pedido> {
    const { data } = await api.patch<Pedido>(`/pedidos/${id}/estado`, {
      nuevo_estado: nuevoEstado,
    });
    return data;
  },

  async cambiarEstadoManual(id: number, estadoHacia: string, motivo?: string): Promise<Pedido> {
    const { data } = await api.post<Pedido>(`/pedidos/${id}/estado`, {
      estado_hacia: estadoHacia,
      motivo: motivo || null,
    });
    return data;
  },

  async cancelar(id: number): Promise<Pedido> {
    const { data } = await api.patch<Pedido>(`/pedidos/${id}/cancelar`);
    return data;
  },
};
