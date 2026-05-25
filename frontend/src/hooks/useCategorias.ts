import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import { categoriasService } from '../services/categoriasService';
import type { CategoriasQuery, CategoriaFormValues } from '../types/categoria';

export function useCategorias(query: CategoriasQuery) {
  const queryClient = useQueryClient();

  // Fetch list
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['categorias', query],
    queryFn: () => categoriasService.getAll(query),
    staleTime: 5000,
  });

  const categorias = useMemo(() => data?.data || [], [data?.data]);
  const total = data?.total || 0;

  const activeCount = useMemo(
    () => categorias.filter((cat) => !cat.deleted_at).length,
    [categorias],
  );

  // Mutations
  const createMutation = useMutation({
    mutationFn: (values: CategoriaFormValues) => categoriasService.create(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['categorias-tree'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: CategoriaFormValues }) => 
      categoriasService.update(id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['categorias-tree'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => categoriasService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['categorias-tree'] });
    },
  });

  const restoreMutation = useMutation({
    mutationFn: (id: number) => categoriasService.restore(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['categorias-tree'] });
    },
  });

  const isMutating = 
    createMutation.isPending || 
    updateMutation.isPending || 
    deleteMutation.isPending ||
    restoreMutation.isPending;

  return {
    categorias,
    total,
    activeCount,
    error: error instanceof Error ? error.message : null,
    isLoading,
    isMutating,
    reload: refetch,
    createCategoria: createMutation.mutateAsync,
    updateCategoria: async (id: number, values: CategoriaFormValues) => updateMutation.mutateAsync({ id, values }),
    deleteCategoria: deleteMutation.mutateAsync,
    restoreCategoria: restoreMutation.mutateAsync,
  };
}

export function useCategoriasTree() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['categorias-tree'],
    queryFn: () => categoriasService.getTree(),
    staleTime: 5000,
  });

  return {
    tree: data || [],
    isLoading,
    error: error instanceof Error ? error.message : null,
  };
}
