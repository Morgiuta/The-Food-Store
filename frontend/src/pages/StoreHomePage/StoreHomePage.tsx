import { useMemo, useState } from 'react';
import { Search, ShoppingCart } from 'lucide-react';
import { useCategorias } from '../../hooks/useCategorias';
import { useProductos } from '../../hooks/useProductos';
import { useCartStore } from '../../store/cartStore';

export function StoreHomePage() {
  const [categoriaId, setCategoriaId] = useState<number | undefined>(undefined);
  const [search, setSearch] = useState('');
  const { categorias } = useCategorias({ offset: 0, limit: 100 });
  const { productos, isLoading, error } = useProductos({
    page: 1,
    limit: 60,
    categoria_id: categoriaId,
    disponible: true,
    q: search.trim() || undefined,
  });
  const addItem = useCartStore((state) => state.addItem);

  const categoriasById = useMemo(
    () => new Map(categorias.map((categoria) => [categoria.id, categoria.nombre])),
    [categorias],
  );

  return (
    <section className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
        <div>
          <span className="section-kicker">Store</span>
          <h1 className="mt-2 text-4xl font-black leading-tight text-charcoal md:text-5xl">
            Hamburguesas, bebidas y combos para pedir ahora
          </h1>
          <p className="mt-3 max-w-2xl text-base font-medium text-muted">
            Elegi productos disponibles, arma tu carrito y confirma el pedido con entrega a domicilio.
          </p>
        </div>

        <div className="rounded-lg border border-border bg-surface p-3 shadow-soft">
          <div className="flex items-center gap-2 rounded-md border border-border bg-white px-3 py-2">
            <Search size={18} className="text-muted" />
            <input
              className="w-full bg-transparent text-sm font-semibold outline-none"
              placeholder="Buscar producto"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </div>
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
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {productos.map((producto) => {
            const principal = producto.categorias.find((categoria) => categoria.es_principal);
            return (
              <article
                key={producto.id}
                className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm"
              >
                <div className="aspect-[4/3] bg-surface-warm">
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
                <div className="p-4">
                  <div className="mb-2 flex items-start justify-between gap-3">
                    <h2 className="text-lg font-black leading-tight">{producto.nombre}</h2>
                    <span className="rounded-md bg-surface-warm px-2 py-1 text-sm font-black text-primary-dark">
                      ${producto.precio_base}
                    </span>
                  </div>
                  <p className="min-h-10 text-sm font-medium text-muted">
                    {producto.descripcion || 'Producto disponible para entrega.'}
                  </p>
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <span className="text-xs font-bold uppercase text-muted">
                      {principal ? categoriasById.get(principal.categoria_id) || 'Categoria' : 'Catalogo'}
                    </span>
                    <span className="text-xs font-bold text-lettuce">Stock {producto.stock_cantidad}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => addItem(producto, 1)}
                    disabled={!producto.disponible || producto.stock_cantidad <= 0}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-black text-white hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <ShoppingCart size={17} />
                    Agregar
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}

      {!isLoading && productos.length === 0 && (
        <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
          No hay productos disponibles para esos filtros.
        </div>
      )}
    </section>
  );
}
