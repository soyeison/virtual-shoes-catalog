import { httpClient } from '../../../shared/lib/httpClient';
import type {
  UserLoginRequest,
  UserRegisterRequest,
  AuthResponse,
} from '../models/Auth';

export const AuthGateway = {
  login: async (credentials: UserLoginRequest): Promise<string> => {
    const response = await httpClient.post<AuthResponse>(
      '/auth/login',
      credentials,
    );

    if (!response.data || !response.data.token) {
      throw new Error('El servidor no devolvió un token válido');
    }

    return response.data.token;
  },

  register: async (userData: UserRegisterRequest): Promise<string> => {
    const response = await httpClient.post<AuthResponse>(
      '/auth/register',
      userData,
    );

    if (!response.data || !response.data.user_id) {
      throw new Error('Error en el registro de usuario');
    }

    return response.data.user_id;
  },
};
