import type { Supply } from '../types/supply';

export const mockSupplies: Supply[] = [
  {
    id: 1,
    nombre: 'Pan brioche',
    descripcion: 'Pan suave para hamburguesas clasicas y premium.',
    es_alergeno: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted_at: null,
  },
  {
    id: 2,
    nombre: 'Medallones de carne',
    descripcion: 'Blend congelado de 120g para burger simple o doble.',
    es_alergeno: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted_at: null,
  },
  {
    id: 3,
    nombre: 'Queso cheddar',
    descripcion: 'Fetas individuales listas para despacho.',
    es_alergeno: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted_at: null,
  },
];
