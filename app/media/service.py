from random import randint
from typing import BinaryIO
from minio import Minio


class S3Service:
    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket_name: str):
        self.client = Minio(endpoint, access_key=access_key,
                            secret_key=secret_key)
        self.url = endpoint
        self.bucket_name = bucket_name

    def upload_file(self, file: BinaryIO, filename: str):
        try:
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)

            key = f"{filename}-{randint(1, 1000)}"

            self.client.put_object(self.bucket_name, key, file, size, metadata={
                                   'x-amz-acl': 'public-read'})

            return f"https://{self.bucket_name}.{self.url}/{key}"
        except Exception as e:
            print(e)
            return None
