from fastapi.security import HTTPBearer

security_scheme = HTTPBearer(scheme_name="Bearer")

