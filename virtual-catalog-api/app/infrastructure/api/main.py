import sqlite3
from typing import List, Optional
from fastapi import (
    HTTPException,
    FastAPI,
    Request,
    status,
    Depends,
    UploadFile,
    File,
    Form,
    Query,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.domain.exceptions import DomainException
from app.infrastructure.config import settings
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.create_article import CreateArticleUseCase
from app.application.use_cases.get_article_by_id import GetArticleByIdUseCase
from app.application.use_cases.get_all_articles import GetAllArticlesUseCase
from app.application.use_cases.search_article_use_case import SearchArticleUseCase
from app.application.use_cases.get_cart import GetCartUseCase
from app.application.use_cases.add_item_to_cart import AddItemToCartUseCase
from app.application.use_cases.remove_item_from_cart import RemoveItemFromCartUseCase
from app.application.use_cases.change_item_quantity import ChangeItemQuantityUseCase
from app.application.use_cases.clear_cart import ClearCartUseCase
from app.application.use_cases.checkout import CheckoutUseCase
from app.application.use_cases.process_payment import ProcessPaymentUseCase
from app.application.ports.payment_gateway import PaymentGateway
from app.application.use_cases.get_order import GetOrderUseCase

from app.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from app.infrastructure.repositories.sqlite_article_repository import (
    SqliteArticleRepository,
)
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_generator import JwtTokenGenerator
from app.infrastructure.storage.minio_file_storage import MinioFileStorage
from app.infrastructure.repositories.sqlite_cart_repository import SqliteCartRepository
from app.infrastructure.repositories.sqlite_order_repository import (
    SqliteOrderRepository,
)
from app.infrastructure.gateways.mock_payment_gateway import MockPaymentGateway
from app.infrastructure.gateways.stripe_payment_gateway import StripePaymentGateway
from app.infrastructure.repositories.sqlite_payment_repository import (
    SqlitePaymentRepository,
)

app = FastAPI(title="Catálogo Virtual - Módulo de Registro")

origins = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite a estos dominios hacer peticiones
    allow_credentials=True,  # Permite el envío de cookies o tokens de autenticación
    allow_methods=[
        "*"
    ],  # Permite todos los verbos HTTP (GET, POST, PATCH, DELETE, OPTIONS)
    allow_headers=["*"],  # Permite todas las cabeceras personalizadas
)


class AddressSchema(BaseModel):
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    zip_code: str
    country: str = Field(..., min_length=1)


class UserRegisterRequest(BaseModel):
    first_name: str
    last_name: str
    birth_date: str
    email: str
    password: str = Field(..., min_length=6)
    shipping_address: AddressSchema


class UserLoginRequest(BaseModel):
    email: str
    password: str


class AddCartItemRequest(BaseModel):
    article_id: str = Field(..., description="The unique identifier of the article")
    quantity: int = Field(..., gt=0, description="Quantity to add (must be at least 1)")


class ChangeQuantityRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="The new exact quantity for the item")


class OrderItemResponse(BaseModel):
    article_id: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    status: str
    total_amount: float
    items: List[OrderItemResponse]


class ProcessPaymentRequest(BaseModel):
    order_id: str = Field(..., description="The ID of the order to pay")
    payment_token: str = Field(
        ..., description="The card token from the frontend interaction"
    )


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    amount: float
    currency: str
    status: str


