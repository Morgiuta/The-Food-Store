import { useState, useMemo } from 'react';
import { Modal } from '../../components/ui/Modal/Modal';
import { Button } from '../../components/ui/Button/Button';
import { useProductos } from '../../hooks/useProductos';
import type { Pedido } from '../../types/pedido';

interface ModalEditarPedidoProps {
  pedido: Pedido;
  isMutating: boolean;
  onClose: () => void;
  onSave: (pedidoId: number, detalles: any[]) => Promise<void>;
}

export function ModalEditarPedido({ pedido, isMutating, onClose, onSave }: ModalEditarPedidoProps) {
  const [detalles, setDetalles] = useState(() => 
    pedido.detalles.map(d => ({
      producto_id: d.producto_id,
      cantidad: d.cantidad,
      personalizacion: d.personalizacion || null,
      nombre_snapshot: d.nombre_snapshot,
      precio_snapshot: d.precio_snapshot,
      subtotal_snapshot: d.subtotal_snapshot,
      isOriginal: true,
      originalCantidad: d.cantidad
    }))
  );

  const [selectedProductId, setSelectedProductId] = useState<number>(0);
  const { productos, isLoading } = useProductos({ page: 1, size: 100, disponible: true });

  const estado = pedido.estado_codigo;
  const isEnPrep = estado === 'EN_PREP';

  const addProducto = (prodId: number) => {
    const prod = productos.find(p => p.id === prodId);
    if (!prod) return;

    setDetalles(prev => {
      const existingIndex = prev.findIndex(d => d.producto_id === prodId && !d.personalizacion);
      if (existingIndex >= 0) {
        const updated = [...prev];
        const d = updated[existingIndex];
        updated[existingIndex] = { 
          ...d, 
          cantidad: d.cantidad + 1, 
          subtotal_snapshot: (d.cantidad + 1) * prod.precio_base 
        };
        return updated;
      }
      return [...prev, {
        producto_id: prodId,
        cantidad: 1,
        personalizacion: null,
        nombre_snapshot: prod.nombre,
        precio_snapshot: prod.precio_base,
        subtotal_snapshot: prod.precio_base,
        isOriginal: false,
        originalCantidad: 0
      }];
    });
  };

  const removeProducto = (index: number) => {
    setDetalles(prev => {
      const target = prev[index];
      if (isEnPrep && target.isOriginal && target.cantidad <= target.originalCantidad) {
         return prev; // Cannot reduce original in EN_PREP
      }
      if (target.cantidad > 1) {
        if (isEnPrep && target.isOriginal && target.cantidad - 1 < target.originalCantidad) {
           return prev; // Cannot reduce original in EN_PREP
        }
        const updated = [...prev];
        updated[index] = { 
          ...target, 
          cantidad: target.cantidad - 1,
          subtotal_snapshot: (target.cantidad - 1) * target.precio_snapshot
        };
        return updated;
      }
      if (isEnPrep && target.isOriginal) return prev; 
      return prev.filter((_, i) => i !== index);
    });
  };

  const increaseCantidad = (index: number) => {
    setDetalles(prev => {
      const target = prev[index];
      const updated = [...prev];
      updated[index] = { 
        ...target, 
        cantidad: target.cantidad + 1,
        subtotal_snapshot: (target.cantidad + 1) * target.precio_snapshot
      };
      return updated;
    });
  };

  const availableProducts = useMemo(() => {
    if (isEnPrep) {
      return productos.filter(p => p.tiempo_prep_min == null || p.tiempo_prep_min <= 0);
    }
    return productos;
  }, [productos, isEnPrep]);

  const subtotalTotal = detalles.reduce((acc, curr) => acc + curr.subtotal_snapshot, 0);

  const handleSave = async () => {
    const payload = detalles.map(d => ({
      producto_id: d.producto_id,
      cantidad: d.cantidad,
      personalizacion: d.personalizacion
    }));
    await onSave(pedido.id, payload);
  };

  return (
    <Modal title={`Editar Pedido #${pedido.id}`} onClose={onClose} size="lg">
      <div className="bg-white p-4">
        {isEnPrep && (
          <div className="mb-4 rounded bg-orange-100 p-3 text-sm text-orange-800">
            <strong>Atención:</strong> El pedido está en preparación. Solo puedes agregar productos de tipo consumidor final (bebidas, postres) y no puedes eliminar productos existentes.
          </div>
        )}

        <div className="mb-6">
          <h3 className="mb-2 text-sm font-black uppercase text-gray-500">Productos del Pedido</h3>
          <ul className="space-y-3">
            {detalles.map((d, i) => {
              const cantReduce = isEnPrep && d.isOriginal && d.cantidad <= d.originalCantidad;
              return (
                <li key={i} className="flex items-center justify-between rounded border border-gray-200 p-3">
                  <div>
                    <div className="font-bold">{d.nombre_snapshot}</div>
                    <div className="text-sm text-gray-500">${d.precio_snapshot} c/u</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <button 
                      type="button" 
                      onClick={() => removeProducto(i)}
                      disabled={cantReduce}
                      className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 font-bold hover:bg-gray-200 disabled:opacity-30"
                    >
                      -
                    </button>
                    <span className="w-6 text-center font-black">{d.cantidad}</span>
                    <button 
                      type="button" 
                      onClick={() => increaseCantidad(i)}
                      className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 font-bold hover:bg-gray-200"
                    >
                      +
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="mb-6">
          <h3 className="mb-2 text-sm font-black uppercase text-gray-500">Agregar Producto</h3>
          {isLoading ? (
            <div className="text-sm text-gray-500">Cargando catálogo...</div>
          ) : (
            <div className="flex gap-2">
              <select
                className="flex-1 rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(Number(e.target.value))}
              >
                <option value={0}>Seleccionar producto...</option>
                {availableProducts.map(p => (
                  <option key={p.id} value={p.id}>{p.nombre} - ${p.precio_base}</option>
                ))}
              </select>
              <Button 
                type="button" 
                onClick={() => {
                  if (selectedProductId > 0) {
                    addProducto(selectedProductId);
                    setSelectedProductId(0);
                  }
                }}
                disabled={selectedProductId === 0}
              >
                Agregar
              </Button>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-gray-200 pt-4">
          <div className="text-xl font-black">Subtotal: ${subtotalTotal}</div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose} disabled={isMutating}>Cancelar</Button>
            <Button onClick={handleSave} disabled={isMutating || detalles.length === 0}>
              {isMutating ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
