import { useMemo, useState } from 'react';
import { Modal } from '../../components/ui/Modal/Modal';
import { useToast } from '../../components/ui/Toast/Toast';
import { SupplyForm } from '../../features/supplies/components/SupplyForm/SupplyForm';
import { SuppliesTable } from '../../features/supplies/components/SuppliesTable/SuppliesTable';
import { useSupplies } from '../../hooks/useSupplies';
import { useProductos } from '../../hooks/useProductos';
import { useUnidadesMedida } from '../../hooks/useUnidadesMedida';
import { suppliesService } from '../../services/suppliesService';
import type { SuppliesQuery, Supply, SupplyFormValues } from '../../types/supply';
import { Download, Plus } from 'lucide-react';

const defaultQuery: SuppliesQuery = {
  search: '',
  es_alergeno: 'all',
  include_deleted: false,
  page: 1,
  size: 8,
  sort_by: 'nombre',
  sort_dir: 'asc',
};

function exportSuppliesToExcel(supplies: Supply[]) {
  const escapeCell = (value: string | number) =>
    String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');

  const rows = supplies.map((supply) => `
    <tr>
      <td>${escapeCell(supply.id)}</td>
      <td>${escapeCell(supply.nombre)}</td>
      <td>${escapeCell(supply.descripcion ?? '')}</td>
      <td>${supply.es_alergeno ? 'Alergeno' : 'Comun'}</td>
      <td>${supply.deleted_at ? 'Inactivo' : 'Activo'}</td>
      <td>${escapeCell(new Date(supply.updated_at).toLocaleDateString('es-AR'))}</td>
    </tr>
  `);
  const html = `
    <html>
      <head><meta charset="UTF-8" /></head>
      <body>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Nombre</th><th>Descripcion</th><th>Tipo</th><th>Estado</th><th>Actualizado</th>
            </tr>
          </thead>
          <tbody>${rows.join('')}</tbody>
        </table>
      </body>
    </html>
  `;
  const blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `insumos-${new Date().toISOString().slice(0, 10)}.xls`;
  link.click();
  URL.revokeObjectURL(url);
}

