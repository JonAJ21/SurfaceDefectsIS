
from abc import ABC, abstractmethod


class BaseStreamService(ABC):
    @abstractmethod
    async def publish_defect(defect_id: str, media_paths: list[str]) -> None:
        ...