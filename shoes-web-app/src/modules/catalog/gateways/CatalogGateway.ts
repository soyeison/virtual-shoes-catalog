import { httpClient, type ApiResponse } from '../../../shared/lib/httpClient';
import type {
  Article,
  SearchArticleItem,
  SearchResult,
} from '../models/Article';

interface ApiSearchResponse {
  status: string;
  pagination: any;
  data: any[];
}

export const CatalogGateway = {
  getAllArticles: async (): Promise<Article[]> => {
    const response = await httpClient.get<ApiResponse<Article[]>>('/articles');
    return response.data;
  },

  getArticleById: async (articleId: string): Promise<Article> => {
    const response = await httpClient.get<ApiResponse<Article>>(
      `/article/${articleId}`,
    );
    return response.data;
  },

  searchCatalog: async (params: {
    name?: string;
    min_price?: number;
    max_price?: number;
    sort_by?: string;
    page?: number;
  }): Promise<SearchResult> => {
    // Construir la URL con los query parameters
    const query = new URLSearchParams();
    if (params.name) query.append('name', params.name);
    if (params.min_price)
      query.append('min_price', params.min_price.toString());
    if (params.max_price)
      query.append('max_price', params.max_price.toString());
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.page) query.append('page', params.page.toString());

    const response = await httpClient.get<ApiSearchResponse>(
      `/articles/search?${query.toString()}`,
    );

    return {
      items: response.data || [],
      pagination: response.pagination || null,
    };
  },
};