export function SuppliesPage() {
  const [query, setQuery] = useState<SuppliesQuery>(defaultQuery);
  const [selectedSupply, setSelectedSupply] = useState<Supply | null>(null);
  const [detailSupply, setDetailSupply] = useState<Supply | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const { notify } = useToast();

  const stableQuery = useMemo(() => query, [query]);
  const {
    supplies,
    total,
    activeCount,
    allergenCount,
    error,
    isLoading,
    isMutating,
    createSupply,
    updateSupply,
    deleteSupply,
    restoreSupply,
  } = useSupplies(stableQuery);

  const { productos } = useProductos({ page: 1, size: 100 });
  const { unidades: unidadesMedida } = useUnidadesMedida({ page: 1, size: 100 });

  const lowStockIds = useMemo(() => {
    const ids = new Set<number>();
    productos.forEach((p) => {
      if (!p.ingredientes || p.ingredientes.length === 0) return;
      p.ingredientes.forEach((ing) => {
        if (ing.cantidad > 0) {
          const supply = supplies.find((s) => s.id === ing.ingrediente_id);
          if (supply) {
            const canMake = (supply.stock_cantidad || 0) / ing.cantidad;
            if (canMake < 10) {
              ids.add(supply.id);
            }
          }
        }
      });
    });
    return ids;
  }, [productos, supplies]);

  const totalPages = Math.max(1, Math.ceil(total / query.size));
  const currentPage = query.page;
  const existingNames = supplies
    .filter((supply) => !supply.deleted_at && supply.id !== selectedSupply?.id)
    .map((supply) => supply.nombre);

  const updateQuery = (patch: Partial<SuppliesQuery>) => {
    setQuery((current) => ({ ...current, ...patch, page: patch.page ?? 1 }));
  };

  const handleSubmit = async (values: SupplyFormValues) => {
    try {
      if (selectedSupply) {
        await updateSupply(selectedSupply.id, values);
        setSelectedSupply(null);
        setIsFormOpen(false);
        notify('success', 'Insumo actualizado correctamente.');
        return;
      }

      await createSupply(values);
      setIsFormOpen(false);
      notify('success', 'Insumo creado correctamente.');
    } catch (requestError) {
      notify(
        'error',
          requestError instanceof Error
            ? requestError.message
            : 'No se pudo guardar el insumo.',
      );
    }
  };

  const handleDelete = async (supply: Supply) => {
    try {
      await deleteSupply(supply.id);
      notify('success', `"${supply.nombre}" fue dado de baja correctamente.`);
    } catch (requestError) {
      notify(
        'error',
          requestError instanceof Error
            ? requestError.message
            : 'No se pudo dar de baja el insumo.',
      );
    }
  };

  const handleRestore = async (supply: Supply) => {
    try {
      await restoreSupply(supply.id);
      notify('success', `"${supply.nombre}" fue dado de alta correctamente.`);
    } catch (requestError) {
      notify(
        'error',
          requestError instanceof Error
            ? requestError.message
            : 'No se pudo dar de alta el insumo.',
      );
    }
  };

  const handleEdit = (supply: Supply) => {
    if (supply.deleted_at) {
      notify('info', 'Los insumos inactivos no se pueden editar.');
      return;
    }

    setSelectedSupply(supply);
    setIsFormOpen(true);
  };

  const handleView = async (supply: Supply) => {
    setDetailSupply(supply);
    try {
      const detail = await suppliesService.getById(supply.id);
      setDetailSupply(detail);
    } catch {
      setDetailSupply(supply);
    }
  };

  const handleSort = (field: SuppliesQuery['sort_by']) => {
    setQuery((current) => ({
      ...current,
      sort_by: field,
      sort_dir: current.sort_by === field && current.sort_dir === 'asc' ? 'desc' : 'asc',
      page: 1,
    }));
  };

  return (
    <section className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <span className="section-kicker">Inventario</span>
          <h2 className="text-3xl font-black text-charcoal mb-2">Ingredientes</h2>
          <p className="text-muted">Gestion operativa de ingredientes base para los productos.</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-primary/10 text-primary-dark px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide">Total</span>
            <strong className="text-2xl font-black">{total}</strong>
          </div>
          <div className="bg-gray-50 border border-gray-100 text-charcoal px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide text-gray-500">Activos</span>
            <strong className="text-2xl font-black">{activeCount}</strong>
          </div>
          <div className="bg-orange-50 border border-orange-100 text-orange-800 px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide text-orange-600">Alergenos</span>
            <strong className="text-2xl font-black">{allergenCount}</strong>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <section className="p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4 border-b border-gray-100 pb-6">
            <div>
              <h3 className="text-lg font-bold">Listado de ingredientes</h3>
              <span className="text-sm text-gray-500">
                Página {currentPage} de {totalPages}
              </span>
            </div>
            <div className="flex gap-3">
              <ButtonLikeExport disabled={supplies.length === 0} onClick={() => exportSuppliesToExcel(supplies)} />
              <button
                className="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded-md transition-colors flex items-center gap-2"
                type="button"
                onClick={() => {
                  setSelectedSupply(null);
                  setIsFormOpen(true);
                }}
              >
                <Plus size={18} /> Nuevo ingrediente
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6 bg-gray-50 p-4 rounded-lg">
            <label className="flex flex-col">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Búsqueda</span>
              <input
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                placeholder="Nombre o descripcion"
                value={query.search}
                onChange={(event) => updateQuery({ search: event.target.value })}
              />
            </label>
            <label className="flex flex-col">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Tipo</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary outline-none bg-white"
                value={query.es_alergeno}
                onChange={(event) =>
                  updateQuery({ es_alergeno: event.target.value as SuppliesQuery['es_alergeno'] })
                }
              >
                <option value="all">Todos</option>
                <option value="true">Alérgenos</option>
                <option value="false">Comunes</option>
              </select>
            </label>
            <label className="flex flex-col">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Estado</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary outline-none bg-white"
                value={query.include_deleted ? 'all' : 'active'}
                onChange={(event) =>
                  updateQuery({ include_deleted: event.target.value === 'all' })
                }
              >
                <option value="active">Solo activos</option>
                <option value="all">Activos e inactivos</option>
              </select>
            </label>
            <label className="flex flex-col">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Por página</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary outline-none bg-white"
                value={query.size}
                onChange={(event) => updateQuery({ size: Number(event.target.value) })}
              >
                <option value={8}>8</option>
                <option value={12}>12</option>
                <option value={20}>20</option>
              </select>
            </label>
          </div>

          {error ? <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6">{error}</div> : null}

          <SuppliesTable
            supplies={supplies}
            sortBy={query.sort_by}
            sortDir={query.sort_dir}
            isLoading={isLoading}
            lowStockIds={lowStockIds}
            onSort={handleSort}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onRestore={handleRestore}
            unidadesMedida={unidadesMedida}
          />

          <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-100">
            <button
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
              type="button"
              disabled={currentPage === 1 || isLoading}
              onClick={() => updateQuery({ page: Math.max(1, query.page - 1) })}
            >
              Anterior
            </button>
            <span className="text-sm font-medium text-gray-500">
              {total === 0 ? '0 resultados' : `${(query.page - 1) * query.size + 1}-${Math.min(query.page * query.size, total)} de ${total}`}
            </span>
            <button
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
              type="button"
              disabled={currentPage >= totalPages || isLoading}
              onClick={() => updateQuery({ page: query.page + 1 })}
            >
              Siguiente
            </button>
          </div>
        </section>
      </div>

      {isFormOpen ? (
        <Modal
          kicker="Stock"
          title={selectedSupply ? 'Editar ingrediente' : 'Nuevo ingrediente'}
          size="lg"
          onClose={() => {
            setIsFormOpen(false);
            setSelectedSupply(null);
          }}
        >
          <SupplyForm
            selectedSupply={selectedSupply}
            isSubmitting={isMutating}
            existingNames={existingNames}
            unidadesMedida={unidadesMedida}
            onSubmit={handleSubmit}
            onCancelEdit={() => {
              setIsFormOpen(false);
              setSelectedSupply(null);
            }}
          />
        </Modal>
      ) : null}

      {detailSupply ? (
        <Modal kicker="Detalle" title={detailSupply.nombre} onClose={() => setDetailSupply(null)}>
            <div className="grid grid-cols-2 gap-6 bg-gray-50 p-6 rounded-lg">
              <div className="col-span-2">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Descripcion</p>
                <p className="text-charcoal font-medium">{detailSupply.descripcion || 'Sin descripcion'}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Tipo</p>
                <p className="text-charcoal font-medium">{detailSupply.es_alergeno ? 'Alérgeno' : 'Común'}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Estado</p>
                <p className="text-charcoal font-medium">
                  {detailSupply.deleted_at ? 
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Inactivo</span> : 
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Activo</span>
                  }
                </p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Stock Actual</p>
                <p className="text-charcoal font-medium">{detailSupply.stock_cantidad ?? 0}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Actualizado</p>
                <p className="text-charcoal font-medium">{new Date(detailSupply.updated_at).toLocaleString('es-AR')}</p>
              </div>
            </div>
        </Modal>
      ) : null}
    </section>
  );
}

function ButtonLikeExport({
  disabled,
  onClick,
}: {
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button 
      className="border-2 border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300 font-bold py-2 px-4 rounded-md transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed" 
      disabled={disabled} 
      type="button" 
      onClick={onClick}
    >
      <Download size={18} /> Exportar Excel
    </button>
  );
}
