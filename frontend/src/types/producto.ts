export interface ProductoCategoriaLink {
  categoria_id: number;
  es_principal: boolean;
}

export interface ProductoIngredienteLink {
  ingrediente_id: number;
  es_removible: boolean;
  es_opcional: boolean;
  cantidad: number;
  unidad_medida_id: number;
}

export interface ProductoIngredientePublic extends ProductoIngredienteLink {
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface ImagenProductoUpdate {
  imagenes_url: string[];
}

export interface UnidadMedidaPublic {
  id: number;
  codigo: string;
  nombre: string;
  simbolo: string;
  descripcion: string | null;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: number;
  imagen_url: string | null;
  imagenes_url: string[];
  stock_cantidad: number;
  unidad_venta_id: number | null;
  unidad_venta: UnidadMedidaPublic | null;
  tiempo_prep_min: number | null;
  disponible: boolean;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
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
  unidad_venta_id: number | null;
  tiempo_prep_min: number | null;
  disponible: boolean;
  categorias: ProductoCategoriaLink[];
  ingredientes: ProductoIngredienteLink[];
}

export interface ProductosQuery {
  page: number;
  size: number;
  categoria_id?: number;
  disponible?: boolean;
  include_deleted?: boolean;
  q?: string;
}

export interface ProductosResponse {
  items: Producto[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
