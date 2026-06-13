export interface Supply {
  id: number;
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  stock_actual: number;
  costo_unitario: number;
  unidad: 'unidad' | 'kg' | 'litros' | 'gramos' | 'ml';
  es_producto_terminado: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface SupplyFormValues {
  nombre: string;
  descripcion: string;
  es_alergeno: boolean;
  stock_actual: number;
  costo_unitario: number;
  unidad: 'unidad' | 'kg' | 'litros' | 'gramos' | 'ml';
  es_producto_terminado: boolean;
}

export interface SuppliesQuery {
  search: string;
  es_alergeno: 'all' | 'true' | 'false';
  include_deleted: boolean;
  page: number;
  size: number;
  sort_by: 'id' | 'nombre' | 'es_alergeno' | 'created_at' | 'updated_at';
  sort_dir: 'asc' | 'desc';
}

export interface SuppliesResponse {
  items: Supply[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
