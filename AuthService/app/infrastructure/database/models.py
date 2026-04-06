

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infrastructure.database.session import Base


user_roles: Table = Table(
    'user_roles',
    Base.metadata,
    Column('user_oid', String, ForeignKey('users.oid'), primary_key=True),
    Column('role_oid', String, ForeignKey('roles.oid'), primary_key=True)
)

role_permissions: Table = Table(
    'role_permissions',
    Base.metadata,
    Column('role_oid', String, ForeignKey('roles.oid'), primary_key=True),
    Column('permission_oid', String, ForeignKey('permissions.oid'), primary_key=True)
)


class UserModel(Base):
    __tablename__ = 'users'
    
    oid: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    roles: Mapped[list['RoleModel']] = relationship(
        'RoleModel',
        secondary=user_roles,
        back_populates='users'
    )
    login_history: Mapped[list['LoginHistoryModel']] = relationship(
        'LoginHistoryModel',
        back_populates='user'
    )

    def __repr__(self):
        return f"UserModel(oid={self.oid!r}, email={self.email!r})"
    

class RoleModel(Base):
    __tablename__ = 'roles'
    
    oid: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    permissions: Mapped[list['PermissionModel']] = relationship(
        'PermissionModel',
        secondary=role_permissions,
        back_populates='roles',
    )
    users: Mapped[list['UserModel']] = relationship(
        'UserModel',
        secondary=user_roles,
        back_populates='roles'
    )

    def __repr__(self):
        return f"RoleModel(oid={self.oid!r}, name={self.name!r})"
    

class PermissionModel(Base):
    __tablename__ = 'permissions'
    
    oid: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    
    roles: Mapped[list['RoleModel']] = relationship(
        'RoleModel',
        secondary=role_permissions,
        back_populates='permissions'
    )

    def __repr__(self):
        return f"PermissionModel(code={self.code!r})"
    
class LoginHistoryModel(Base):
    __tablename__ = "login_history"

    oid: Mapped[str] = mapped_column(String, primary_key=True)
    user_oid: Mapped[str] = mapped_column(String, ForeignKey('users.oid'), index=True)
    login_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    ip_address: Mapped[str] = mapped_column(String)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String, default="local")
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="login_history")

    def __repr__(self) -> str:
        return f"LoginHistoryModel(oid={self.oid}, user_oid={self.user_oid})"