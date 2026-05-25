import type { AuthUserResponse, LoginCredentials, RegisterCredentials, User } from '../types/auth';
import { api } from './api';

function mapAuthUser(payload: AuthUserResponse): User {
  return {
    id: payload.id,
    name: payload.full_name,
    role: payload.role,
  };
}

export const authService = {
  async login({ username, password }: LoginCredentials): Promise<User> {
    await api.post('/auth/login', {
      email: username,
      password: password
    });

    const { data: userPayload } = await api.get<AuthUserResponse>('/auth/me');
    return mapAuthUser(userPayload);
  },
  async register(input: RegisterCredentials): Promise<void> {
    await api.post('/auth/register', input);
  },
  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },
};
