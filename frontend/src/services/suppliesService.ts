import type { SuppliesQuery, SuppliesResponse, Supply, SupplyFormValues } from '../types/supply';
import { api } from './api';

function buildQuery(params: SuppliesQuery): string {
  const query = new URLSearchParams();
  query.set('offset', String(params.offset));
  query.set('limit', String(params.limit));
  query.set('sort_by', params.sort_by);
  query.set('sort_dir', params.sort_dir);
  query.set('include_deleted', String(params.include_deleted));

  if (params.search.trim()) {
    query.set('search', params.search.trim());
  }

  if (params.es_alergeno !== 'all') {
    query.set('es_alergeno', params.es_alergeno);
  }

  return query.toString();
}

export const suppliesService = {
  async getAll(params: SuppliesQuery): Promise<SuppliesResponse> {
    const { data } = await api.get<SuppliesResponse>(`/ingredientes/?${buildQuery(params)}`);
    return data;
  },

  async getById(id: number): Promise<Supply> {
    const { data } = await api.get<Supply>(`/ingredientes/${id}`);
    return data;
  },

  async create(input: SupplyFormValues): Promise<Supply> {
    const { data } = await api.post<Supply>('/ingredientes/', input);
    return data;
  },

  async update(id: number, input: SupplyFormValues): Promise<Supply> {
    const { data } = await api.patch<Supply>(`/ingredientes/${id}`, input);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/ingredientes/${id}`);
  },

  async restore(id: number): Promise<Supply> {
    const { data } = await api.patch<Supply>(`/ingredientes/${id}/restore`);
    return data;
  },
};
