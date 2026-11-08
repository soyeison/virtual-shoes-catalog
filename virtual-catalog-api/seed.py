import sqlite3
import urllib.request
import random
from app.infrastructure.config import settings
from app.infrastructure.storage.minio_file_storage import MinioFileStorage
from app.infrastructure.repositories.sqlite_article_repository import (
    SqliteArticleRepository,
)
from app.application.use_cases.create_article import CreateArticleUseCase


def download_placeholder_image():
    url = "https://picsum.photos/400"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        return response.read()


def run_seeder():
    print("Running seeder...")

    db_conn = sqlite3.connect(settings.database_path)
    repo = SqliteArticleRepository(db_conn)

    storage = MinioFileStorage(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket_name=settings.minio_bucket,
        public_url=settings.minio_public_url,
    )

    use_case = CreateArticleUseCase(article_repository=repo)

    products = [
        "Zapatos Skechers",
        "Zapatos Adidas",
        "Zapatos Nike",
        "Zapatos Puma",
        "Zapatos Reebook",
        "Zapatos New Balance",
        "Zapatos converse",
        "Zapatos Vans",
        "Zapatos Croydon",
        "Zapatos Timberland",
        "Zapatos Reebook 1.1",
        "Zapatos Nike 1.1",
        "Zapatos Adidas 1.1",
        "Zapatos Puma 1.1",
        "Zapatos Vans 1.1",
        "Zapatos Croydon 1.1",
        "Zapatos Timberland 1.1",
        "Zapatos Schechers 1.1",
        "Zapatos Adidas 1.2",
        "Zapatos Nike 1.2",
    ]

    for i, nombre in enumerate(products):
        print(f"Generating article {i+1}/20: {nombre}...")

        image_urls = []

        # 1. Procesar la imagen local de la carpeta 'static'
        local_image_path = f"static/zapato{i+1}.jpg.jpeg"
        try:
            with open(local_image_path, "rb") as f:
                local_img_bytes = f.read()

            url_local = storage.upload_image(
                file_name=f"producto_{i+1}_local.jpg",
                file_bytes=local_img_bytes,
                content_type="image/jpeg",
            )
            image_urls.append(url_local)
        except FileNotFoundError:
            print(
                f"  -> Advertencia: No se encontró {local_image_path}. Saltando imagen local."
            )

        # 2. Procesar la imagen de internet (placeholder)
        try:
            placeholder_img_bytes = download_placeholder_image()
            url_placeholder = storage.upload_image(
                file_name=f"producto_{i+1}_placeholder.jpg",
                file_bytes=placeholder_img_bytes,
                content_type="image/jpeg",
            )
            image_urls.append(url_placeholder)
        except Exception as e:
            print(f"  -> Error al obtener la imagen placeholder: {e}")

        precio = round(random.uniform(50000, 1500000), 2)
        stock = random.randint(5, 50)

        use_case.execute(
            name=nombre,
            description=f"Descripción detallada para {nombre}. Ideal para mejorar tu setup.",
            stock_qty=stock,
            price_amount=precio,
            price_currency="COP",
            image_urls=image_urls,
        )

    print("Base de datos y MinIO poblados con éxito")


if __name__ == "__main__":
    run_seeder()
