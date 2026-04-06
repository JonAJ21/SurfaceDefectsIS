from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from application.dto.user import GetUserLoginHistoryResponseDTO, GetUserResponseDTO, GetUserSessionResponseDTO
from presentation.api.v1.schemas.role import GetRoleResponseSchema, GetRolesResponseSchema


class UserRegisterRequestSchema(BaseModel):
    email: str
    password: str
    password_confirm: str
    
class UserRegisterResponseSchema(BaseModel):
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dto(cls, dto):
        return cls(
            email=dto.email,
            is_active=dto.is_active,
            is_verified=dto.is_verified,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
      
        
class UserLoginRequestSchema(BaseModel):
    email: str
    password: str
    
class UserLoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    
    @classmethod
    def from_dto(cls, dto):
        return cls(
            access_token=dto.access_token,
            token_type=dto.token_type,
            expires_in=dto.expires_in,
            refresh_token=dto.refresh_token
        )
        
class UserRefreshTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    
    @classmethod
    def from_dto(cls, dto):
        return cls(
            access_token=dto.access_token,
            token_type=dto.token_type,
            expires_in=dto.expires_in,
            refresh_token=dto.refresh_token
        )

class GetUserSessionResponseSchema(BaseModel):
    oid: str
    user_oid: str
    user_agent: str
    provider: str
    refresh_token_oid: str
    refreshed_at: datetime
    created_at: datetime
    
    @classmethod
    def from_dto(cls, dto: GetUserSessionResponseDTO):
        return cls(
            oid=dto.oid,
            user_oid=dto.user_oid,
            user_agent=dto.user_agent,
            provider=dto.provider,
            refresh_token_oid=dto.refresh_token_oid,
            refreshed_at=dto.refreshed_at,
            created_at=dto.created_at
        )
        
class GetUserSessionsResponseSchema(BaseModel):
    sessions: list[GetUserSessionResponseSchema]
    
    @classmethod
    def from_dto(cls, dto: list[GetUserSessionResponseDTO]):
        return cls(
            sessions=[GetUserSessionResponseSchema.from_dto(s) for s in dto]
        )


class GetUserLoginHistoryResponseSchema(BaseModel):
    oid: str
    user_oid: str
    login_at: datetime
    ip_address: str
    user_agent: str
    provider: str
    success: bool
    failure_reason: Optional[str] = None
    
    @classmethod
    def from_dto(cls, dto: GetUserLoginHistoryResponseDTO):
        return cls(
            oid=dto.oid,
            user_oid=dto.user_oid,
            login_at=dto.login_at,
            ip_address=dto.ip_address,
            user_agent=dto.user_agent,
            provider=dto.provider,
            success=dto.success,
            failure_reason=dto.failure_reason
        )
        
class GetUserLoginHistoriesResponseSchema(BaseModel):
    login_history: list[GetUserLoginHistoryResponseSchema]
    
    @classmethod
    def from_dto(cls, dto: list[GetUserLoginHistoryResponseDTO]):
        return cls(
            login_history=[GetUserLoginHistoryResponseSchema.from_dto(h) for h in dto]
        )

class GetUserResponseSchema(BaseModel):
    oid: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    roles: Optional[list[GetRoleResponseSchema]] = None
    sessions: Optional[list[GetUserSessionResponseSchema]] = None
    login_history: Optional[list[GetUserLoginHistoryResponseSchema]] = None
    
    @classmethod
    def from_dto(cls, dto: GetUserResponseDTO):
        return cls(
            oid=dto.oid,
            email=dto.email,
            is_active=dto.is_active,
            is_verified=dto.is_verified,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            roles=[GetRoleResponseSchema.from_dto(r) for r in dto.roles] if dto.roles else None,
            sessions=[GetUserSessionResponseSchema.from_dto(s) for s in dto.sessions] if dto.sessions else None,
            login_history=[GetUserLoginHistoryResponseSchema.from_dto(h) for h in dto.login_history] if dto.login_history else None
        )
        
class GetUsersResponseSchema(BaseModel):
    users: list[GetUserResponseSchema]
    
    @classmethod
    def from_dto(cls, dto: list[GetUserResponseDTO]):
        return cls(
            users=[GetUserResponseSchema.from_dto(u) for u in dto]
        )
        
    