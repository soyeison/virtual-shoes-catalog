import { useAuthStore } from "../../auth/store/useAuthStore";
import { useCartStore } from "../store/useCartStore";

interface Props {
  articleId: string;
  stock: number;
}

export const AddToCartButton = ({ articleId, stock }: Props) => {
  const addItem = useCartStore((state) => state.addItem);
  const isLoading = useCartStore((state) => state.isLoading);
  const error = useCartStore((state) => state.error);

  const { userId, isAuthenticated } = useAuthStore();

  const handleAddToCart = async () => {
    if (stock <= 0) return;
    
    if (!isAuthenticated || !userId) {
      window.location.href = '/login';
      return;
    }
    
    await addItem(userId, articleId, 1);
  };

  return (
    <div className="w-full flex flex-col gap-2">
      <button 
        onClick={handleAddToCart}
        disabled={isLoading || stock <= 0}
        className="w-full bg-orange-500 text-black font-black uppercase tracking-widest py-5 rounded-xl hover:bg-white transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-3"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            Agregando...
          </>
        ) : stock <= 0 ? (
          'Agotado'
        ) : (
          'Agregar al Carrito'
        )}
      </button>

      {/* Manejo de errores visual */}
      {error && (
        <span className="text-red-500 text-sm font-bold text-center bg-red-900/20 py-2 rounded-lg border border-red-500/30">
          {error}
        </span>
      )}
    </div>
  );
};