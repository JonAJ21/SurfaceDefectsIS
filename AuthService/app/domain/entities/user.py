from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from domain.entities.session import Session
from domain.exceptions.auth import InvalidPasswordOrEmailException
from domain.exceptions.user import UserInactiveException
from domain.services.password import BasePasswordService
from domain.entities.login_history import LoginHistory
from domain.entities.role import Role
from domain.values.password import Password
from domain.values.email import Email
from domain.entities.base import BaseEntity

@dataclass
class User(BaseEntity):
    email: Email = field(kw_only=True)
    password: Password = field(kw_only=True)
    is_active: bool = field(kw_only=True, default=True)
    is_verified: bool = field(kw_only=True, default=False)
    created_at: datetime = field(kw_only=True, default_factory=datetime.now)
    updated_at: datetime = field(kw_only=True, default_factory=datetime.now)
    
    roles: Optional[set[Role]] = None
    login_history: Optional[list[LoginHistory]] = None
    sessions: Optional[list[Session]] = None
    
    @classmethod
    def register(cls, email: Email, plain_password: str, password_service: BasePasswordService) -> "User":
        return cls(
            email=email,
            password=Password.from_plain(plain_password, password_service)
        )
    
    def create_session(
        self,
        user_agent: str,
        provider: str,
        refresh_token_oid: str
    ) -> Session:
        if self.sessions is None:
            raise ValueError("Sessions have not been loaded. Use load_sessions=True")
        
        if len(self.sessions) >= 5:
            oldest_refreshed_session = min(self.sessions, key=lambda s: s.refreshed_at)
            self.sessions.remove(oldest_refreshed_session)
        
        session = Session(
            user_oid=self.oid,
            user_agent=user_agent,
            provider=provider,
            refresh_token_oid=refresh_token_oid
        )
        
        self.sessions.append(session)
        
        return session
    
    def refresh_session(
        self,
        session: Session,
        user_agent: str,
        provider: str,
        token_oid: str
    ) -> None:
        if self.sessions is None:
            raise ValueError("Sessions have not been loaded. Use load_sessions=True")
        for s in self.sessions:
            if s.oid == session.oid:
                s.refresh(
                    user_agent=user_agent,
                    provider=provider,
                    refresh_token_oid=token_oid
                )
        
        
        
    def revoke_session(self, session: Session) -> None:
        if self.sessions is None:
            raise ValueError("Sessions have not been loaded. Use load_sessions=True")
        self.sessions.remove(session)
            
    def assign_role(self, role: Role) -> None:
        if self.roles is None:
            raise ValueError("Roles have not been loaded. Use load_roles=True")
        self.roles.add(role)
        self.updated_at = datetime.now()
        
    def revoke_role(self, role: Role) -> None:
        if self.roles is None:
            raise ValueError("Roles have not been loaded. Use load_roles=True")
        self.roles.discard(role)
        self.updated_at = datetime.now()
        
    def has_role(self, role: Role) -> bool:
        if self.roles is None:
            raise ValueError("Roles have not been loaded. Use load_roles=True")
        return role in self.roles
        
    def has_permission(self, permission: str) -> bool:
        if self.roles is None:
            raise ValueError("Roles have not been loaded. Use load_roles=True")
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False
    
    @property
    def permissions(self) -> set[str]:
        if self.roles is None:
            raise ValueError("Roles have not been loaded. Use load_roles=True")
        return {permission for role in self.roles for permission in role.permissions}
    
    def activate(self) -> None:
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.now()
            
    def deactivate(self) -> None:
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.now()
            
    def verify(self) -> None:
        if not self.is_verified:
            self.is_verified = True
            self.updated_at = datetime.now()
            
    def unverify(self) -> None:
        if self.is_verified:
            self.is_verified = False
            self.updated_at = datetime.now()

    def change_email(self, email: Email) -> None:
        self.email = email
        self.updated_at = datetime.now()
    
    def change_password(self, old_password: str, new_password: str, password_service: BasePasswordService) -> None:
        if not old_password:
            raise ValueError("Old password is required")
        if not new_password:
            raise ValueError("New password is required")
        if self.password.verify(old_password, password_service):
            self.password = Password.from_plain(new_password, password_service)
            self.updated_at = datetime.now()
            
    
            
    