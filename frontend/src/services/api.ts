import axios from 'axios';
import { useAuthStore } from '../store/authStore';

export const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Trigger logout if unauthenticated (e.g. token expired)
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
