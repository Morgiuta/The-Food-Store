import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pedidosService } from '../services/pedidosService';

export function usePedidos() {
  const queryClient = useQueryClient();

  // Fetch list (Polling every 15 seconds)
  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['pedidos'],
    queryFn: () => pedidosService.getAll(1, 100), // Get latest 100 orders
    refetchInterval: 15000, 
    staleTime: 5000,
  });

  const pedidos = data?.items || [];
  const total = data?.total || 0;

  // Mutations
  const avanzarEstadoMutation = useMutation({
    mutationFn: ({ id, nuevoEstado }: { id: number; nuevoEstado: string }) => 
      pedidosService.avanzarEstado(id, nuevoEstado),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pedidos'] });
    },
  });

  const cancelarMutation = useMutation({
    mutationFn: (id: number) => pedidosService.cancelar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pedidos'] });
    },
  });

  const isMutating = 
    avanzarEstadoMutation.isPending || 
    cancelarMutation.isPending;

  return {
    pedidos,
    total,
    error: error instanceof Error ? error.message : null,
    isLoading,
    isFetching,
    isMutating,
    reload: refetch,
    avanzarEstado: async (id: number, nuevoEstado: string) => avanzarEstadoMutation.mutateAsync({ id, nuevoEstado }),
    cancelarPedido: cancelarMutation.mutateAsync,
  };
}
