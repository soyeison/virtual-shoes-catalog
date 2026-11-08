import { useAuthStore } from '../../auth/store/useAuthStore';
import { useCartStore } from '../../cart/store/useCartStore';
import type { Article, SearchArticleItem } from '../models/Article';

interface Props {
  article: Article | SearchArticleItem;
}

export const ArticleCard = ({ article }: Props) => {
  const addItem = useCartStore((state) => state.addItem);
  const { userId, isAuthenticated } = useAuthStore();
  const priceAmount = typeof article.price === 'number' 
    ? article.price 
    : article.price.amount;

  const formatter = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });

  const imageUrl = article.image_urls[0] || '/placeholder-shoe.png';

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated || !userId) {
      window.location.href = '/login';
      return;
    }
    
    await addItem(userId, article.id, 1);
  };

  return (
    <a href={`/article/${article.id}`} className="group bg-[#1a1a1a] rounded-2xl p-4 flex flex-col gap-4 border border-transparent hover:border-orange-500/30 transition-all shadow-xl block cursor-pointer">
      <div className="overflow-hidden rounded-xl bg-neutral-800 aspect-square">
        <img 
          src={imageUrl} 
          alt={article.name} 
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
      </div>
      
      <div className="flex flex-col flex-grow">
        <span className="text-[10px] uppercase tracking-widest text-orange-500 font-bold mb-1">Running</span>
        <h3 className="text-white font-semibold text-lg line-clamp-1">{article.name}</h3>
        {('description' in article) && (
          <p className="text-neutral-400 text-sm line-clamp-2 mt-2 leading-relaxed">
            {article.description}
          </p>
        )}
      </div>

      <div className="flex justify-between items-center mt-4">
        <span className="text-white font-bold text-xl">
          {formatter.format(priceAmount)}
        </span>
        <button 
          onClick={handleAddToCart}
          className="bg-white text-black p-2 rounded-full hover:bg-orange-500 hover:text-white transition-colors cursor-pointer z-10"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        </button>
      </div>
    </a>
  );
};