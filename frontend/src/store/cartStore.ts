import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Producto } from '../types/producto';

export interface CartItem {
  id: string; // Unique ID for the cart item since the same product can have different personalizations
  producto: Producto;
  cantidad: number;
  personalizacion?: Record<string, any>;
}

interface CartState {
  items: CartItem[];
  addItem: (producto: Producto, cantidad?: number, personalizacion?: Record<string, any>) => void;
  updateQuantity: (cartItemId: string, cantidad: number) => void;
  removeItem: (cartItemId: string) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      addItem: (producto, cantidad = 1, personalizacion) =>
        set((state) => {
          // Check if there is an identical product with the exact same personalization
          const persStr = JSON.stringify(personalizacion || null);
          const current = state.items.find(
            (item) => item.producto.id === producto.id && JSON.stringify(item.personalizacion || null) === persStr
          );

          if (current) {
            return {
              items: state.items.map((item) =>
                item.id === current.id
                  ? {
                      ...item,
                      producto,
                      cantidad: Math.min(
                        item.cantidad + cantidad,
                        Math.max(producto.stock_cantidad, 1),
                      ),
                    }
                  : item,
              ),
            };
          }

          return {
            items: [
              ...state.items,
              {
                id: crypto.randomUUID(),
                producto,
                cantidad: Math.min(cantidad, Math.max(producto.stock_cantidad, 1)),
                personalizacion,
              },
            ],
          };
        }),
      updateQuantity: (cartItemId, cantidad) =>
        set((state) => ({
          items: state.items
            .map((item) =>
              item.id === cartItemId
                ? {
                    ...item,
                    cantidad: Math.min(
                      Math.max(cantidad, 1),
                      Math.max(item.producto.stock_cantidad, 1),
                    ),
                  }
                : item,
            )
            .filter((item) => item.cantidad > 0),
        })),
      removeItem: (cartItemId) =>
        set((state) => ({
          items: state.items.filter((item) => item.id !== cartItemId),
        })),
      clearCart: () => set({ items: [] }),
    }),
    {
      name: 'food-store-cart',
      partialize: (state) => ({ items: state.items }),
    },
  ),
);

export function getCartSubtotal(items: CartItem[]): number {
  return items.reduce((total, item) => total + item.producto.precio_base * item.cantidad, 0);
}
