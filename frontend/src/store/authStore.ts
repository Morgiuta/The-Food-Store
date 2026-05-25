import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, LoginCredentials, RegisterCredentials } from '../types/auth';
import { authService } from '../services/authService';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: async (credentials) => {
        const user = await authService.login(credentials);
        set({ user, isAuthenticated: true });
      },

      register: async (credentials) => {
        const user = await authService.register(credentials);
        set({ user, isAuthenticated: true });
      },

      logout: async () => {
        try {
          await authService.logout();
        } catch (error) {
          console.error("Logout failed", error);
        } finally {
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: 'auth-storage', // saves to localStorage by default
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
