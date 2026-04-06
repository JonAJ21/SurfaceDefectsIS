
from domain.exceptions.role import RoleNotFoundException
from domain.repositories.uow import BaseUnitOfWork
from domain.values.password import Password
from domain.values.email import Email
from domain.entities.user import User
from domain.exceptions.user import UserWithEmailAlreadyExistsExcception
from domain.exceptions.auth import PasswordDoesNotMatchException
from domain.services.password import BasePasswordService
from application.dto.user import UserRegisterRequestDTO, UserRegisterResponseDTO
from application.usecases.base import BaseUseCase


class BaseUserRegisterUseCase(BaseUseCase[UserRegisterRequestDTO, UserRegisterResponseDTO]):
    ...
    
class UserRegisterUseCase(BaseUserRegisterUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        password_service: BasePasswordService,
    ):
        self.uow = uow
        self.password_service = password_service
    
    async def execute(self, request: UserRegisterRequestDTO) -> UserRegisterResponseDTO:
        async with self.uow as uow:
            if request.password != request.password_confirm:
                raise PasswordDoesNotMatchException()
            
            existing_user = await uow.users.get_by_email(Email(request.email))
            if existing_user:
                raise UserWithEmailAlreadyExistsExcception(request.email)
            
            user: User = User(
                email=Email(request.email),
                password=Password.from_plain(request.password, self.password_service),
                is_active=True,
                is_verified=False,
                roles=set()
            )
            
            await uow.users.create(user)
            
            role = await uow.roles.get_by_name("user")
            if not role:
                raise RoleNotFoundException(name="user")
            
            user.assign_role(role)
            
            await uow.users.update(user)
            
            return UserRegisterResponseDTO(
                email=user.email.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )