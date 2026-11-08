export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface ShippingAddress {
  city: string;
  street: string;
  country: string;
  zip_code: string;
}

export interface UserRegisterRequest {
  first_name: string;
  last_name: string;
  birth_date: string; // Formato YYYY-MM-DD
  email: string;
  password: string;
  shipping_address: ShippingAddress;
}

export interface AuthResponse {
  status: string;
  data: {
    token?: string;
    user_id?: string;
  };
}
