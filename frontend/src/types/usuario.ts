export interface RolPublic {
  codigo: string;
  nombre: string;
  expires_at?: string | null;
}

export interface UsuarioPublic {
  id: number;
  nombre: string;
  apellido: string;
  email: string;
  celular?: string | null;
  roles: RolPublic[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UsuarioListResponse {
  items: UsuarioPublic[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface UsuariosQuery {
  page: number;
  size: number;
  rol?: string;
}

export interface UsuarioUpdate {
  nombre?: string;
  apellido?: string;
  email?: string;
  celular?: string | null;
  password?: string;
}

export interface UsuarioCreate {
  nombre: string;
  apellido: string;
  email: string;
  password: string;
  celular?: string | null;
  rol_nombre: string;
  rol_expires_at?: string | null;
}

export interface UsuarioRolUpdate {
  rol_nombre: string;
  expires_at?: string | null;
}
