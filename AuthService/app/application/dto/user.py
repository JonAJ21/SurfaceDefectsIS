from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from application.dto.role import GetRoleResponseDTO


@dataclass
class UserRegisterRequestDTO:
    email: str
    password: str
    password_confirm: str
    
@dataclass
class UserRegisterResponseDTO:
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
@dataclass
class UserLoginRequestDTO:
    email: str
    password: str
    ip_address: str
    user_agent: str
    provider: str = "local"
 
@dataclass
class UserRefreshTokenRequestDTO:
    refresh_token: str
    user_agent: str
    provider: str = "local"
    
@dataclass
class GetUsersRequestDTO:
    offset: int = 0
    limit: int = 10
    
 
@dataclass
class GetUserLoginHistoryResponseDTO:
    oid: str
    user_oid: str
    login_at: datetime
    ip_address: str
    user_agent: str
    provider: str
    success: bool
    failure_reason: Optional[str] = None
    

@dataclass
class GetUserSessionResponseDTO:
    oid: str
    user_oid: str
    user_agent: str
    provider: str
    refresh_token_oid: str
    refreshed_at: datetime
    created_at: datetime
    
@dataclass
class TokenDTO:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    
@dataclass
class UserAuthRequestDTO:
    access_token: str
    needs_verified_email: bool = False
    needed_permission_codes: list[str] = field(default_factory=list)

@dataclass 
class UserAuthResponseDTO:
    user_oid: str
    session_oid: str
    is_verified: bool

@dataclass
class UserLogoutRequestDTO:
    user_oid: str
    session_oid: str    

@dataclass
class GetUserByIdentifierRequestDTO:
    identifier: str
    load_roles: bool = False
    load_permissions: bool = False
    load_sessions: bool = False
    load_login_history: bool = False
    login_history_offset: int = 0
    login_history_limit: int = 10
    
@dataclass
class GetUserResponseDTO:
    oid: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    roles: Optional[list[GetRoleResponseDTO]] = None
    sessions: Optional[list[GetUserSessionResponseDTO]] = None
    login_history: Optional[list[GetUserLoginHistoryResponseDTO]] = None
    
    
@dataclass
class UserUpdateByIdentifierRequestDTO:
    identifier: str
    new_email: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    new_is_active: Optional[bool] = None
    new_is_verified: Optional[bool] = None
    role_identifiers_to_add: Optional[list[str]] = None
    role_identifiers_to_remove: Optional[list[str]] = None
    
@dataclass
class EmailVerificationByEmailRequestDTO:
    user_oid: str
    