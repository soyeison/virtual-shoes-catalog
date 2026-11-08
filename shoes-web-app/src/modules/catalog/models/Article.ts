export interface Price {
  amount: number;
  currency: string;
}

export interface Article {
  id: string;
  name: string;
  stock: number;
  price: Price;
  image_urls: string[];
  description?: string; // Solo viene en el detalle, no en el listado
}

export interface SearchArticleItem {
  id: string;
  name: string;
  price: number; // En búsqueda, el precio viene como float directo
  image_urls: string[];
}

export interface PaginationMeta {
  current_page: number;
  total_pages: number;
  total_records: number;
  results_on_this_page: number;
}

// Estructura completa de la respuesta del endpoint de búsqueda
export interface SearchResult {
  items: SearchArticleItem[];
  pagination: PaginationMeta;
}
