from dataclasses import dataclass, field
from datetime import datetime, timedelta

from domain.exceptions.session import UserAgentOrProviderMismatchException
from domain.entities.base import BaseEntity
from core.config.settings import settings


@dataclass
class Session(BaseEntity):
    user_oid: str = field(kw_only=True)
    user_agent: str = field(kw_only=True)
    provider: str = field(kw_only=True) 
    
    refresh_token_oid: str = field(kw_only=True)
    
    refreshed_at: datetime = field(default_factory=datetime.now, kw_only=True)
    created_at: datetime = field(default_factory=datetime.now, kw_only=True)
    
    def is_access_token_expired(self) -> bool:
        access_expiry = self.refreshed_at + timedelta(minutes=settings.access_token_expire_minutes)
        return datetime.now() > access_expiry
    
    def is_refresh_token_expired(self) -> bool:
        return datetime.now() > self.refreshed_at + timedelta(days=settings.refresh_token_expire_days)

    def should_refresh(self) -> bool:
        access_expiry = self.refreshed_at + timedelta(minutes=settings.access_token_expire_minutes)
        refresh_threshold = access_expiry - timedelta(minutes=settings.refresh_threshold_minutes)
        return datetime.now() > refresh_threshold
    
    def get_ttl(self) -> int:
        refresh_expiry = self.refreshed_at + timedelta(days=settings.refresh_token_expire_days)
        return int((refresh_expiry - datetime.now()).total_seconds())

    def refresh(
        self,
        user_agent: str,
        provider: str,
        refresh_token_oid: str
    ) -> None:
        if self.user_agent != user_agent or self.provider != provider:
            raise UserAgentOrProviderMismatchException()
        self.refresh_token_oid = refresh_token_oid
        self.refreshed_at = datetime.now()
        