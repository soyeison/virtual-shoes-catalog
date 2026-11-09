# Referencia de la API

Base URL: `http://localhost:8000/api/v1`

FastAPI genera documentación interactiva con todos los esquemas:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

Esta página resume los endpoints y el comportamiento que el esquema OpenAPI no muestra.

## Formato de respuesta

Las respuestas exitosas siguen esta forma:

```json
{
  "status": "success",
  "message": "texto opcional",
  "data": { }
}
```

Los listados agregan `results` (en `GET /articles`) o `pagination` (en la búsqueda). Los formatos de error se describen en [errors-and-validation.md](errors-and-validation.md).

## Autenticación

`POST /auth/login` devuelve un JWT, pero **ningún endpoint lo exige ni lo valida**. Los endpoints de carrito y checkout identifican al usuario por el `{user_id}` de la ruta. Ver [security.md](security.md).

## Endpoints

| Método | Ruta | Descripción | Éxito |
| --- | --- | --- | --- |
| POST | `/auth/register` | Registra un usuario | 201 |
| POST | `/auth/login` | Inicia sesión y devuelve un JWT | 200 |
| POST | `/articles` | Crea un artículo con imágenes (multipart) | 201 |
| GET | `/articles` | Lista todos los artículos | 200 |
| GET | `/articles/search` | Busca con filtros, orden y paginación | 200 |
| GET | `/article/{article_id}` | Detalle de un artículo (ojo: `article` en singular) | 200 |
| GET | `/cart/{user_id}` | Obtiene el carrito (lo crea vacío si no existe) | 200 |
| POST | `/cart/{user_id}/items` | Agrega un artículo al carrito | 200 |
| PATCH | `/cart/{user_id}/items/{article_id}` | Cambia la cantidad de un artículo | 200 |
| DELETE | `/cart/{user_id}/items/{article_id}` | Quita un artículo del carrito | 200 |
| DELETE | `/cart/{user_id}/items` | Vacía el carrito | 200 |
| POST | `/checkout/{user_id}` | Convierte el carrito en un pedido | 201 |
| GET | `/orders/{order_id}` | Resumen de un pedido | 200 |
| POST | `/process-payment` | Cobra un pedido | 200 |

### Autenticación

#### `POST /auth/register`

```json
{
  "first_name": "Ana",
  "last_name": "Pérez",
  "birth_date": "1995-04-20",
  "email": "ana@example.com",
  "password": "secreto123",
  "shipping_address": {
    "street": "Calle 10 # 20-30",
    "city": "Medellín",
    "zip_code": "050001",
    "country": "Colombia"
  }
}
```

- `password`: mínimo 6 caracteres. `birth_date`: formato `YYYY-MM-DD`, y la persona debe ser mayor de edad.
- Respuesta: `{"status": "success", "data": {"user_id": "<uuid>"}}`.
- Si el email ya existe responde `400` con `"error": "ApplicationError"`.

#### `POST /auth/login`

```json
{ "email": "ana@example.com", "password": "secreto123" }
```

- Respuesta: `{"status": "success", "data": {"token": "<jwt>"}}`.
- Si el email o la contraseña son incorrectos responde `400` con `"message": "Invalid email or password."`. El mensaje es el mismo en los dos casos para no revelar qué emails existen.

### Artículos

#### `POST /articles` (multipart/form-data)

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `name` | texto | obligatorio, mínimo 1 carácter |
| `description` | texto | obligatorio |
| `stock` | entero | `>= 0` |
| `price_amount` | número | `> 0` |
| `price_currency` | texto | 3 letras, por defecto `COP` |
| `images` | archivos | opcional, máximo 5 |

```bash
curl -X POST http://localhost:8000/api/v1/articles \
  -F name="Zapatos Nike" -F description="Running" \
  -F stock=10 -F price_amount=250000 \
  -F images=@static/zapato1.jpg.jpeg
```

