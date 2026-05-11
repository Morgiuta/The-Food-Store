import { useMemo, useState } from 'react';
import { Modal } from '../../components/ui/Modal/Modal';
import { ToastViewport, type ToastMessage, type ToastType } from '../../components/ui/Toast/Toast';
import { SupplyForm } from '../../features/supplies/components/SupplyForm/SupplyForm';
import { SuppliesTable } from '../../features/supplies/components/SuppliesTable/SuppliesTable';
import { useSupplies } from '../../hooks/useSupplies';
import { suppliesService } from '../../services/suppliesService';
import type { SuppliesQuery, Supply, SupplyFormValues } from '../../types/supply';
import './SuppliesPage.css';

const defaultQuery: SuppliesQuery = {
  search: '',
  es_alergeno: 'all',
  include_deleted: false,
  offset: 0,
  limit: 8,
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
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

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

  const totalPages = Math.max(1, Math.ceil(total / query.limit));
  const currentPage = Math.floor(query.offset / query.limit) + 1;
  const existingNames = supplies
    .filter((supply) => !supply.deleted_at && supply.id !== selectedSupply?.id)
    .map((supply) => supply.nombre);

  const updateQuery = (patch: Partial<SuppliesQuery>) => {
    setQuery((current) => ({ ...current, ...patch, offset: patch.offset ?? 0 }));
  };

  const dismissToast = (id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  };

  const notify = (type: ToastType, message: string) => {
    const id = Date.now();
    setToasts((current) => [...current.slice(-2), { id, message, type }]);
    window.setTimeout(() => dismissToast(id), 4200);
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
      offset: 0,
    }));
  };

  return (
    <section className="supplies-page">
      <ToastViewport toasts={toasts} onDismiss={dismissToast} />

      <div className="supplies-page__heading">
        <div>
          <span className="section-kicker">Inventario</span>
          <h2>Insumos</h2>
          <p>Gestion operativa de insumos basada en ingredientes y alergenos.</p>
        </div>
        <div className="supplies-page__stats">
          <div className="supplies-page__summary">
            <span>Total filtrado</span>
            <strong>{total}</strong>
          </div>
          <div className="supplies-page__summary supplies-page__summary--light">
            <span>Activos</span>
            <strong>{activeCount}</strong>
          </div>
          <div className="supplies-page__summary supplies-page__summary--light">
            <span>Alergenos</span>
            <strong>{allergenCount}</strong>
          </div>
        </div>
      </div>

      <div className="supplies-page__content">
        <section className="supplies-page__list">
          <div className="supplies-page__list-header">
            <div>
              <h3>Listado de insumos</h3>
              <span>
                Pagina {currentPage} de {totalPages}
              </span>
            </div>
            <div className="supplies-page__list-actions">
              <button
                className="supplies-page__new"
                type="button"
                onClick={() => {
                  setSelectedSupply(null);
                  setIsFormOpen(true);
                }}
              >
                Nuevo insumo
              </button>
              <ButtonLikeExport disabled={supplies.length === 0} onClick={() => exportSuppliesToExcel(supplies)} />
            </div>
          </div>

          <div className="supplies-page__toolbar">
            <label>
              <span>Busqueda</span>
              <input
                placeholder="Nombre o descripcion"
                value={query.search}
                onChange={(event) => updateQuery({ search: event.target.value })}
              />
            </label>
            <label>
              <span>Tipo</span>
              <select
                value={query.es_alergeno}
                onChange={(event) =>
                  updateQuery({ es_alergeno: event.target.value as SuppliesQuery['es_alergeno'] })
                }
              >
                <option value="all">Todos</option>
                <option value="true">Alergenos</option>
                <option value="false">Comunes</option>
              </select>
            </label>
            <label>
              <span>Estado</span>
              <select
                value={query.include_deleted ? 'all' : 'active'}
                onChange={(event) =>
                  updateQuery({ include_deleted: event.target.value === 'all' })
                }
              >
                <option value="active">Solo activos</option>
                <option value="all">Activos e inactivos</option>
              </select>
            </label>
            <label>
              <span>Por pagina</span>
              <select
                value={query.limit}
                onChange={(event) => updateQuery({ limit: Number(event.target.value) })}
              >
                <option value={8}>8</option>
                <option value={12}>12</option>
                <option value={20}>20</option>
              </select>
            </label>
          </div>

          {error ? <div className="supplies-page__error">{error}</div> : null}

          <SuppliesTable
            supplies={supplies}
            sortBy={query.sort_by}
            sortDir={query.sort_dir}
            isLoading={isLoading}
            onSort={handleSort}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onRestore={handleRestore}
          />

          <div className="supplies-page__pagination">
            <button
              type="button"
              disabled={currentPage === 1 || isLoading}
              onClick={() => updateQuery({ offset: Math.max(0, query.offset - query.limit) })}
            >
              Anterior
            </button>
            <span>
              {total === 0 ? '0 resultados' : `${query.offset + 1}-${Math.min(query.offset + query.limit, total)} de ${total}`}
            </span>
            <button
              type="button"
              disabled={currentPage >= totalPages || isLoading}
              onClick={() => updateQuery({ offset: query.offset + query.limit })}
            >
              Siguiente
            </button>
          </div>
        </section>
      </div>

      {isFormOpen ? (
        <Modal
          kicker="Stock"
          title={selectedSupply ? 'Editar insumo' : 'Nuevo insumo'}
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
            <dl className="supplies-modal__grid">
              <div>
                <dt>Descripcion</dt>
                <dd>{detailSupply.descripcion || 'Sin descripcion'}</dd>
              </div>
              <div>
                <dt>Tipo</dt>
                <dd>{detailSupply.es_alergeno ? 'Alergeno' : 'Comun'}</dd>
              </div>
              <div>
                <dt>Estado</dt>
                <dd>{detailSupply.deleted_at ? 'Inactivo' : 'Activo'}</dd>
              </div>
              <div>
                <dt>Actualizado</dt>
                <dd>{new Date(detailSupply.updated_at).toLocaleString('es-AR')}</dd>
              </div>
            </dl>
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
    <button className="supplies-page__export" disabled={disabled} type="button" onClick={onClick}>
      Exportar Excel
    </button>
  );
}
