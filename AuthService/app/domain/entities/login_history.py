from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from domain.entities.base import BaseEntity


@dataclass
class LoginHistory(BaseEntity):
    user_oid: str = field(default="", kw_only=True)
    login_at: datetime = field(default_factory=datetime.now, kw_only=True)
    ip_address: str = field(default="", kw_only=True)
    user_agent: Optional[str] = field(default=None, kw_only=True)
    provider: str = field(default="local", kw_only=True)
    success: bool = field(default=True, kw_only=True)
    failure_reason: Optional[str] = field(default=None, kw_only=True)

    @classmethod
    def create_success(
        cls,
        user_oid: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        provider: str = "local",
    ) -> "LoginHistory":
        return cls(
            user_oid=user_oid,
            ip_address=ip_address,
            user_agent=user_agent,
            provider=provider,
            success=True,
        )

    @classmethod
    def create_failure(
        cls,
        user_oid: str,
        ip_address: str,
        reason: str,
        user_agent: Optional[str] = None,
        provider: str = "local",
    ) -> "LoginHistory":
        return cls(
            user_oid=user_oid,
            ip_address=ip_address,
            user_agent=user_agent,
            provider=provider,
            success=False,
            failure_reason=reason,
        )