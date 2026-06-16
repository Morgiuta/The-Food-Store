import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Modal } from '../../../../components/ui/Modal/Modal';
import { Button } from '../../../../components/ui/Button/Button';
import type { Pedido } from '../../../../types/pedido';

interface PedidoDetailModalProps {
  pedido: Pedido;
  isMutating: boolean;
  onClose: () => void;
  onAdvance: (pedido: Pedido) => void;
  onCancel: (pedido: Pedido) => void;
  onEdit: () => void;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(value);
}

const statusConfig: Record<string, { label: string; buttonColor: string; next?: string }> = {
  PENDIENTE: { 
    buttonColor: 'bg-yellow-500 hover:bg-yellow-600 text-charcoal',
    label: 'Pendiente', 
    next: 'CONFIRMADO' 
  },
  CONFIRMADO: { 
    buttonColor: 'bg-blue-600 hover:bg-blue-700 text-white',
    label: 'Confirmado', 
    next: 'EN_PREP' 
  },
  EN_PREP: { 
    buttonColor: 'bg-orange-500 hover:bg-orange-600 text-white',
    label: 'En Preparación', 
    next: 'ENTREGADO' 
  },
  ENTREGADO: { 
    buttonColor: 'bg-green-600 hover:bg-green-700 text-white',
    label: 'Entregado' 
  },
  CANCELADO: { 
    buttonColor: 'bg-gray-600 hover:bg-gray-700 text-white',
    label: 'Cancelado' 
  },
};

