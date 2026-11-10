import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from app.application.ports.file_storage import FileStoragePort


class S3FileStorage(FileStoragePort):
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        public_url: Optional[str] = None,
    ):
        # Configuramos boto3 para que apunte a nuestro localhost en vez de a los servidores de Amazon
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",  # Required inclusive for local development
        )
        self.bucket_name = bucket_name
        # URL base para el navegador; puede diferir del endpoint interno (ej. dentro de Docker)
        self.public_url = public_url or endpoint_url

    def upload_image(self, file_name: str, file_bytes: bytes, content_type: str) -> str:
        unique_file_name = f"{uuid.uuid4().hex[:8]}_{file_name}"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_file_name,
                Body=file_bytes,
                ContentType=content_type,
            )

            return f"{self.public_url}/{self.bucket_name}/{unique_file_name}"

        except ClientError as e:
            # Aquí podrías lanzar una excepción personalizada de tu dominio de infraestructura
            raise RuntimeError(f"Error al subir la imagen al almacenamiento S3: {str(e)}")
