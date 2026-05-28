export interface Supply {
  id: number;
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  stock_actual: number;
  costo_unitario?: number;
  unidad: 'unidad' | 'kg' | 'litros' | 'gramos' | 'ml';
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface SupplyFormValues {
  nombre: string;
  descripcion: string;
  es_alergeno: boolean;
  stock_actual: number;
  unidad: 'unidad' | 'kg' | 'litros' | 'gramos' | 'ml';
}

export interface SuppliesQuery {
  search: string;
  es_alergeno: 'all' | 'true' | 'false';
  include_deleted: boolean;
  offset: number;
  limit: number;
  sort_by: 'id' | 'nombre' | 'es_alergeno' | 'created_at' | 'updated_at';
  sort_dir: 'asc' | 'desc';
}

export interface SuppliesResponse {
  data: Supply[];
  total: number;
}
