import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { Supply } from '../../../../types/supply';
import type { UnidadMedida } from '../../../../types/unidadMedida';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface SuppliesTableProps {
  supplies: Supply[];
  sortBy: string;
  sortDir: 'asc' | 'desc';
  isLoading?: boolean;
  lowStockIds?: Set<number>;
  onSort: (field: 'id' | 'nombre' | 'es_alergeno' | 'created_at' | 'updated_at') => void;
  onView: (supply: Supply) => void;
  onEdit: (supply: Supply) => void;
  onDelete: (supply: Supply) => void;
  onRestore: (supply: Supply) => void;
  unidadesMedida: UnidadMedida[];
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(value);
}

export function SuppliesTable({
  supplies,
  sortBy,
  sortDir,
  isLoading = false,
  lowStockIds,
  onSort,
  onView,
  onEdit,
  onDelete,
  onRestore,
  unidadesMedida,
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
      <table className="w-full min-w-[1100px] text-left border-collapse table-fixed">
        <thead>
          <tr className="bg-gray-50 border-y border-gray-200">
            <th className="p-4 font-bold text-sm text-charcoal w-[17%]">
              <button className="flex items-center hover:text-primary transition-colors" type="button" onClick={() => onSort('nombre')}>
                Nombre {renderSortIcon('nombre')}
              </button>
            </th>
            <th className="p-4 font-bold text-sm text-charcoal w-[14%]">Descripción</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[10%]">
              <button className="flex items-center hover:text-primary transition-colors" type="button" onClick={() => onSort('es_alergeno')}>
                Tipo {renderSortIcon('es_alergeno')}
              </button>
            </th>
            <th className="p-4 font-bold text-sm text-charcoal w-[10%]">Estado</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[10%]">Stock</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[10%]">Unidad</th>
            <th className="p-4 pr-8 font-bold text-sm text-charcoal w-[14%]">Precio unitario</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[15%] text-right" aria-label="Acciones">Acciones</th>
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
                <div className="flex flex-col items-start gap-1">
                  <span>{supply.stock_cantidad ?? 0}</span>
                  {lowStockIds?.has(supply.id) && !supply.deleted_at && (
                    <span className="text-[10px] font-black uppercase tracking-wider text-red-600 bg-red-100 px-2 py-0.5 rounded-full">
                      ¡Poco Stock!
                    </span>
                  )}
                </div>
              </td>
              <td className="p-4 text-sm text-gray-600">
                {unidadesMedida.find(u => u.id === supply.unidad_medida_id)?.simbolo ?? 'N/A'}
              </td>
              <td className="p-4 pr-8 text-sm font-medium text-charcoal whitespace-nowrap">
                {formatCurrency(supply.costo_unitario ?? 0)}
              </td>
              <td className="p-4">
                <div className="flex items-center justify-end gap-2 whitespace-nowrap">
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
