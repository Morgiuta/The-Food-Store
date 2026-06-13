export interface UnidadMedida {
  id: number;
  codigo: string;
  nombre: string;
  simbolo: string;
  descripcion: string | null;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
}

export interface UnidadMedidaFormValues {
  codigo: string;
  nombre: string;
  simbolo: string;
  descripcion: string;
}

export interface UnidadesMedidaQuery {
  page: number;
  size: number;
}

export interface UnidadesMedidaResponse {
  items: UnidadMedida[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
