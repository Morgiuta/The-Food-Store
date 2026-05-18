import type {
  AuthUserResponse,
  LoginCredentials,
  User,
} from '../types/auth';

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace(
  /\/$/,
  '',
);

const userStorageKey = 'food-store-user';

function mapAuthUser(payload: AuthUserResponse): User {
  return {
    id: payload.id,
    name: payload.full_name,
    role: payload.role,
  };
}

async function parseError(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    return payload.detail ?? payload.message ?? 'No se pudo iniciar sesion.';
  } catch {
    return response.statusText || 'No se pudo iniciar sesion.';
  }
}

export function getStoredUser(): User | null {
  const rawUser = window.localStorage.getItem(userStorageKey);

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser) as User;
  } catch {
    clearAuthSession();
    return null;
  }
}

export function saveAuthSession(user: User): void {
  window.localStorage.setItem(userStorageKey, JSON.stringify(user));
}

export function clearAuthSession(): void {
  window.localStorage.removeItem(userStorageKey);
}

export const authService = {
  async login({ username, password }: LoginCredentials): Promise<User> {
    const formData = new URLSearchParams();
    formData.set('username', username);
    formData.set('password', password);

    const tokenResponse = await fetch(`${apiBaseUrl}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include',
    });

    if (!tokenResponse.ok) {
      throw new Error(await parseError(tokenResponse));
    }

    const userResponse = await fetch(`${apiBaseUrl}/auth/me`, {
      credentials: 'include',
    });

    if (!userResponse.ok) {
      throw new Error(await parseError(userResponse));
    }

    const user = mapAuthUser((await userResponse.json()) as AuthUserResponse);
    saveAuthSession(user);
    return user;
  },
  async logout(): Promise<void> {
    await fetch(`${apiBaseUrl}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    clearAuthSession();
  },
};
