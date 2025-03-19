from .service import S3Service
from app.conf import settings

s3_service = S3Service(
    access_key=settings.AWS_ACCESS_KEY_ID,
    secret_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint=settings.AWS_URL,
    bucket_name=settings.AWS_BUCKET_NAME
)

__all__ = [s3_service]
