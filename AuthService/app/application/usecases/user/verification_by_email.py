from core.config.settings import settings
from domain.services.token import BaseTokenService
from domain.exceptions.user import UserNotFoundException
from domain.services.email import BaseEmailService
from domain.repositories.uow import BaseUnitOfWork
from application.dto.user import EmailVerificationByEmailRequestDTO
from application.usecases.base import BaseUseCase


class BaseEmailVerificationByEmailUseCase(BaseUseCase[EmailVerificationByEmailRequestDTO, None]):
    ...

class EmailVerificationByEmailUseCase(BaseEmailVerificationByEmailUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        email_service: BaseEmailService,
        jwt_service: BaseTokenService
    ):
        self.uow = uow
        self.email_service = email_service
        self.jwt_service = jwt_service
        
    async def execute(self, request: EmailVerificationByEmailRequestDTO) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_oid(request.user_oid)
            if not user:
                raise UserNotFoundException(request.user_oid)
            
            access_token_oid, access_token = self.jwt_service.create_access_token(
                user_oid=user.oid,
                session_oid="",
                permission_codes=["user.verify"],
                is_verified=user.is_verified
            )
            
            await uow.email_tokens.create_email_token_with_ttl(
                oid=access_token_oid,
                ttl=settings.access_token_expire_minutes * 60
            )
            
            self.email_service.send_email(
                email=user.email,
                subject="Email Verification",
                body=f"Click <a href='{settings.verify_url}?access_token={access_token}'>here</a> to verify your email"
            )
            
            
            
            

                