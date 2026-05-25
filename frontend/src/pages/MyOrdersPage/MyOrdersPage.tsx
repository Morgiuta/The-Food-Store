import { format } from 'date-fns';
import { RefreshCcw, XCircle } from 'lucide-react';
import { usePedidos } from '../../hooks/usePedidos';

const cancelables = new Set(['PENDIENTE', 'CONFIRMADO']);

const estadoStyles: Record<string, string> = {
  PENDIENTE: 'bg-cheddar text-charcoal',
  CONFIRMADO: 'bg-primary text-white',
  EN_PREP: 'bg-surface-warm text-primary-dark',
  EN_CAMINO: 'bg-lettuce text-white',
  ENTREGADO: 'bg-charcoal text-white',
  CANCELADO: 'bg-ketchup text-white',
};

export function MyOrdersPage() {
  const { pedidos, isLoading, isFetching, error, reload, cancelarPedido, isMutating } = usePedidos();

  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <span className="section-kicker">Cuenta</span>
          <h1 className="mt-1 text-3xl font-black">Mis pedidos</h1>
        </div>
        <button
          type="button"
          onClick={() => reload()}
          className="inline-flex items-center gap-2 rounded-md border border-border bg-surface px-4 py-2 text-sm font-black hover:border-primary"
        >
          <RefreshCcw size={16} className={isFetching ? 'animate-spin' : ''} />
          Actualizar
        </button>
      </div>

      {error && <div className="mb-4 rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}

      {isLoading ? (
        <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
          Cargando pedidos...
        </div>
      ) : pedidos.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
          Todavia no realizaste pedidos.
        </div>
      ) : (
        <div className="space-y-4">
          {pedidos.map((pedido) => (
            <article key={pedido.id} className="rounded-lg border border-border bg-surface p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-black">Pedido #{pedido.id}</h2>
                    <span
                      className={`rounded-md px-2 py-1 text-xs font-black ${
                        estadoStyles[pedido.estado_codigo] || 'bg-surface-warm text-charcoal'
                      }`}
                    >
                      {pedido.estado_codigo}
                    </span>
                  </div>
                  <p className="mt-1 text-sm font-semibold text-muted">
                    {format(new Date(pedido.created_at), 'dd/MM/yyyy HH:mm')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-black">${pedido.total}</p>
                  <p className="text-sm font-semibold text-muted">{pedido.forma_pago_codigo}</p>
                </div>
              </div>

              <div className="mt-4 rounded-md bg-surface-warm p-4">
                <h3 className="mb-2 text-sm font-black uppercase text-muted">Detalle</h3>
                <div className="space-y-2">
                  {pedido.detalles.map((detalle) => (
                    <div
                      key={`${detalle.pedido_id}-${detalle.producto_id}`}
                      className="flex justify-between gap-3 text-sm font-bold"
                    >
                      <span>
                        {detalle.cantidad} x {detalle.nombre_snapshot}
                      </span>
                      <span>${detalle.subtotal_snapshot}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <div className="text-sm font-semibold text-muted">
                  {pedido.historial.length > 0
                    ? `Ultimo movimiento: ${pedido.historial[pedido.historial.length - 1].estado_hacia}`
                    : 'Sin historial'}
                </div>
                {cancelables.has(pedido.estado_codigo) && (
                  <button
                    type="button"
                    onClick={() => cancelarPedido(pedido.id)}
                    disabled={isMutating}
                    className="inline-flex items-center gap-2 rounded-md border border-ketchup px-4 py-2 text-sm font-black text-ketchup hover:bg-red-50 disabled:opacity-60"
                  >
                    <XCircle size={16} />
                    Cancelar pedido
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
