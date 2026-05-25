import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { direccionesService } from '../services/direccionesService';
import type { DireccionFormValues } from '../types/direccion';

export function useDirecciones() {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['direcciones'],
    queryFn: () => direccionesService.getAll(),
    staleTime: 5000,
  });

  const createMutation = useMutation({
    mutationFn: (values: DireccionFormValues) => direccionesService.create(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: DireccionFormValues }) =>
      direccionesService.update(id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] });
    },
  });

  const principalMutation = useMutation({
    mutationFn: (id: number) => direccionesService.markPrincipal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => direccionesService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] });
    },
  });

  return {
    direcciones: data || [],
    isLoading,
    error: error instanceof Error ? error.message : null,
    isMutating:
      createMutation.isPending ||
      updateMutation.isPending ||
      principalMutation.isPending ||
      deleteMutation.isPending,
    reload: refetch,
    createDireccion: createMutation.mutateAsync,
    updateDireccion: async (id: number, values: DireccionFormValues) =>
      updateMutation.mutateAsync({ id, values }),
    markPrincipal: principalMutation.mutateAsync,
    deleteDireccion: deleteMutation.mutateAsync,
  };
}
