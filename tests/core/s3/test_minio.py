import os


class TestMinio:
    async def test_upload_file(
        self, minio_client, fake_file, faker, minio_cleanup
    ):
        file_name = faker.file_name()
        minio_client.upload_file(file_path=fake_file, object_name=file_name)
        response = minio_client.get_object(object_name=file_name)
        assert response.status == 200

    async def test_download_file(
        self, minio_client, fake_file, faker, minio_cleanup, tmp_path
    ):
        file_name = faker.file_name()
        minio_client.upload_file(file_path=fake_file, object_name=file_name)

        download_path = tmp_path / file_name
        response = minio_client.download_file(
            object_name=file_name, file_path=str(download_path)
        )

        assert response.status == 200
        assert os.path.exists(download_path)
        assert open(fake_file).read() == open(download_path).read()

        os.remove(download_path)

    async def test_delete_file(
        self, minio_client, fake_file, faker, minio_cleanup
    ):
        file_name = faker.file_name()
        minio_client.upload_file(file_path=fake_file, object_name=file_name)
        response = minio_client.delete_file(file_name)
        assert response.status == 200
        assert minio_client.get_object(object_name=file_name).status == 404
