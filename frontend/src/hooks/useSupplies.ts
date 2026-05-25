import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import { suppliesService } from '../services/suppliesService';
import type { SuppliesQuery, SupplyFormValues } from '../types/supply';

export function useSupplies(query: SuppliesQuery) {
  const queryClient = useQueryClient();

  // Fetch list
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['supplies', query],
    queryFn: () => suppliesService.getAll(query),
    staleTime: 5000,
  });

  const supplies = useMemo(() => data?.data || [], [data?.data]);
  const total = data?.total || 0;

  const activeCount = useMemo(
    () => supplies.filter((supply) => !supply.deleted_at).length,
    [supplies],
  );

  const allergenCount = useMemo(
    () => supplies.filter((supply) => supply.es_alergeno && !supply.deleted_at).length,
    [supplies],
  );

  // Mutations
  const createMutation = useMutation({
    mutationFn: (values: SupplyFormValues) => suppliesService.create(values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['supplies'] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: SupplyFormValues }) => 
      suppliesService.update(id, values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['supplies'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => suppliesService.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['supplies'] }),
  });

  const restoreMutation = useMutation({
    mutationFn: (id: number) => suppliesService.restore(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['supplies'] }),
  });

  const isMutating = 
    createMutation.isPending || 
    updateMutation.isPending || 
    deleteMutation.isPending || 
    restoreMutation.isPending;

  return {
    supplies,
    total,
    activeCount,
    allergenCount,
    error: error instanceof Error ? error.message : null,
    isLoading,
    isMutating,
    reload: refetch,
    createSupply: createMutation.mutateAsync,
    updateSupply: async (id: number, values: SupplyFormValues) => updateMutation.mutateAsync({ id, values }),
    deleteSupply: deleteMutation.mutateAsync,
    restoreSupply: restoreMutation.mutateAsync,
  };
}
