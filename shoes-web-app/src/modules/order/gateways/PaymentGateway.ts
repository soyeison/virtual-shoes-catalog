import { httpClient } from '../../../shared/lib/httpClient';

export interface ProcessPaymentRequest {
  order_id: string;
  payment_token: string;
}

export interface PaymentResponse {
  payment_id: string;
  order_id: string;
  amount: number;
  currency: string;
  status: string;
}

interface PaymentApiResponse {
  status: string;
  message: string;
  data: PaymentResponse;
}

export const PaymentGateway = {
  processPayment: async (request: ProcessPaymentRequest): Promise<PaymentResponse> => {
    const response = await httpClient.post<PaymentApiResponse>('/process-payment', request);
    return response.data;
  }
};