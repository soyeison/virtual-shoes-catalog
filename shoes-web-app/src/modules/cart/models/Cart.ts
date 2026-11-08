export interface CartItem {
  article_id: string;
  name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  image_url: string;
}

export interface Cart {
  user_id: string;
  total_amount: number;
  items: CartItem[];
}

// Requests
export interface AddCartItemRequest {
  article_id: string;
  quantity: number;
}

export interface ChangeQuantityRequest {
  quantity: number;
}
