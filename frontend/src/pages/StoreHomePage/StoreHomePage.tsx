import { useMemo, useState } from "react";
import { Search, ShoppingCart, Minus, Plus, Trash2, X } from "lucide-react";
import type { Producto } from "../../types/producto";
import { useSearchParams } from "react-router-dom";
import { useCategorias } from "../../hooks/useCategorias";
import { useProductos } from "../../hooks/useProductos";
import { useCartStore } from "../../store/cartStore";

export function StoreHomePage() {
  const [categoriaId, setCategoriaId] = useState<number | undefined>(undefined);
  const [searchParams] = useSearchParams();
  const search = searchParams.get("q") || "";
  const { categorias } = useCategorias({ page: 1, size: 100 });
  const { productos, isLoading, error } = useProductos({
    page: 1,
    size: 60,
    categoria_id: categoriaId,
    disponible: true,
    q: search.trim() || undefined,
  });
  const { items, addItem, updateQuantity, removeItem } = useCartStore();

  const [selectedProduct, setSelectedProduct] = useState<Producto | null>(null);
  const [removedIngredients, setRemovedIngredients] = useState<number[]>([]);

  const handleAddToCart = (producto: Producto) => {
    const removable =
      producto.ingredientes?.filter((i) => i.es_removible) || [];
    if (removable.length > 0) {
      setSelectedProduct(producto);
      setRemovedIngredients([]);
    } else {
      addItem(producto, 1);
    }
  };

  const confirmAddToCart = () => {
    if (selectedProduct) {
      const personalizacion =
        removedIngredients.length > 0
          ? { removed_ingredients: removedIngredients }
          : undefined;
      addItem(selectedProduct, 1, personalizacion);
      setSelectedProduct(null);
      setRemovedIngredients([]);
    }
  };

  const categoriasById = useMemo(
    () =>
      new Map(categorias.map((categoria) => [categoria.id, categoria.nombre])),
    [categorias],
  );

  const selectedCategoria = useMemo(
    () => categorias.find((c) => c.id === categoriaId),
    [categorias, categoriaId],
  );

  const fallbackImage =
    "https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=1965&auto=format&fit=crop";
  const heroImage =
    (selectedCategoria && selectedCategoria.imagen_url) || fallbackImage;

  return (
    <div className="relative min-h-screen">
      {/* Category Background Hero */}
      {heroImage && (
        <div
          className="absolute inset-x-0 top-0 h-[60vh] z-0 animate-in fade-in duration-700"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
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
              {selectedCategoria ? selectedCategoria.nombre : "Store"}
            </span>
            <h1 className="mt-2 text-4xl font-black leading-tight md:text-5xl text-white drop-shadow-md">
              {selectedCategoria
                ? `Todo en ${selectedCategoria.nombre}`
                : "Todos nuestros productos"}
            </h1>
            <p className="mt-3 max-w-2xl text-base font-medium text-white/80 drop-shadow">
              {selectedCategoria?.descripcion ||
                "Elegí productos disponibles, armá tu carrito y confirmá el pedido con entrega a domicilio."}
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
                ? "bg-primary text-white"
                : "border border-border bg-surface text-charcoal hover:border-primary"
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
                  ? "bg-primary text-white"
                  : "border border-border bg-surface text-charcoal hover:border-primary"
              }`}
            >
              {categoria.nombre}
            </button>
          ))}
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-100 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
            Cargando productos...
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 items-stretch">
            {productos
              .filter((p) => p.stock_cantidad > 0)
              .map((producto) => {
                const principal = producto.categorias.find(
                  (categoria) => categoria.es_principal,
                );
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
                          <h2 className="text-lg font-black leading-tight">
                            {producto.nombre}
                          </h2>
                          <span className="rounded-md bg-surface-warm px-2 py-1 text-sm font-black text-primary-dark">
                            ${producto.precio_base}
                          </span>
                        </div>
                        <p className="min-h-10 text-sm font-medium text-muted">
                          {producto.descripcion ||
                            "Producto disponible para entrega."}
                        </p>
                        <div className="mt-auto pt-4 flex items-center justify-between gap-3">
                          <span className="text-xs font-bold uppercase text-muted">
                            {principal
                              ? categoriasById.get(principal.categoria_id) ||
                                "Categoria"
                              : "Catalogo"}
                          </span>
                          <span className="text-xs font-bold text-lettuce">
                            Stock {producto.stock_cantidad}{" "}
                            {producto.unidad_venta?.simbolo ?? "un."}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 pt-0">
                      {(() => {
                        const normalCartItem = items.find(
                          (i) => i.producto.id === producto.id && (!i.personalizacion?.removed_ingredients || i.personalizacion.removed_ingredients.length === 0)
                        );
                        
                        const hasCustomizations = (producto.ingredientes?.filter(i => i.es_removible) || []).length > 0;
                        const totalInCart = items.filter(i => i.producto.id === producto.id).reduce((acc, item) => acc + item.cantidad, 0);

                        return (
                          <div className="flex flex-col gap-2">
                            {!normalCartItem ? (
                              <button
                                type="button"
                                onClick={() => handleAddToCart(producto)}
                                disabled={
                                  !producto.disponible ||
                                  producto.stock_cantidad <= 0 ||
                                  totalInCart >= producto.stock_cantidad
                                }
                                className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-black text-white hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
                              >
                                <ShoppingCart size={17} />
                                {totalInCart > 0 ? `Agregar otra (${totalInCart} en carrito)` : "Agregar"}
                              </button>
                            ) : (
                              <>
                                <div className="flex w-full items-center justify-between rounded-md bg-surface-warm p-1">
                                  <button
                                    type="button"
                                    onClick={() =>
                                      normalCartItem.cantidad > 1
                                        ? updateQuantity(
                                            normalCartItem.id,
                                            normalCartItem.cantidad - 1,
                                          )
                                        : removeItem(normalCartItem.id)
                                    }
                                    className="flex h-8 w-8 items-center justify-center rounded bg-white text-charcoal shadow-sm hover:text-primary transition-colors"
                                  >
                                    {normalCartItem.cantidad > 1 ? (
                                      <Minus size={16} />
                                    ) : (
                                      <Trash2
                                        size={16}
                                        className="text-red-500 hover:text-red-600"
                                      />
                                    )}
                                  </button>
                                  <span className="font-black text-charcoal">
                                    {normalCartItem.cantidad}
                                  </span>
                                  <button
                                    type="button"
                                    onClick={() =>
                                      updateQuantity(
                                        normalCartItem.id,
                                        normalCartItem.cantidad + 1,
                                      )
                                    }
                                    disabled={
                                      totalInCart >= producto.stock_cantidad
                                    }
                                    className="flex h-8 w-8 items-center justify-center rounded bg-white text-charcoal shadow-sm hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    <Plus size={16} />
                                  </button>
                                </div>
                                {hasCustomizations && (
                                  <button
                                    type="button"
                                    onClick={() => handleAddToCart(producto)}
                                    disabled={totalInCart >= producto.stock_cantidad}
                                    className="text-xs font-bold text-primary hover:underline text-center w-full disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    + Personalizar otra
                                  </button>
                                )}
                              </>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  </article>
                );
              })}
          </div>
        )}

        {!isLoading &&
          productos.filter((p) => p.stock_cantidad > 0).length === 0 && (
            <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
              No hay productos disponibles para esos filtros.
            </div>
          )}

        {/* Modal de Personalización */}
        {selectedProduct && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl animate-in zoom-in-95 duration-200">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-black text-charcoal">
                    Personalizar pedido
                  </h2>
                  <p className="mt-1 text-sm font-medium text-muted">
                    {selectedProduct.nombre}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedProduct(null)}
                  className="rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-charcoal"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="mb-6">
                <p className="mb-3 text-sm font-bold text-charcoal">
                  Ingredientes removibles (opcional):
                </p>
                <div className="space-y-2 max-h-[40vh] overflow-y-auto pr-2">
                  {selectedProduct.ingredientes
                    .filter((i) => i.es_removible)
                    .map((ing) => (
                      <label
                        key={ing.ingrediente_id}
                        className={`flex cursor-pointer items-center justify-between rounded-xl border p-3 transition-colors ${
                          removedIngredients.includes(ing.ingrediente_id)
                            ? "border-ketchup bg-red-50 text-ketchup"
                            : "border-border bg-surface hover:border-gray-300"
                        }`}
                      >
                        <span className="font-semibold text-sm">
                          {ing.nombre}
                        </span>
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-gray-300 text-ketchup focus:ring-ketchup"
                          checked={removedIngredients.includes(
                            ing.ingrediente_id,
                          )}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setRemovedIngredients([
                                ...removedIngredients,
                                ing.ingrediente_id,
                              ]);
                            } else {
                              setRemovedIngredients(
                                removedIngredients.filter(
                                  (id) => id !== ing.ingrediente_id,
                                ),
                              );
                            }
                          }}
                        />
                      </label>
                    ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedProduct(null)}
                  className="flex-1 rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm font-bold text-gray-600 hover:bg-gray-50 hover:text-charcoal"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={confirmAddToCart}
                  className="flex-1 rounded-xl bg-primary px-4 py-3 text-sm font-black text-white shadow-sm hover:bg-primary-dark"
                >
                  Agregar al carrito
                </button>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
