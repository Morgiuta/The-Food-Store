import type {
  UnidadMedida,
  UnidadMedidaFormValues,
  UnidadesMedidaQuery,
  UnidadesMedidaResponse,
} from '../types/unidadMedida';
import { api } from './api';

function buildQuery(params: UnidadesMedidaQuery): string {
  const query = new URLSearchParams();
  query.set('page', String(params.page));
  query.set('size', String(params.size));
  return query.toString();
}

export const unidadesMedidaService = {
  async getAll(params: UnidadesMedidaQuery): Promise<UnidadesMedidaResponse> {
    const { data } = await api.get<UnidadesMedidaResponse>(
      `/unidades-medida/?${buildQuery(params)}`,
    );
    return data;
  },

  async getById(id: number): Promise<UnidadMedida> {
    const { data } = await api.get<UnidadMedida>(`/unidades-medida/${id}`);
    return data;
  },

  async create(input: UnidadMedidaFormValues): Promise<UnidadMedida> {
    const { data } = await api.post<UnidadMedida>('/unidades-medida/', {
      ...input,
      descripcion: input.descripcion || null,
    });
    return data;
  },

  async update(id: number, input: UnidadMedidaFormValues): Promise<UnidadMedida> {
    const { data } = await api.patch<UnidadMedida>(`/unidades-medida/${id}`, {
      ...input,
      descripcion: input.descripcion || null,
    });
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/unidades-medida/${id}`);
  },
};
