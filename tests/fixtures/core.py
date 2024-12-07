import os
import tempfile

import pytest
from faker import Faker

from core.containers import get_container
from core.storages.s3 import MinioS3Storage


@pytest.fixture(scope="session")
def minio_client() -> MinioS3Storage:
    return MinioS3Storage(bucket_name="test-cinema-bucket")


@pytest.fixture
def minio_cleanup(minio_client):
    yield
    objects = minio_client.list_objects()
    for obj in objects:
        minio_client.delete_file(obj)


@pytest.fixture(scope="session")
def fake_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as fake_file:
        fake_file.write("Hello world!")
        fake_file_path = fake_file.name
    yield fake_file_path
    os.remove(fake_file_path)


@pytest.fixture(scope="session")
def faker():
    return Faker(locale="ru_RU")


@pytest.fixture(scope="session")
def container():
    return get_container()
