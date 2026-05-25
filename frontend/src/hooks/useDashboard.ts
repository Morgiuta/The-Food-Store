import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboard.api';
import { pedidosService } from '../services/pedidosService';

export function useDashboard() {
  const metricsQuery = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => dashboardService.getMetrics(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const recientesQuery = useQuery({
    queryKey: ['pedidos-recientes'],
    queryFn: () => pedidosService.getAll(1, 5),
    refetchInterval: 30000,
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
