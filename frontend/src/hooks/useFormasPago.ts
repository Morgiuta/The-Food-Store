import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export interface FormaPago {
  codigo: string;
  descripcion: string;
  habilitado: boolean;
}

export function useFormasPago() {
  const { data: formasPago = [], isLoading, error } = useQuery({
    queryKey: ['formas-pago'],
    queryFn: async () => {
      const { data } = await api.get<FormaPago[]>('/ventas/formas-pago');
      return data;
    },
  });

  return {
    formasPago,
    isLoading,
    error,
  };
}
