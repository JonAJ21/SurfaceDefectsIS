from domain.exceptions.user import UserNotFoundException
from core.config.settings import settings
from domain.exceptions.session import SessionAlredyRefreshedWithTokenException, SessionNotFoundException, UserAgentOrProviderMismatchException
from domain.entities.session import Session
from application.dto.user import TokenDTO, UserRefreshTokenRequestDTO
from application.usecases.base import BaseUseCase
from domain.repositories.uow import BaseUnitOfWork
from domain.services.token import BaseTokenService


class BaseUserRefreshTokenUseCase(BaseUseCase[UserRefreshTokenRequestDTO, TokenDTO]):
    ...

class UserRefreshUseCase(BaseUserRefreshTokenUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        jwt_service: BaseTokenService,
    ):
        self.uow = uow
        self.jwt_service = jwt_service
        
    async def execute(self, request: UserRefreshTokenRequestDTO) -> TokenDTO:
        async with self.uow as uow:
            token_payload = self.jwt_service.verify_refresh_token(request.refresh_token)
            session_oid = token_payload["sub"]
            user_oid = token_payload["user_oid"]
            scopes = token_payload["scopes"]
            
            sessions: list[Session] = await uow.sessions.get_all_by_user_oid(user_oid)
            
            current_session = None
            for session in sessions:
                if session.oid == session_oid:
                    current_session = session
                    break
            else:
                raise SessionNotFoundException(session_oid)
            
            if current_session.refresh_token_oid != token_payload["token_oid"]:
                raise SessionAlredyRefreshedWithTokenException()

            if current_session.user_agent != request.user_agent or current_session.provider != request.provider:
                raise UserAgentOrProviderMismatchException()
            
            user = await uow.users.get_by_oid(user_oid)
            if not user:
                raise UserNotFoundException(user_oid)
            
            _, access_token = self.jwt_service.create_access_token(
                user_oid=user_oid,
                session_oid=session_oid,
                permission_codes=scopes,
                is_verified=user.is_verified
            )
            
            refresh_token_oid, refresh_token = self.jwt_service.create_refresh_token(
                user_oid=user_oid,
                session_oid=session_oid,
                permission_codes=scopes
            )
            
            
            session.refresh(
                user_agent=request.user_agent,
                provider=request.provider,
                refresh_token_oid=refresh_token_oid
            )
            
            await uow.sessions.update(current_session)
            
            return TokenDTO(
                access_token=access_token,
                token_type="Bearer",
                expires_in=settings.access_token_expire_minutes * 60,
                refresh_token=refresh_token
            )

                