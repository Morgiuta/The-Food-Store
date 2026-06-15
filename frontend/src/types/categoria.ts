export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string | null;
  imagen_url: string | null;
  parent_id: number | null;
  orden_display: number;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface CategoriaFormValues {
  nombre: string;
  descripcion: string;
  imagen_url: string;
  parent_id: number | null;
  orden_display: number;
}

export interface ImagenCategoriaUpdate {
  imagen_url: string;
}

export interface CategoriasQuery {
  page: number;
  size: number;
  parent_id?: number | null;
  include_deleted?: boolean;
}

export interface CategoriasResponse {
  items: Categoria[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CategoriaTree extends Categoria {
  children: CategoriaTree[];
}