# ---  Inyección de Dependencias (El núcleo de FastAPI) ---
def get_db_connection():
    conn = sqlite3.connect(settings.database_path, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def get_user_repository(
    db: sqlite3.Connection = Depends(get_db_connection),
) -> SqliteUserRepository:
    return SqliteUserRepository(db)


def get_article_repository(
    db: sqlite3.Connection = Depends(get_db_connection),
) -> SqliteArticleRepository:
    return SqliteArticleRepository(db)


def get_password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


def get_token_generator() -> JwtTokenGenerator:
    return JwtTokenGenerator(
        secret_key="supersecretkey", algorithm="HS256", expiration_minutes=60
    )


def get_register_use_case(
    user_repo: SqliteUserRepository = Depends(get_user_repository),
    hasher: BcryptPasswordHasher = Depends(get_password_hasher),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repository=user_repo, hasher=hasher)


def get_login_use_case(
    user_repo: SqliteUserRepository = Depends(get_user_repository),
    hasher: BcryptPasswordHasher = Depends(get_password_hasher),
    token_generator: JwtTokenGenerator = Depends(get_token_generator),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repository=user_repo, hasher=hasher, token_generator=token_generator
    )


def get_create_article_use_case(
    article_repo: SqliteArticleRepository = Depends(get_article_repository),
) -> CreateArticleUseCase:
    return CreateArticleUseCase(article_repository=article_repo)


def get_article_by_id_use_case(
    repo: SqliteArticleRepository = Depends(get_article_repository),
) -> GetArticleByIdUseCase:
    return GetArticleByIdUseCase(article_repository=repo)


def get_all_articles_use_case(
    repo: SqliteArticleRepository = Depends(get_article_repository),
) -> GetAllArticlesUseCase:
    return GetAllArticlesUseCase(article_repository=repo)


def get_search_articles_use_case(
    repo: SqliteArticleRepository = Depends(get_article_repository),
) -> SearchArticleUseCase:
    return SearchArticleUseCase(article_repository=repo)


def get_file_storage() -> MinioFileStorage:
    return MinioFileStorage(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket_name=settings.minio_bucket,
        public_url=settings.minio_public_url,
    )


def get_cart_repository(db=Depends(get_db_connection)) -> SqliteCartRepository:
    return SqliteCartRepository(db)


def get_get_cart_use_case(
    cart_repo: SqliteCartRepository = Depends(get_cart_repository),
    article_repo: SqliteArticleRepository = Depends(get_article_repository),
) -> GetCartUseCase:
    return GetCartUseCase(cart_repo=cart_repo, article_repo=article_repo)


def get_add_item_to_cart_use_case(
    cart_repo: SqliteCartRepository = Depends(get_cart_repository),
    article_repo: SqliteArticleRepository = Depends(get_article_repository),
) -> AddItemToCartUseCase:
    return AddItemToCartUseCase(cart_repo=cart_repo, article_repo=article_repo)


def get_remove_item_from_cart_use_case(
    cart_repo: SqliteCartRepository = Depends(get_cart_repository),
) -> RemoveItemFromCartUseCase:
    return RemoveItemFromCartUseCase(cart_repository=cart_repo)


def get_change_item_quantity_use_case(
    cart_repo: SqliteCartRepository = Depends(get_cart_repository),
    article_repo: SqliteArticleRepository = Depends(get_article_repository),
) -> ChangeItemQuantityUseCase:
    return ChangeItemQuantityUseCase(
        cart_repository=cart_repo, article_repository=article_repo
    )


def get_clear_cart_use_case(
    cart_repo: SqliteCartRepository = Depends(get_cart_repository),
) -> ClearCartUseCase:
    return ClearCartUseCase(cart_repository=cart_repo)


def get_order_repository(db=Depends(get_db_connection)) -> SqliteOrderRepository:
    return SqliteOrderRepository(db)


def get_checkout_use_case(
    cart_repository: SqliteCartRepository = Depends(get_cart_repository),
    article_repository: SqliteArticleRepository = Depends(get_article_repository),
    order_repository: SqliteOrderRepository = Depends(get_order_repository),
) -> CheckoutUseCase:
    return CheckoutUseCase(
        cart_repository=cart_repository,
        article_repository=article_repository,
        order_repository=order_repository,
    )


def get_payment_repository(db=Depends(get_db_connection)) -> SqlitePaymentRepository:
    return SqlitePaymentRepository(db)


def get_payment_gateway() -> PaymentGateway:
    provider = settings.payment_gateway_provider.lower()

    if provider == "stripe":
        stripe_secret_key = settings.stripe_secret_key
        if not stripe_secret_key:
            raise ValueError(
                "STRIPE_SECRET_KEY variable is missing for Stripe provider."
            )

        return StripePaymentGateway(api_key=stripe_secret_key)

    elif provider == "mock":
        return MockPaymentGateway()

    else:
        raise ValueError(f"Unsupported payment provider: {provider}")


def get_process_payment_use_case(
    payment_repository: SqlitePaymentRepository = Depends(get_payment_repository),
    payment_gateway: PaymentGateway = Depends(get_payment_gateway),
    order_repository: SqliteOrderRepository = Depends(get_order_repository),
) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(
        payment_repository=payment_repository,
        payment_gateway=payment_gateway,
        order_repository=order_repository,
    )


def get_get_order_use_case(
    order_repository: SqliteOrderRepository = Depends(get_order_repository),
) -> GetOrderUseCase:
    return GetOrderUseCase(order_repository=order_repository)


# --- Manejadores de Excepciones ---
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "DomainValidationError", "message": str(exc)},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "ApplicationError", "message": str(exc)},
    )


# --- Endpoints ---
@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    request_data: UserRegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    new_user = use_case.execute(
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        birth_date=request_data.birth_date,
        raw_email=request_data.email,
        password=request_data.password,
        city=request_data.shipping_address.city,
        street=request_data.shipping_address.street,
        country=request_data.shipping_address.country,
        postal_code=request_data.shipping_address.zip_code,
    )

    return {
        "status": "success",
        "data": {
            "user_id": new_user,
        },
    }


