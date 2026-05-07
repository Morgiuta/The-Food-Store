export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: string;
  name: string;
  role: 'ADMIN' | 'STOCK';
}
