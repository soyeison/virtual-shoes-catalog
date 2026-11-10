# Tests

Los tests usan **pytest** y siguen la misma división en capas que el código. Hoy hay **63 tests** y la cobertura de `app/` es de alrededor del **60 %**.

```
tests/
├── domain/           # 34 tests — agregados y value objects, sin dependencias
├── application/      # 13 tests — casos de uso con repositorios simulados (MagicMock)
└── infrastructure/   # 16 tests — repositorios contra SQLite en memoria
```

## Ejecutar

Desde `virtual-catalog-api/`:

```bash
pytest -v                                   # todos
pytest tests/domain                         # una capa
pytest tests/domain/test_cart.py            # un archivo
pytest -k checkout                          # por nombre
pytest --cov=app --cov-report=term-missing  # con cobertura (pytest-cov)
```

En Docker:

```bash
docker compose exec api pytest -v
```

Los tests **no necesitan** `.env`, RustFS ni la base de datos real: no importan `main.py` ni `config.py`.

## Cómo están construidos

### Dominio (`tests/domain/`)

Prueban las reglas de negocio instanciando directamente agregados y value objects. Son los más rápidos y no usan dobles de prueba, salvo el `ArticleStockChecker` que necesita el carrito:

```python
@pytest.fixture
def stock_checker_mock():
    checker = MagicMock(spec=ArticleStockChecker)
    checker.has_sufficient_stock.return_value = True
    return checker

def test_add_item_enforces_maximum_business_limit(empty_cart, stock_checker_mock):
    empty_cart.add_item("art-1", 10, stock_checker_mock)
    with pytest.raises(DomainException, match="Cannot add more than 10 units"):
        empty_cart.add_item("art-1", 1, stock_checker_mock)
```

Cubren `Article`, `Cart`, `CartItem`, `Order`, `Payment`, `User`, `Price`, `Stock`, `Email`, `BirthDate`, `ShippingAddress` e `ImageURL`.

### Aplicación (`tests/application/`)

Prueban los casos de uso reemplazando los puertos por `unittest.mock.MagicMock`. Esto es posible porque los casos de uso dependen de interfaces y no de SQLite (ver [architecture.md](architecture.md)). Siguen el patrón **Arrange / Act / Assert**:

```python
def test_checkout_successful_flow(mocks):
    # Arrange
    mocks["article_repository"].find_by_id.return_value = article
    mocks["cart_repository"].find_by_user_id.return_value = cart
    use_case = CheckoutUseCase(**mocks)

    # Act
    order = use_case.execute(user_id)

    # Assert
    assert order.total_amount.amount == Decimal("300.00")
    mocks["order_repository"].save.assert_called_once_with(order)
```

Verifican tanto el resultado como las interacciones con los repositorios (`assert_called_once_with`, `assert_not_called`). Cubren registro, login, artículos, carrito, checkout y `StockCheckerService`.

### Infraestructura (`tests/infrastructure/`)

Prueban los repositorios SQLite contra una base de datos **en memoria** (`sqlite3.connect(":memory:")`), creada y destruida en cada test por un fixture:

```python
@pytest.fixture
def populated_repo():
    connection = sqlite3.connect(":memory:")
    repo = SqliteArticleRepository(connection)
    for article in test_articles:
        repo.create(article)
    yield repo
    connection.close()
```

Comprueban que guardar y leer conserve los datos (mappers, JSON, `Decimal`, fechas) y el comportamiento de la búsqueda: filtro por nombre, rango de precio, orden y paginación.

## Qué no está cubierto

| Módulo | Cobertura |
| --- | --- |
| `app/infrastructure/api/main.py` (endpoints, DI, manejadores de error) | 0 % |
| `app/infrastructure/gateways/` (Mock y Stripe) | 0 % |
| `app/infrastructure/security/` (bcrypt, JWT) | 0 % |
| `app/infrastructure/storage/s3_file_storage.py` | 0 % |
| `app/infrastructure/config.py` | 0 % |
| `ProcessPaymentUseCase` | sin tests propios |

Siguientes pasos sugeridos:
- Tests de endpoints con `fastapi.testclient.TestClient` y `app.dependency_overrides`, para reemplazar la conexión por una base de datos en memoria.
- Tests de `ProcessPaymentUseCase` con `MockPaymentGateway` (los tokens `tok_declined`, etc. ya están pensados para eso).
- Tests de `StripePaymentGateway` simulando `stripe.PaymentIntent.create`.

## Advertencia conocida

Al ejecutar los tests aparece un `DeprecationWarning` de Python 3.12: *"The default date adapter is deprecated"*. Se produce porque `SqliteUserRepository` guarda un objeto `date` directamente. Se corrige guardando `birth_date.isoformat()` en `UserMapper.to_persistence`.
