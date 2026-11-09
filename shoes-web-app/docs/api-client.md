# Cliente HTTP y gateways

Todo el acceso a la API pasa por `src/shared/lib/httpClient.ts`, envuelto en un gateway por módulo. La referencia completa de los endpoints está en [api-reference.md](../../virtual-catalog-api/docs/api-reference.md) del backend.

## `httpClient`

| Método | Firma | Notas |
| --- | --- | --- |
| `get` | `get<T>(endpoint): Promise<T>` | Devuelve el JSON completo |
| `post` | `post<T>(endpoint, body): Promise<T>` | `body` se serializa con `JSON.stringify` |
| `patch` | `patch<T>(endpoint, body): Promise<T>` | Igual que `post` |
| `delete` | `delete(endpoint): Promise<void>` | No lee el cuerpo de la respuesta |

- URL: `${BASE_URL}${endpoint}`. Cómo se resuelve `BASE_URL` en [configuration.md](configuration.md#cómo-elige-la-url-httpclient).
- Headers: siempre `Content-Type: application/json`, y `Authorization: Bearer <token>` si hay token en `useAuthStore` (ver [auth.md](auth.md)).
- Solo envía JSON: no hay soporte para `multipart/form-data` (el front no crea artículos).
- No hay timeouts, reintentos, `AbortController` ni interceptores.

También exporta el tipo del sobre de respuesta:

```ts
export interface ApiResponse<T> {
  status: string;
  message?: string;
  results?: number;
  page?: number;
  data: T;
}
```

### Manejo de errores

Si `response.ok` es falso, `httpClient` lanza un `Error` con **solo el código HTTP** y descarta el cuerpo:

| Método | Mensaje |
| --- | --- |
| `get` | `HTTP error! status: <código>` |
| `post`, `patch`, `delete` | `HTTP Error: <código>` |

Los mensajes de la API (`"Invalid email or password."`, los rechazos por stock o por el límite de 10 unidades del carrito, los errores de validación `422`, etc.; ver [errors-and-validation.md](../../virtual-catalog-api/docs/errors-and-validation.md)) **nunca llegan a la UI**. Un fallo de red (API caída, CORS) lanza el `TypeError` de `fetch`, con mensajes como `Failed to fetch`.

Cómo trata cada capa el error:

| Lugar | Comportamiento |
| --- | --- |
| Páginas `.astro` (SSR) | `try/catch` con mensaje fijo en español en la página |
| `useAuthStore` | Guarda `err.message` en `error` (lo muestra `LoginForm`) |
| `useCartStore` | Guarda `err.message` en `error`; solo `checkout` relanza |
| `CatalogSearchGrid` | `console.error` y deja los resultados anteriores |
| `PaymentProcessor` | `console.log` y mensaje genérico fijo |

## Gateways y endpoints

| Gateway | Función | Método y ruta | Devuelve | Usado por |
| --- | --- | --- | --- | --- |
| `CatalogGateway` | `getAllArticles()` | `GET /articles` | `Article[]` | Nadie (sin uso) |
| | `getArticleById(id)` | `GET /article/{id}` | `Article` | `article/[id].astro`, `checkout/[id].astro` (SSR) |
| | `searchCatalog(params)` | `GET /articles/search?name&min_price&max_price&sort_by&page` | `{items, pagination}` | `index.astro` (SSR), `CatalogSearchGrid` |
| `AuthGateway` | `login(credentials)` | `POST /auth/login` | `token` | `useAuthStore` |
| | `register(userData)` | `POST /auth/register` | `user_id` | `useAuthStore` |
| `CartGateway` | `getCart(userId)` | `GET /cart/{user_id}` | `Cart` | `useCartStore.fetchCart` |
| | `addItem(userId, articleId, qty)` | `POST /cart/{user_id}/items` | — | `useCartStore.addItem` |
| | `changeQuantity(userId, articleId, qty)` | `PATCH /cart/{user_id}/items/{article_id}` | — | `useCartStore.changeQuantity` |
| | `removeItem(userId, articleId)` | `DELETE /cart/{user_id}/items/{article_id}` | — | `useCartStore.removeItem` |
| | `clearCart(userId)` | `DELETE /cart/{user_id}/items` | — | `useCartStore.clearCart` (sin uso en la UI) |
| `OrderGateway` | `checkout(userId)` | `POST /checkout/{user_id}` (body `{}`) | `order_id` | `useCartStore.checkout` |
| | `getOrderById(orderId)` | `GET /orders/{order_id}` | `OrderResponse` | `checkout/[id].astro` (SSR) |
| `PaymentGateway` | `processPayment({order_id, payment_token})` | `POST /process-payment` | `PaymentResponse` | `PaymentProcessor` |

El front no usa `POST /articles` (crear artículos) ni la ruta `GET /articles` sin filtros.

### Validaciones en los gateways

Algunos gateways comprueban la respuesta además del código HTTP:

- `AuthGateway.login`: lanza `'El servidor no devolvió un token válido'` si no hay `data.token`.
- `AuthGateway.register`: lanza `'Error en el registro de usuario'` si no hay `data.user_id`.
- `OrderGateway.checkout`: lanza `'No se pudo procesar la orden'` si no hay `data.order_id`.
- `OrderGateway.getOrderById`: lanza `'No se pudo cargar la información de la orden.'` si no hay `data`.

## Modelos

| Archivo | Tipos |
| --- | --- |
| `catalog/models/Article.ts` | `Price {amount, currency}`, `Article` (con `price: Price` y `description?`), `SearchArticleItem` (con `price: number`), `PaginationMeta`, `SearchResult` |
| `cart/models/Cart.ts` | `CartItem`, `Cart`, `AddCartItemRequest`, `ChangeQuantityRequest` |
| `auth/models/Auth.ts` | `UserLoginRequest`, `ShippingAddress`, `UserRegisterRequest`, `AuthResponse` |
| `order/gateways/OrderGateway.ts` | `OrderItemResponse`, `OrderResponse` |
| `order/gateways/PaymentGateway.ts` | `ProcessPaymentRequest`, `PaymentResponse` |

Hay dos tipos de artículo porque la API devuelve `price` con formas distintas: número en `/articles/search` y objeto `{amount, currency}` en `/article/{id}` (ver [known-issues.md](../../virtual-catalog-api/docs/known-issues.md) del backend). `ArticleCard` acepta los dos y normaliza con `typeof article.price === 'number'`.

Los tipos son solo anotaciones de TypeScript: no se valida en tiempo de ejecución que la respuesta tenga esa forma. `CatalogGateway` declara la respuesta de búsqueda con `pagination: any` y `data: any[]`.

## Agregar un endpoint

1. Si hace falta, define los tipos en `modules/<módulo>/models/`.
2. Agrega una función al gateway del módulo que llame a `httpClient` y devuelva `response.data`.
3. Úsala desde el store (si el estado se comparte entre islas), desde la isla, o desde el frontmatter de la página (si el dato se carga en el servidor).
