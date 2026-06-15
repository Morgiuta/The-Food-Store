import { useState } from 'react';
import { useToast } from '../../components/ui/Toast/Toast';
import { PedidoCard } from '../../features/pedidos/components/PedidoCard/PedidoCard';
import { PedidoDetailModal } from '../../features/pedidos/components/PedidoDetailModal/PedidoDetailModal';
import { usePedidos } from '../../hooks/usePedidos';
import type { Pedido } from '../../types/pedido';

export function PedidosPage() {
  const [selectedPedido, setSelectedPedido] = useState<Pedido | null>(null);
  const { confirm, notify } = useToast();

  const {
    pedidos,
    isLoading,
    isFetching,
    isMutating,
    avanzarEstado,
    cancelarPedido,
  } = usePedidos();

  const statusMap: Record<string, string> = {
    PENDIENTE: 'CONFIRMADO',
    CONFIRMADO: 'EN_PREP',
    EN_PREP: 'ENTREGADO',
  };

  const handleAdvance = async (pedido: Pedido, e?: React.MouseEvent) => {
    if (e) {
      e.stopPropagation();
    }
    const nextState = statusMap[pedido.estado_codigo];
    if (!nextState) return;

    try {
      await avanzarEstado(pedido.id, nextState);
      notify('success', `Pedido #${pedido.id} movido a ${nextState}`);
      if (selectedPedido?.id === pedido.id) {
         setSelectedPedido(null); // Close modal on success if it was open
      }
    } catch (error) {
      notify('error', 'Error al cambiar de estado');
    }
  };

  const handleCancel = async (pedido: Pedido) => {
    const confirmed = await confirm({
      confirmLabel: 'Cancelar pedido',
      message: `¿Estás seguro que deseas cancelar el pedido #${pedido.id}? Esta acción es irreversible.`,
      title: 'Cancelar pedido',
      type: 'danger',
    });
    if (!confirmed) {
      return;
    }

    try {
      await cancelarPedido(pedido.id);
      notify('success', `Pedido #${pedido.id} cancelado`);
      if (selectedPedido?.id === pedido.id) {
         setSelectedPedido(null);
      }
    } catch (error) {
      notify('error', 'Error al cancelar el pedido');
    }
  };

  // Group by status
  const pendientes = pedidos.filter(p => {
    if (p.estado_codigo === 'PENDIENTE') {
      return p.forma_pago_codigo !== 'MERCADOPAGO'; // Ocultar pedidos de MP hasta que se paguen y pasen a CONFIRMADO
    }
    return p.estado_codigo === 'CONFIRMADO';
  });
  const preparando = pedidos.filter(p => p.estado_codigo === 'EN_PREP');
  const terminales = pedidos.filter(p => p.estado_codigo === 'ENTREGADO' || p.estado_codigo === 'CANCELADO').slice(0, 10); // Show only last 10 terminales

  return (
    <section className="space-y-6 animate-in fade-in duration-300 h-full flex flex-col">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <span className="section-kicker">Operación</span>
          <h2 className="text-3xl font-black text-charcoal mb-2">Gestor de Pedidos</h2>
          <p className="text-muted">Visualización en tiempo real. Autorefresh activado.</p>
        </div>
        <div className="flex gap-3">
           {isLoading && (
             <div className="text-xs font-bold px-3 py-1.5 rounded-full border border-gray-200 text-gray-500">
                Cargando...
             </div>
           )}
           <div className={`text-xs font-bold px-3 py-1.5 rounded-full border ${isFetching ? 'border-green-300 bg-green-50 text-green-700 animate-pulse' : 'border-gray-200 text-gray-500'}`}>
              {isFetching ? 'Actualizando...' : 'Online'}
           </div>
        </div>
      </div>

      <div className="flex-1 pb-4">
        <div className="flex gap-4 h-full">
          
          {/* Pendientes Column */}
          <div className="flex-1 min-w-0 flex flex-col bg-gray-50 rounded-lg border border-gray-200">
             <div className="p-3 border-b border-gray-200 flex justify-between items-center bg-gray-100/50 rounded-t-lg">
                <h3 className="font-bold text-gray-700 uppercase tracking-wider text-sm">Nuevos</h3>
                <span className="bg-red-100 text-red-700 font-black text-xs px-2 py-0.5 rounded-full">{pendientes.length}</span>
             </div>
             <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                {pendientes.map(p => (
                   <PedidoCard key={p.id} pedido={p} onClick={setSelectedPedido} onAdvance={handleAdvance} />
                ))}
             </div>
          </div>

          {/* Preparando Column */}
          <div className="flex-1 min-w-0 flex flex-col bg-gray-50 rounded-lg border border-gray-200">
             <div className="p-3 border-b border-gray-200 flex justify-between items-center bg-gray-100/50 rounded-t-lg">
                <h3 className="font-bold text-gray-700 uppercase tracking-wider text-sm">En Preparación</h3>
                <span className="bg-orange-100 text-orange-700 font-black text-xs px-2 py-0.5 rounded-full">{preparando.length}</span>
             </div>
             <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                {preparando.map(p => (
                   <PedidoCard key={p.id} pedido={p} onClick={setSelectedPedido} onAdvance={handleAdvance} />
                ))}
             </div>
          </div>

          {/* Completados Column */}
          <div className="flex-1 min-w-0 flex flex-col bg-gray-50 rounded-lg border border-gray-200 opacity-60 hover:opacity-100 transition-opacity">
             <div className="p-3 border-b border-gray-200 flex justify-between items-center bg-gray-100/50 rounded-t-lg">
                <h3 className="font-bold text-gray-700 uppercase tracking-wider text-sm">Finalizados</h3>
                <span className="bg-gray-200 text-gray-700 font-black text-xs px-2 py-0.5 rounded-full">{terminales.length}</span>
             </div>
             <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                {terminales.map(p => (
                   <PedidoCard key={p.id} pedido={p} onClick={setSelectedPedido} onAdvance={handleAdvance} />
                ))}
             </div>
          </div>

        </div>
      </div>

      {selectedPedido && (
         <PedidoDetailModal 
            pedido={selectedPedido} 
            isMutating={isMutating} 
            onClose={() => setSelectedPedido(null)}
            onAdvance={handleAdvance}
            onCancel={handleCancel}
         />
      )}

    </section>
  );
}
