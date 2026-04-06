from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.permission import Permission
from infrastructure.database.models import PermissionModel
from domain.repositories.permission import BasePermissionRepository


class PermissionRepository(BasePermissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _map_to_permission(self, model: PermissionModel) -> Permission:
        return Permission(
            oid=model.oid,
            code=model.code,
            description=model.description
        )

    async def create(self, permission: Permission) -> None:
        model = PermissionModel(
            oid=permission.oid,
            code=permission.code,
            description=permission.description
        )
        self.session.add(model)
        await self.session.flush()
    
    async def get(self, limit: int = 10, offset: int = 0) -> list[Permission]:
        result = await self.session.execute(
            select(PermissionModel).limit(limit).offset(offset)
        )
        permission_models = result.scalars().all()
        return [self._map_to_permission(permission_model) for permission_model in permission_models]
    
    async def get_by_oid(self, oid: str) -> Optional[Permission]:
        result = await self.session.execute(
            select(PermissionModel).where(PermissionModel.oid == oid)
        )
        permission_model = result.scalars().one_or_none()
        if not permission_model:
            return None
        return self._map_to_permission(permission_model)
    
    async def get_by_code(self, code: str) -> Optional[Permission]:
        result = await self.session.execute(
            select(PermissionModel).where(PermissionModel.code == code)
        )
        permission_model = result.scalars().one_or_none()
        if not permission_model:
            return None
        return self._map_to_permission(permission_model)
    
    async def update(self, permission: Permission) -> None:
        result = await self.session.execute(
            select(PermissionModel).where(PermissionModel.oid == permission.oid)
        )
        model = result.scalars().one()
        model.code = permission.code
        model.description = permission.description
        await self.session.flush()
    
    async def delete(self, permission: Permission) -> None:
        result = await self.session.execute(
            select(PermissionModel).where(PermissionModel.oid == permission.oid)
        )
        model = result.scalars().one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()