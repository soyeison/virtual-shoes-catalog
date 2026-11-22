from app.infrastructure.storage.s3_file_storage import S3FileStorage


def build_storage(**overrides):
    values = dict(
        endpoint_url="http://storage:9000",
        access_key="key",
        secret_key="secret",
        bucket_name="catalogo-images",
        region_name="eu-west-1",
    )
    values.update(overrides)
    return S3FileStorage(**values)


def test_uses_configured_region():
    storage = build_storage()

    assert storage.s3_client.meta.region_name == "eu-west-1"


def test_public_url_defaults_to_endpoint():
    storage = build_storage()

    assert storage.public_url == "http://storage:9000"


def test_public_url_can_differ_from_endpoint():
    storage = build_storage(public_url="http://localhost:9000")

    assert storage.public_url == "http://localhost:9000"
