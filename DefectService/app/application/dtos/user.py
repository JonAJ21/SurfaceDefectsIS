
from dataclasses import dataclass, field


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