import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { Supply } from '../../../../types/supply';
import './SuppliesTable.css';

interface SuppliesTableProps {
  supplies: Supply[];
  sortBy: string;
  sortDir: 'asc' | 'desc';
  isLoading?: boolean;
  onSort: (field: 'id' | 'nombre' | 'es_alergeno' | 'created_at' | 'updated_at') => void;
  onView: (supply: Supply) => void;
  onEdit: (supply: Supply) => void;
  onDelete: (supply: Supply) => void;
  onRestore: (supply: Supply) => void;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(value));
}

export function SuppliesTable({
  supplies,
  sortBy,
  sortDir,
  isLoading = false,
  onSort,
  onView,
  onEdit,
  onDelete,
  onRestore,
}: SuppliesTableProps) {
  const renderSortLabel = (field: SuppliesTableProps['sortBy'], label: string) =>
    `${label}${sortBy === field ? (sortDir === 'asc' ? ' ASC' : ' DESC') : ''}`;

  if (isLoading) {
    return <div className="supplies-table__state">Cargando insumos...</div>;
  }

  if (supplies.length === 0) {
    return (
      <EmptyState
        title="No hay insumos cargados"
        description="Agrega el primer insumo para empezar a controlar el stock del local."
      />
    );
  }

  return (
    <div className="supplies-table">
      <table>
        <colgroup>
          <col className="supplies-table__col supplies-table__col--name" />
          <col className="supplies-table__col supplies-table__col--description" />
          <col className="supplies-table__col supplies-table__col--type" />
          <col className="supplies-table__col supplies-table__col--status" />
          <col className="supplies-table__col supplies-table__col--date" />
          <col className="supplies-table__col supplies-table__col--actions" />
        </colgroup>
        <thead>
          <tr>
            <th>
              <button type="button" onClick={() => onSort('nombre')}>
                {renderSortLabel('nombre', 'Nombre')}
              </button>
            </th>
            <th>Descripcion</th>
            <th>
              <button type="button" onClick={() => onSort('es_alergeno')}>
                {renderSortLabel('es_alergeno', 'Tipo')}
              </button>
            </th>
            <th>Estado</th>
            <th>
              <button type="button" onClick={() => onSort('updated_at')}>
                {renderSortLabel('updated_at', 'Actualizado')}
              </button>
            </th>
            <th aria-label="Acciones" />
          </tr>
        </thead>
        <tbody>
          {supplies.map((supply) => (
            <tr key={supply.id}>
              <td data-label="Nombre">
                <strong>{supply.nombre}</strong>
              </td>
              <td data-label="Descripcion">{supply.descripcion || 'Sin descripcion'}</td>
              <td data-label="Tipo">
                <span
                  className={
                    supply.es_alergeno
                      ? 'supplies-table__badge supplies-table__badge--warning'
                      : 'supplies-table__badge'
                  }
                >
                  {supply.es_alergeno ? 'Alergeno' : 'Comun'}
                </span>
              </td>
              <td data-label="Estado">
                <span
                  className={
                    supply.deleted_at
                      ? 'supplies-table__badge supplies-table__badge--inactive'
                      : 'supplies-table__badge supplies-table__badge--active'
                  }
                >
                  {supply.deleted_at ? 'Inactivo' : 'Activo'}
                </span>
              </td>
              <td data-label="Actualizado">{formatDate(supply.updated_at)}</td>
              <td data-label="Acciones">
                <div className="supplies-table__actions">
                  <Button variant="ghost" onClick={() => onView(supply)}>
                    Detalle
                  </Button>
                  <Button
                    variant="secondary"
                    disabled={Boolean(supply.deleted_at)}
                    onClick={() => onEdit(supply)}
                  >
                    Editar
                  </Button>
                  {supply.deleted_at ? (
                    <Button variant="primary" onClick={() => onRestore(supply)}>
                      Alta
                    </Button>
                  ) : (
                    <Button variant="danger" onClick={() => onDelete(supply)}>
                      Baja
                    </Button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
