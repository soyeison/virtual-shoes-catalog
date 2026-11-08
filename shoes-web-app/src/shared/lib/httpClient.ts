import { useAuthStore } from '../../modules/auth/store/useAuthStore';

export interface ApiResponse<T> {
  status: string;
  message?: string;
  results?: number;
  page?: number;
  data: T;
}

// En el servidor (SSR) se usa INTERNAL_API_URL si existe (ej. http://api:8000 dentro de Docker);
// en el navegador siempre PUBLIC_API_URL. import.meta.env.SSR se resuelve en el build.
const BASE_URL = import.meta.env.SSR
  ? process.env.INTERNAL_API_URL ||
    import.meta.env.PUBLIC_API_URL ||
    'http://localhost:8000/api/v1'
  : import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const getHeaders = () => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Extraemos el token del estado actual de Zustand
  const token = useAuthStore.getState().token;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

export const httpClient = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json = await response.json();

    return json;
  },
  async post<T>(endpoint: string, body: any): Promise<T> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const json = await response.json();
    return json;
  },

  async patch<T>(endpoint: string, body: any): Promise<T> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const json = await response.json();
    return json;
  },

  async delete(endpoint: string): Promise<void> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }
  },
};
