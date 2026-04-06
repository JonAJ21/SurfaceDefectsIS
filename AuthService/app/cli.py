import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typer import Typer

from redis.asyncio.client import Redis

from domain.entities.user import User

from domain.values.email import Email
from domain.values.password import Password
from domain.exceptions.permission import PermissionNotFoundException
from domain.entities.role import Role
from domain.entities.permission import Permission
from domain.exceptions.role import RoleNotFoundException
from application.dependencies.factories import password_service_factory, uow_factory
from infrastructure.database import redis
from core.config.settings import settings


cli = Typer()


@asynccontextmanager
async def lifespan():
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True
    )
    yield
    await redis.redis.aclose()



def async_typer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper
      
# @cli.command()
# @async_typer       
async def create_permissions():
    async with lifespan():
        async with uow_factory() as uow:            
            permissions = [
                "permissions.create",
                "permissions.get",
                "permissions.update",
                "permissions.delete",
                "roles.create",
                "roles.get",
                "roles.update",
                "roles.delete",
                "roles.assign-permission",
                "roles.revoke-permission",
                "users.logout",
                "users.get-me",
                "users.get",
                "users.assign-role",
                "users.revoke-role",
                "users.verify",
                "users.activate",
                "users.deactivate"
            ]
            
            for permission in permissions:
                existing_permission = await uow.permissions.get_by_code(permission)
                if not existing_permission:
                    p = Permission(code=permission, description="")
                    await uow.permissions.create(p)

async def create_admin_role():
    async with lifespan():
        async with uow_factory() as uow:
            role = await uow.roles.get_by_name(
                name="admin"
            )
            if role:
                print("Role already exists")
                return
            
            role = Role(
                name="admin",
                description="admin role",
                permissions=set()
            )
            
            await uow.roles.create(role)
            
            permissions = [
                "permissions.create",
                "permissions.get",
                "permissions.update",
                "permissions.delete",
                "roles.create",
                "roles.get",
                "roles.update",
                "roles.delete",
                "roles.assign-permission",
                "roles.revoke-permission",
                "users.logout",
                "users.get-me",
                "users.get",
                "users.assign-role",
                "users.revoke-role",
                "users.verify",
                "users.activate",
                "users.deactivate"
            ]
            
            for permission in permissions:
                permission = await uow.permissions.get_by_code(permission)
                if not permission:
                    raise PermissionNotFoundException(permission)
                role.assign_permission(permission)
        
            await uow.roles.update(role)
            
async def create_user_role():
    async with lifespan():
        async with uow_factory() as uow:
            role = await uow.roles.get_by_name(
                name="user"
            )
            if role:
                print("Role already exists")
                return
            
            role = Role(
                name="user",
                description="user role",
                permissions=set()
            )
            
            await uow.roles.create(role)
            
            permissions = [
                "users.logout",
                "users.get-me",
                "users.verify",
            ]
            
            for permission in permissions:
                permission = await uow.permissions.get_by_code(permission)
                if not permission:
                    raise PermissionNotFoundException(permission)
                role.assign_permission(permission)
        
            await uow.roles.update(role)


async def create_admin_user():
    async with lifespan():
        async with uow_factory() as uow:
            email = settings.email_address
            password = settings.app_password
            
            existing_user = await uow.users.get_by_email(Email(email))
            if existing_user:
                print("User already exists")
                return
            
            user: User = User(
                email=Email(email),
                password=Password.from_plain(password, password_service_factory()),
                is_active=True,
                is_verified=True,
                roles=set()
            )
            
            await uow.users.create(user)
            
            role = await uow.roles.get_by_name("admin")
            if not role:
                raise RoleNotFoundException(name="admin")
            
            user.assign_role(role)
            
            await uow.users.update(user)
        

@cli.command()
@async_typer   
async def init():
    await create_permissions()
    await create_admin_role()
    await create_user_role()
    await create_admin_user()
    
if __name__ == "__main__":
    cli()