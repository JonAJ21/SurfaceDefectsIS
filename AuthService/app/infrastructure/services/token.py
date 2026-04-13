from datetime import timedelta
from uuid import uuid4

from authx import AuthX, AuthXConfig, RequestToken

from domain.exceptions.auth import AuthenticationException
from domain.services.token import BaseTokenService
from core.config.settings import settings

class JSONWebTokenService(BaseTokenService):
    def __init__(self):
        self.config = AuthXConfig(
            JWT_PRIVATE_KEY=settings.jwt_private_key,
            JWT_PUBLIC_KEY=settings.jwt_public_key,
            JWT_ALGORITHM=settings.jwt_algorithm,
            JWT_ACCESS_TOKEN_EXPIRES=timedelta(
                minutes=settings.access_token_expire_minutes
            ),
            JWT_REFRESH_TOKEN_EXPIRES=timedelta(
                days=settings.refresh_token_expire_days
            ),
            JWT_TOKEN_LOCATION=["headers"],
            JWT_HEADER_NAME="Authorization",
            JWT_HEADER_TYPE="Bearer",
        )
        self.authx = AuthX(config=self.config)
    
    def create_access_token(
        self,
        user_oid: str,
        session_oid: str,
        permission_codes: list[str],
        is_verified: bool
    ) -> tuple[str, str]:
        oid = str(uuid4())
        
        return oid, self.authx.create_access_token(
            uid=session_oid,
            scopes=permission_codes,
            data = {
                "user_oid": user_oid,
                "token_oid": oid,
                "is_verified": is_verified,
            }
        )
        
    def create_refresh_token(
        self,
        user_oid: str,
        session_oid: str,
        permission_codes: list[str]
    ) -> tuple[str, str]:
        oid = str(uuid4())
        return oid, self.authx.create_refresh_token(
            uid=session_oid,
            scopes=permission_codes,
            data = {
                "user_oid": user_oid,
                "token_oid": oid
            }
        )
    
    def verify_access_token(self, token: str) -> dict:
        request_token = RequestToken(
            token=token,
            type="access",
            location="headers"
        )
        try:
            token_payload = self.authx.verify_token(
                token=request_token,
                verify_type=True
            )
        except Exception:
            raise AuthenticationException()
        
        return token_payload.model_dump()
    
    def verify_refresh_token(self, token: str) -> dict:
        request_token = RequestToken(
            token=token,
            type="refresh",
            location="headers"
        )
        try:
            token_payload = self.authx.verify_token(
                token=request_token,
                verify_type=True
            )
        except Exception:
            raise AuthenticationException()
        
        return token_payload.model_dump()
    

