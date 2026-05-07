import { useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';
import type { User } from '../../types/auth';
import { AuthContext, type AuthContextValue } from '../contexts/AuthContext';

const storageKey = 'food-store-user';

function getStoredUser(): User | null {
  const rawUser = window.localStorage.getItem(storageKey);

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser) as User;
  } catch {
    window.localStorage.removeItem(storageKey);
    return null;
  }
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(() => getStoredUser());

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      login: async ({ username, password }) => {
        await new Promise((resolve) => {
          window.setTimeout(resolve, 450);
        });

        const normalizedUser = username.trim().toLowerCase();
        const isAdmin = normalizedUser === 'admin' && password === '1234';
        const isStock = normalizedUser === 'stock' && password === 'stock';

        if (!isAdmin && !isStock) {
          throw new Error('Credenciales invalidas. Usa admin/1234 o stock/stock.');
        }

        const nextUser: User = {
          id: isAdmin ? 'demo-admin' : 'demo-stock',
          name: isAdmin ? 'Food Store Admin' : 'Gestor de Stock',
          role: isAdmin ? 'ADMIN' : 'STOCK',
        };

        setUser(nextUser);
        window.localStorage.setItem(storageKey, JSON.stringify(nextUser));
      },
      logout: () => {
        setUser(null);
        window.localStorage.removeItem(storageKey);
      },
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
