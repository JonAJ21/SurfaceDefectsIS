from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Конфигурация сервиса детекции"""
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    redis_stream: str = Field(default="defect:detection", alias="REDIS_STREAM")
    consumer_group: str = Field(default="detectors", alias="CONSUMER_GROUP")
    consumer_name: str = Field(default="detector-1", alias="CONSUMER_NAME")
    
    # Сервисы
    auth_service_url: str = Field(default="http://localhost:8001", alias="AUTH_SERVICE_URL")
    defects_service_url: str = Field(default="http://localhost:8002", alias="DEFECTS_SERVICE_URL")
    minio_url: str = Field(default="http://localhost:9000", alias="MINIO_URL")
    
    # Авторизация сервиса
    service_name: str = Field(default="detection_service", alias="SERVICE_NAME")
    service_secret: str = Field(required=True, alias="SERVICE_SECRET")
    
    # Модель YOLO
    model_path: str = Field(default="yolov8n.pt", alias="MODEL_PATH")
    confidence_threshold: float = Field(default=0.7, alias="CONFIDENCE_THRESHOLD")
    img_size: int = Field(default=448, alias="IMG_SIZE")
    
    # Обработка
    batch_size: int = Field(default=10, alias="BATCH_SIZE")
    block_ms: int = Field(default=5000, alias="BLOCK_MS")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()