export function PedidoDetailModal({ pedido, isMutating, onClose, onAdvance, onCancel, onEdit }: PedidoDetailModalProps) {
  const isTerminal = pedido.estado_codigo === 'ENTREGADO' || pedido.estado_codigo === 'CANCELADO';
  
  const currentConfig = statusConfig[pedido.estado_codigo];
  const nextConfig = currentConfig?.next ? statusConfig[currentConfig.next] : null;

  return (
    <Modal kicker="Gestor de Comandas" title={`Orden #${pedido.id}`} size="lg" onClose={onClose}>
      <div className="flex flex-col md:flex-row gap-6 bg-white">
        {/* Lado Izquierdo: Ticket de compra */}
        <div className="flex-1 bg-yellow-50/30 p-6 rounded-lg border border-yellow-100 relative">
          <div className="absolute top-0 left-0 right-0 h-4 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIxMCI+PHBhdGggZD0iTTAgMTBMNSAwTDEwIDEwTDE1IDBMMjAgMTBMMjAgMEwwIDBaIiBmaWxsPSIjRkZGRkZGIi8+PC9zdmc+')] opacity-20"></div>
          
          <div className="text-center mb-6 pt-4 border-b border-dashed border-gray-300 pb-4">
             <h3 className="font-black text-charcoal uppercase tracking-widest text-lg">Ticket de Cocina</h3>
             <p className="text-sm text-gray-500">{format(new Date(pedido.created_at), "dd/MM/yyyy HH:mm", { locale: es })}</p>
             <p className="text-sm font-bold text-gray-700 mt-1">Cliente: {pedido.usuario_nombre || `Cliente #${pedido.usuario_id}`}</p>
          </div>

          <ul className="space-y-4 mb-6">
            {pedido.detalles.map(d => (
              <li key={d.producto_id} className="text-sm">
                 <div className="flex justify-between items-start font-bold text-charcoal">
                    <span>{d.cantidad}x {d.nombre_snapshot}</span>
                    <span>{formatCurrency(d.subtotal_snapshot)}</span>
                 </div>
                 {d.personalizacion && Object.keys(d.personalizacion).length > 0 && (
                    <div className="pl-5 mt-1 text-xs text-red-600 font-medium">
                       {Object.entries(d.personalizacion).map(([k, v]) => (
                         <div key={k}>- {k}: {String(v)}</div>
                       ))}
                    </div>
                 )}
              </li>
            ))}
          </ul>

          {pedido.notas && (
            <div className="mb-6 p-3 bg-white border-2 border-charcoal text-charcoal rounded-md">
               <strong className="block uppercase text-xs tracking-wider mb-1">Notas del cliente:</strong>
               <p className="font-bold text-sm">{pedido.notas}</p>
            </div>
          )}

          <div className="border-t-2 border-dashed border-gray-300 pt-4 space-y-2 text-sm text-gray-600">
             <div className="flex justify-between">
                <span>Subtotal</span>
                <span>{formatCurrency(pedido.subtotal)}</span>
             </div>
             {pedido.descuento > 0 && (
                <div className="flex justify-between text-green-600">
                   <span>Descuento</span>
                   <span>-{formatCurrency(pedido.descuento)}</span>
                </div>
             )}
             <div className="flex justify-between">
                <span>Costo de Envío</span>
                <span>{formatCurrency(pedido.costo_envio)}</span>
             </div>
             <div className="flex justify-between text-lg font-black text-charcoal pt-2 border-t border-gray-200 mt-2">
                <span>TOTAL</span>
                <span>{formatCurrency(pedido.total)}</span>
             </div>
          </div>
        </div>

        {/* Lado Derecho: Estado e Historial */}
        <div className="w-full md:w-1/3 flex flex-col gap-6">
           <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
              <h4 className="font-bold text-xs uppercase tracking-wider text-gray-500 mb-2">Estado Actual</h4>
              <p className={`font-black text-lg ${
                 pedido.estado_codigo === 'PENDIENTE' ? 'text-yellow-600' :
                 pedido.estado_codigo === 'CONFIRMADO' ? 'text-blue-600' :
                 pedido.estado_codigo === 'EN_PREP' ? 'text-orange-600' :
                 pedido.estado_codigo === 'ENTREGADO' ? 'text-green-600' :
                 'text-gray-600'
              }`}>{currentConfig?.label || pedido.estado_codigo}</p>
              
              <div className="mt-4 pt-4 border-t border-gray-200 text-sm">
                 <p className="text-gray-500 mb-1">Forma de Pago:</p>
                 <p className="font-bold text-charcoal">{pedido.forma_pago_codigo}</p>
              </div>
           </div>

           <div className="flex-1 overflow-y-auto">
              <h4 className="font-bold text-xs uppercase tracking-wider text-gray-500 mb-3">Historial</h4>
              <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                 {pedido.historial.map(h => (
                   <div key={h.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-4 h-4 rounded-full border border-white bg-slate-300 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2"></div>
                      <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-white p-2 rounded border border-slate-200 shadow-sm text-xs">
                        <span className="font-bold text-slate-800">{statusConfig[h.estado_hacia]?.label || h.estado_hacia}</span>
                        <p className="text-slate-500">{format(new Date(h.created_at), 'HH:mm')}</p>
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           {!isTerminal && nextConfig && (
             <div className="mt-auto space-y-2 pt-4">
                <Button 
                   className={`w-full py-3 text-lg border-transparent ${nextConfig.buttonColor}`} 
                   disabled={isMutating}
                   onClick={() => onAdvance(pedido)}
                >
                   {isMutating ? 'Actualizando...' : nextConfig.label}
                </Button>
                {['PENDIENTE', 'CONFIRMADO', 'EN_PREP'].includes(pedido.estado_codigo) && pedido.forma_pago_codigo === 'EFECTIVO' && (
                  <Button
                    variant="secondary"
                    className="w-full py-3 text-lg border border-gray-300 text-charcoal hover:bg-gray-100"
                    disabled={isMutating}
                    onClick={onEdit}
                  >
                    Modificar Pedido
                  </Button>
                )}
                <Button 
                   variant="ghost" 
                   className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                   disabled={isMutating}
                   onClick={() => onCancel(pedido)}
                >
                   Cancelar pedido
                </Button>
             </div>
           )}
        </div>
      </div>
    </Modal>
  );
}
