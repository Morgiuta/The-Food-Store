export interface Direccion {
  id: number;
  usuario_id: number;
  alias: string | null;
  calle: string;
  numero: string;
  ciudad: string;
  provincia: string | null;
  codigo_postal: string | null;
  es_principal: boolean;
  deleted_at: string | null;
}

export interface DireccionFormValues {
  alias: string;
  calle: string;
  numero: string;
  ciudad: string;
  provincia: string;
  codigo_postal: string;
  es_principal: boolean;
}
