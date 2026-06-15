import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { Producto } from '../../../../types/producto';

interface ProductosTableProps {
  productos: Producto[];
  isLoading?: boolean;
  stockPosibleMap?: Map<number, number>;
  onView: (producto: Producto) => void;
  onEdit: (producto: Producto) => void;
  onDelete: (producto: Producto) => void;
  onToggleDisponibilidad: (producto: Producto) => void;
  onRestore: (producto: Producto) => void;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(value);
}

export function ProductosTable({
  productos,
  isLoading = false,
  stockPosibleMap,
  onView,
  onEdit,
  onDelete,
  onToggleDisponibilidad,
  onRestore,
}: ProductosTableProps) {
  
  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 bg-gray-50 rounded-lg">Cargando productos...</div>;
  }

  if (productos.length === 0) {
    return (
      <EmptyState
        title="No hay productos cargados"
        description="Empieza a poblar tu catálogo creando el primer producto."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse table-fixed">
        <thead>
          <tr className="bg-gray-50 border-y border-gray-200">
            <th className="p-4 font-bold text-sm text-charcoal w-[35%]">Producto</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[15%]">Precio</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[15%]">Stock</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[15%] text-center">Disponibilidad</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[20%] text-right" aria-label="Acciones">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {productos.map((prod) => {
            const isAvailable = prod.disponible;
            const principalCategory = prod.categorias.find(c => c.es_principal);

            const isDeleted = Boolean(prod.deleted_at);

            return (
            <tr key={prod.id} className={`hover:bg-gray-50/50 transition-colors ${isDeleted ? 'opacity-60 bg-red-50/30' : ''}`}>
              <td className="p-4">
                <div className="flex items-center gap-4">
                  {prod.imagen_url ? (
                    <img src={prod.imagen_url} alt={prod.nombre} className="w-12 h-12 rounded-lg object-cover shadow-sm border border-gray-100" />
                  ) : (
                    <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400 shadow-sm border border-gray-100 text-xs font-bold">
                      IMG
                    </div>
                  )}
                  <div>
                    <strong className="text-charcoal block mb-0.5 truncate max-w-[150px] sm:max-w-[200px]" title={prod.nombre}>{prod.nombre}</strong>
                    <div className="flex items-center gap-2 text-xs">
                      {principalCategory ? (
                        <span className="text-gray-500">Cat ID: {principalCategory.categoria_id}</span>
                      ) : (
                        <span className="text-gray-400 italic">Sin categoría</span>
                      )}
                      {prod.ingredientes.length > 0 && (
                         <span className="bg-orange-50 text-orange-600 px-1.5 py-0.5 rounded font-bold">Receta: {prod.ingredientes.length}</span>
                      )}
                    </div>
                    {isDeleted && (
                      <span className="mt-1 inline-block bg-red-100 text-red-800 text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wide">
                        Dado de baja
                      </span>
                    )}
                  </div>
                </div>
              </td>
              <td className="p-4 font-bold text-green-700 text-lg">
                {formatCurrency(prod.precio_base)}
              </td>
              <td className="p-4">
                <div className="flex flex-col items-start gap-1">
                  {(() => {
                    const stockBase = (
                      <span className={`font-bold ${prod.stock_cantidad <= 5 ? 'text-red-500' : 'text-gray-600'}`}>
                        {prod.stock_cantidad} {prod.unidad_venta?.simbolo ?? 'u.'}
                      </span>
                    );
                    
                    if (!stockPosibleMap || prod.ingredientes.length === 0) return stockBase;
                    
                    const posible = stockPosibleMap.get(prod.id);
                    if (posible === undefined) return stockBase;
                    
                    return (
                      <>
                        {stockBase}
                        {posible >= 10 ? (
                          <span className="text-[10px] font-bold text-green-700 bg-green-100 px-2 py-0.5 rounded-full mt-1">
                            Elaborables: {posible}
                          </span>
                        ) : posible >= 1 ? (
                          <span className="text-[10px] font-bold text-orange-700 bg-orange-100 px-2 py-0.5 rounded-full mt-1">
                            ⚠ Solo {posible} posibles
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded-full mt-1">
                            ✗ Sin stock de insumos
                          </span>
                        )}
                      </>
                    );
                  })()}
                </div>
              </td>
              <td className="p-4">
                <div className="flex justify-center">
                  <button
                    onClick={() => onToggleDisponibilidad(prod)}
                    disabled={isDeleted}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                      isAvailable ? 'bg-green-500' : 'bg-gray-200'
                    } ${isDeleted ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        isAvailable ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <div className="text-center mt-1">
                   <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide">
                     {isAvailable ? 'Activo' : 'Pausado'}
                   </span>
                </div>
              </td>
              <td className="p-4">
                <div className="flex items-center justify-end gap-2">
                  <Button variant="ghost" onClick={() => onView(prod)}>
                    Ver
                  </Button>
                  {!isDeleted ? (
                    <>
                      <Button
                        variant="secondary"
                        onClick={() => onEdit(prod)}
                      >
                        Editar
                      </Button>
                      <Button variant="danger" onClick={() => onDelete(prod)}>
                        Baja
                      </Button>
                    </>
                  ) : (
                    <Button variant="success" onClick={() => onRestore(prod)}>
                      Alta
                    </Button>
                  )}
                </div>
              </td>
            </tr>
          )})}
        </tbody>
      </table>
    </div>
  );
}
