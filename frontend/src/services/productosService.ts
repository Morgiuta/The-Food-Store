import type {
  ImagenProductoUpdate,
  Producto,
  ProductoFormValues,
  ProductoIngredienteLink,
  ProductoIngredientePublic,
  ProductosQuery,
  ProductosResponse,
} from '../types/producto';
import { api } from './api';

function buildQuery(params: ProductosQuery): string {
  const query = new URLSearchParams();
  query.set('page', String(params.page));
  query.set('size', String(params.size));
  
  if (params.categoria_id) {
    query.set('categoria_id', String(params.categoria_id));
  }
  if (params.disponible !== undefined) {
    query.set('disponible', String(params.disponible));
  }
  if (params.q) {
    query.set('q', params.q);
  }
  if (params.include_deleted !== undefined) {
    query.set('include_deleted', String(params.include_deleted));
  }

  return query.toString();
}

export const productosService = {
  async getAll(params: ProductosQuery): Promise<ProductosResponse> {
    const { data } = await api.get<ProductosResponse>(`/productos/?${buildQuery(params)}`);
    return data;
  },

  async getById(id: number): Promise<Producto> {
    const { data } = await api.get<Producto>(`/productos/${id}`);
    return data;
  },

  async create(input: ProductoFormValues): Promise<Producto> {
    const { data } = await api.post<Producto>('/productos/', {
      ...input,
      descripcion: input.descripcion || null,
      imagen_url: input.imagen_url || null,
    });
    return data;
  },

  async update(id: number, input: ProductoFormValues): Promise<Producto> {
    const { imagenes_url, ingredientes, ...productoBase } = input;
    await api.put<Producto>(`/productos/${id}`, {
      ...productoBase,
      descripcion: input.descripcion || null,
      imagen_url: input.imagen_url || null,
    });

    await this.updateImagenes(id, { imagenes_url });
    await this.updateIngredientes(id, ingredientes);
    return this.getById(id);
  },

  async updateImagenes(id: number, input: ImagenProductoUpdate): Promise<Producto> {
    const { data } = await api.patch<Producto>(`/productos/${id}/imagenes`, input);
    return data;
  },

  async getIngredientes(id: number): Promise<ProductoIngredientePublic[]> {
    const { data } = await api.get<ProductoIngredientePublic[]>(`/productos/${id}/ingredientes`);
    return data;
  },

  async updateIngredientes(
    id: number,
    ingredientes: ProductoIngredienteLink[],
  ): Promise<ProductoIngredientePublic[]> {
    const { data } = await api.post<ProductoIngredientePublic[]>(
      `/productos/${id}/ingredientes`,
      ingredientes,
    );
    return data;
  },

  async updateDisponibilidad(id: number, disponible: boolean): Promise<Producto> {
    const { data } = await api.patch<Producto>(`/productos/${id}/disponibilidad`, {
      disponible,
    });
    return data;
  },

  async updateStock(id: number, stock_cantidad: number): Promise<Producto> {
    const { data } = await api.patch<Producto>(`/productos/${id}/stock`, {
      stock_cantidad,
    });
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/productos/${id}`);
  },

  async restore(id: number): Promise<Producto> {
    const { data } = await api.patch<Producto>(`/productos/${id}/restore`);
    return data;
  },
};
