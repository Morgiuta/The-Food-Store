import { AxiosError } from 'axios';

interface ApiErrorPayload {
  detail?: unknown;
  message?: unknown;
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorPayload | undefined;
    const detail = data?.detail ?? data?.message;

    if (typeof detail === 'string') {
      return detail;
    }

    if (detail && typeof detail === 'object' && 'mensaje' in detail) {
      const mensaje = (detail as { mensaje?: unknown }).mensaje;
      if (typeof mensaje === 'string') {
        return mensaje;
      }
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}
