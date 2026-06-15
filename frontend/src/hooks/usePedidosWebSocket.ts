import { useEffect, useMemo, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '../components/ui/Toast/Toast';
import { useAuthStore } from '../store/authStore';

const PEDIDO_EVENTS = new Set([
  'NUEVO_PEDIDO',
  'PEDIDO_CONFIRMADO',
  'PEDIDO_EN_PREPARACION',
  'PEDIDO_EN_CAMINO',
  'PEDIDO_ENTREGADO',
  'PEDIDO_CANCELADO',
]);

function getPedidosWsUrl() {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
  return `${apiBase.replace(/^http/, 'ws').replace(/\/$/, '')}/pedidos/ws`;
}

export function usePedidosWebSocket(orderIds: number[]) {
  const queryClient = useQueryClient();
  const { info } = useToast();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const userRole = useAuthStore((state) => state.user?.role);
  const subscribedOrdersKey = useMemo(
    () => [...new Set(orderIds)].sort((a, b) => a - b).join(','),
    [orderIds],
  );
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      return undefined;
    }

    let reconnectTimer: number | undefined;
    let closedByEffect = false;

    const connect = () => {
      const socket = new WebSocket(getPedidosWsUrl());
      socketRef.current = socket;

      socket.onopen = () => {
        if (userRole !== 'CLIENT') {
          return;
        }

        subscribedOrdersKey
          .split(',')
          .filter(Boolean)
          .forEach((orderId) => {
            socket.send(JSON.stringify({
              action: 'subscribe-order',
              order_id: Number(orderId),
            }));
          });
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (!PEDIDO_EVENTS.has(message.event)) {
            return;
          }

          queryClient.invalidateQueries({ queryKey: ['pedidos'] });
          queryClient.invalidateQueries({ queryKey: ['pedidos-recientes'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] });
          const pedidoId = message.data?.id;
          info(pedidoId ? `Pedido #${pedidoId}: ${message.event}` : 'Pedidos actualizados');
        } catch {
          queryClient.invalidateQueries({ queryKey: ['pedidos'] });
          queryClient.invalidateQueries({ queryKey: ['pedidos-recientes'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] });
        }
      };

      socket.onclose = () => {
        if (!closedByEffect) {
          reconnectTimer = window.setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      closedByEffect = true;
      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer);
      }
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [info, isAuthenticated, queryClient, subscribedOrdersKey, userRole]);
}
