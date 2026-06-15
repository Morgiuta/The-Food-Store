import { FormEvent, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { pedidosService } from '../../services/pedidosService';
import { pagosService } from '../../services/pagosService';
import { getCartSubtotal, useCartStore } from '../../store/cartStore';
import { useDirecciones } from '../../hooks/useDirecciones';
import { getErrorMessage } from '../../utils/errors';
import { ModalFinalizarCompra } from './ModalFinalizarCompra';

export function CheckoutPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { items, clearCart } = useCartStore();
  const { direcciones, isLoading: isLoadingDirecciones } = useDirecciones();
  const [direccionId, setDireccionId] = useState<number | null>(null);
  const [notas, setNotas] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [mpPreference, setMpPreference] = useState<{
    preferenceId: string;
    publicKey: string;
  } | null>(null);
  const [modalData, setModalData] = useState<{ items: any[], subtotal: number, envio: number } | null>(null);

  const subtotal = getCartSubtotal(items);
  const envio = items.length > 0 ? 50 : 0;

  const principal = useMemo(
    () => direcciones.find((direccion) => direccion.es_principal) || direcciones[0],
    [direcciones],
  );

  const createPedidoMutation = useMutation({
    mutationFn: (formaPagoCodigo: string) =>
      pedidosService.create({
        direccion_id: direccionId ?? principal?.id ?? null,
        forma_pago_codigo: formaPagoCodigo,
        descuento: 0,
        costo_envio: envio,
        notas: notas.trim() || null,
        detalles: items.map((item) => ({
          producto_id: item.producto.id,
          cantidad: item.cantidad,
          personalizacion: item.personalizacion
            ? { ingredientes_removidos: item.personalizacion.removed_ingredients || [] }
            : null,
        })),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pedidos'] });
    },
  });

  const crearPagoMutation = useMutation({
    mutationFn: (pedidoId: number) => pagosService.crear(pedidoId),
  });

  const isMutating = createPedidoMutation.isPending || crearPagoMutation.isPending;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (items.length === 0) {
      setError('El carrito está vacío.');
      return;
    }

    if (!direccionId && !principal) {
      setError('Agrega una dirección de entrega antes de continuar.');
      return;
    }

    // Instead of creating the order, open the payment modal
    setModalData({ items, subtotal, envio });
    setMpPreference(null);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setMpPreference(null);
    setModalData(null);
  };

  const handleConfirmOrder = async (formaPagoCodigo: string) => {
    setError(null);
    try {
      const pedido = await createPedidoMutation.mutateAsync(formaPagoCodigo);

      if (formaPagoCodigo === 'MERCADOPAGO') {
        // Crear la preferencia de Checkout Pro y mostrar el Wallet Brick (sin salir del sitio).
        const preferencia = await crearPagoMutation.mutateAsync(pedido.id);
        if (!preferencia.preference_id) {
          setError('No se pudo iniciar el pago con MercadoPago.');
          return;
        }
        clearCart();
        setMpPreference({
          preferenceId: preferencia.preference_id,
          publicKey: preferencia.public_key,
        });
        return;
      }

      // Otras formas de pago: el pedido queda registrado.
      clearCart();
      closeModal();
      navigate('/mis-pedidos', { replace: true });
    } catch (checkoutError: unknown) {
      setError(getErrorMessage(checkoutError, 'No se pudo procesar el pedido.'));
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
                <h2 className="text-lg font-black">Dirección de entrega</h2>
                <Link to="/mis-direcciones" className="text-sm font-black text-primary-dark hover:underline">
                  Gestionar
                </Link>
              </div>

              {isLoadingDirecciones ? (
                <p className="font-bold text-muted">Cargando direcciones...</p>
              ) : direcciones.length === 0 ? (
                <div className="rounded-md bg-surface-warm p-4">
                  <p className="font-bold text-muted">Todavía no tenés direcciones guardadas.</p>
                  <Link
                    to="/mis-direcciones"
                    className="mt-3 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-black text-white"
                  >
                    Agregar dirección
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
                        <strong>{direccion.alias || 'Dirección'}</strong>
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
                <div key={item.id} className="flex flex-col gap-1">
                  <div className="flex justify-between gap-3 text-sm font-bold">
                    <span>
                      {item.cantidad} x {item.producto.nombre}
                    </span>
                    <span>${item.producto.precio_base * item.cantidad}</span>
                  </div>
                  {item.personalizacion?.removed_ingredients && item.personalizacion.removed_ingredients.length > 0 && (
                    <span className="text-xs text-red-500">
                      Sin: {item.producto.ingredientes?.filter(i => item.personalizacion?.removed_ingredients.includes(i.ingrediente_id))?.map(i => i.nombre)?.join(', ') || item.personalizacion.removed_ingredients.length + ' ingredientes'}
                    </span>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-2 border-t border-border pt-4 text-sm font-bold">
              <div className="flex justify-between">
                <span className="text-muted">Subtotal</span>
                <span>${subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Envío</span>
                <span>${envio}</span>
              </div>
              <div className="flex justify-between text-base font-black">
                <span>Total</span>
                <span>${subtotal + envio}</span>
              </div>
            </div>

            <button
              type="submit"
              className="mt-5 w-full rounded-md bg-primary px-4 py-3 font-black text-white hover:bg-primary-dark"
            >
              Elegir forma de pago
            </button>
          </aside>
        </form>
      )}

      <ModalFinalizarCompra
        isOpen={isModalOpen}
        onClose={closeModal}
        items={modalData?.items || items}
        subtotal={modalData?.subtotal ?? subtotal}
        envio={modalData?.envio ?? envio}
        isMutating={isMutating}
        onConfirm={handleConfirmOrder}
        error={error}
        preferenceId={mpPreference?.preferenceId}
        publicKey={mpPreference?.publicKey}
      />
    </section>
  );
}
