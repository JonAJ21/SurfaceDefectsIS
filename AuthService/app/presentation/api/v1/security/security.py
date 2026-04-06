from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/users/login",
    refreshUrl="/v1/users/me/refresh",
    auto_error=False
)
