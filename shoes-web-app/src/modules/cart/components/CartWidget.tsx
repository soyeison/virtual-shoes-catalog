import { useEffect } from 'react';
import { useCartStore } from '../store/useCartStore';
import { useAuthStore } from '../../auth/store/useAuthStore';

export const CartWidget = () => {
  const cart = useCartStore((state) => state.cart);
  const fetchCart = useCartStore((state) => state.fetchCart);
  const toggleSidebar = useCartStore((state) => state.toggleSidebar);

  // Usamos el mismo ID temporal que en el botón de agregar
  const { userId, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && userId) {
      fetchCart(userId);
    }
  }, [fetchCart, isAuthenticated, userId]);

  const totalItems = cart?.items?.reduce((total, item) => total + item.quantity, 0) || 0;

  return (
    <div 
      onClick={toggleSidebar} // <-- Abrimos el sidebar aquí
      className="relative cursor-pointer hover:text-orange-500 transition-colors"
    >
    <div className="relative cursor-pointer hover:text-orange-500 transition-colors">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="9" cy="21" r="1"></circle>
        <circle cx="20" cy="21" r="1"></circle>
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
      </svg>
      
      {/* Solo mostramos el globo si hay elementos */}
      {totalItems > 0 && (
        <span className="absolute -top-2 -right-2 bg-orange-500 text-black text-[10px] font-black w-5 h-5 flex items-center justify-center rounded-full transition-transform scale-in">
          {totalItems}
        </span>
      )}
    </div>
    </div>
  );
};