@app.post("/api/v1/auth/login", status_code=status.HTTP_200_OK)
async def login_user(
    request_data: UserLoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
):
    token = use_case.execute(
        raw_email=request_data.email,
        plain_password=request_data.password,
    )

    return {
        "status": "success",
        "data": {
            "token": token,
        },
    }


@app.post("/api/v1/articles", status_code=status.HTTP_201_CREATED)
async def create_article(
    name: str = Form(..., min_length=1),
    description: str = Form(...),
    stock: int = Form(..., ge=0),
    price_amount: float = Form(..., gt=0),
    price_currency: str = Form(default="COP", min_length=3, max_length=3),
    images: List[UploadFile] = File(default=[]),
    use_case: CreateArticleUseCase = Depends(get_create_article_use_case),
    storage: MinioFileStorage = Depends(get_file_storage),
):
    if len(images) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden subir más de 5 imágenes por artículo.",
        )

    uploaded_urls = []
    for image in images:
        file_bytes = await image.read()

        if not image.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo de imagen no tiene un nombre válido.",
            )

        if not image.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo de imagen no tiene un tipo de contenido válido.",
            )

        url = storage.upload_image(
            file_name=image.filename,
            file_bytes=file_bytes,
            content_type=image.content_type,
        )
        uploaded_urls.append(url)

    new_article = use_case.execute(
        name=name,
        description=description,
        stock_qty=stock,
        price_amount=price_amount,
        price_currency=price_currency,
        image_urls=uploaded_urls,
    )

    return {
        "status": "success",
        "data": {
            "id": new_article.id,
            "name": new_article.name,
            "stock": new_article.get_stock().value,
            "price": {
                "amount": float(new_article.get_price().amount),
                "currency": new_article.get_price().currency,
            },
            "image_urls": [img.url for img in new_article.get_image_urls()],
        },
    }


@app.get("/api/v1/articles", status_code=status.HTTP_200_OK)
async def list_articles(
    use_case: GetAllArticlesUseCase = Depends(get_all_articles_use_case),
):
    articles = use_case.execute()

    # Transformamos la lista de Agregados a una lista de diccionarios
    response_data = []
    for article in articles:
        response_data.append(
            {
                "id": article.id,
                "name": article.name,
                "stock": article.get_stock().value,
                "price": {
                    "amount": float(article.get_price().amount),
                    "currency": article.get_price().currency,
                },
                "image_urls": [img.url for img in article.get_image_urls()],
            }
        )

    return {"status": "success", "results": len(response_data), "data": response_data}


@app.get("/api/v1/article/{article_id}", status_code=status.HTTP_200_OK)
async def get_article_details(
    article_id: str,
    use_case: GetArticleByIdUseCase = Depends(get_article_by_id_use_case),
):
    article = use_case.execute(article_id)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo con ID '{article_id}' no encontrado.",
        )

    return {
        "status": "success",
        "data": {
            "id": article.id,
            "name": article.name,
            "description": article.description,
            "stock": article.get_stock().value,
            "price": {
                "amount": float(article.get_price().amount),
                "currency": article.get_price().currency,
            },
            "image_urls": [img.url for img in article.get_image_urls()],
        },
    }


