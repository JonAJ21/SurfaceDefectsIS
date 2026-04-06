from datetime import datetime
import json
from typing import Optional

from sqlalchemy import delete, desc, insert, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis

from domain.entities.session import Session
from domain.entities.login_history import LoginHistory
from domain.entities.permission import Permission
from domain.entities.role import Role
from domain.values.password import Password
from domain.values.email import Email
from domain.entities.user import User
from domain.repositories.user import BaseUserRepository
from infrastructure.database.models import LoginHistoryModel, PermissionModel, RoleModel, UserModel, user_roles, role_permissions


class UserRepository(BaseUserRepository):
    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.redis = redis

    def _map_to_user(
        self,
        user_model: UserModel,
        role_models: Optional[list[RoleModel]] = None,
        login_history_models: Optional[list[LoginHistoryModel]] = None,
        session_models: Optional[list[str]] = None,
        load_permissions: bool = False
    ) -> User:
        return User(
            oid=user_model.oid,
            email=Email(user_model.email),
            password=Password(user_model.password_hash),
            is_active=user_model.is_active,
            is_verified=user_model.is_verified,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            roles=self._map_to_roles(role_models, load_permissions) if role_models is not None else None,
            login_history=self._map_to_login_history(login_history_models) if login_history_models is not None else None,
            sessions=self._map_to_sessions(session_models) if session_models is not None else None
        )
    
    def _map_to_roles(
        self,
        role_models: list[RoleModel],
        load_permissions: bool = False
    ) -> set[Role]:
        roles = set()
        for rm in role_models:
            permissions = None
            if load_permissions:
                permissions = {
                    Permission.create(code=pm.code, description=pm.description)
                    for pm in rm.permissions
                }
            roles.add(Role(
                oid=rm.oid,
                name=rm.name,
                description=rm.description,
                created_at=rm.created_at,
                updated_at=rm.updated_at,
                permissions=permissions,
            ))
        return roles

    def _map_to_login_history(
        self,
        history_models: list[LoginHistoryModel]
    ) -> list[LoginHistory]:
        return [
            LoginHistory(
                oid=h.oid,
                user_oid=h.user_oid,
                login_at=h.login_at,
                ip_address=h.ip_address,
                user_agent=h.user_agent,
                provider=h.provider,
                success=h.success,
                failure_reason=h.failure_reason
            )
            for h in history_models
        ]
        
    def _map_to_sessions(
        self,
        session_models: list[str]
    ) -> list[Session]:
        sessions = []
        for session in session_models:        
            data = json.loads(session)
            sessions.append(Session(
                oid=data["oid"],
                user_oid=data["user_oid"],
                user_agent=data["user_agent"],
                provider=data["provider"],
                refresh_token_oid=data["refresh_token_oid"],
                refreshed_at=datetime.fromisoformat(data["refreshed_at"]),
                created_at=datetime.fromisoformat(data["created_at"]),
            ))
        return sessions
    
    async def create(self, user: User) -> None:
        model = UserModel(
            oid=user.oid,
            email=user.email.value,
            password_hash=user.password.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        self.session.add(model)
        await self.session.flush()
    

    
    async def _get_user_role_models(
        self,
        user_oid: str,
        load_permissions: bool = False
    ) -> list[RoleModel]:
        query = select(RoleModel).join(
            user_roles, RoleModel.oid == user_roles.c.role_oid
        ).where(user_roles.c.user_oid == user_oid)
        
        if load_permissions:
            query = query.options(selectinload(RoleModel.permissions))
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def _get_user_login_history_models(
        self,
        user_oid: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[LoginHistoryModel]:
        query = (
            select(LoginHistoryModel).
            where(LoginHistoryModel.user_oid == user_oid).
            order_by(desc(LoginHistoryModel.login_at)).
            limit(limit).offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    def _get_session_key(self, session_oid: str) -> str:
        return f"session:{session_oid}"
    
    def _get_user_sessions_key(self, user_oid: str) -> str:
        return f"user:sessions:{user_oid}"
    
    async def _get_sesion_models(
        self,
        user_oid: str
    ) -> list[str]:
        user_key = self._get_user_sessions_key(user_oid)
        session_oids = await self.redis.smembers(user_key)
        if not session_oids:
            return []
        session_models = []
        for session_oid in session_oids:
            session_key = self._get_session_key(session_oid)
            session_model = await self.redis.get(session_key)
            if session_model:
                session_models.append(session_model)
        return session_models
    
    async def get(self, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self.session.execute(
            select(UserModel).limit(limit).offset(offset)
        )
        user_models = result.scalars().all()
        return [self._map_to_user(user_model) for user_model in user_models]
    
    async def get_by_oid(
        self,
        oid: str,
        load_sessions: bool = False,
        load_roles: bool = False,
        load_permissions: bool = False,
        load_login_history: bool = False,
        login_history_limit: int = 10,
        login_history_offset: int = 0
    ) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.oid == oid)
        )
        user_model = result.scalars().one_or_none()
        if not user_model:
            return None
        
        role_models = None
        if load_roles:
            role_models = await self._get_user_role_models(oid, load_permissions)
        
        login_history_models = None
        if load_login_history:
            login_history_models = await self._get_user_login_history_models(
                oid,
                limit=login_history_limit,
                offset=login_history_offset
            )
        
        session_models = None
        if load_sessions:
            session_models = await self._get_sesion_models(oid)
        
        return self._map_to_user(user_model, role_models, login_history_models, session_models, load_permissions)
    
    async def get_by_email(
        self,
        email: Email,
        load_sessions: bool = False,
        load_roles: bool = False,
        load_permissions: bool = False,
        load_login_history: bool = False,
        login_history_limit: int = 10,
        login_history_offset: int = 0
    ) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.value)
        )
        user_model = result.scalars().one_or_none()
        if not user_model:
            return None
        
        role_models = None
        if load_roles:
            role_models = await self._get_user_role_models(user_model.oid, load_permissions)
        
        login_history_models = None
        if load_login_history:
            login_history_models = await self._get_user_login_history_models(
                user_model.oid,
                limit=login_history_limit,
                offset=login_history_offset
            )
        
        session_models = None
        if load_sessions:
            session_models = await self._get_sesion_models(user_model.oid)
        
        return self._map_to_user(user_model, role_models, login_history_models, session_models, load_permissions)
    
    async def _update_roles(
        self,
        user_model: UserModel,
        roles: set[Role]
    ) -> None:
        
        current_result = await self.session.execute(
            select(user_roles.c.role_oid).where(user_roles.c.user_oid == user_model.oid)
        )
        current_role_oids = {row[0] for row in current_result.all()}
        
        new_role_oids = {r.oid for r in roles}
        to_add = new_role_oids - current_role_oids
        to_remove = current_role_oids - new_role_oids
        
        if to_remove:
            await self.session.execute(
                delete(user_roles)
                .where(user_roles.c.user_oid == user_model.oid)
                .where(user_roles.c.role_oid.in_(to_remove))
            )
        
        if to_add:
            valid_result = await self.session.execute(
                select(RoleModel.oid).where(RoleModel.oid.in_(to_add))
            )
            valid_oids = {row[0] for row in valid_result.all()}
            
            insert_data = [
                {"user_oid": user_model.oid, "role_oid": oid}
                for oid in valid_oids
            ]
            if insert_data:
                await self.session.execute(insert(user_roles), insert_data)
    
    async def _update_login_history(
        self,
        user_model: UserModel,
        login_history: list[LoginHistory]
    ) -> None:
        if not login_history:
            return
        
        max_result = await self.session.execute(
            select(LoginHistoryModel.login_at)
            .where(LoginHistoryModel.user_oid == user_model.oid)
            .order_by(desc(LoginHistoryModel.login_at))
            .limit(1)
        )
        max_login_at = max_result.scalar_one_or_none()
        
        if max_login_at:
            new_records = [h for h in login_history if h.login_at > max_login_at]
        else:
            new_records = login_history
            
        if new_records:
            insert_data = [
                {
                    "oid": h.oid,
                    "user_oid": user_model.oid,
                    "login_at": h.login_at,
                    "ip_address": h.ip_address,
                    "user_agent": h.user_agent,
                    "provider": h.provider,
                    "success": h.success,
                    "failure_reason": h.failure_reason
                }
                for h in new_records
            ]
            await self.session.execute(insert(LoginHistoryModel), insert_data)
            
    async def _update_sessions(self, user_oid: str, sessions: list[Session]) -> None:
        if not sessions:
            return
        
        old_session_models = await self._get_sesion_models(user_oid)
        old_sessions = self._map_to_sessions(old_session_models)
        
        for session in sessions:
            if session not in old_sessions:
                session_data = {
                    "oid": session.oid,
                    "user_oid": user_oid,
                    "user_agent": session.user_agent,
                    "provider": session.provider,
                    "refresh_token_oid": session.refresh_token_oid,
                    "refreshed_at": session.refreshed_at.isoformat(),
                    "created_at": session.created_at.isoformat(),
                }
                session_key = self._get_session_key(session.oid)
                ttl = session.get_ttl()
                await self.redis.setex(
                    name=session_key,
                    time=ttl,
                    value=json.dumps(session_data)
                )
                
                user_key = self._get_user_sessions_key(user_oid)
                await self.redis.sadd(user_key, session.oid)
                await self.redis.expire(user_key, ttl)
                
        for session in old_sessions:
            if session not in sessions:
                session_key = self._get_session_key(session.oid)
                await self.redis.delete(session_key)
                
                user_key = self._get_user_sessions_key(user_oid)
                await self.redis.srem(user_key, session.oid)
                
    async def update(self, user: User) -> None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.oid == user.oid)
        )
        user_model = result.scalars().one()
    
        user_model.email = user.email.value
        user_model.password_hash = user.password.value
        user_model.is_active = user.is_active
        user_model.is_verified = user.is_verified
        user_model.updated_at = user.updated_at
        
        if user.roles:
            await self._update_roles(user_model, user.roles)
        
        if user.login_history:
            await self._update_login_history(user_model, user.login_history)
            
        if user.sessions:
            await self._update_sessions(user.oid, user.sessions)
        
        await self.session.flush()
    
    async def delete(self, user: User) -> None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.oid == user.oid)
        )
        user_model = result.scalars().one_or_none()
        if user_model:
            await self.session.delete(user_model)
            await self.session.flush()