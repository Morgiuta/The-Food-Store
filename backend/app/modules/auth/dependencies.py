from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.api.deps import DbSession
from app.core.security import decode_access_token
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import TokenData
from app.modules.auth.service import (
    get_user_by_username,
    user_has_permission,
    user_has_role,
)


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        token = request.cookies.get("access_token")

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        return token


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales incorrectas",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: DbSession,
) -> Usuario:
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    token_data = TokenData(
        email=payload.get("sub"),
        roles=payload.get("roles", []),
    )

    if token_data.email is None:
        raise credentials_exception

    user = get_user_by_username(session, token_data.email)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return current_user


def require_roles(*roles: str):
    allowed_roles_set = {role.strip().upper() for role in roles}
    allowed_roles_text = ", ".join(sorted(allowed_roles_set))

    def role_checker(
        current_user: Annotated[Usuario, Depends(get_current_active_user)],
        session: DbSession,
    ) -> Usuario:
        if current_user.id is not None and user_has_role(
            session,
            current_user.id,
            allowed_roles_set,
        ):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permisos insuficientes. Se requiere uno de: {allowed_roles_text}",
        )

    return role_checker


def require_role(allowed_roles: list[str]):
    return require_roles(*allowed_roles)


def require_permission(resource: str, action: str):
    def permission_checker(
        current_user: Annotated[Usuario, Depends(get_current_active_user)],
        session: DbSession,
    ) -> Usuario:
        if current_user.id is None:
            raise credentials_exception

        if user_has_permission(session, current_user.id, resource, action):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Permisos insuficientes. "
                f"Se requiere permiso '{resource}:{action}'."
            ),
        )

    return permission_checker
