import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { Categoria } from '../../../../types/categoria';

interface CategoriasTableProps {
  categorias: Categoria[];
  isLoading?: boolean;
  onView: (categoria: Categoria) => void;
  onEdit: (categoria: Categoria) => void;
  onDelete: (categoria: Categoria) => void;
}

export function CategoriasTable({
  categorias,
  isLoading = false,
  onView,
  onEdit,
  onDelete,
}: CategoriasTableProps) {
  
  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 bg-gray-50 rounded-lg">Cargando categorías...</div>;
  }

  if (categorias.length === 0) {
    return (
      <EmptyState
        title="No hay categorías cargadas"
        description="Agrega la primera categoría para organizar tu menú."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse min-w-[800px]">
        <thead>
          <tr className="bg-gray-50 border-y border-gray-200">
            <th className="p-4 font-bold text-sm text-charcoal w-16 text-center">Orden</th>
            <th className="p-4 font-bold text-sm text-charcoal w-1/4">Nombre</th>
            <th className="p-4 font-bold text-sm text-charcoal w-1/4">Descripción</th>
            <th className="p-4 font-bold text-sm text-charcoal w-24">Estado</th>
            <th className="p-4 font-bold text-sm text-charcoal w-48 text-right" aria-label="Acciones">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {categorias.map((cat) => (
            <tr key={cat.id} className="hover:bg-gray-50/50 transition-colors">
              <td className="p-4 text-center font-bold text-gray-400">
                {cat.orden_display}
              </td>
              <td className="p-4">
                <div className="flex items-center gap-3">
                  {cat.imagen_url ? (
                    <img src={cat.imagen_url} alt={cat.nombre} className="w-10 h-10 rounded object-cover shadow-sm" />
                  ) : (
                    <div className="w-10 h-10 rounded bg-gray-200 flex items-center justify-center text-gray-500 shadow-sm">
                      IMG
                    </div>
                  )}
                  <div>
                    <strong className="text-primary-dark">{cat.nombre}</strong>
                    {cat.parent_id && <p className="text-xs text-gray-400">Subcategoría</p>}
                  </div>
                </div>
              </td>
              <td className="p-4 text-sm text-gray-600 truncate max-w-[200px]" title={cat.descripcion || ''}>
                {cat.descripcion || 'Sin descripción'}
              </td>
              <td className="p-4">
                <span
                  className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                    cat.deleted_at
                      ? 'bg-red-100 text-red-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  {cat.deleted_at ? 'Inactiva' : 'Activa'}
                </span>
              </td>
              <td className="p-4">
                <div className="flex items-center justify-end gap-2">
                  <Button variant="ghost" onClick={() => onView(cat)}>
                    Ver
                  </Button>
                  <Button
                    variant="secondary"
                    disabled={Boolean(cat.deleted_at)}
                    onClick={() => onEdit(cat)}
                  >
                    Editar
                  </Button>
                  {!cat.deleted_at && (
                    <Button variant="danger" onClick={() => onDelete(cat)}>
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
