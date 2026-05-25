import type { CategoriasQuery, CategoriasResponse, Categoria, CategoriaFormValues, CategoriaTree } from '../types/categoria';
import { api } from './api';

function buildQuery(params: CategoriasQuery): string {
  const query = new URLSearchParams();
  query.set('offset', String(params.offset));
  query.set('limit', String(params.limit));
  
  if (params.parent_id !== undefined && params.parent_id !== null) {
    query.set('parent_id', String(params.parent_id));
  } else if (params.parent_id === null) {
    query.set('parent_id', 'null');
  }
  
  if (params.include_deleted !== undefined) {
    query.set('include_deleted', String(params.include_deleted));
  }

  return query.toString();
}

export const categoriasService = {
  async getAll(params: CategoriasQuery): Promise<CategoriasResponse> {
    const { data } = await api.get<CategoriasResponse>(`/categorias?${buildQuery(params)}`);
    return data;
  },

  async getTree(include_deleted: boolean = false): Promise<CategoriaTree[]> {
    const { data } = await api.get<CategoriaTree[]>(`/categorias/tree?include_deleted=${include_deleted}`);
    return data;
  },

  async getById(id: number): Promise<Categoria> {
    const { data } = await api.get<Categoria>(`/categorias/${id}`);
    return data;
  },

  async create(input: CategoriaFormValues): Promise<Categoria> {
    const { data } = await api.post<Categoria>('/categorias/', {
      ...input,
      descripcion: input.descripcion || null,
      imagen_url: input.imagen_url || null,
    });
    return data;
  },

  async update(id: number, input: CategoriaFormValues): Promise<Categoria> {
    const { data } = await api.patch<Categoria>(`/categorias/${id}`, {
      ...input,
      descripcion: input.descripcion || null,
      imagen_url: input.imagen_url || null,
    });
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/categorias/${id}`);
  },

  async restore(id: number): Promise<Categoria> {
    const { data } = await api.patch<Categoria>(`/categorias/${id}/restore`);
    return data;
  },
};
