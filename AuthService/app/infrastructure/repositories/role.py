from datetime import datetime
import json
from typing import Optional

from redis.asyncio.client import Redis
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions.role import RoleNotFoundException
from domain.entities.permission import Permission
from domain.entities.role import Role
from infrastructure.database.models import PermissionModel, RoleModel, role_permissions
from domain.repositories.role import BaseRoleRepository


class RoleRepository(BaseRoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def _map_to_role(
        self,
        model: RoleModel,
        permission_models: Optional[list[PermissionModel]]
    ) -> Role:
        permissions: Optional[set[Permission]] = None
        if permission_models is not None:
            permissions = {
                Permission(oid=p.oid, code=p.code, description=p.description)
                for p in permission_models
            }
        return Role(
            oid=model.oid,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            permissions=permissions
        )
    
    async def _get_permissions_by_role_oid(
        self,
        role_oid: str
    ) -> list[PermissionModel]:
        result = await self.session.execute(
            select(PermissionModel)
            .join(role_permissions, PermissionModel.oid == role_permissions.c.permission_oid)
            .where(role_permissions.c.role_oid == role_oid)
        )
        return result.scalars().all()
    
    async def create(self, role: Role) -> None:
        model = RoleModel(
            oid=role.oid,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        self.session.add(model)
        await self.session.flush()
    
    async def get(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> list[Role]:
        result = await self.session.execute(
            select(RoleModel).limit(limit).offset(offset)
        )
        role_models = result.scalars().all()
        return [self._map_to_role(role_model, None) for role_model in role_models]
    
    async def get_by_oid(
        self,
        oid: str,
        load_permissions: bool = False
    ) -> Optional[Role]:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.oid == oid)
        )
        role_model = result.scalars().one_or_none()
        if not role_model:
            return None
        
        permission_models = None
        if load_permissions:
            permission_models = await self._get_permissions_by_role_oid(oid)
        
        return self._map_to_role(role_model, permission_models)
    
    async def get_by_name(
        self,
        name: str,
        load_permissions: bool = False
    ) -> Optional[Role]:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.name == name)
        )
        role_model = result.scalars().one_or_none()
        if not role_model:
            return None
        
        permission_models = None
        if load_permissions:
            permission_models = await self._get_permissions_by_role_oid(role_model.oid)
        
        return self._map_to_role(role_model, permission_models)
    
    async def _update_permissions(
        self,
        role_model: RoleModel,
        new_permissions: set[Permission]
    ) -> None:
        current_result = await self.session.execute(
            select(role_permissions.c.permission_oid)
            .where(role_permissions.c.role_oid == role_model.oid)
        )
        current_permission_oids = {row[0] for row in current_result.all()}
        
        new_permission_oids = {p.oid for p in new_permissions}
        to_add = new_permission_oids - current_permission_oids
        to_remove = current_permission_oids - new_permission_oids
        
        if to_remove:
            await self.session.execute(
                delete(role_permissions)
                .where(role_permissions.c.role_oid == role_model.oid)
                .where(role_permissions.c.permission_oid.in_(to_remove))
            )
        
        if to_add:
            valid_result = await self.session.execute(
                select(PermissionModel.oid)
                .where(PermissionModel.oid.in_(to_add))
            )
            valid_permission_oids = {row[0] for row in valid_result.all()}
            
            insert_data = [
                {"role_oid": role_model.oid, "permission_oid": oid}
                for oid in valid_permission_oids
            ]
            if insert_data:
                await self.session.execute(insert(role_permissions), insert_data)

    async def update(self, role: Role) -> None:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.oid == role.oid)
        )
        role_model = result.scalars().one()
        
        role_model.name = role.name
        role_model.description = role.description
        role_model.updated_at = role.updated_at
        
        if role.permissions is not None:
            await self._update_permissions(role_model, role.permissions)
        
        await self.session.flush()

    async def delete(self, role: Role) -> None:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.oid == role.oid)
        )
        role_model = result.scalars().one_or_none()
        if role_model:
            await self.session.delete(role_model)
            await self.session.flush()
            
              
