import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { Supply } from '../../../../types/supply';
import { ChevronUp, ChevronDown } from 'lucide-react';

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
  const renderSortIcon = (field: string) => {
    if (sortBy !== field) return null;
    return sortDir === 'asc' ? <ChevronUp size={16} className="inline ml-1" /> : <ChevronDown size={16} className="inline ml-1" />;
  };

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 bg-gray-50 rounded-lg">Cargando ingredientes...</div>;
  }

  if (supplies.length === 0) {
    return (
      <EmptyState
        title="No hay ingredientes cargados"
        description="Agrega el primer ingrediente para empezar a controlar el stock del local."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse min-w-[800px]">
        <thead>
          <tr className="bg-gray-50 border-y border-gray-200">
            <th className="p-4 font-bold text-sm text-charcoal w-1/5">
              <button className="flex items-center hover:text-primary transition-colors" type="button" onClick={() => onSort('nombre')}>
                Nombre {renderSortIcon('nombre')}
              </button>
            </th>
            <th className="p-4 font-bold text-sm text-charcoal w-1/4">Descripción</th>
            <th className="p-4 font-bold text-sm text-charcoal w-32">
              <button className="flex items-center hover:text-primary transition-colors" type="button" onClick={() => onSort('es_alergeno')}>
                Tipo {renderSortIcon('es_alergeno')}
              </button>
            </th>
            <th className="p-4 font-bold text-sm text-charcoal w-24">Estado</th>
            <th className="p-4 font-bold text-sm text-charcoal w-32">Stock</th>
            <th className="p-4 font-bold text-sm text-charcoal w-32">
              <button className="flex items-center hover:text-primary transition-colors" type="button" onClick={() => onSort('updated_at')}>
                Actualizado {renderSortIcon('updated_at')}
              </button>
            </th>
            <th className="p-4 font-bold text-sm text-charcoal w-48 text-right" aria-label="Acciones">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {supplies.map((supply) => (
            <tr key={supply.id} className="hover:bg-gray-50/50 transition-colors">
              <td className="p-4">
                <strong className="text-primary-dark">{supply.nombre}</strong>
              </td>
              <td className="p-4 text-sm text-gray-600 truncate max-w-[200px]" title={supply.descripcion || undefined}>
                {supply.descripcion || 'Sin descripción'}
              </td>
              <td className="p-4">
                <span
                  className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                    supply.es_alergeno
                      ? 'bg-orange-100 text-orange-800'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {supply.es_alergeno ? 'Alérgeno' : 'Común'}
                </span>
              </td>
              <td className="p-4">
                <span
                  className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                    supply.deleted_at
                      ? 'bg-red-100 text-red-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  {supply.deleted_at ? 'Inactivo' : 'Activo'}
                </span>
              </td>
              <td className="p-4 font-medium text-charcoal">
                {supply.stock_actual ?? 0}
              </td>
              <td className="p-4 text-sm text-gray-500">{formatDate(supply.updated_at)}</td>
              <td className="p-4">
                <div className="flex items-center justify-end gap-2">
                  <Button variant="ghost" onClick={() => onView(supply)}>
                    Ver
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