Las imágenes se suben a MinIO **antes** de crear el artículo; la respuesta incluye sus URLs públicas (ver [storage.md](storage.md)).

#### `GET /articles`

Devuelve todos los artículos con `id`, `name`, `stock`, `price {amount, currency}` e `image_urls`. No incluye `description`.

#### `GET /articles/search`

| Query param | Descripción |
| --- | --- |
| `name` | Fragmento del nombre (`LIKE %name%`) |
| `min_price`, `max_price` | Rango de precio |
| `sort_by` | `price_asc` o `price_desc`. Sin valor ordena por `id` descendente |
| `page` | Página, `>= 1` (por defecto 1). Tamaño fijo: 20 |

```json
{
  "status": "success",
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_records": 20,
    "results_on_this_page": 20
  },
  "data": [
    { "id": "…", "name": "Zapatos Nike", "price": 250000.0, "image_urls": ["…"] }
  ]
}
```

> En la búsqueda, `price` es un número, no un objeto `{amount, currency}` como en los demás endpoints. Además, `total_records` hoy cuenta solo los resultados de la página actual (ver [known-issues.md](known-issues.md)).

#### `GET /article/{article_id}`

Devuelve el artículo completo, incluida `description`. Responde `404` con `{"detail": "..."}` si no existe.

### Carrito

#### `GET /cart/{user_id}`

```json
{
  "status": "success",
  "data": {
    "user_id": "…",
    "total_amount": 500000.0,
    "items": [
      {
        "article_id": "…",
        "name": "Zapatos Nike",
        "quantity": 2,
        "unit_price": 250000.0,
        "subtotal": 500000.0,
        "image_url": "http://localhost:9000/catalogo-images/…"
      }
    ]
  }
}
```

Usa el precio **actual** de cada artículo e ignora los artículos que ya no existen.

#### `POST /cart/{user_id}/items`

```json
{ "article_id": "…", "quantity": 2 }
```

`quantity` debe ser mayor que 0. Si el artículo ya está en el carrito, **suma** la cantidad. Falla con `400` si se superan 10 unidades o no hay stock. Las operaciones de carrito responden `{"user_id", "total_items"}`, donde `total_items` es la cantidad de artículos distintos.

#### `PATCH /cart/{user_id}/items/{article_id}`

```json
{ "quantity": 5 }
```

Fija la cantidad exacta. El artículo debe estar en el carrito.

#### `DELETE /cart/{user_id}/items/{article_id}` y `DELETE /cart/{user_id}/items`

Quitan un artículo o vacían el carrito. Si el carrito no existe, no fallan.

### Pedidos y pagos

#### `POST /checkout/{user_id}`

Sin body. Crea un pedido `PENDING` con los precios del momento, descuenta el stock y vacía el carrito.

```json
{
  "status": "success",
  "message": "Checkout completed successfully",
  "data": {
    "order_id": "ord-1a2b3c4d",
    "user_id": "…",
    "status": "PENDING",
    "total_amount": 500000.0,
    "items": [
      { "article_id": "…", "quantity": 2, "unit_price": 250000.0, "subtotal": 500000.0 }
    ]
  }
}
```

Falla con `400` si el carrito está vacío, si algún artículo ya no existe o si no queda stock.

#### `GET /orders/{order_id}`

Mismo formato de `data` que el checkout. Responde `400` si el pedido no existe.

#### `POST /process-payment`

```json
{ "order_id": "ord-1a2b3c4d", "payment_token": "tok_visa" }
```

```json
{
  "status": "success",
  "message": "Payment processed and captured successfully.",
  "data": {
    "payment_id": "pay-9f8e7d6c",
    "order_id": "ord-1a2b3c4d",
    "amount": 500000.0,
    "currency": "COP",
    "status": "COMPLETED"
  }
}
```

Si el cobro se rechaza responde `400` con `{"detail": "Payment failed: <motivo>"}`. Qué valor enviar en `payment_token` depende de la pasarela configurada (ver [payments.md](payments.md)).
