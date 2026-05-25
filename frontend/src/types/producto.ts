export interface ProductoCategoriaLink {
  categoria_id: number;
  es_principal: boolean;
}

export interface ProductoIngredienteLink {
  ingrediente_id: number;
  es_removible: boolean;
  es_opcional: boolean;
  cantidad_requerida: number;
}

export interface ProductoIngredientePublic extends ProductoIngredienteLink {
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: number;
  imagen_url: string | null;
  imagenes_url: string[];
  stock_cantidad: number;
  tiempo_prep_min: number | null;
  disponible: boolean;
  categorias: ProductoCategoriaLink[];
  ingredientes: ProductoIngredientePublic[];
}

export interface ProductoFormValues {
  nombre: string;
  descripcion: string;
  precio_base: number;
  imagen_url: string;
  imagenes_url: string[];
  stock_cantidad: number;
  tiempo_prep_min: number | null;
  disponible: boolean;
  categorias: ProductoCategoriaLink[];
  ingredientes: ProductoIngredienteLink[];
}

export interface ProductosQuery {
  page: number;
  limit: number;
  categoria_id?: number;
  disponible?: boolean;
  q?: string;
}

export interface ProductosResponse {
  items: Producto[];
  total: number;
  page: number;
  limit: number;
}
