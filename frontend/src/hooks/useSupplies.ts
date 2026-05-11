import { useCallback, useEffect, useMemo, useState } from 'react';
import { suppliesService } from '../services/suppliesService';
import type { SuppliesQuery, Supply, SupplyFormValues } from '../types/supply';

export function useSupplies(query: SuppliesQuery) {
  const [supplies, setSupplies] = useState<Supply[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);

  const activeCount = useMemo(
    () => supplies.filter((supply) => !supply.deleted_at).length,
    [supplies],
  );

  const allergenCount = useMemo(
    () => supplies.filter((supply) => supply.es_alergeno && !supply.deleted_at).length,
    [supplies],
  );

  const loadSupplies = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await suppliesService.getAll(query);
      setSupplies(response.data);
      setTotal(response.total);
    } catch (requestError) {
      setSupplies([]);
      setTotal(0);
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo cargar el listado de insumos.',
      );
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  useEffect(() => {
    void loadSupplies();
  }, [loadSupplies]);

  const createSupply = async (values: SupplyFormValues) => {
    setIsMutating(true);
    try {
      await suppliesService.create(values);
      await loadSupplies();
    } finally {
      setIsMutating(false);
    }
  };

  const updateSupply = async (id: number, values: SupplyFormValues) => {
    setIsMutating(true);
    try {
      await suppliesService.update(id, values);
      await loadSupplies();
    } finally {
      setIsMutating(false);
    }
  };

  const deleteSupply = async (id: number) => {
    setIsMutating(true);
    try {
      await suppliesService.remove(id);
      await loadSupplies();
    } finally {
      setIsMutating(false);
    }
  };

  const restoreSupply = async (id: number) => {
    setIsMutating(true);
    try {
      await suppliesService.restore(id);
      await loadSupplies();
    } finally {
      setIsMutating(false);
    }
  };

  return {
    supplies,
    total,
    activeCount,
    allergenCount,
    error,
    isLoading,
    isMutating,
    reload: loadSupplies,
    createSupply,
    updateSupply,
    deleteSupply,
    restoreSupply,
  };
}
