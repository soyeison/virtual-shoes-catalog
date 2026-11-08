import { useState } from 'react';
import { useAuthStore } from '../../auth/store/useAuthStore';
import { useCartStore } from '../store/useCartStore';

export const CartSidebar = () => {
  const { cart, isSidebarOpen, toggleSidebar, changeQuantity, removeItem, isLoading, checkout } = useCartStore();
  const userId = useAuthStore((state) => state.userId);

  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  const handleCheckout = async () => {
    if (!userId) {
      window.location.href = '/login';
      return;
    }

    try {
      setCheckoutError(null);
      // Procesamos la orden
      const orderId = await checkout(userId);
      
      // Redirigimos a una página de éxito (que podemos crear luego)
      window.location.href = `/checkout/${orderId}`;
    } catch (err: any) {
      setCheckoutError(err.message);
    }
  };

  const formatter = new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', maximumFractionDigits: 0
  });

  return (
    <>
      {/* Overlay: Fondo oscuro cuando el carrito está abierto */}
      <div 
        className={`fixed inset-0 bg-black/60 z-[60] transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={toggleSidebar}
      />

      {/* Panel Lateral */}
      <aside className={`fixed right-0 top-0 h-full w-full max-w-md bg-[#121212] z-[70] shadow-2xl border-l border-neutral-800 transition-transform duration-500 ease-in-out ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-neutral-800 flex justify-between items-center">
            <h2 className="text-xl font-black uppercase italic tracking-tighter">Tu <span className="text-orange-500">Carrito</span></h2>
            <button onClick={toggleSidebar} className="text-neutral-400 hover:text-white cursor-pointer uppercase text-xs font-bold">Cerrar ✕</button>
          </div>

          {/* Lista de Items */}
          <div className="flex-grow overflow-y-auto p-6 flex flex-col gap-6">
            {!cart || cart.items.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-neutral-500 gap-4">
                <p>Tu carrito está vacío</p>
                <button onClick={toggleSidebar} className="text-orange-500 font-bold uppercase text-xs tracking-widest">Empezar a comprar</button>
              </div>
            ) : (
              cart.items.map((item) => (
                <div key={item.article_id} className="flex gap-4 group">
                  <div className="w-20 h-20 bg-neutral-800 rounded-lg overflow-hidden flex-shrink-0">
                    <img src={item.image_url} alt={item.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-grow flex flex-col justify-between">
                    <div>
                      <h3 className="text-white font-bold text-sm leading-tight mb-1">{item.name}</h3>
                      <p className="text-orange-500 font-bold text-xs">{formatter.format(item.subtotal)}</p>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center border border-neutral-800 rounded-lg">
                        <button 
                          onClick={() => {
                            if (!userId) return;
                            item.quantity === 1 
                            ? removeItem(userId, item.article_id) 
                            : changeQuantity(userId, item.article_id, item.quantity - 1)}
                          }
                          className="px-2 py-1 text-neutral-400 hover:text-white cursor-pointer"
                        >
                          {item.quantity === 1 ? '🗑️' : '–'}
                        </button>
                        <span className="px-2 text-sm font-bold w-8 text-center">{item.quantity}</span>
                        <button 
                          onClick={() => {
                            if (!userId) return;
                            changeQuantity(userId, item.article_id, item.quantity + 1)
                          }}
                          className="px-2 py-1 text-neutral-400 cursor-pointer hover:text-white"
                        >+</button>
                      </div>
                      <button 
                        onClick={() => {
                          if (!userId) return;
                          removeItem(userId, item.article_id)
                        }}
                        className="text-neutral-600 hover:text-red-500 cursor-pointer text-xs transition-colors"
                      >Eliminar</button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer del Sidebar */}
          {cart && cart.items.length > 0 && (
            <div className="p-6 border-t border-neutral-800 bg-[#161616]">

              {checkoutError && (
                <div className="mb-4 text-red-500 text-xs font-bold bg-red-900/20 p-3 rounded-lg border border-red-500/30">
                  {checkoutError}
                </div>
              )}

              <div className="flex justify-between items-center mb-6">
                <span className="text-neutral-400 uppercase text-xs font-bold tracking-widest">Total estimado</span>
                <span className="text-2xl font-black text-white">{formatter.format(cart.total_amount)}</span>
              </div>
              <button 
                onClick={handleCheckout}
                disabled={isLoading}
                className="w-full bg-white text-black font-black uppercase tracking-widest py-4 rounded-xl hover:bg-orange-500 hover:text-white transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
              >
                {isLoading ? 'Procesando...' : 'Finalizar Compra'}
              </button>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};