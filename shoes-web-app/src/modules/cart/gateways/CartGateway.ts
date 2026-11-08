import { httpClient, type ApiResponse } from '../../../shared/lib/httpClient';
import type {
  AddCartItemRequest,
  Cart,
  ChangeQuantityRequest,
} from '../models/Cart';

export const CartGateway = {
  getCart: async (userId: string): Promise<Cart> => {
    const response = await httpClient.get<ApiResponse<Cart>>(`/cart/${userId}`);
    return response.data;
  },

  addItem: async (
    userId: string,
    articleId: string,
    quantity: number,
  ): Promise<void> => {
    const body: AddCartItemRequest = { article_id: articleId, quantity };
    await httpClient.post(`/cart/${userId}/items`, body);
  },

  removeItem: async (userId: string, articleId: string): Promise<void> => {
    await httpClient.delete(`/cart/${userId}/items/${articleId}`);
  },

  changeQuantity: async (
    userId: string,
    articleId: string,
    quantity: number,
  ): Promise<void> => {
    const body: ChangeQuantityRequest = { quantity };
    await httpClient.patch(`/cart/${userId}/items/${articleId}`, body);
  },

  clearCart: async (userId: string): Promise<void> => {
    await httpClient.delete(`/cart/${userId}/items`);
  },
};
