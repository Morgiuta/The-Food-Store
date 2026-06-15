import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboard.api';
import { pedidosService } from '../services/pedidosService';

export function useDashboard() {
  const metricsQuery = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => dashboardService.getMetrics(),
  });

  const recientesQuery = useQuery({
    queryKey: ['pedidos-recientes'],
    queryFn: () => pedidosService.getAll(1, 5),
  });

  return {
    metrics: metricsQuery.data,
    isLoadingMetrics: metricsQuery.isLoading,
    isErrorMetrics: metricsQuery.isError,
    
    pedidosRecientes: recientesQuery.data?.items || [],
    isLoadingRecientes: recientesQuery.isLoading,
    isErrorRecientes: recientesQuery.isError,
  };
}
