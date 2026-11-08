import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthGateway } from '../../auth/gateway/AuthGateway';
import type { UserLoginRequest, UserRegisterRequest } from '../models/Auth';

const parseJwt = (token: string) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join(''),
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

interface AuthState {
  token: string | null;
  userId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (credentials: UserLoginRequest) => Promise<void>;
  register: (userData: UserRegisterRequest) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const token = await AuthGateway.login(credentials);
          const decoded = parseJwt(token);

          const userId = decoded?.sub || decoded?.user_id || null;

          set({
            token,
            userId,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (err: any) {
          set({
            error: err.message || 'Error al iniciar sesión',
            isLoading: false,
          });
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          await AuthGateway.register(userData);

          const token = await AuthGateway.login({
            email: userData.email,
            password: userData.password,
          });
          const decoded = parseJwt(token);
          const userId = decoded?.sub || decoded?.user_id || null;

          set({ token, userId, isAuthenticated: true, isLoading: false });
        } catch (err: any) {
          set({
            error: err.message || 'Error al registrar la cuenta',
            isLoading: false,
          });
        }
      },

      logout: () => {
        set({ token: null, userId: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    },
  ),
);
