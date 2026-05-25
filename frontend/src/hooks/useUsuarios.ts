import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usuariosService } from '../services/usuariosService';
import type { UsuariosQuery, UsuarioUpdate } from '../types/usuario';

export function useUsuarios(query: UsuariosQuery) {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['usuarios', query],
    queryFn: () => usuariosService.getAll(query),
    staleTime: 5000,
  });

  const usuarios = data?.items || [];
  const total = data?.total || 0;

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: UsuarioUpdate }) => 
      usuariosService.update(id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  const assignRolMutation = useMutation({
    mutationFn: ({ id, rol_nombre }: { id: number; rol_nombre: string }) => 
      usuariosService.assignRol(id, rol_nombre),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => usuariosService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  const isMutating = 
    updateMutation.isPending || 
    assignRolMutation.isPending || 
    deleteMutation.isPending;

  return {
    usuarios,
    total,
    error: error instanceof Error ? error.message : null,
    isLoading,
    isMutating,
    reload: refetch,
    updateUsuario: async (id: number, values: UsuarioUpdate) => updateMutation.mutateAsync({ id, values }),
    assignRol: async (id: number, rol_nombre: string) => assignRolMutation.mutateAsync({ id, rol_nombre }),
    deleteUsuario: deleteMutation.mutateAsync,
  };
}
