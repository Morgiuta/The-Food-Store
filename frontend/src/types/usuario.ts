export interface RolPublic {
  codigo: string;
  nombre: string;
}

export interface UsuarioPublic {
  id: number;
  nombre: string;
  apellido: string;
  email: string;
  roles: RolPublic[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UsuarioListResponse {
  items: UsuarioPublic[];
  total: number;
  page: number;
  limit: number;
}

export interface UsuariosQuery {
  page: number;
  limit: number;
  rol?: string;
}

export interface UsuarioUpdate {
  nombre?: string;
  email?: string;
}

export interface UsuarioRolUpdate {
  rol_nombre: string;
}
