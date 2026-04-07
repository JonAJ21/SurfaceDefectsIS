
from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BasePhotosRepository(ABC):
    """Интерфейс репозитория для работы с фотографиями"""
    
    @abstractmethod
    async def upload(self, defect_id: str, filename: str, data: bytes, content_type: str) -> str:
        """Загружает фото и возвращает URL"""
        pass
    
    @abstractmethod
    async def get(self, photo_url: str) -> Optional[Tuple[bytes, str]]:
        """Получает фото по URL, возвращает (data, content_type) или None"""
        pass
    
    @abstractmethod
    async def delete(self, photo_url: str) -> None:
        """Удаляет одно фото по URL"""
        pass
    
    @abstractmethod
    async def delete_all(self, defect_id: str) -> None:
        """Удаляет все фото дефекта"""
        pass