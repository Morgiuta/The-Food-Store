import type { SuppliesQuery, SuppliesResponse, Supply, SupplyFormValues } from '../types/supply';

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace(
  /\/$/,
  '',
);

class ApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    let message = 'No se pudo completar la operacion.';
    try {
      const payload = await response.json();
      message = payload.detail ?? payload.message ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function buildQuery(params: SuppliesQuery): string {
  const query = new URLSearchParams();
  query.set('offset', String(params.offset));
  query.set('limit', String(params.limit));
  query.set('sort_by', params.sort_by);
  query.set('sort_dir', params.sort_dir);
  query.set('include_deleted', String(params.include_deleted));

  if (params.search.trim()) {
    query.set('search', params.search.trim());
  }

  if (params.es_alergeno !== 'all') {
    query.set('es_alergeno', params.es_alergeno);
  }

  return query.toString();
}

export const suppliesService = {
  getAll(params: SuppliesQuery): Promise<SuppliesResponse> {
    return request<SuppliesResponse>(`/ingredientes?${buildQuery(params)}`);
  },

  getById(id: number): Promise<Supply> {
    return request<Supply>(`/ingredientes/${id}`);
  },

  create(input: SupplyFormValues): Promise<Supply> {
    return request<Supply>('/ingredientes/', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },

  update(id: number, input: SupplyFormValues): Promise<Supply> {
    return request<Supply>(`/ingredientes/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  },

  remove(id: number): Promise<void> {
    return request<void>(`/ingredientes/${id}`, {
      method: 'DELETE',
    });
  },

  restore(id: number): Promise<Supply> {
    return request<Supply>(`/ingredientes/${id}/restore`, {
      method: 'PATCH',
    });
  },
};