@app.get("/api/v1/articles/search", status_code=status.HTTP_200_OK)
async def search_catalog(
    name: Optional[str] = Query(None, description="Buscar por fragmento del nombre"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo"),
    sort_by: Optional[str] = Query(None, description="Ej: price_asc, price_desc"),
    page: int = Query(1, ge=1, description="Número de página"),
    use_case: SearchArticleUseCase = Depends(get_search_articles_use_case),
):
    result = use_case.execute(
        name=name, min_price=min_price, max_price=max_price, sort_by=sort_by, page=page
    )

    response_data = [
        {
            "id": art.id,
            "name": art.name,
            "price": float(art.get_price().amount),
            "image_urls": [img.url for img in art.get_image_urls()],
        }
        for art in result.items
    ]

    return {
        "status": "success",
        "pagination": {
            "current_page": result.current_page,
            "total_pages": result.total_pages,
            "total_records": result.total_records,
            "results_on_this_page": len(response_data),
        },
        "data": response_data,
    }


@app.get("/api/v1/cart/{user_id}", status_code=status.HTTP_200_OK)
async def get_cart(
    user_id: str, use_case: GetCartUseCase = Depends(get_get_cart_use_case)
):
    cart_dto = use_case.execute(user_id)

    return {
        "status": "success",
        "data": {
            "user_id": cart_dto.user_id,
            "total_amount": cart_dto.total_amount,
            "items": [
                {
                    "article_id": item.article_id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                    "image_url": item.image_url,
                }
                for item in cart_dto.items
            ],
        },
    }


@app.post("/api/v1/cart/{user_id}/items", status_code=status.HTTP_200_OK)
async def add_item_to_cart(
    user_id: str,
    request_data: AddCartItemRequest,
    use_case: AddItemToCartUseCase = Depends(get_add_item_to_cart_use_case),
):
    updated_cart = use_case.execute(
        user_id=user_id,
        article_id=request_data.article_id,
        quantity=request_data.quantity,
    )

    return {
        "status": "success",
        "message": "Item added to cart successfully",
        "data": {
            "user_id": updated_cart.user_id,
            "total_items": len(updated_cart.get_items()),
        },
    }


@app.delete("/api/v1/cart/{user_id}/items/{article_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_cart(
    user_id: str,
    article_id: str,
    use_case: RemoveItemFromCartUseCase = Depends(get_remove_item_from_cart_use_case),
):
    updated_cart = use_case.execute(user_id=user_id, article_id=article_id)

    return {
        "status": "success",
        "message": "Item successfully removed from cart",
        "data": {
            "user_id": updated_cart.user_id,
            "total_items": len(updated_cart.get_items()),
        },
    }


@app.patch("/api/v1/cart/{user_id}/items/{article_id}", status_code=status.HTTP_200_OK)
async def change_item_quantity(
    user_id: str,
    article_id: str,
    request_data: ChangeQuantityRequest,
    use_case: ChangeItemQuantityUseCase = Depends(get_change_item_quantity_use_case),
):
    updated_cart = use_case.execute(
        user_id=user_id, article_id=article_id, new_quantity=request_data.quantity
    )

    return {
        "status": "success",
        "message": "Item quantity updated successfully",
        "data": {
            "user_id": updated_cart.user_id,
            "total_items": len(updated_cart.get_items()),
        },
    }


@app.delete("/api/v1/cart/{user_id}/items", status_code=status.HTTP_200_OK)
async def clear_cart(
    user_id: str, use_case: ClearCartUseCase = Depends(get_clear_cart_use_case)
):
    cleared_cart = use_case.execute(user_id=user_id)

    return {
        "status": "success",
        "message": "Cart cleared successfully",
        "data": {"user_id": cleared_cart.user_id, "total_items": 0},
    }


@app.post("/api/v1/checkout/{user_id}", status_code=status.HTTP_201_CREATED)
async def process_checkout(
    user_id: str, use_case: CheckoutUseCase = Depends(get_checkout_use_case)
):
    order = use_case.execute(user_id=user_id)

    items_response = [
        OrderItemResponse(
            article_id=item.article_id,
            quantity=item.quantity,
            unit_price=float(item.unit_price.amount),
            subtotal=float(item.subtotal),
        )
        for item in order.get_items()
    ]

    response_data = OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        total_amount=float(order.total_amount.amount),
        items=items_response,
    )

    # 3. Return Standard API Format
    return {
        "status": "success",
        "message": "Checkout completed successfully",
        "data": response_data,
    }


@app.get("/api/v1/orders/{order_id}", status_code=status.HTTP_200_OK)
async def get_order_summary(
    order_id: str, use_case: GetOrderUseCase = Depends(get_get_order_use_case)
):
    order = use_case.execute(order_id=order_id)

    items_response = [
        OrderItemResponse(
            article_id=item.article_id,
            quantity=item.quantity,
            unit_price=float(item.unit_price.amount),
            subtotal=float(item.subtotal),
        )
        for item in order.get_items()
    ]

    response_data = OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        total_amount=float(order.total_amount.amount),
        items=items_response,
    )

    return {"status": "success", "data": response_data}


@app.post("/api/v1/process-payment", status_code=status.HTTP_200_OK)
async def process_payment(
    request_data: ProcessPaymentRequest,
    use_case: ProcessPaymentUseCase = Depends(get_process_payment_use_case),
):
    try:
        payment = use_case.execute(
            order_id=request_data.order_id, payment_token=request_data.payment_token
        )

        return {
            "status": "success",
            "message": "Payment processed and captured successfully.",
            "data": PaymentResponse(
                payment_id=payment.id,
                order_id=payment.order_id,
                amount=float(payment.amount.amount),
                currency=payment.amount.currency,
                status=payment.status.value,
            ),
        }
    except DomainException as e:
        # Si el pago falla por fondos o tarjeta declinada, capturamos la excepción de negocio
        # y la transformamos en un código HTTP 400 Bad Request
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
