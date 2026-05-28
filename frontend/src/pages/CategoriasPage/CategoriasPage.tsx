import { useMemo, useState } from 'react';
import { Modal } from '../../components/ui/Modal/Modal';
import { useToast } from '../../components/ui/Toast/Toast';
import { CategoriaForm } from '../../features/categorias/components/CategoriaForm/CategoriaForm';
import { CategoriasTable } from '../../features/categorias/components/CategoriasTable/CategoriasTable';
import { CategoriasTree } from '../../features/categorias/components/CategoriasTree/CategoriasTree';
import { useCategorias, useCategoriasTree } from '../../hooks/useCategorias';
import type { CategoriasQuery, Categoria, CategoriaFormValues } from '../../types/categoria';
import { Plus } from 'lucide-react';

const defaultQuery: CategoriasQuery = {
  offset: 0,
  limit: 8,
  parent_id: null,
};

export function CategoriasPage() {
  const [query, setQuery] = useState<CategoriasQuery>(defaultQuery);
  const [selectedCategoria, setSelectedCategoria] = useState<Categoria | null>(null);
  const [detailCategoria, setDetailCategoria] = useState<Categoria | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const { confirm, notify } = useToast();
  const [vistaActual, setVistaActual] = useState<'grilla' | 'arbol'>('arbol');

  const stableQuery = useMemo(() => query, [query]);
  const {
    categorias,
    total,
    activeCount,
    error,
    isLoading,
    isMutating,
    createCategoria,
    updateCategoria,
    deleteCategoria,
    restoreCategoria,
  } = useCategorias(stableQuery);

  const { tree: categoriasTree } = useCategoriasTree();

  const totalPages = Math.max(1, Math.ceil(total / query.limit));
  const currentPage = Math.floor(query.offset / query.limit) + 1;
  const existingNames = categorias
    .filter((cat) => !cat.deleted_at && cat.id !== selectedCategoria?.id)
    .map((cat) => cat.nombre);

  const updateQuery = (patch: Partial<CategoriasQuery>) => {
    setQuery((current) => ({ ...current, ...patch, offset: patch.offset ?? 0 }));
  };

  const handleSubmit = async (values: CategoriaFormValues) => {
    try {
      if (selectedCategoria) {
        await updateCategoria(selectedCategoria.id, values);
        setSelectedCategoria(null);
        setIsFormOpen(false);
        notify('success', 'Categoría actualizada correctamente.');
        return;
      }

      await createCategoria(values);
      setIsFormOpen(false);
      notify('success', 'Categoría creada correctamente.');
    } catch (requestError) {
      notify(
        'error',
          requestError instanceof Error
            ? requestError.message
            : 'No se pudo guardar la categoría.',
      );
    }
  };

  const handleDelete = async (cat: Categoria) => {
    const confirmed = await confirm({
      confirmLabel: 'Dar de baja',
      message: `¿Estás seguro que deseas dar de baja la categoría "${cat.nombre}"?`,
      title: 'Dar de baja categoria',
      type: 'danger',
    });
    if (confirmed) {
        try {
        await deleteCategoria(cat.id);
        notify('success', `"${cat.nombre}" fue dada de baja correctamente.`);
        } catch (requestError) {
        notify(
            'error',
            requestError instanceof Error
                ? requestError.message
                : 'No se pudo dar de baja la categoría.',
        );
        }
    }
  };

  const handleRestore = async (cat: Categoria) => {
    try {
      await restoreCategoria(cat.id);
      notify('success', `"${cat.nombre}" fue dada de alta correctamente.`);
    } catch (requestError) {
      notify(
        'error',
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo dar de alta la categoría.',
      );
    }
  };

  const handleEdit = (cat: Categoria) => {
    if (cat.deleted_at) {
      notify('info', 'Las categorías inactivas no se pueden editar.');
      return;
    }
    setSelectedCategoria(cat);
    setIsFormOpen(true);
  };

  const handleView = (cat: Categoria) => {
    setDetailCategoria(cat);
  };

  return (
    <section className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <span className="section-kicker">Catálogo</span>
          <h2 className="text-3xl font-black text-charcoal mb-2">Categorías</h2>
          <p className="text-muted">Estructura y organización visual del menú de productos.</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-primary/10 text-primary-dark px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide">Total</span>
            <strong className="text-2xl font-black">{total}</strong>
          </div>
          <div className="bg-gray-50 border border-gray-100 text-charcoal px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide text-gray-500">Activas</span>
            <strong className="text-2xl font-black">{activeCount}</strong>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <section className="p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4 border-b border-gray-100 pb-6">
            <div>
              <h3 className="text-lg font-bold">Listado de Categorías</h3>
              {vistaActual === 'grilla' && (
                <span className="text-sm text-gray-500">
                  Página {currentPage} de {totalPages}
                </span>
              )}
            </div>
            <div className="flex gap-3 items-center">
              {/* Toggle vista */}
              <div className="flex rounded-lg border border-gray-200 overflow-hidden">
                <button
                  type="button"
                  onClick={() => setVistaActual('grilla')}
                  className={`px-3 py-1.5 text-sm font-bold transition-colors ${
                    vistaActual === 'grilla'
                      ? 'bg-primary text-white'
                      : 'bg-white text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  📋 Grilla
                </button>
                <button
                  type="button"
                  onClick={() => setVistaActual('arbol')}
                  className={`px-3 py-1.5 text-sm font-bold transition-colors ${
                    vistaActual === 'arbol'
                      ? 'bg-primary text-white'
                      : 'bg-white text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  🌳 Árbol
                </button>
              </div>
              <button
                className="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded-md transition-colors flex items-center gap-2"
                type="button"
                onClick={() => {
                  setSelectedCategoria(null);
                  setIsFormOpen(true);
                }}
              >
                <Plus size={18} /> Nueva categoría
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 mb-6 bg-gray-50 p-4 rounded-lg">
            <label className="flex flex-col flex-1 min-w-[200px]">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Filtro de Padre</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none bg-white"
                value={query.parent_id === null ? 'null' : (query.parent_id === undefined ? 'all' : query.parent_id)}
                onChange={(event) => {
                    const val = event.target.value;
                    if (val === 'all') updateQuery({ parent_id: undefined });
                    else if (val === 'null') updateQuery({ parent_id: null });
                    else updateQuery({ parent_id: Number(val) });
                }}
              >
                <option value="all">Todas las categorías</option>
                <option value="null">Solo Categorías Principales</option>
              </select>
            </label>
            <label className="flex flex-col flex-1 min-w-[200px]">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Estado (Bajas)</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none bg-white"
                value={query.include_deleted ? 'all' : 'active'}
                onChange={(e) => updateQuery({ include_deleted: e.target.value === 'all' })}
              >
                <option value="active">Solo Activas</option>
                <option value="all">Incluir Dadas de Baja</option>
              </select>
            </label>
            
            <label className="flex flex-col w-32">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Por página</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none bg-white"
                value={query.limit}
                onChange={(event) => updateQuery({ limit: Number(event.target.value) })}
              >
                <option value={8}>8</option>
                <option value={12}>12</option>
                <option value={20}>20</option>
              </select>
            </label>
          </div>

          {error ? <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6">{error}</div> : null}

          {vistaActual === 'arbol' ? (
            <CategoriasTree
              tree={categoriasTree}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onRestore={handleRestore}
            />
          ) : (
            <>
              <div className="flex flex-wrap gap-4 mb-6 bg-gray-50 p-4 rounded-lg">
                <label className="flex flex-col flex-1 min-w-[200px]">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Filtro de Padre</span>
                  <select
                    className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none bg-white"
                    value={query.parent_id === null ? 'null' : (query.parent_id === undefined ? 'all' : query.parent_id)}
                    onChange={(event) => {
                        const val = event.target.value;
                        if (val === 'all') updateQuery({ parent_id: undefined });
                        else if (val === 'null') updateQuery({ parent_id: null });
                        else updateQuery({ parent_id: Number(val) });
                    }}
                  >
                    <option value="all">Todas las categorías</option>
                    <option value="null">Solo Categorías Principales</option>
                  </select>
                </label>
                <label className="flex flex-col flex-1 min-w-[200px]">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Estado (Bajas)</span>
                  <select
                    className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none bg-white"
                    value={query.include_deleted ? 'all' : 'active'}
                    onChange={(e) => updateQuery({ include_deleted: e.target.value === 'all' })}
                  >
                    <option value="active">Solo Activas</option>
                    <option value="all">Incluir Dadas de Baja</option>
                  </select>
                </label>
                <label className="flex flex-col w-32">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Por página</span>
                  <select
                    className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none bg-white"
                    value={query.limit}
                    onChange={(event) => updateQuery({ limit: Number(event.target.value) })}
                  >
                    <option value={8}>8</option>
                    <option value={12}>12</option>
                    <option value={20}>20</option>
                  </select>
                </label>
              </div>

              <CategoriasTable
                categorias={categorias}
                isLoading={isLoading}
                onView={handleView}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onRestore={handleRestore}
              />

              <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-100">
                <button
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
                  type="button"
                  disabled={currentPage === 1 || isLoading}
                  onClick={() => updateQuery({ offset: Math.max(0, query.offset - query.limit) })}
                >
                  Anterior
                </button>
                <span className="text-sm font-medium text-gray-500">
                  {total === 0 ? '0 resultados' : `${query.offset + 1}-${Math.min(query.offset + query.limit, total)} de ${total}`}
                </span>
                <button
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
                  type="button"
                  disabled={currentPage >= totalPages || isLoading}
                  onClick={() => updateQuery({ offset: query.offset + query.limit })}
                >
                  Siguiente
                </button>
              </div>
            </>
          )}
        </section>
      </div>

      {isFormOpen ? (
        <Modal
          kicker="Catálogo"
          title={selectedCategoria ? 'Editar categoría' : 'Nueva categoría'}
          size="lg"
          onClose={() => {
            setIsFormOpen(false);
            setSelectedCategoria(null);
          }}
        >
          <CategoriaForm
            selectedCategoria={selectedCategoria}
            categoriasTree={categoriasTree}
            isSubmitting={isMutating}
            existingNames={existingNames}
            onSubmit={handleSubmit}
            onCancelEdit={() => {
              setIsFormOpen(false);
              setSelectedCategoria(null);
            }}
          />
        </Modal>
      ) : null}

      {detailCategoria ? (
        <Modal kicker="Detalle" title={detailCategoria.nombre} onClose={() => setDetailCategoria(null)}>
            <div className="grid grid-cols-2 gap-6 bg-gray-50 p-6 rounded-lg">
              {detailCategoria.imagen_url && (
                <div className="col-span-2 flex justify-center mb-4">
                  <img src={detailCategoria.imagen_url} alt={detailCategoria.nombre} className="max-h-48 rounded-lg shadow-sm" />
                </div>
              )}
              <div className="col-span-2">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Descripción</p>
                <p className="text-charcoal font-medium">{detailCategoria.descripcion || 'Sin descripción'}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Jerarquía</p>
                <p className="text-charcoal font-medium">{detailCategoria.parent_id ? 'Subcategoría' : 'Principal'}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Estado</p>
                <p className="text-charcoal font-medium">
                  {detailCategoria.deleted_at ? 
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Inactiva</span> : 
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Activa</span>
                  }
                </p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Orden Visual</p>
                <p className="text-charcoal font-medium">{detailCategoria.orden_display}</p>
              </div>
            </div>
        </Modal>
      ) : null}
    </section>
  );
}
