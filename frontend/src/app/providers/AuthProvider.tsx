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
      login: ({ username }) => {
        const nextUser: User = {
          id: crypto.randomUUID(),
          name: username.trim() || 'Food Store Admin',
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
