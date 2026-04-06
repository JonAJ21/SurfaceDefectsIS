from domain.exceptions.session import AccessTokenIsRequiredException
from application.dto.user import UserAuthRequestDTO, UserAuthResponseDTO
from domain.exceptions.user import UserDoesNotHavePermissionException, UserEmailNotVerifiedException
from domain.repositories.uow import BaseUnitOfWork
from domain.services.token import BaseTokenService
from application.usecases.base import BaseUseCase


class BaseUserAuthUseCase(BaseUseCase[UserAuthRequestDTO, UserAuthResponseDTO]):
    ...
    
class UserAuthUseCase(BaseUserAuthUseCase):
    def __init__(self,
        uow: BaseUnitOfWork,
        jwt_service: BaseTokenService
    ):
        self.uow = uow
        self.jwt_service = jwt_service
        
    async def execute(self, request: UserAuthRequestDTO) -> UserAuthResponseDTO:
        if not request.access_token:
            raise AccessTokenIsRequiredException()
        token_payload = self.jwt_service.verify_access_token(request.access_token)
        
        if request.needs_verified_email and not token_payload["is_verified"]:
            raise UserEmailNotVerifiedException()
        
        needed_permission_codes = request.needed_permission_codes
        user_permission_codes = token_payload["scopes"]
        
        for needed_permission_code in needed_permission_codes:
            if needed_permission_code not in user_permission_codes:
                raise UserDoesNotHavePermissionException(needed_permission_code)
        
        return UserAuthResponseDTO(
            user_oid=token_payload["user_oid"],
            session_oid=token_payload["sub"],
            is_verified=token_payload["is_verified"]
        )
        
        
        