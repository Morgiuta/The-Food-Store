import { formatDistanceToNowStrict } from 'date-fns';
import { es } from 'date-fns/locale';
import { Clock, CheckCircle, Package, Truck, XCircle } from 'lucide-react';
import type { Pedido } from '../../../../types/pedido';

interface PedidoCardProps {
  pedido: Pedido;
  onClick: (pedido: Pedido) => void;
  onAdvance: (pedido: Pedido, e: React.MouseEvent) => void;
}

const statusConfig: Record<string, { color: string; icon: React.FC<any>; label: string; next?: string }> = {
  PENDIENTE: { color: 'border-red-500 bg-red-50 text-red-700', icon: Clock, label: 'Pendiente', next: 'PREPARANDO' },
  PREPARANDO: { color: 'border-orange-500 bg-orange-50 text-orange-700', icon: Package, label: 'En Preparación', next: 'EN_CAMINO' },
  EN_CAMINO: { color: 'border-blue-500 bg-blue-50 text-blue-700', icon: Truck, label: 'En Camino', next: 'ENTREGADO' },
  ENTREGADO: { color: 'border-green-500 bg-green-50 text-green-700', icon: CheckCircle, label: 'Entregado' },
  CANCELADO: { color: 'border-gray-500 bg-gray-50 text-gray-700', icon: XCircle, label: 'Cancelado' },
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(value);
}

export function PedidoCard({ pedido, onClick, onAdvance }: PedidoCardProps) {
  const config = statusConfig[pedido.estado_codigo] || { color: 'border-gray-300 bg-white text-gray-800', icon: Clock, label: pedido.estado_codigo };
  const Icon = config.icon;

  const totalArticulos = pedido.detalles.reduce((acc, curr) => acc + curr.cantidad, 0);
  const timeAgo = formatDistanceToNowStrict(new Date(pedido.created_at), { locale: es, addSuffix: false });

  const isTerminal = pedido.estado_codigo === 'ENTREGADO' || pedido.estado_codigo === 'CANCELADO';

  return (
    <div 
      className={`border-l-4 rounded-r-lg shadow-sm cursor-pointer hover:shadow-md transition-shadow relative overflow-hidden flex flex-col group ${config.color.split(' ')[0]} bg-white`}
      onClick={() => onClick(pedido)}
    >
      <div className="p-4 flex-1">
        <div className="flex justify-between items-start mb-2">
          <div>
             <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Orden #{pedido.id}</span>
             <h4 className="font-black text-charcoal">{formatCurrency(pedido.total)}</h4>
          </div>
          <div className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded ${config.color}`}>
             <Icon size={14} />
             {timeAgo}
          </div>
        </div>
        
        <p className="text-sm text-gray-600 font-medium mb-3">
          {totalArticulos} artículos
        </p>

        {pedido.notas && (
          <div className="bg-yellow-50 text-yellow-800 text-xs p-2 rounded mb-3 border border-yellow-200 line-clamp-2">
             <span className="font-bold">Nota:</span> {pedido.notas}
          </div>
        )}
      </div>

      {!isTerminal && (
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-100 flex gap-2">
          <button
            className={`w-full py-2 font-bold text-sm rounded transition-colors ${
              pedido.estado_codigo === 'PENDIENTE' 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : pedido.estado_codigo === 'PREPARANDO'
                ? 'bg-orange-600 hover:bg-orange-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
            onClick={(e) => onAdvance(pedido, e)}
          >
            Mover a {statusConfig[config.next || '']?.label || 'Siguiente'}
          </button>
        </div>
      )}
    </div>
  );
}
