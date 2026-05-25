import type { Direccion, DireccionFormValues } from '../types/direccion';
import { api } from './api';

function toPayload(input: DireccionFormValues) {
  return {
    alias: input.alias.trim() || null,
    calle: input.calle.trim(),
    numero: input.numero.trim(),
    ciudad: input.ciudad.trim(),
    provincia: input.provincia.trim() || null,
    codigo_postal: input.codigo_postal.trim() || null,
    es_principal: input.es_principal,
  };
}

export const direccionesService = {
  async getAll(): Promise<Direccion[]> {
    const { data } = await api.get<Direccion[]>('/direcciones/');
    return data;
  },

  async create(input: DireccionFormValues): Promise<Direccion> {
    const { data } = await api.post<Direccion>('/direcciones/', toPayload(input));
    return data;
  },

  async update(id: number, input: DireccionFormValues): Promise<Direccion> {
    const { data } = await api.put<Direccion>(`/direcciones/${id}`, toPayload(input));
    return data;
  },

  async markPrincipal(id: number): Promise<Direccion> {
    const { data } = await api.patch<Direccion>(`/direcciones/${id}/principal`);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/direcciones/${id}`);
  },
};
