from uuid import uuid4

from authx import AuthX, AuthXConfig, RequestToken

from domain.services.token import BaseTokenService
from core.config.settings import settings

class JSONWebTokenService(BaseTokenService):
    def __init__(self):
        self.config = AuthXConfig(
            JWT_PUBLIC_KEY=settings.jwt_public_key,
            JWT_ALGORITHM=settings.jwt_algorithm,
            JWT_TOKEN_LOCATION=["headers"],
            JWT_HEADER_NAME="Authorization",
            JWT_HEADER_TYPE="Bearer",
        )
        self.authx = AuthX(config=self.config)
    
    def verify_access_token(self, token: str) -> dict:
        request_token = RequestToken(
            token=token,
            type="access",
            location="headers"
        )
        token_payload = self.authx.verify_token(
            token=request_token,
            verify_type=True
        )
        
        return token_payload.model_dump()
    