import { useMemo, useState } from 'react';
import { Modal } from '../../components/ui/Modal/Modal';
import { useToast } from '../../components/ui/Toast/Toast';
import { ProductoForm } from '../../features/productos/components/ProductoForm/ProductoForm';
import { ProductosTable } from '../../features/productos/components/ProductosTable/ProductosTable';
import { useProductos } from '../../hooks/useProductos';
import { useCategoriasTree } from '../../hooks/useCategorias';
import { useSupplies } from '../../hooks/useSupplies';
import type { ProductosQuery, Producto, ProductoFormValues } from '../../types/producto';
import { Plus, Search } from 'lucide-react';
import type { CategoriaTree } from '../../types/categoria';

const defaultQuery: ProductosQuery = {
  page: 1,
  limit: 10,
};

export function ProductosPage() {
  const [query, setQuery] = useState<ProductosQuery>(defaultQuery);
  const [searchDraft, setSearchDraft] = useState('');
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(null);
  const [detailProducto, setDetailProducto] = useState<Producto | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const { confirm, notify } = useToast();

  const stableQuery = useMemo(() => query, [query]);
  
  // Queries
  const {
    productos,
    total,
    error,
    isLoading,
    isMutating,
    createProducto,
    updateProducto,
    toggleDisponibilidad,
    deleteProducto,
    restoreProducto,
  } = useProductos(stableQuery);

  const { tree: categoriasTree } = useCategoriasTree();
  // We need to fetch all active supplies for the ingredients list (offset 0, high limit up to 100)
  const { supplies } = useSupplies({ offset: 0, limit: 100, es_alergeno: 'all', include_deleted: false, sort_by: 'nombre', sort_dir: 'asc', search: '' });

  // Mapa de stockPosible: producto_id → cuántas unidades se pueden elaborar con el stock de insumos
  const stockPosibleMap = useMemo(() => {
    const map = new Map<number, number>();
    productos.forEach((prod) => {
      if (prod.ingredientes.length === 0) return; // sin receta → no calculamos
      let minPosible = Infinity;
      for (const ing of prod.ingredientes) {
        if (ing.ingrediente_id === 0 || ing.cantidad_requerida <= 0) continue;
        const supply = supplies.find((s) => s.id === ing.ingrediente_id);
        const stockDisponible = supply ? Number(supply.stock_actual) : 0;
        const posible = Math.floor(stockDisponible / Number(ing.cantidad_requerida));
        if (posible < minPosible) minPosible = posible;
      }
      map.set(prod.id, minPosible === Infinity ? 0 : minPosible);
    });
    return map;
  }, [productos, supplies]);

  const totalPages = Math.max(1, Math.ceil(total / query.limit));

  const updateQuery = (patch: Partial<ProductosQuery>) => {
    setQuery((current) => ({ ...current, ...patch, page: patch.page ?? current.page }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateQuery({ q: searchDraft, page: 1 });
  };

  const handleSubmit = async (values: ProductoFormValues) => {
    try {
      if (selectedProducto) {
        await updateProducto(selectedProducto.id, values);
        setSelectedProducto(null);
        setIsFormOpen(false);
        notify('success', 'Producto actualizado correctamente.');
        return;
      }

      await createProducto(values);
      setIsFormOpen(false);
      notify('success', 'Producto creado correctamente.');
    } catch (requestError) {
      notify(
        'error',
          requestError instanceof Error
            ? requestError.message
            : 'No se pudo guardar el producto.',
      );
    }
  };

  const handleDelete = async (prod: Producto) => {
    const confirmed = await confirm({
      confirmLabel: 'Dar de baja',
      message: `¿Estás seguro que deseas dar de baja el producto "${prod.nombre}"?`,
      title: 'Dar de baja producto',
      type: 'danger',
    });
    if (confirmed) {
        try {
        await deleteProducto(prod.id);
        notify('success', `"${prod.nombre}" fue dado de baja correctamente.`);
        } catch (requestError) {
        notify(
            'error',
            requestError instanceof Error
                ? requestError.message
                : 'No se pudo dar de baja el producto.',
        );
        }
    }
  };

  const handleRestore = async (prod: Producto) => {
    try {
      await restoreProducto(prod.id);
      notify('success', `"${prod.nombre}" fue restaurado correctamente.`);
    } catch (requestError) {
      notify(
        'error',
        requestError instanceof Error
            ? requestError.message
            : 'No se pudo restaurar el producto.',
      );
    }
  };

  const handleToggleDisponibilidad = async (prod: Producto) => {
    try {
       await toggleDisponibilidad(prod.id, !prod.disponible);
       notify('success', `El producto ahora está ${!prod.disponible ? 'disponible' : 'pausado'}.`);
    } catch {
       notify('error', 'No se pudo cambiar la disponibilidad del producto.');
    }
  };

  const handleEdit = (prod: Producto) => {
    setSelectedProducto(prod);
    setIsFormOpen(true);
  };

  const handleView = (prod: Producto) => {
    setDetailProducto(prod);
  };

  const getFlatOptions = (tree: CategoriaTree[], prefix = ''): { id: number, label: string }[] => {
    let options: { id: number, label: string }[] = [];
    tree.forEach(node => {
      options.push({ id: node.id, label: `${prefix}${node.nombre}` });
      if (node.children && node.children.length > 0) {
        options = options.concat(getFlatOptions(node.children, prefix + '— '));
      }
    });
    return options;
  };
  const catOptions = getFlatOptions(categoriasTree);

  return (
    <section className="space-y-6 animate-in fade-in duration-300 h-full flex flex-col">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <span className="section-kicker">Catálogo</span>
          <h2 className="text-3xl font-black text-charcoal mb-2">Productos</h2>
          <p className="text-muted">Gestión de platillos, precios, stock y recetas.</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-primary/10 text-primary-dark px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide">Total</span>
            <strong className="text-2xl font-black">{total}</strong>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex-1 flex flex-col">
        <section className="p-6 flex-1 flex flex-col">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4 border-b border-gray-100 pb-6">
            <form onSubmit={handleSearch} className="flex w-full md:max-w-md relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                 <Search size={18} className="text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Buscar por nombre..."
                value={searchDraft}
                onChange={(e) => setSearchDraft(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-l-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
              />
              <button type="submit" className="bg-gray-100 border border-gray-300 border-l-0 text-charcoal px-4 rounded-r-md font-bold hover:bg-gray-200 transition-colors">
                Buscar
              </button>
            </form>
            <div className="flex gap-3 shrink-0">
              <button
                className="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded-md transition-colors flex items-center gap-2"
                type="button"
                onClick={() => {
                  setSelectedProducto(null);
                  setIsFormOpen(true);
                }}
              >
                <Plus size={18} /> Nuevo producto
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 mb-6 bg-gray-50 p-4 rounded-lg">
            <label className="flex flex-col flex-1 min-w-[200px]">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Filtrar Categoría</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary outline-none bg-white"
                value={query.categoria_id || 0}
                onChange={(e) => {
                    const val = Number(e.target.value);
                    updateQuery({ categoria_id: val === 0 ? undefined : val, page: 1 });
                }}
              >
                <option value={0}>Todas las categorías</option>
                {catOptions.map(o => <option key={o.id} value={o.id}>{o.label}</option>)}
              </select>
            </label>
            <label className="flex flex-col flex-1 min-w-[200px]">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Disponibilidad</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary outline-none bg-white"
                value={query.disponible === undefined ? 'all' : String(query.disponible)}
                onChange={(e) => {
                    const val = e.target.value;
                    if (val === 'all') updateQuery({ disponible: undefined, page: 1 });
                    else updateQuery({ disponible: val === 'true', page: 1 });
                }}
              >
                <option value="all">Todos (Activos y Pausados)</option>
                <option value="true">Solo Disponibles</option>
                <option value="false">Solo Pausados</option>
              </select>
            </label>
            <label className="flex flex-col flex-1 min-w-[200px]">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Estado (Bajas)</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary outline-none bg-white"
                value={query.include_deleted ? 'true' : 'false'}
                onChange={(e) => {
                    const val = e.target.value === 'true';
                    updateQuery({ include_deleted: val, page: 1 });
                }}
              >
                <option value="false">Solo Activos</option>
                <option value="true">Incluir Dados de Baja</option>
              </select>
            </label>
            <label className="flex flex-col w-32">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Por página</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary outline-none bg-white"
                value={query.limit}
                onChange={(event) => updateQuery({ limit: Number(event.target.value), page: 1 })}
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </label>
          </div>

          {error ? <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6">{error}</div> : null}

          <div className="flex-1">
             <ProductosTable
                productos={productos}
                isLoading={isLoading}
                stockPosibleMap={stockPosibleMap}
                onView={handleView}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onToggleDisponibilidad={handleToggleDisponibilidad}
                onRestore={handleRestore}
             />
          </div>

          <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-100">
            <button
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
              type="button"
              disabled={query.page <= 1 || isLoading}
              onClick={() => updateQuery({ page: query.page - 1 })}
            >
              Anterior
            </button>
            <span className="text-sm font-medium text-gray-500">
              Página {query.page} de {totalPages} ({total} resultados)
            </span>
            <button
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
              type="button"
              disabled={query.page >= totalPages || isLoading}
              onClick={() => updateQuery({ page: query.page + 1 })}
            >
              Siguiente
            </button>
          </div>
        </section>
      </div>

      {isFormOpen ? (
        <Modal
          kicker="Catálogo"
          title={selectedProducto ? 'Editar producto' : 'Nuevo producto'}
          size="lg"
          onClose={() => {
            setIsFormOpen(false);
            setSelectedProducto(null);
          }}
        >
          <ProductoForm
            selectedProducto={selectedProducto}
            categoriasTree={categoriasTree}
            ingredientesList={supplies}
            isSubmitting={isMutating}
            onSubmit={handleSubmit}
            onCancelEdit={() => {
              setIsFormOpen(false);
              setSelectedProducto(null);
            }}
          />
        </Modal>
      ) : null}

      {detailProducto ? (
        <Modal kicker="Detalle" title={detailProducto.nombre} size="lg" onClose={() => setDetailProducto(null)}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 bg-gray-50 p-6 rounded-lg">
              {detailProducto.imagen_url && (
                <div className="col-span-2 md:col-span-4 flex justify-center mb-4">
                  <img src={detailProducto.imagen_url} alt={detailProducto.nombre} className="h-48 w-full object-cover rounded-lg shadow-sm" />
                </div>
              )}
              <div className="col-span-2 md:col-span-4">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Descripción</p>
                <p className="text-charcoal font-medium">{detailProducto.descripcion || 'Sin descripción'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Precio Base</p>
                <p className="text-2xl text-green-700 font-black">${detailProducto.precio_base}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Stock Disp.</p>
                <p className="text-charcoal font-bold text-lg">{detailProducto.stock_cantidad} u.</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">T. Prep.</p>
                <p className="text-charcoal font-bold text-lg">{detailProducto.tiempo_prep_min ? `${detailProducto.tiempo_prep_min} min` : 'N/A'}</p>
              </div>
              
              <div className="col-span-2 md:col-span-4 border-t border-gray-200 mt-2 pt-4">
                 <h4 className="font-bold text-charcoal mb-3">Receta ({detailProducto.ingredientes.length} insumos)</h4>
                 {detailProducto.ingredientes.length === 0 ? (
                    <p className="text-gray-500 italic text-sm">Este producto no descuenta insumos.</p>
                 ) : (
                    <ul className="space-y-2">
                      {detailProducto.ingredientes.map(i => (
                         <li key={i.ingrediente_id} className="flex justify-between items-center bg-white p-2 border border-gray-100 rounded text-sm">
                            <span className="font-bold text-charcoal">{i.nombre}</span>
                            <div className="flex gap-3">
                               <span className="text-gray-500">x{i.cantidad_requerida}</span>
                               {i.es_opcional && <span className="px-1.5 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">Extra</span>}
                               {i.es_removible && <span className="px-1.5 py-0.5 bg-orange-50 text-orange-700 text-xs rounded">Removible</span>}
                            </div>
                         </li>
                      ))}
                    </ul>
                 )}
              </div>
            </div>
        </Modal>
      ) : null}
    </section>
  );
}
