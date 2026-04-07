
import io
from typing import Optional, Tuple
import uuid

from minio import Minio, S3Error

from domain.repositories.photo import BasePhotosRepository
from core.config.settings import settings

class MinioPhotosRepository(BasePhotosRepository):
    """Реализация репозитория фото через MinIO"""
    
    def __init__(self):
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_secure,
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(settings.minio_bucket):
                self.client.make_bucket(settings.minio_bucket)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")
    
    def _extract_object_name(self, photo_url: str) -> Optional[str]:
        """Извлекает имя объекта из URL"""
        prefix = f"{settings.minio_external_endpoint}/{settings.minio_bucket}/"
        if photo_url.startswith(prefix):
            return photo_url[len(prefix):]
        return None
    
    async def upload(self, defect_id: str, filename: str, data: bytes, content_type: str) -> str:
        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        object_name = f"defects/{defect_id}/{uuid.uuid4()}.{ext}"
        
        self.client.put_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type
        )
        
        return f"{settings.minio_external_endpoint}/{settings.minio_bucket}/{object_name}"
    
    async def get(self, photo_url: str) -> Optional[Tuple[bytes, str]]:
        """Получает фото по URL"""
        
        object_name = self._extract_object_name(photo_url)
        if not object_name:
            return None
        
        try:
            response = self.client.get_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name
            )
            
            data = response.read()
            content_type = response.getheader('Content-Type', 'application/octet-stream')
            response.close()
            response.release_conn()
            
            return (data, content_type)
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            raise Exception(f"Failed to get photo: {e}")
    
    async def delete(self, photo_url: str) -> None:
        """Удаляет одно фото по URL"""
        
        object_name = self._extract_object_name(photo_url)
        if not object_name:
            return
        
        try:
            self.client.remove_object(settings.minio_bucket, object_name)
        except S3Error as e:
            print(f"Failed to delete photo {photo_url}: {e}")
    
    async def delete_all(self, defect_id: str) -> None:
        """Удаляет все фото дефекта"""
        
        try:
            objects = self.client.list_objects(
                settings.minio_bucket,
                prefix=f"defects/{defect_id}/",
                recursive=True
            )
            
            for obj in objects:
                self.client.remove_object(settings.minio_bucket, obj.object_name)
        except S3Error as e:
            print(f"Failed to delete photos for defect {defect_id}: {e}")