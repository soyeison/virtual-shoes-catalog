# Limitaciones conocidas

Comportamientos del código actual que conviene conocer o corregir. Están ordenados por impacto.

## Seguridad

### 1. El JWT no se valida en ningún endpoint
La API emite tokens en el login pero no los exige. Carrito, checkout, pedidos y pagos confían en el `user_id` o `order_id` de la ruta o el body, y `POST /articles` es público. Ver [security.md](security.md#estado-actual-de-la-autorización), donde se describe cómo implementarlo.

### 2. Secreto del JWT fijo en el código
`get_token_generator()` en `main.py` usa `secret_key="supersecretkey"`. Debería ir en `Settings` y en el `.env`.

## Integridad de datos

### 3. El checkout no es atómico
Cada repositorio hace `commit()` por su cuenta. Si el checkout falla a mitad (por ejemplo, el segundo artículo no tiene stock), el stock del primero ya quedó descontado. Ver [database.md](database.md#transacciones).

### 4. Se puede cobrar un pedido ya pagado
`ProcessPaymentUseCase` llama a la pasarela **antes** de verificar el estado del pedido. Si el pedido ya está `PAID`, se cobra de nuevo y después `order.pay()` falla con *"Cannot pay an order that is currently PAID."* Solución: verificar que `order.status == PENDING` antes de crear el `Payment`.

### 5. El `transaction_id` de la pasarela no se guarda
La tabla `payments` no tiene una columna para el ID del PaymentIntent de Stripe. Eso dificulta conciliar pagos o hacer reembolsos.

### 6. Imágenes huérfanas en RustFS
`POST /articles` sube las imágenes antes de crear el artículo. Si la creación falla, las imágenes quedan en el bucket sin ningún artículo asociado.

### 7. Sin claves foráneas ni migraciones
Las relaciones entre tablas no están declaradas, y el esquema se crea con `CREATE TABLE IF NOT EXISTS` en el constructor de cada repositorio, en cada petición. Agregar o cambiar columnas exige migrar a mano.

## Comportamiento

### 8. La paginación de la búsqueda está mal calculada
`SqliteArticleRepository.search` ejecuta un `COUNT(*)` correcto pero devuelve `len(articles)`, es decir, la cantidad de la página actual. Por eso `total_records` nunca supera 20 y `total_pages` siempre es 1. Solución: devolver `total_records` en lugar de `len(articles)` y actualizar los tests de `tests/infrastructure/test_sqlite_article_repository.py`, que hoy asumen el comportamiento actual.

### 9. Orden por defecto arbitrario
Sin `sort_by`, la búsqueda ordena por `id DESC`. Como los IDs son UUID aleatorios, el orden es efectivamente aleatorio, aunque estable.

### 10. Validación de edad aproximada
`BirthDate` calcula la edad restando solo los años. Alguien que cumple 18 más adelante en el año actual ya se considera mayor de edad.

### 11. Email duplicado en condición de carrera
El registro verifica el email antes de insertar. Si dos registros simultáneos pasan esa verificación, el `UNIQUE` de la base de datos lanza `sqlite3.IntegrityError`, que termina en `500` en vez de `400`.

### 12. Formatos de error inconsistentes
Conviven `{"detail": ...}` y `{"error", "message"}`. Ver [errors-and-validation.md](errors-and-validation.md#resumen-de-formatos-de-error).

### 13. `price` cambia de forma entre endpoints
En `/articles/search`, `price` es un número; en los demás endpoints es `{amount, currency}`.

### 14. `GET /orders/{id}` inexistente devuelve 400
Un pedido que no existe responde `400` en lugar de `404`, porque el caso de uso lanza `DomainException`.

## Pagos con Stripe

### 15. COP tratado como moneda sin decimales
`StripePaymentGateway` envía los montos en COP sin multiplicar por 100. Hay que confirmar contra la lista de monedas de cero decimales de Stripe: si COP no está en ella, los cobros saldrían 100 veces menores.

## Mantenimiento

### 16. Advertencia de Python 3.12 con fechas en SQLite
`SqliteUserRepository` guarda un `date` directamente y Python 3.12 lo marca como obsoleto. Basta con guardar `birth_date.isoformat()`.

### 17. Credenciales de RustFS fijas en el compose
`admin`/`password123` están escritas en el `docker-compose.yml` y el bucket es de lectura pública. Es válido para desarrollo, pero no para producción.

### 18. `app/main.py` sin uso
Es un archivo de ejemplo (`Hello, World!`); el punto de entrada real es `app/infrastructure/api/main.py`.
