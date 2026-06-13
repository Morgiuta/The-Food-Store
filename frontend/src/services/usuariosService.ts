import type { UsuarioPublic, UsuarioListResponse, UsuariosQuery, UsuarioUpdate } from '../types/usuario';
import { api } from './api';

function buildQuery(params: UsuariosQuery): string {
  const query = new URLSearchParams();
  query.set('page', String(params.page));
  query.set('size', String(params.size));
  
  if (params.rol) {
    query.set('rol', params.rol);
  }

  return query.toString();
}

export const usuariosService = {
  async getAll(params: UsuariosQuery): Promise<UsuarioListResponse> {
    const { data } = await api.get<UsuarioListResponse>(`/admin/usuarios/?${buildQuery(params)}`);
    return data;
  },

  async getById(id: number): Promise<UsuarioPublic> {
    const { data } = await api.get<UsuarioPublic>(`/admin/usuarios/${id}`);
    return data;
  },

  async update(id: number, input: UsuarioUpdate): Promise<UsuarioPublic> {
    const { data } = await api.patch<UsuarioPublic>(`/admin/usuarios/${id}`, input);
    return data;
  },

  async assignRol(id: number, rol_nombre: string): Promise<UsuarioPublic> {
    const { data } = await api.patch<UsuarioPublic>(`/admin/usuarios/${id}/rol`, {
      rol_nombre,
    });
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/admin/usuarios/${id}`);
  },
};
