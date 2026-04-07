import base64

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # SQLAlchemy
    
    pbf_file_path: str = Field(
        "/app/osm/small.osm.pbf",
        env="DEFECTS_PBF_FILE_PATH",
        alias="defects_pbf_file_path",
    )
    
    postgres_port: int = 5432
    
    postgres_host: str = Field(
        "defects-postgres",
        env="DEFECTS_POSTGRES_HOST",
        alias="defects_postgres_host",
    )
    
    postgres_user: str = Field(
        "user",
        env="DEFECTS_POSTGRES_USER",
        alias="defects_postgres_user",
    )
    
    postgres_password: str = Field(
        "password",
        env="DEFECTS_POSTGRES_PASSWORD",
        alias="defects_postgres_password",
    )
    
    postgres_name: str = Field(
        "defects-postgres",
        env="DEFECTS_POSTGRES_NAME",
        alias="defects_postgres_name",
    )
    
    
    postgres_sync_connection: str = Field(
        "postgresql+psycopg2://user:password@defects-postgres:5432/defects-postgres",
        env="DEFECTS_POSTGRES_SYNC_CONNECTION",
        alias="defects_postgres_sync_connection",
    )
    
    postgres_async_connection: str = Field(
        "postgresql+asyncpg://user:password@defects-postgres:5432/defects-postgres",
        env="DEFECTS_POSTGRES_ASYNC_CONNECTION",
        alias="defects_postgres_async_connection",
    )
    
    sqlalchemy_echo: bool = Field(
        False,
        env="SQLALCHEMY_ECHO",
        alias="sqlalchemy_echo",
    )
    
    # JWT
    
    
    jwt_algorithm: str = Field(
        "RS256",
        env="JWT_ALGORITHM",
        alias="jwt_algorithm",
    )
    
    jwt_public_key_base64: str = Field(
        "",
        env="JWT_PUBLIC_KEY_BASE64",
        alias="jwt_public_key_base64",
    )
    
    @property
    def jwt_public_key(self) -> str:
        if not self.jwt_public_key_base64:
            raise ValueError("JWT_PUBLIC_KEY_BASE64 is not set")
        return base64.b64decode(self.jwt_public_key_base64).decode("utf-8")
    
    # Redis
    
    redis_db: int = Field(
        0,
        env="REDIS_DB",
        alias="redis_db",
    )
    
    redis_host: str = Field(
        "localhost",
        env="DEFECTS_REDIS_HOST",
        alias="defects_redis_host",
    )
    
    redis_port: int = Field(
        6379,
        env="DEFECTS_REDIS_PORT",
        alias="defects_redis_port",
    )
    
    redis_password: str = Field(
        "",
        env="REDIS_PASSWORD",
        alias="redis_password",
    )
    
    # Cache
    
    role_cache_ttl_minutes: int = Field(
        5,
        env="ROLE_CACHE_TTL_MINUTES",
        alias="role_cache_ttl_minutes",
    )
    
    # Minio
    
    minio_api_port: int = Field(
        9000,
        env="DEFECTS_MINIO_API_PORT",
        alias="defects_minio_api_port",
    )
    
    minio_root_user: str = Field(
        "minio",
        env="DEFECTS_MINIO_ROOT_USER",
        alias="defects_minio_root_user",
    )
    
    minio_root_password: str = Field(
        "minio",
        env="DEFECTS_MINIO_ROOT_PASSWORD",
        alias="defects_minio_root_password",
    )
    
    minio_bucket: str = Field(
        "defects",
        env="DEFECTS_MINIO_BUCKET",
        alias="defects_minio_bucket",
    )
    minio_secure: bool = Field(
        False,
        env="DEFECTS_MINIO_SECURE",
        alias="defects_minio_secure",
    )

    @property
    def minio_endpoint(self) -> str:
        """MinIO API endpoint"""
        return f"defects-minio:{self.minio_api_port}"
    
    @property
    def minio_external_endpoint(self) -> str:
        """Внешний endpoint для доступа к файлам (для URL)"""
        protocol = "https" if self.minio_secure else "http"
        return f"{protocol}://localhost:{self.minio_api_port}"
    
    max_distance_meters: int = Field(
        15,
        env="MAX_DISTANCE_METERS",
        alias="max_distance_meters",
    )
    
    duplicate_time_window_minutes: int = Field(
        5,
        env="DUPLICATE_TIME_WINDOW_MINUTES",
        alias="duplicate_time_window_minutes",
    )
    
    duplicate_distance_tolerance_meters: float = Field(
        5.0,
        env="DUPLICATE_DISTANCE_TOLERANCE_METERS",
        alias="duplicate_distance_tolerance_meters",
    )

settings = Settings()