import type { PagoPublic } from '../types/pedido';
import { api } from './api';

export interface CrearPagoResponse {
  pedido_id: number;
  preference_id: string;
  init_point: string;
  sandbox_init_point: string | null;
  public_key: string;
}

export const pagosService = {
  /** Crea la preferencia de Checkout Pro para un pedido y devuelve los links de pago. */
  async crear(pedidoId: number): Promise<CrearPagoResponse> {
    const { data } = await api.post<CrearPagoResponse>('/pagos/crear', {
      pedido_id: pedidoId,
    });
    return data;
  },

  /** Consulta el pago asociado a un pedido. */
  async getByPedido(pedidoId: number): Promise<PagoPublic> {
    const { data } = await api.get<PagoPublic>(`/pagos/${pedidoId}`);
    return data;
  },
};
