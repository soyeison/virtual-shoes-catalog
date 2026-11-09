# Limitaciones conocidas

Comportamientos del código actual del frontend que conviene conocer o corregir. Están ordenados por impacto. Las limitaciones del backend están en [known-issues.md](../../virtual-catalog-api/docs/known-issues.md) de la API; aquí solo se repiten cuando afectan directamente al front.

## Seguridad y sesión

### 1. El usuario se identifica con un `user_id` que controla el navegador
Como la API no valida el JWT ([security.md](../../virtual-catalog-api/docs/security.md#estado-actual-de-la-autorización)), lo que decide de quién es el carrito es el `userId` que el front pone en la ruta (`/cart/{user_id}`, `/checkout/{user_id}`). Ese valor sale de decodificar el token en el cliente y se guarda en `localStorage` (`auth-storage`). Editándolo desde las herramientas del navegador se puede operar sobre el carrito de otro usuario. Del mismo modo, `/checkout/:id` muestra y permite pagar cualquier orden conociendo su ID, con o sin sesión.

### 2. Token en `localStorage` y sin control de expiración
El JWT se guarda en `localStorage`, accesible para cualquier script de la página (riesgo ante XSS). Nunca se revisa el claim `exp` (60 minutos): la sesión del navegador no caduca, y `parseJwt` no verifica la firma. Hoy no tiene consecuencias porque la API ignora el token; en cuanto lo valide, el front recibirá `401` sin manejarlos (ver [auth.md](auth.md#lo-que-no-hay)).

### 3. El pago usa un token fijo
`PaymentProcessor` siempre envía `payment_token: "test_token_123"` (hay un comentario para integrar Stripe en el futuro). Con el adaptador `mock` de la API el pago se aprueba siempre; con `stripe` falla siempre, porque no es un `PaymentMethod` válido. La "tarjeta" `**** 4242` es solo decorativa: no se piden datos de pago.

### 4. Una orden ya pagada vuelve a mostrar el botón "Pagar"
`/checkout/:id` no lee `order.status`. Recargar la página tras pagar vuelve a ofrecer el pago. Junto con la limitación 4 del backend (cobra antes de comprobar el estado), eso permite **cobrar dos veces** la misma orden.

## Manejo de errores

### 5. Los mensajes de la API se pierden
`httpClient` lanza `Error("HTTP Error: <código>")` (o `HTTP error! status: <código>` en `get`) sin leer el cuerpo. El usuario ve, por ejemplo, "HTTP Error: 400" en lugar de "Invalid email or password." o del motivo de un registro rechazado. Solución: leer `await response.json()` en el error y propagar `message` o `detail` (ver [errors-and-validation.md](../../virtual-catalog-api/docs/errors-and-validation.md)).

### 6. Errores del carrito invisibles
`useCartStore` guarda los errores en `error`, pero solo `AddToCartButton` (página de detalle) lo muestra. En el catálogo (botón "+" de `ArticleCard`) y en el sidebar (+, –, Eliminar) los fallos no se ven: por ejemplo, superar el límite de 10 unidades o quedarse sin stock. Además `addItem` abre el sidebar antes de la petición y no limpia `error` al empezar, así que un error viejo puede seguir apareciendo.

### 7. Búsqueda en el navegador sin feedback de error
Si `GET /articles/search` falla en `CatalogSearchGrid`, solo hay un `console.error` y se mantienen los resultados anteriores. Si falla en el SSR, la página muestra un mensaje y no monta la grilla, sin opción de reintentar.

### 8. Las páginas de error responden HTTP 200
"Artículo no encontrado" y "No pudimos cargar la orden" se renderizan con estado `200` (comprobado ejecutando el build). Debería usarse `Astro.response.status = 404`. Tampoco hay página `404.astro` personalizada.

## Comportamiento

### 9. El código postal es "opcional" en la UI pero obligatorio en la API
El formulario de registro etiqueta "Código Postal (opcional)" y no marca el input como `required`, pero `ShippingAddress` del backend exige un `zip_code` numérico de al menos 5 dígitos. Si se deja vacío, el registro falla con un error genérico (limitación 5).

### 10. Recursos estáticos que no existen
`/placeholder-shoe.png` (imagen por defecto en `ArticleCard`, `ImageGallery` y el checkout) y `/icons/shoe-icon.png`, `/icons/bolt-icon.png`, `/icons/run-icon.png` (login) no están en `public/`. Se ven como imágenes rotas.

### 11. La paginación nunca aparece
Los controles solo se muestran si `total_pages > 1`, y por la limitación 8 del backend `total_pages` siempre es 1 y `total_records` (el "N productos encontrados") nunca supera 20. El front está listo: al corregir el backend debería funcionar sin cambios.

### 12. La primera página del catálogo se pide dos veces
El `useEffect` de `CatalogSearchGrid` corre también al montar, así que 500 ms después de cargar `/` se repite la misma búsqueda que ya hizo el SSR. Se puede evitar saltando la primera ejecución del efecto.

### 13. Respuestas de búsqueda fuera de orden
El debounce reduce las peticiones, pero no las cancela: si una búsqueda lenta termina después de una más reciente, la grilla muestra resultados viejos. Se resolvería con `AbortController` o ignorando respuestas obsoletas. Los filtros tampoco se guardan en la URL, así que se pierden al recargar o compartir el enlace.

### 14. Mensaje de pago exitoso con referencia truncada
`PaymentProcessor` muestra `orderId.split('-')[0]`. Como los IDs tienen la forma `ord-1a2b3c4d`, el texto queda "Tu orden **ord** ha sido confirmada".

### 15. El estado de error y carga del login se persiste
`persist` guarda todo `useAuthStore`, incluidos `error` e `isLoading`. Un error de login vuelve a mostrarse al abrir `/login` días después. Se corrige con `partialize: (s) => ({ token: s.token, userId: s.userId, isAuthenticated: s.isAuthenticated })`.

### 16. Sesión "a medias" si el token no se decodifica
Si `parseJwt` falla, queda `isAuthenticated: true` con `userId: null`: la cabecera muestra "Salir", pero el carrito no carga, "Agregar" redirige a `/login` y los botones del sidebar no hacen nada.

### 17. Navegación tras el login
Después del login o registro siempre se redirige a `/`, no a la página desde la que se pidió iniciar sesión. Un usuario ya logueado que abre `/login` ve el formulario de nuevo.

### 18. N+1 peticiones en el checkout
`checkout/[id].astro` hace un `GET /article/{id}` por cada ítem de la orden para obtener nombre e imagen, porque `GET /orders/{id}` no los incluye. Son en paralelo (`Promise.all`), pero crecen con el número de ítems.

### 19. Moneda y datos fijos
El detalle formatea con `article.price.currency`, pero `ArticleCard`, `CartSidebar`, el checkout y `PaymentProcessor` asumen siempre `COP`. Las etiquetas "Running" (tarjetas) y "Edición Profesional" (detalle) son texto fijo, no datos del artículo. El indicador de stock del detalle es verde aunque el stock sea 0, y no se actualiza al agregar al carrito.

## Accesibilidad y HTML

### 20. Marcado inválido o incompleto
- Las páginas con `MainLayout` anidan un `<main>` dentro del `<main>` del layout.
- `ArticleCard` es un `<a>` que contiene un `<button>` (contenido interactivo anidado).
- Los `<label>` de los formularios no están asociados a sus inputs (`htmlFor`/`id`).
- El botón 👁️ del campo contraseña no hace nada.
- El enlace "Catálogo" de la cabecera se oculta en pantallas pequeñas (`hidden md:flex`); queda el logo como enlace a `/`.

### 21. Clases CSS sin efecto
`animate-fade-in`, `scale-in` y `prose`/`prose-invert` no generan CSS (ver [styles.md](styles.md#clases-que-no-tienen-efecto)).

## Mantenimiento

### 22. Código sin uso
- Restos de la plantilla de Astro: `src/components/Welcome.astro`, `src/layouts/Layout.astro` y `src/assets/*.svg`.
- `src/shared/ui/ArticleImage.astro`, `CatalogGateway.getAllArticles` y `useCartStore.clearCart` / `CartGateway.clearCart` no se usan.
- Comentarios desactualizados: `CartWidget` habla de un "ID temporal" y `CartSidebar` de una "página de éxito que podemos crear luego" (hoy es `/checkout/:id`).

### 23. Inconsistencias de estructura
- `modules/auth/gateway/` está en singular; los demás módulos usan `gateways/`.
- `order` define sus tipos dentro de los gateways en lugar de `models/`.
- Dependencia circular `httpClient` → `useAuthStore` → `AuthGateway` → `httpClient` (ver [architecture.md](architecture.md#dependencias-entre-módulos)).

### 24. Tipado débil
Varios `any`: `hydratedItems: any[]` en el checkout, `pagination: any` y `data: any[]` en `CatalogGateway`, `body: any` en `httpClient`, `err: any` en los `catch`. `PUBLIC_API_URL` no está declarada en `env.d.ts`. No hay validación en tiempo de ejecución de las respuestas.

### 25. Sin tests ni verificación
No hay tests, linter, formateador ni `astro check` (no están instalados `typescript` ni `@astrojs/check`). Tampoco hay `.env.example` en el frontend.

### 26. Store de auth compartido en el servidor
En SSR, `useAuthStore` es un singleton del proceso Node. Hoy siempre está vacío, pero si algún día se llama a `login` en el servidor, el estado se compartiría entre todas las peticiones y usuarios.
