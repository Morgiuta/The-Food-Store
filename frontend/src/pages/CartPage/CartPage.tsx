import { Link } from 'react-router-dom';
import { Minus, Plus, Trash2 } from 'lucide-react';
import { getCartSubtotal, useCartStore } from '../../store/cartStore';

export function CartPage() {
  const { items, updateQuantity, removeItem } = useCartStore();
  const subtotal = getCartSubtotal(items);

  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <span className="section-kicker">Carrito</span>
          <h1 className="mt-1 text-3xl font-black">Tu pedido</h1>
        </div>
        <Link to="/" className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-black hover:border-primary">
          Seguir comprando
        </Link>
      </div>

      {items.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface p-8 text-center">
          <p className="font-bold text-muted">El carrito esta vacio.</p>
          <Link
            to="/"
            className="mt-4 inline-flex rounded-md bg-primary px-4 py-2.5 font-black text-white hover:bg-primary-dark"
          >
            Ver catalogo
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="space-y-3">
            {items.map((item) => (
              <article key={item.id} className="rounded-lg border border-border bg-surface p-4">
                <div className="flex gap-4">
                  <div className="h-20 w-24 overflow-hidden rounded-md bg-surface-warm">
                    {item.producto.imagen_url ? (
                      <img
                        src={item.producto.imagen_url}
                        alt={item.producto.nombre}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center bg-primary text-lg font-black text-white">
                        FS
                      </div>
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h2 className="font-black">{item.producto.nombre}</h2>
                    <p className="text-sm font-medium text-muted">${item.producto.precio_base} c/u</p>
                    
                    {item.personalizacion?.removed_ingredients && item.personalizacion.removed_ingredients.length > 0 && (
                      <p className="mt-1 text-xs text-red-500 font-bold">
                        Sin: {item.producto.ingredientes?.filter(i => item.personalizacion?.removed_ingredients.includes(i.ingrediente_id))?.map(i => i.nombre)?.join(', ') || item.personalizacion.removed_ingredients.length + ' ingredientes'}
                      </p>
                    )}

                    <div className="mt-3 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.id, item.cantidad - 1)}
                        className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border hover:border-primary"
                        title="Restar"
                      >
                        <Minus size={16} />
                      </button>
                      <span className="flex h-9 min-w-12 items-center justify-center rounded-md bg-surface-warm px-3 font-black">
                        {item.cantidad}
                      </span>
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.id, item.cantidad + 1)}
                        className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border hover:border-primary"
                        title="Sumar"
                      >
                        <Plus size={16} />
                      </button>
                      <button
                        type="button"
                        onClick={() => removeItem(item.id)}
                        className="ml-auto inline-flex h-9 w-9 items-center justify-center rounded-md border border-border text-ketchup hover:border-ketchup"
                        title="Quitar"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <strong className="text-right text-lg">${item.producto.precio_base * item.cantidad}</strong>
                </div>
              </article>
            ))}
          </div>

          <aside className="h-fit rounded-lg border border-border bg-surface p-5">
            <h2 className="text-lg font-black">Resumen</h2>
            <div className="mt-4 space-y-2 text-sm font-bold">
              <div className="flex justify-between">
                <span className="text-muted">Subtotal</span>
                <span>${subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Envio</span>
                <span>$50</span>
              </div>
              <div className="border-t border-border pt-3 text-base">
                <div className="flex justify-between">
                  <span>Total estimado</span>
                  <span>${subtotal + 50}</span>
                </div>
              </div>
            </div>
            <Link
              to="/checkout"
              className="mt-5 inline-flex w-full justify-center rounded-md bg-primary px-4 py-3 font-black text-white hover:bg-primary-dark"
            >
              Finalizar compra
            </Link>
          </aside>
        </div>
      )}
    </section>
  );
}
