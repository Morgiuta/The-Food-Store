export interface DetallePedidoPublic {
  pedido_id: number;
  producto_id: number;
  cantidad: number;
  nombre_snapshot: string;
  precio_snapshot: number;
  subtotal_snapshot: number;
  personalizacion: Record<string, unknown> | null;
  created_at: string;
}

export interface PagoPublic {
  id: number;
  pedido_id: number;
  mp_payment_id: number | null;
  mp_status: string;
  mp_status_detail: string | null;
  external_reference: string;
  idempotency_key: string;
  transaction_amount: number;
  payment_method: string | null;
  created_at: string;
  updated_at: string;
}

export interface HistorialEstadoPedidoPublic {
  id: number;
  pedido_id: number;
  estado_desde: string | null;
  estado_hacia: string;
  usuario_id: number | null;
  motivo: string | null;
  created_at: string;
}

export interface Pedido {
  id: number;
  usuario_id: number;
  direccion_id: number | null;
  estado_codigo: string;
  forma_pago_codigo: string;
  subtotal: number;
  descuento: number;
  costo_envio: number;
  total: number;
  notas: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  detalles: DetallePedidoPublic[];
  pagos: PagoPublic[];
  historial: HistorialEstadoPedidoPublic[];
}

export interface PedidosResponse {
  items: Pedido[];
  total: number;
  page: number;
  limit: number;
}
