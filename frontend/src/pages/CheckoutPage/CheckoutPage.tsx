import { FormEvent, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { pedidosService } from '../../services/pedidosService';
import { getCartSubtotal, useCartStore } from '../../store/cartStore';
import { useDirecciones } from '../../hooks/useDirecciones';
import { getErrorMessage } from '../../utils/errors';

export function CheckoutPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { items, clearCart } = useCartStore();
  const { direcciones, isLoading: isLoadingDirecciones } = useDirecciones();
  const [direccionId, setDireccionId] = useState<number | null>(null);
  const [notas, setNotas] = useState('');
  const [error, setError] = useState<string | null>(null);
  const subtotal = getCartSubtotal(items);
  const envio = items.length > 0 ? 50 : 0;

  const principal = useMemo(
    () => direcciones.find((direccion) => direccion.es_principal) || direcciones[0],
    [direcciones],
  );

  const createPedidoMutation = useMutation({
    mutationFn: () =>
      pedidosService.create({
        direccion_id: direccionId ?? principal?.id ?? null,
        forma_pago_codigo: 'EFECTIVO',
        descuento: 0,
        costo_envio: envio,
        notas: notas.trim() || null,
        detalles: items.map((item) => ({
          producto_id: item.producto.id,
          cantidad: item.cantidad,
          personalizacion: null,
        })),
      }),
    onSuccess: () => {
      clearCart();
      queryClient.invalidateQueries({ queryKey: ['pedidos'] });
      navigate('/mis-pedidos', { replace: true });
    },
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (items.length === 0) {
      setError('El carrito esta vacio.');
      return;
    }

    if (!direccionId && !principal) {
      setError('Agrega una direccion de entrega antes de confirmar.');
      return;
    }

    try {
      await createPedidoMutation.mutateAsync();
    } catch (checkoutError: unknown) {
      setError(getErrorMessage(checkoutError, 'No se pudo crear el pedido.'));
    }
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6">
        <span className="section-kicker">Checkout</span>
        <h1 className="mt-1 text-3xl font-black">Finalizar compra</h1>
      </div>

      {items.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface p-8 text-center">
          <p className="font-bold text-muted">No hay productos para confirmar.</p>
          <Link
            to="/"
            className="mt-4 inline-flex rounded-md bg-primary px-4 py-2.5 font-black text-white hover:bg-primary-dark"
          >
            Ver catalogo
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="space-y-5">
            <section className="rounded-lg border border-border bg-surface p-5">
              <div className="mb-4 flex items-center justify-between gap-4">
                <h2 className="text-lg font-black">Direccion de entrega</h2>
                <Link to="/direcciones" className="text-sm font-black text-primary-dark hover:underline">
                  Gestionar
                </Link>
              </div>

              {isLoadingDirecciones ? (
                <p className="font-bold text-muted">Cargando direcciones...</p>
              ) : direcciones.length === 0 ? (
                <div className="rounded-md bg-surface-warm p-4">
                  <p className="font-bold text-muted">Todavia no tenes direcciones guardadas.</p>
                  <Link
                    to="/direcciones"
                    className="mt-3 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-black text-white"
                  >
                    Agregar direccion
                  </Link>
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2">
                  {direcciones.map((direccion) => (
                    <label
                      key={direccion.id}
                      className={`cursor-pointer rounded-md border p-4 ${
                        (direccionId ?? principal?.id) === direccion.id
                          ? 'border-primary bg-surface-warm'
                          : 'border-border bg-white'
                      }`}
                    >
                      <input
                        type="radio"
                        name="direccion"
                        className="sr-only"
                        checked={(direccionId ?? principal?.id) === direccion.id}
                        onChange={() => setDireccionId(direccion.id)}
                      />
                      <div className="flex items-center justify-between gap-3">
                        <strong>{direccion.alias || 'Direccion'}</strong>
                        {direccion.es_principal && (
                          <span className="rounded-md bg-lettuce px-2 py-1 text-xs font-black text-white">
                            Principal
                          </span>
                        )}
                      </div>
                      <p className="mt-2 text-sm font-semibold text-muted">
                        {direccion.calle} {direccion.numero}, {direccion.ciudad}
                      </p>
                    </label>
                  ))}
                </div>
              )}
            </section>

            <section className="rounded-lg border border-border bg-surface p-5">
              <h2 className="text-lg font-black">Notas del pedido</h2>
              <textarea
                className="mt-3 min-h-28 w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
                value={notas}
                onChange={(event) => setNotas(event.target.value)}
                placeholder="Aclaraciones para cocina o entrega"
              />
            </section>
          </div>

          <aside className="h-fit rounded-lg border border-border bg-surface p-5">
            <h2 className="text-lg font-black">Resumen</h2>
            <div className="mt-4 space-y-3">
              {items.map((item) => (
                <div key={item.producto.id} className="flex justify-between gap-3 text-sm font-bold">
                  <span>
                    {item.cantidad} x {item.producto.nombre}
                  </span>
                  <span>${item.producto.precio_base * item.cantidad}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-2 border-t border-border pt-4 text-sm font-bold">
              <div className="flex justify-between">
                <span className="text-muted">Subtotal</span>
                <span>${subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Envio</span>
                <span>${envio}</span>
              </div>
              <div className="flex justify-between text-base font-black">
                <span>Total</span>
                <span>${subtotal + envio}</span>
              </div>
            </div>

            {error && <div className="mt-4 rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}

            <button
              type="submit"
              disabled={createPedidoMutation.isPending}
              className="mt-5 w-full rounded-md bg-primary px-4 py-3 font-black text-white hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-70"
            >
              {createPedidoMutation.isPending ? 'Confirmando...' : 'Confirmar pedido'}
            </button>
          </aside>
        </form>
      )}
    </section>
  );
}
