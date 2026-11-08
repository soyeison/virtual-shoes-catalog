import { useState } from 'react';
import { PaymentGateway } from '../gateways/PaymentGateway';

interface Props {
    orderId: string;
    totalAmount: number;
}

export const PaymentProcessor = ({ orderId, totalAmount }: Props) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isSuccess, setIsSuccess] = useState(false);

    const formatter = new Intl.NumberFormat('es-CO', {
        style: 'currency', currency: 'COP', maximumFractionDigits: 0
    });

    const handlePayment = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Usamos un token mock. Cuando integres Stripe, aquí llamarás a stripe.createToken()
            const mockToken = "test_token_123";

            await PaymentGateway.processPayment({
                order_id: orderId,
                payment_token: mockToken
            });

            setIsSuccess(true);
        } catch (err: any) {
            // Capturamos el 400 Bad Request si el caso de uso falla
            console.log('Error procesando el pago:', err);
            setError('Hubo un error con el pago. Por favor intenta de nuevo más tarde o con otro medio de pago.');
        } finally {
            setIsLoading(false);
        }
    };

    if (isSuccess) {
        return (
            <div className="bg-green-50 border border-green-200 p-8 rounded-2xl text-center animate-fade-in">
                <div className="w-16 h-16 bg-green-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">✓</div>
                <h3 className="text-xl font-black text-green-800 mb-2">¡Pago Exitoso!</h3>
                <p className="text-green-700">Tu orden {orderId.split('-')[0]} ha sido confirmada y está en preparación.</p>
                <a href="/" className="inline-block mt-6 px-6 py-3 bg-green-600 text-white font-bold rounded-xl hover:bg-green-700 transition-colors">
                    Volver al catálogo
                </a>
            </div>
        );
    }

    return (
        <div className="bg-[#1a1a1a] p-8 rounded-2xl border border-neutral-800">
            <h3 className="text-white font-black text-xl mb-6 uppercase tracking-widest">Resumen de Pago</h3>

            <div className="flex justify-between items-center mb-8 pb-8 border-b border-neutral-800">
                <span className="text-neutral-400 font-medium">Total a pagar:</span>
                <span className="text-white text-3xl font-black">{formatter.format(totalAmount)}</span>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-xl text-red-500 text-sm font-semibold">
                    {error}
                </div>
            )}

            {/* Simulador de Tarjeta (UI visual para dar contexto) */}
            <div className="mb-6 p-4 border border-neutral-700 rounded-xl bg-[#222]">
                <div className="flex items-center gap-3 text-neutral-400 mb-2">
                    <span>💳</span> <span className="text-xs uppercase tracking-widest">Tarjeta de Crédito Simulada</span>
                </div>
                <p className="text-white font-mono tracking-widest text-lg">**** **** **** 4242</p>
            </div>

            <button
                onClick={handlePayment}
                disabled={isLoading}
                className="w-full flex justify-center items-center gap-2 bg-gradient-to-r from-[#DB6F32] to-[#EE6239] text-white font-black uppercase tracking-widest py-5 rounded-xl hover:from-[#DD6D31] hover:to-[#E3663C] transition-all shadow-[0_4px_14px_0_rgba(238,98,57,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isLoading ? 'Procesando pago...' : `Pagar ${formatter.format(totalAmount)}`}
            </button>

            <p className="text-center text-neutral-500 text-xs mt-4">
                🔒 Transacción simulada segura end-to-end.
            </p>
        </div>
    );
};