from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.api.deps import DbSession
from app.core.security import decode_access_token
from app.modules.auth.models import Permission, Role, RolePermission, User, UserRole
from app.modules.auth.schemas import TokenData
from app.modules.auth.service import get_user_by_username


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
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username = payload.get("sub")
    token_data = TokenData(username=username)

    if token_data.username is None:
        raise credentials_exception

    user = get_user_by_username(session, token_data.username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return current_user


def require_role(allowed_roles: list[str]):
    allowed_roles_set = set(allowed_roles)
    allowed_roles_text = ", ".join(allowed_roles)

    def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permisos insuficientes. Tu rol es '{current_user.role}'. "
                    f"Se requiere uno de: {allowed_roles_text}"
                ),
            )

        return current_user

    return role_checker


def require_permission(resource: str, action: str):
    def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: DbSession,
    ) -> User:
        if current_user.id is None:
            raise credentials_exception

        statement = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                Role.is_active == True,  # noqa: E712
                Permission.resource == resource,
                Permission.action == action,
            )
            .limit(1)
        )
        if session.exec(statement).first() is not None:
            return current_user

        legacy_admin_allowed = current_user.role == "ADMIN"
        if legacy_admin_allowed:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Permisos insuficientes. "
                f"Se requiere permiso '{resource}:{action}'."
            ),
        )

    return permission_checker
