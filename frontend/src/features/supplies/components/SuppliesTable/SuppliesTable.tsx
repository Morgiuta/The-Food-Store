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
              <td>
                <strong>{supply.nombre}</strong>
              </td>
              <td>{supply.descripcion || 'Sin descripcion'}</td>
              <td>
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
              <td>
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
              <td>{formatDate(supply.updated_at)}</td>
              <td>
                <div className="supplies-table__actions">
                  <Button variant="ghost" onClick={() => onView(supply)}>
                    Detalle
                  </Button>
                  <Button variant="secondary" onClick={() => onEdit(supply)}>
                    Editar
                  </Button>
                  <Button
                    variant="danger"
                    disabled={Boolean(supply.deleted_at)}
                    onClick={() => onDelete(supply)}
                  >
                    Baja
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
