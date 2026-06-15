import { useState, useMemo, useRef, useEffect } from 'react';
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
      precio_snapshot: Number(d.precio_snapshot),
      subtotal_snapshot: Number(d.subtotal_snapshot),
      isOriginal: true,
      originalCantidad: d.cantidad
    }))
  );

  const [searchTerm, setSearchTerm] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { productos, isLoading } = useProductos({ page: 1, size: 100, disponible: true });

  const estado = pedido.estado_codigo;
  const isEnPrep = estado === 'EN_PREP';

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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
          subtotal_snapshot: (d.cantidad + 1) * Number(prod.precio_base) 
        };
        return updated;
      }
      return [...prev, {
        producto_id: prodId,
        cantidad: 1,
        personalizacion: null,
        nombre_snapshot: prod.nombre,
        precio_snapshot: Number(prod.precio_base),
        subtotal_snapshot: Number(prod.precio_base),
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
    let prods = productos;
    if (isEnPrep) {
      prods = productos.filter(p => p.tiempo_prep_min == null || p.tiempo_prep_min <= 0);
    }
    const term = searchTerm.toLowerCase();
    if (!term) return prods;
    return prods.filter(p => p.nombre.toLowerCase().includes(term));
  }, [productos, isEnPrep, searchTerm]);

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
                    <div className="text-sm text-gray-500">${d.precio_snapshot.toFixed(2)} c/u</div>
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
            <div className="relative" ref={dropdownRef}>
              <input
                type="text"
                placeholder="Buscar por nombre..."
                value={searchTerm}
                onFocus={() => setIsDropdownOpen(true)}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setIsDropdownOpen(true);
                }}
                className="w-full rounded-md border border-gray-300 p-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
              {isDropdownOpen && (
                <div className="absolute z-10 mt-1 max-h-60 w-full overflow-y-auto rounded-md border border-gray-200 bg-white shadow-lg">
                  {availableProducts.length > 0 ? (
                    <ul className="py-1">
                      {availableProducts.map(p => (
                        <li 
                          key={p.id}
                          className="cursor-pointer px-4 py-2 text-sm hover:bg-gray-100"
                          onClick={() => {
                            addProducto(p.id);
                            setSearchTerm('');
                            setIsDropdownOpen(false);
                          }}
                        >
                          <span className="font-bold">{p.nombre}</span> <span className="text-gray-500">- ${Number(p.precio_base).toFixed(2)}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="p-4 text-center text-sm text-gray-500">No se encontraron productos</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-gray-200 pt-4">
          <div className="text-xl font-black">Subtotal: ${subtotalTotal.toFixed(2)}</div>
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
