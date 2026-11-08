import { create } from 'zustand';
import type { Cart } from '../models/Cart';
import { CartGateway } from '../gateways/CartGateway';
import { OrderGateway } from '../../order/gateways/OrderGateway';

interface CartState {
  cart: Cart | null;
  isLoading: boolean;
  error: string | null;
  isSidebarOpen: boolean;

  toggleSidebar: () => void;

  fetchCart: (userId: string) => Promise<void>;
  addItem: (
    userId: string,
    articleId: string,
    quantity: number,
  ) => Promise<void>;
  removeItem: (userId: string, articleId: string) => Promise<void>;
  changeQuantity: (
    userId: string,
    articleId: string,
    quantity: number,
  ) => Promise<void>;
  clearCart: (userId: string) => Promise<void>;

  checkout: (userId: string) => Promise<string>;
}

export const useCartStore = create<CartState>((set, get) => ({
  cart: null,
  isLoading: false,
  error: null,
  isSidebarOpen: false,

  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  fetchCart: async (userId) => {
    set({ isLoading: true, error: null });
    try {
      const cartData = await CartGateway.getCart(userId);
      set({ cart: cartData, isLoading: false });
    } catch (err: any) {
      set({
        error: err.message || 'Error al obtener el carrito',
        isLoading: false,
      });
    }
  },

  addItem: async (userId, articleId, quantity) => {
    set({ isLoading: true, isSidebarOpen: true });
    try {
      // 1. Llama al backend para aplicar la regla de negocio (ej: validar stock)
      await CartGateway.addItem(userId, articleId, quantity);
      // 2. Refresca el estado local volviendo a pedir el carrito actualizado
      await get().fetchCart(userId);
    } catch (err: any) {
      set({
        error: err.message || 'No se pudo agregar el producto',
        isLoading: false,
      });
    }
  },

  removeItem: async (userId, articleId) => {
    set({ isLoading: true, error: null });
    try {
      await CartGateway.removeItem(userId, articleId);
      await get().fetchCart(userId);
    } catch (err: any) {
      set({
        error: err.message || 'No se pudo eliminar el producto',
        isLoading: false,
      });
    }
  },

  changeQuantity: async (userId, articleId, quantity) => {
    set({ isLoading: true, error: null });
    try {
      await CartGateway.changeQuantity(userId, articleId, quantity);
      await get().fetchCart(userId);
    } catch (err: any) {
      set({
        error: err.message || 'No se pudo actualizar la cantidad',
        isLoading: false,
      });
    }
  },

  clearCart: async (userId) => {
    set({ isLoading: true, error: null });
    try {
      await CartGateway.clearCart(userId);
      set({ cart: null, isLoading: false });
    } catch (err: any) {
      set({
        error: err.message || 'No se pudo vaciar el carrito',
        isLoading: false,
      });
    }
  },

  checkout: async (userId) => {
    set({ isLoading: true, error: null });
    try {
      const orderId = await OrderGateway.checkout(userId);

      // 2. Si es exitoso, limpiamos el estado del carrito
      // (Opcionalmente podrías llamar al endpoint de clearCart, pero si el checkout
      // del backend ya lo vacía, solo necesitamos actualizar el estado local)
      set({ cart: null, isSidebarOpen: false, isLoading: false });

      return orderId;
    } catch (err: any) {
      set({
        error: err.message || 'Error al procesar el pago',
        isLoading: false,
      });
      throw err; // Relanzamos el error para manejarlo en la UI
    }
  },
}));
