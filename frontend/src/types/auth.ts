export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: number;
  name: string;
  role: 'ADMIN' | 'STOCK';
}

export interface AuthToken {
  access_token: string;
  token_type: 'bearer';
}

export interface AuthUserResponse {
  id: number;
  username: string;
  full_name: string;
  role: 'ADMIN' | 'STOCK';
  is_active: boolean;
}
