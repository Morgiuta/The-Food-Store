import type {
  AuthUserResponse,
  LoginCredentials,
  RegisterCredentials,
  TokenResponse,
  User,
} from '../types/auth';
import { api } from './api';

function mapAuthUser(payload: AuthUserResponse): User {
  return {
    id: payload.id,
    name: payload.full_name,
    role: payload.role,
  };
}

export const authService = {
  async login({ username, password }: LoginCredentials): Promise<{ user: User; accessToken: string; refreshToken: string }> {
    const { data: tokenPayload } = await api.post<TokenResponse>('/auth/login', {
      email: username,
      password: password
    });

    const { data: userPayload } = await api.get<AuthUserResponse>('/auth/me', {
      headers: {
        Authorization: `Bearer ${tokenPayload.access_token}`,
      },
    });
    return {
      user: mapAuthUser(userPayload),
      accessToken: tokenPayload.access_token,
      refreshToken: tokenPayload.refresh_token,
    };
  },
  async refresh(refreshToken: string): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return data;
  },
  async register(input: RegisterCredentials): Promise<void> {
    await api.post('/auth/register', input);
  },
  async logout(refreshToken?: string | null): Promise<void> {
    await api.post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
  },
};
