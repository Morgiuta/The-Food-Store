import { useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';
import type { User } from '../../types/auth';
import { AuthContext, type AuthContextValue } from '../contexts/AuthContext';
import { authService, clearAuthSession, getStoredUser } from '../../services/authService';

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(() => getStoredUser());

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      login: async (credentials) => {
        const nextUser = await authService.login(credentials);
        setUser(nextUser);
      },
      logout: () => {
        setUser(null);
        clearAuthSession();
      },
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
