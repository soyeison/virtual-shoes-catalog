import { httpClient } from '../../../shared/lib/httpClient';

export interface OrderItemResponse {
  article_id: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface OrderResponse {
  order_id: string;
  user_id: string;
  status: string;
  total_amount: number;
  items: OrderItemResponse[];
}

interface OrderApiResponse {
  status: string;
  message?: string;
  data: OrderResponse;
}

export const OrderGateway = {
  checkout: async (userId: string): Promise<string> => {
    const response = await httpClient.post<OrderApiResponse>(
      `/checkout/${userId}`,
      {},
    );

    if (!response.data || !response.data.order_id) {
      throw new Error('No se pudo procesar la orden');
    }

    return response.data.order_id;
  },

  getOrderById: async (orderId: string): Promise<OrderResponse> => {
    const response = await httpClient.get<OrderApiResponse>(`/orders/${orderId}`);
    
    if (!response.data) {
      throw new Error('No se pudo cargar la información de la orden.');
    }
    
    return response.data;
  }
};