class CachedRoleRepository(RoleRepository):
    
    def __init__(self, session: AsyncSession, redis: Redis, cache_ttl: int = 60):
        super().__init__(session)
        self.redis: Redis = redis
        self.cache_ttl: int = cache_ttl
        
    def _get_role_oid_cache_key(self, role_oid: str) -> str:
        return f"role:oid:{role_oid}"
    
    def _get_role_name_cache_key(self, role_name: str) -> str:
        return f"role:name:{role_name}"
    
    def _get_role_permissions_cache_key(self, role_oid: str) -> str:
        return f"role:permissions:{role_oid}"
    
    def _serialize_role(self, role: Role) -> str:
        data = {
            "oid": role.oid,
            "name": role.name,
            "description": role.description,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None,
        }
        return json.dumps(data)
    
    def _deserialize_role(self, cached: str) -> Role:
        data = json.loads(cached)
        return Role(
            oid=data["oid"],
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            permissions=None
        )
    
    def _serialize_permissions(self, permissions: set[Permission]) -> str:
        data = [
            {"oid": p.oid, "code": p.code, "description": p.description}
            for p in permissions
        ]
        return json.dumps(data)
    
    def _deserialize_permissions(self, cached: str) -> set[Permission]:
        data = json.loads(cached)
        return {
            Permission(oid=p["oid"], code=p["code"], description=p["description"])
            for p in data
        }
    
    async def _cache_role(self, role: Role) -> None:
        role_key = self._get_role_oid_cache_key(role.oid)
        await self.redis.setex(
            name=role_key,
            time=self.cache_ttl,
            value=self._serialize_role(role)
        )
        
        name_key = self._get_role_name_cache_key(role.name)
        await self.redis.setex(
            name=name_key,
            time=self.cache_ttl,
            value=role.oid
        )
        
        if role.permissions is not None:
            permissions_key = self._get_role_permissions_cache_key(role.oid)
            await self.redis.setex(
                name=permissions_key,
                time=self.cache_ttl,
                value=self._serialize_permissions(role.permissions)
            )
            
    async def _invalidate_role_cache(self, role_oid: str, role_name: str) -> None:
        role_key = self._get_role_oid_cache_key(role_oid)
        await self.redis.delete(role_key)
        
        name_key = self._get_role_name_cache_key(role_name)
        await self.redis.delete(name_key)
        
        permissions_key = self._get_role_permissions_cache_key(role_oid)
        await self.redis.delete(permissions_key)
     
    async def get_by_oid(
        self,
        oid: str,
        load_permissions: bool = False
    ) -> Optional[Role]:
        role_key = self._get_role_oid_cache_key(oid)
        cached = await self.redis.get(role_key)
        
        if cached:
            role: Role = self._deserialize_role(cached)
            if load_permissions:
                permissions_key = self._get_role_permissions_cache_key(oid)
                permissions_cached = await self.redis.get(permissions_key)
                role.permissions = self._deserialize_permissions(permissions_cached)
            return role
        
        role = await super().get_by_oid(
            oid=oid,
            load_permissions=True
        )
        
        if not role:
            return None
        
        await self._cache_role(role)
            
        if not load_permissions:
            role.permissions = None
        
        return role
    
    async def get_by_name(
        self,
        name: str,
        load_permissions: bool = False
    ) -> Optional[Role]:
        role_name_key = self._get_role_name_cache_key(name)
        cached_oid = await self.redis.get(role_name_key)
        
        if cached_oid:
            return await self.get_by_oid(
                oid=cached_oid,
                load_permissions=load_permissions
            )
        
        role = await super().get_by_name(
            name=name,
            load_permissions=True
        )
        
        if not role:
            return None
        
        await self._cache_role(role)
        
        if not load_permissions:
            role.permissions = None
        
        return role
    

    async def update(self, role: Role) -> None:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.oid == role.oid)
        )
        old_role = result.scalars().one()
        
        old_name = old_role.name
        
        await super().update(role)
        
        await self._invalidate_role_cache(
            role_oid=role.oid,
            role_name=old_name
        )
        
    async def delete(self, role: Role) -> None:
        await super().delete(role)
        
        await self._invalidate_role_cache(
            role_oid=role.oid,
            role_name=role.name
        )
        
        