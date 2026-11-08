import { useState, useEffect } from 'react';
import { CatalogGateway } from '../gateways/CatalogGateway';
import { ArticleCard } from './ArticleCard';
import type { Article, PaginationMeta, SearchArticleItem } from '../models/Article';

interface Props {
  initialArticles: SearchArticleItem[]; 
  initialPagination: PaginationMeta | null;
}

export const CatalogSearchGrid = ({ initialArticles, initialPagination }: Props) => {
  const [articles, setArticles] = useState<Array<Article | SearchArticleItem>>(initialArticles);
  const [pagination, setPagination] = useState<PaginationMeta | null>(initialPagination);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('');

  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Un debounce simple: no queremos atacar a tu API por cada letra que el usuario teclea
    const delayDebounceFn = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await CatalogGateway.searchCatalog({
          name: searchTerm || undefined,
          sort_by: sortBy || undefined,
          min_price: minPrice ? Number(minPrice) : undefined,
          max_price: maxPrice ? Number(maxPrice) : undefined,
          page: page
        });
        setArticles(results.items);
        setPagination(results.pagination);
      } catch (error) {
        console.error("Error buscando artículos:", error);
      } finally {
        setIsLoading(false);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, sortBy, minPrice, maxPrice, page]);

  const handleTextChange = (value: string) => { setSearchTerm(value); setPage(1); };
  const handleMinPriceChange = (value: string) => { setMinPrice(value); setPage(1); };
  const handleMaxPriceChange = (value: string) => { setMaxPrice(value); setPage(1); };
  const handleSortChange = (value: string) => { setSortBy(value); setPage(1); };

  return (
    <div className="w-full">
      {/* Barra de Filtros y Búsqueda */}
      <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
        
        <div className="w-full md:w-1/3">
          <label className="text-xs uppercase font-bold text-neutral-500 mb-2 block">Buscar</label>
          <div className="relative">
            <input 
              type="text" 
              placeholder="Buscar zapatos, modelos..." 
              value={searchTerm}
              onChange={(e) => handleTextChange(e.target.value)}
              className="w-full bg-[#1a1a1a] border border-neutral-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-orange-500 transition-colors"
            />
            {isLoading && (
              <span className="absolute right-4 top-3 text-orange-500">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </span>
            )}
          </div>
        </div>
        
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex flex-col">
            <label className="text-xs uppercase font-bold text-neutral-500 mb-2 block">Precio Min ($)</label>
            <input 
              type="number" 
              placeholder="Ej: 50000"
              value={minPrice}
              min="0"
              onChange={(e) => handleMinPriceChange(e.target.value)}
              className="w-32 bg-[#1a1a1a] border border-neutral-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-orange-500 transition-colors"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-xs uppercase font-bold text-neutral-500 mb-2 block">Precio Max ($)</label>
            <input 
              type="number" 
              placeholder="Ej: 300000"
              value={maxPrice}
              min="0"
              onChange={(e) => handleMaxPriceChange(e.target.value)}
              className="w-32 bg-[#1a1a1a] border border-neutral-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-orange-500 transition-colors"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-xs uppercase font-bold text-neutral-500 mb-2 block">Ordenar</label>
            <select 
              onChange={(e) => handleSortChange(e.target.value)}
              className="bg-[#1a1a1a] text-white px-4 py-3 rounded-lg border border-neutral-800 focus:outline-none focus:border-orange-500 appearance-none cursor-pointer h-[50px]"
            >
              <option value="">Relevancia</option>
              <option value="price_asc">Menor precio</option>
              <option value="price_desc">Mayor precio</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center mb-8">
        <h2 className="text-neutral-400 text-sm uppercase tracking-widest">
          {pagination ? `${pagination.total_records} productos encontrados` : `${articles.length} productos`}
        </h2>
      </div>

      {/* Grilla de Resultados */}
      {articles.length === 0 && !isLoading ? (
        <div className="text-center py-20 bg-[#1a1a1a] rounded-2xl border border-neutral-800">
          <p className="text-neutral-400">No encontramos resultados para tu búsqueda.</p>
        </div>
      ) : (
        <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 transition-opacity duration-300 ${isLoading ? 'opacity-50' : 'opacity-100'}`}>
          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}

      {/* CONTROLES DE PAGINACIÓN */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex justify-center items-center gap-6 mt-16 border-t border-neutral-900 pt-8">
          <button
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page === 1 || isLoading}
            className="bg-[#1a1a1a] text-white px-5 py-2.5 rounded-xl border border-neutral-800 font-bold text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:border-neutral-700 transition-colors"
          >
            Anterior
          </button>
          
          <span className="text-neutral-400 text-sm font-medium">
            Página <span className="text-white font-bold">{page}</span> de {pagination.total_pages}
          </span>

          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= pagination.total_pages || isLoading}
            className="bg-[#1a1a1a] text-white px-5 py-2.5 rounded-xl border border-neutral-800 font-bold text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:border-neutral-700 transition-colors"
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
};