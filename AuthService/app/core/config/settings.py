import base64

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # SQLAlchemy
    
    postgres_sync_connection: str = Field(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
        env="POSTGRES_SYNC_CONNECTION",
        alias="postgres_sync_connection",
    )
    
    postgres_async_connection: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        env="POSTGRES_ASYNC_CONNECTION",
        alias="postgres_async_connection",
    )
    
    sqlalchemy_echo: bool = Field(
        False,
        env="SQLALCHEMY_ECHO",
        alias="sqlalchemy_echo",
    )
    
    # JWT
    
    jwt_secret_key: str = Field(
        "secret",
        env="JWT_SECRET_KEY",
        alias="jwt_secret_key",
    )
    
    jwt_algorithm: str = Field(
        "HS256",
        env="JWT_ALGORITHM",
        alias="jwt_algorithm",
    )
    
    jwt_private_key_base64: str = Field(
        "",
        env="JWT_PRIVATE_KEY_BASE64",
        alias="jwt_private_key_base64",
    )
    
    jwt_public_key_base64: str = Field(
        "",
        env="JWT_PUBLIC_KEY_BASE64",
        alias="jwt_public_key_base64",
    )
    
    @property
    def jwt_private_key(self) -> str:
        if not self.jwt_private_key_base64:
            raise ValueError("JWT_PRIVATE_KEY_BASE64 is not set")
        return base64.b64decode(self.jwt_private_key_base64).decode("utf-8")
    
    @property
    def jwt_public_key(self) -> str:
        if not self.jwt_public_key_base64:
            raise ValueError("JWT_PUBLIC_KEY_BASE64 is not set")
        return base64.b64decode(self.jwt_public_key_base64).decode("utf-8")
    
    access_token_expire_minutes: int = Field(
        30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        alias="jwt_access_token_expire_minutes",
    )
    
    refresh_token_expire_days: int = Field(
        7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
        alias="jwt_refresh_token_expire_days",
    )
    
    refresh_threshold_minutes: int = Field(
        5,
        env="JWT_REFRESH_THRESHOLD_MINUTES",
        alias="jwt_refresh_threshold_minutes",
    )
    
    max_refresh_token_per_user: int = Field(
        5,
        env="MAX_REFRESH_TOKEN_PER_USER",
        alias="max_refresh_token_PER_user",
    )
    
    # Redis
    
    redis_db: int = Field(
        0,
        env="REDIS_DB",
        alias="redis_db",
    )
    
    redis_host: str = Field(
        "localhost",
        env="REDIS_HOST",
        alias="redis_host",
    )
    
    redis_port: int = Field(
        6379,
        env="REDIS_PORT",
        alias="redis_port",
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

    # Email
    
    smtp_server: str = Field(
        "smtp.gmail.com",
        env="SMTP_SERVER",
        alias="smtp_server",
    )
    
    smtp_port: int = Field(
        587,
        env="SMTP_PORT",
        alias="smtp_port",
    )
    
    
    email_address: str = Field(
        "",
        env="EMAIL_ADDRESS",
        alias="email_address",
    )
    
    email_password: str = Field(
        "",
        env="EMAIL_PASSWORD",
        alias="email_password",
    )
    app_password: str = Field(
        "String123@",
        env="APP_PASSWORD",
        alias="app_password",
    )
    
    verify_url: str = Field(
        "http://localhost:8001/v1/users/me/verify",
        env="VERIFY_URL",
        alias="verify_url",
    )

settings = Settings()