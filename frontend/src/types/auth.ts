export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  nombre: string;
  apellido: string;
  celular?: string;
  email: string;
  password: string;
}

export type UserRole = 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT';

export interface User {
  id: number;
  name: string;
  nombre?: string;
  apellido?: string;
  role: UserRole;
}

export interface AuthUserResponse {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}
