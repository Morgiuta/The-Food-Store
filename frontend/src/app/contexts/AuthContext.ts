import { createContext } from 'react';
import type { LoginCredentials, User } from '../../types/auth';

export interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
