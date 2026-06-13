import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { unidadesMedidaService } from '../services/unidadesMedidaService';
import type { UnidadMedidaFormValues, UnidadesMedidaQuery } from '../types/unidadMedida';

export function useUnidadesMedida(query: UnidadesMedidaQuery = { page: 1, size: 100 }) {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['unidades-medida', query],
    queryFn: () => unidadesMedidaService.getAll(query),
    staleTime: 30000,
  });

  const createMutation = useMutation({
    mutationFn: (values: UnidadMedidaFormValues) => unidadesMedidaService.create(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['unidades-medida'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: UnidadMedidaFormValues }) =>
      unidadesMedidaService.update(id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['unidades-medida'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => unidadesMedidaService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['unidades-medida'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  return {
    unidades: data?.items || [],
    total: data?.total || 0,
    error: error instanceof Error ? error.message : null,
    isLoading,
    isMutating:
      createMutation.isPending || updateMutation.isPending || deleteMutation.isPending,
    reload: refetch,
    createUnidadMedida: createMutation.mutateAsync,
    updateUnidadMedida: async (id: number, values: UnidadMedidaFormValues) =>
      updateMutation.mutateAsync({ id, values }),
    deleteUnidadMedida: deleteMutation.mutateAsync,
  };
}
