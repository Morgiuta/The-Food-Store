import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Modal } from '../../components/ui/Modal/Modal';
import { Button } from '../../components/ui/Button/Button';
import type { Pedido } from '../../types/pedido';

interface ClientOrderModalProps {
  pedido: Pedido;
  isMutating: boolean;
  onClose: () => void;
  onCancel: (pedido: Pedido) => void;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(value);
}

const statusConfig: Record<string, { label: string; textColor: string }> = {
  PENDIENTE: { 
    label: 'Pendiente', 
    textColor: 'text-yellow-600'
  },
  CONFIRMADO: { 
    label: 'Confirmado', 
    textColor: 'text-blue-600'
  },
  EN_PREP: { 
    label: 'En Preparación', 
    textColor: 'text-orange-600'
  },
  EN_CAMINO: { 
    label: 'En Camino', 
    textColor: 'text-green-500'
  },
  ENTREGADO: { 
    label: 'Entregado',
    textColor: 'text-green-600'
  },
  CANCELADO: { 
    label: 'Cancelado',
    textColor: 'text-gray-600'
  },
};

export function ClientOrderModal({ pedido, isMutating, onClose, onCancel }: ClientOrderModalProps) {
  const isTerminal = pedido.estado_codigo === 'ENTREGADO' || pedido.estado_codigo === 'CANCELADO';
  const cancelables = new Set(['PENDIENTE', 'CONFIRMADO']);
  const canCancel = cancelables.has(pedido.estado_codigo);
  
  const currentConfig = statusConfig[pedido.estado_codigo] || { label: pedido.estado_codigo, textColor: 'text-charcoal' };

  return (
    <Modal kicker="Mi Cuenta" title={`Detalle del Pedido #${pedido.id}`} size="lg" onClose={onClose}>
      <div className="flex flex-col md:flex-row gap-6 bg-white">
        
        {/* Lado Izquierdo: Ticket de compra */}
        <div className="flex-1 bg-gray-50 p-6 rounded-lg border border-gray-200">
          <div className="text-center mb-6 pt-2 border-b border-gray-200 pb-4">
             <h3 className="font-black text-charcoal uppercase tracking-widest text-lg">Resumen de Compra</h3>
             <p className="text-sm text-gray-500">{format(new Date(pedido.created_at), "dd/MM/yyyy HH:mm", { locale: es })}</p>
          </div>

          <ul className="space-y-4 mb-6">
            {pedido.detalles.map(d => (
              <li key={d.producto_id} className="text-sm">
                 <div className="flex justify-between items-start font-bold text-charcoal">
                    <span>{d.cantidad}x {d.nombre_snapshot}</span>
                    <span>{formatCurrency(d.subtotal_snapshot)}</span>
                 </div>
                 {d.personalizacion && Object.keys(d.personalizacion).length > 0 && (
                    <div className="pl-5 mt-1 text-xs text-muted font-medium">
                       {Object.entries(d.personalizacion).map(([k, v]) => (
                         <div key={k}>- {k}: {String(v)}</div>
                       ))}
                    </div>
                 )}
              </li>
            ))}
          </ul>

          {pedido.notas && (
            <div className="mb-6 p-3 bg-white border border-gray-200 text-charcoal rounded-md">
               <strong className="block uppercase text-xs tracking-wider mb-1 text-gray-500">Mis notas:</strong>
               <p className="font-bold text-sm">{pedido.notas}</p>
            </div>
          )}

          <div className="border-t border-gray-200 pt-4 space-y-2 text-sm text-gray-600">
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

        {/* Lado Derecho: Trayecto e Historial */}
        <div className="w-full md:w-1/3 flex flex-col gap-6">
           <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
              <h4 className="font-bold text-xs uppercase tracking-wider text-gray-500 mb-2">Estado Actual</h4>
              <p className={`font-black text-xl ${currentConfig.textColor}`}>
                 {currentConfig.label}
              </p>
              
              <div className="mt-4 pt-4 border-t border-gray-100 text-sm">
                 <p className="text-gray-500 mb-1">Forma de Pago:</p>
                 <p className="font-bold text-charcoal uppercase">{pedido.forma_pago_codigo}</p>
              </div>
           </div>

           <div className="flex-1 overflow-y-auto">
              <h4 className="font-bold text-xs uppercase tracking-wider text-gray-500 mb-3">Trayecto del pedido</h4>
              <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-300 before:to-transparent">
                 {pedido.historial.map(h => (
                   <div key={h.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-white bg-primary shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2"></div>
                      <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-white p-3 rounded-lg border border-gray-200 shadow-sm text-xs">
                        <span className="font-black text-charcoal text-sm block mb-0.5">{statusConfig[h.estado_hacia]?.label || h.estado_hacia}</span>
                        <p className="text-gray-500">{format(new Date(h.created_at), "dd/MM 'a las' HH:mm")}</p>
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           <div className="mt-auto space-y-2 pt-4 border-t border-gray-100">
              <Button 
                 className="w-full py-3" 
                 onClick={onClose}
              >
                 Cerrar detalle
              </Button>
              {canCancel && !isTerminal && (
                 <Button 
                    variant="ghost" 
                    className="w-full text-ketchup hover:text-red-700 hover:bg-red-50"
                    disabled={isMutating}
                    onClick={() => {
                      if (confirm('¿Estás seguro que deseas cancelar este pedido?')) {
                         onCancel(pedido);
                      }
                    }}
                 >
                    Cancelar pedido
                 </Button>
              )}
           </div>
        </div>
      </div>
    </Modal>
  );
}
