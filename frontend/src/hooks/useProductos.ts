import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productosService } from '../services/productosService';
import type { ProductosQuery, ProductoFormValues } from '../types/producto';

export function useProductos(query: ProductosQuery) {
  const queryClient = useQueryClient();

  // Fetch list
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['productos', query],
    queryFn: () => productosService.getAll(query),
    staleTime: 5000,
  });

  const productos = data?.items || [];
  const total = data?.total || 0;

  // Mutations
  const createMutation = useMutation({
    mutationFn: (values: ProductoFormValues) => productosService.create(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: ProductoFormValues }) => 
      productosService.update(id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const toggleDisponibilidadMutation = useMutation({
    mutationFn: ({ id, disponible }: { id: number; disponible: boolean }) => 
      productosService.updateDisponibilidad(id, disponible),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const updateStockMutation = useMutation({
    mutationFn: ({ id, stock_cantidad }: { id: number; stock_cantidad: number }) => 
      productosService.updateStock(id, stock_cantidad),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => productosService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const restoreMutation = useMutation({
    mutationFn: (id: number) => productosService.restore(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const isMutating = 
    createMutation.isPending || 
    updateMutation.isPending || 
    toggleDisponibilidadMutation.isPending ||
    updateStockMutation.isPending ||
    deleteMutation.isPending ||
    restoreMutation.isPending;

  return {
    productos,
    total,
    error: error instanceof Error ? error.message : null,
    isLoading,
    isMutating,
    reload: refetch,
    createProducto: createMutation.mutateAsync,
    updateProducto: async (id: number, values: ProductoFormValues) => updateMutation.mutateAsync({ id, values }),
    toggleDisponibilidad: async (id: number, disponible: boolean) => toggleDisponibilidadMutation.mutateAsync({ id, disponible }),
    updateStock: async (id: number, stock_cantidad: number) => updateStockMutation.mutateAsync({ id, stock_cantidad }),
    deleteProducto: deleteMutation.mutateAsync,
    restoreProducto: restoreMutation.mutateAsync,
  };
}
