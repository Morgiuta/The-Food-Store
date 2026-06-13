import { useMemo, useState } from 'react';
import { Search, ShoppingCart, Minus, Plus, Trash2 } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { useCategorias } from '../../hooks/useCategorias';
import { useProductos } from '../../hooks/useProductos';
import { useCartStore } from '../../store/cartStore';

export function StoreHomePage() {
  const [categoriaId, setCategoriaId] = useState<number | undefined>(undefined);
  const [searchParams] = useSearchParams();
  const search = searchParams.get('q') || '';
  const { categorias } = useCategorias({ page: 1, size: 100 });
  const { productos, isLoading, error } = useProductos({
    page: 1,
    size: 60,
    categoria_id: categoriaId,
    disponible: true,
    q: search.trim() || undefined,
  });
  const { items, addItem, updateQuantity, removeItem } = useCartStore();

  const categoriasById = useMemo(
    () => new Map(categorias.map((categoria) => [categoria.id, categoria.nombre])),
    [categorias],
  );

  const selectedCategoria = useMemo(
    () => categorias.find((c) => c.id === categoriaId),
    [categorias, categoriaId]
  );

  const fallbackImage = 'https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=1965&auto=format&fit=crop';
  const heroImage = (selectedCategoria && selectedCategoria.imagen_url) || fallbackImage;

  return (
    <div className="relative min-h-screen">
      {/* Category Background Hero */}
      {heroImage && (
        <div 
          className="absolute inset-x-0 top-0 h-[60vh] z-0 animate-in fade-in duration-700"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {/* Gradient to fade into the background */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-bg/90 to-bg"></div>
        </div>
      )}

      <section className="relative z-10 mx-auto max-w-7xl px-4 py-8">
        <div className="mb-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <div className="transition-colors duration-500">
            <span className="section-kicker text-white/90 bg-white/20 border-white/30">
              {selectedCategoria ? selectedCategoria.nombre : 'Store'}
            </span>
            <h1 className="mt-2 text-4xl font-black leading-tight md:text-5xl text-white drop-shadow-md">
              {selectedCategoria ? `Todo en ${selectedCategoria.nombre}` : 'Todos nuestros productos'}
            </h1>
            <p className="mt-3 max-w-2xl text-base font-medium text-white/80 drop-shadow">
              {selectedCategoria?.descripcion || 'Elegí productos disponibles, armá tu carrito y confirmá el pedido con entrega a domicilio.'}
            </p>
          </div>

          <div className="hidden lg:block"></div>
        </div>

      <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
        <button
          type="button"
          onClick={() => setCategoriaId(undefined)}
          className={`whitespace-nowrap rounded-md px-4 py-2 text-sm font-black ${
            categoriaId === undefined
              ? 'bg-primary text-white'
              : 'border border-border bg-surface text-charcoal hover:border-primary'
          }`}
        >
          Todo
        </button>
        {categorias.map((categoria) => (
          <button
            key={categoria.id}
            type="button"
            onClick={() => setCategoriaId(categoria.id)}
            className={`whitespace-nowrap rounded-md px-4 py-2 text-sm font-black ${
              categoriaId === categoria.id
                ? 'bg-primary text-white'
                : 'border border-border bg-surface text-charcoal hover:border-primary'
            }`}
          >
            {categoria.nombre}
          </button>
        ))}
      </div>

      {error && <div className="mb-4 rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}

      {isLoading ? (
        <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
          Cargando productos...
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 items-stretch">
          {productos.filter(p => p.stock_cantidad > 0).map((producto) => {
            const principal = producto.categorias.find((categoria) => categoria.es_principal);
            return (
              <article
                key={producto.id}
                className="flex flex-col h-full overflow-hidden rounded-lg border border-border bg-surface shadow-sm"
              >
                <div className="flex-1 flex flex-col">
                  <div className="aspect-[4/3] bg-surface-warm relative">
                    {producto.stock_cantidad < 10 && (
                      <span className="absolute top-3 right-3 shadow-sm text-[10px] font-black uppercase tracking-wider text-orange-600 bg-orange-100 px-2.5 py-1 rounded-full z-10">
                        ¡Aprovecha que vuelan!
                      </span>
                    )}
                    {producto.imagen_url ? (
                      <img
                        src={producto.imagen_url}
                        alt={producto.nombre}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center bg-gradient-to-br from-primary to-cheddar text-4xl font-black text-white">
                        FS
                      </div>
                    )}
                  </div>
                  <div className="p-4 flex flex-col flex-1">
                    <div className="mb-2 flex items-start justify-between gap-3">
                      <h2 className="text-lg font-black leading-tight">{producto.nombre}</h2>
                      <span className="rounded-md bg-surface-warm px-2 py-1 text-sm font-black text-primary-dark">
                        ${producto.precio_base}
                      </span>
                    </div>
                    <p className="min-h-10 text-sm font-medium text-muted">
                      {producto.descripcion || 'Producto disponible para entrega.'}
                    </p>
                    <div className="mt-auto pt-4 flex items-center justify-between gap-3">
                      <span className="text-xs font-bold uppercase text-muted">
                        {principal ? categoriasById.get(principal.categoria_id) || 'Categoria' : 'Catalogo'}
                      </span>
                      <span className="text-xs font-bold text-lettuce">
                        Stock {producto.stock_cantidad} {producto.unidad_venta?.simbolo ?? 'u.'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="p-4 pt-0">
                  {(() => {
                    const cartItem = items.find((i) => i.producto.id === producto.id);
                    return !cartItem ? (
                      <button
                        type="button"
                        onClick={() => addItem(producto, 1)}
                        disabled={!producto.disponible || producto.stock_cantidad <= 0}
                        className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-black text-white hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        <ShoppingCart size={17} />
                        Agregar
                      </button>
                    ) : (
                      <div className="flex w-full items-center justify-between rounded-md bg-surface-warm p-1">
                        <button
                          type="button"
                          onClick={() => cartItem.cantidad > 1 ? updateQuantity(producto.id, cartItem.cantidad - 1) : removeItem(producto.id)}
                          className="flex h-8 w-8 items-center justify-center rounded bg-white text-charcoal shadow-sm hover:text-primary transition-colors"
                        >
                          {cartItem.cantidad > 1 ? <Minus size={16} /> : <Trash2 size={16} className="text-red-500 hover:text-red-600" />}
                        </button>
                        <span className="font-black text-charcoal">{cartItem.cantidad}</span>
                        <button
                          type="button"
                          onClick={() => updateQuantity(producto.id, cartItem.cantidad + 1)}
                          disabled={cartItem.cantidad >= producto.stock_cantidad}
                          className="flex h-8 w-8 items-center justify-center rounded bg-white text-charcoal shadow-sm hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Plus size={16} />
                        </button>
                      </div>
                    );
                  })()}
                </div>
              </article>
            );
          })}
        </div>
      )}

      {!isLoading && productos.filter(p => p.stock_cantidad > 0).length === 0 && (
        <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
          No hay productos disponibles para esos filtros.
        </div>
      )}
    </section>
    </div>
  );
}
