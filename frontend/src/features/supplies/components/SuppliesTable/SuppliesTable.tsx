import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { Supply } from '../../../../types/supply';
import './SuppliesTable.css';

interface SuppliesTableProps {
  supplies: Supply[];
  onEdit: (supply: Supply) => void;
  onDelete: (id: string) => void;
}

export function SuppliesTable({ supplies, onEdit, onDelete }: SuppliesTableProps) {
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
            <th>Nombre</th>
            <th>Descripcion</th>
            <th>Cantidad</th>
            <th aria-label="Acciones" />
          </tr>
        </thead>
        <tbody>
          {supplies.map((supply) => (
            <tr key={supply.id}>
              <td>
                <strong>{supply.name}</strong>
              </td>
              <td>{supply.description || 'Sin descripcion'}</td>
              <td>
                <span className="supplies-table__quantity">{supply.quantity}</span>
              </td>
              <td>
                <div className="supplies-table__actions">
                  <Button variant="secondary" onClick={() => onEdit(supply)}>
                    Editar
                  </Button>
                  <Button variant="danger" onClick={() => onDelete(supply.id)}>
                    Eliminar
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
