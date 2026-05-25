import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Producto } from '../types/producto';

export interface CartItem {
  producto: Producto;
  cantidad: number;
}

interface CartState {
  items: CartItem[];
  addItem: (producto: Producto, cantidad?: number) => void;
  updateQuantity: (productoId: number, cantidad: number) => void;
  removeItem: (productoId: number) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      addItem: (producto, cantidad = 1) =>
        set((state) => {
          const current = state.items.find((item) => item.producto.id === producto.id);
          if (current) {
            return {
              items: state.items.map((item) =>
                item.producto.id === producto.id
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
                producto,
                cantidad: Math.min(cantidad, Math.max(producto.stock_cantidad, 1)),
              },
            ],
          };
        }),
      updateQuantity: (productoId, cantidad) =>
        set((state) => ({
          items: state.items
            .map((item) =>
              item.producto.id === productoId
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
      removeItem: (productoId) =>
        set((state) => ({
          items: state.items.filter((item) => item.producto.id !== productoId),
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
