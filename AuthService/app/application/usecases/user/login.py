from typing import Optional

from domain.values.email import Email
from core.config.settings import settings
from domain.entities.user import User
from domain.entities.login_history import LoginHistory
from domain.exceptions.auth import InvalidPasswordOrEmailException
from domain.exceptions.user import UserInactiveException, UserNotFoundException
from application.dto.user import TokenDTO, UserLoginRequestDTO
from domain.repositories.uow import BaseUnitOfWork
from domain.services.password import BasePasswordService
from domain.services.token import BaseTokenService
from application.usecases.base import BaseUseCase


class BaseUserLoginUseCase(BaseUseCase[UserLoginRequestDTO, TokenDTO]):
    ...

class UserLoginUseCase(BaseUserLoginUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        password_service: BasePasswordService,
        jwt_service: BaseTokenService,
    ):
        self.uow = uow
        self.password_service = password_service
        self.jwt_service = jwt_service
        
    async def execute(self, request: UserLoginRequestDTO) -> TokenDTO:
        async with self.uow as uow:
            user: Optional[User] = await uow.users.get_by_email(
                email=Email(request.email),
                load_sessions=True,
                load_roles=True,
                load_permissions=True,
                load_login_history=True,
                login_history_limit=0,
                login_history_offset=0
            )
            if not user:
                raise UserNotFoundException(email=request.email)
            
            if user.login_history is None:
                    raise ValueError("Login history has not been loaded. Use load_login_history=True")
            
            if not user.is_active:
                user.login_history.append(
                    LoginHistory.create_failure(
                        user_oid=user.oid,
                        ip_address=request.ip_address,
                        user_agent=request.user_agent,
                        reason="User is inactive",
                    )
                )
                await uow.users.update(user)
                await uow.commit()
                raise UserInactiveException(email=request.email)
            
            if not self.password_service.verify(request.password, user.password.value):
                user.login_history.append(
                    LoginHistory.create_failure(
                        user_oid=user.oid,
                        ip_address=request.ip_address,
                        user_agent=request.user_agent,
                        reason="Invalid password or email",
                    )
                )
                await uow.users.update(user)
                await uow.commit()
                raise InvalidPasswordOrEmailException()
            
            user.login_history.append(
                LoginHistory.create_success(
                    user_oid=user.oid,
                    ip_address=request.ip_address,
                    user_agent=request.user_agent,
                )
            )
            
            session = user.create_session(
                user_agent=request.user_agent,
                provider=request.provider,
                refresh_token_oid="",
            )
            
            permission_codes = [p.code for p in user.permissions]
            
            refresh_token_oid, refresh_token = self.jwt_service.create_refresh_token(
                user_oid=user.oid,
                session_oid=session.oid,
                permission_codes=permission_codes)
            _, access_token = self.jwt_service.create_access_token(
                user_oid=user.oid,
                session_oid=session.oid,
                permission_codes=permission_codes,
                is_verified=user.is_verified
            )
            
            user.refresh_session(
                session=session,
                user_agent=request.user_agent,
                provider=request.provider,
                token_oid=refresh_token_oid
            )
            
            await uow.users.update(user) 
            return TokenDTO(
                access_token=access_token,
                token_type="Bearer",
                expires_in=settings.access_token_expire_minutes * 60,
                refresh_token=refresh_token
            )

                