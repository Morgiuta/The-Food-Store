from datetime import timedelta
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.unit_of_work import UnitOfWork
from app.core.utils import utcnow
from app.modules.auth.models import RefreshToken, Usuario, UsuarioRol
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import Token, UserRegister


ROLE_PERMISSIONS: dict[str, set[tuple[str, str]]] = {
    "ADMIN": {("*", "*")},
    "STOCK": {
        ("producto", "read"),
        ("producto", "stock"),
        ("producto", "disponibilidad"),
        ("ingrediente", "read"),
    },
    "PEDIDOS": {("pedido", "read"), ("pedido", "update")},
    "CLIENT": {
        ("categoria", "read"),
        ("producto", "read"),
        ("ingrediente", "read"),
        ("pedido", "create"),
        ("pedido", "read"),
    },
}


def normalize_login(login: str) -> str:
    return login.strip().lower()


def get_user_by_username(session: Session, username: str) -> Usuario | None:
    login = normalize_login(username)
    return AuthRepository(session).get_active_user_by_email(login)


def get_user_by_email_any_status(session: Session, email: str) -> Usuario | None:
    return AuthRepository(session).get_user_by_email_any_status(normalize_login(email))


def authenticate_user(session: Session, username: str, password: str) -> Usuario | None:
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def hash_refresh_token(refresh_token: str) -> str:
    return sha256(refresh_token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> str:
    return token_urlsafe(48)


def create_refresh_token_for_user(session: Session, usuario_id: int) -> str:
    refresh_token = generate_refresh_token()
    expires_at = utcnow() + timedelta(days=settings.refresh_token_expire_days)
    AuthRepository(session).add_refresh_token(
        RefreshToken(
            usuario_id=usuario_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=expires_at,
        )
    )
    return refresh_token


def create_token_response_for_user(session: Session, user: Usuario) -> Token:
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "roles": get_user_role_codes(session, user.id)}
    )
    with UnitOfWork(session):
        refresh_token = create_refresh_token_for_user(session, user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


def rotate_refresh_token(session: Session, refresh_token: str) -> tuple[Usuario, str]:
    repo = AuthRepository(session)
    stored_token = repo.get_refresh_token_by_hash(hash_refresh_token(refresh_token))
    now = utcnow()
    if (
        stored_token is None
        or stored_token.revoked_at is not None
        or stored_token.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = repo.get_active_user_by_id(stored_token.usuario_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    with UnitOfWork(session):
        repo.revoke_refresh_token(stored_token, now)
        new_refresh_token = create_refresh_token_for_user(session, stored_token.usuario_id)

    return user, new_refresh_token


def refresh_token_response(session: Session, refresh_token: str) -> Token:
    user, new_refresh_token = rotate_refresh_token(session, refresh_token)
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "roles": get_user_role_codes(session, user.id)}
    )
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


def revoke_refresh_token(session: Session, refresh_token: str) -> None:
    stored_token = AuthRepository(session).get_refresh_token_by_hash(
        hash_refresh_token(refresh_token)
    )
    if stored_token is None or stored_token.revoked_at is not None:
        return

    with UnitOfWork(session):
        AuthRepository(session).revoke_refresh_token(stored_token, utcnow())


def get_user_role_codes(session: Session, usuario_id: int) -> list[str]:
    return AuthRepository(session).list_role_codes_by_usuario(usuario_id)


def user_has_role(session: Session, usuario_id: int, allowed_roles: set[str]) -> bool:
    current_roles = set(get_user_role_codes(session, usuario_id))
    return bool(current_roles.intersection(allowed_roles))


def user_has_permission(
    session: Session,
    usuario_id: int,
    resource: str,
    action: str,
) -> bool:
    for role_code in get_user_role_codes(session, usuario_id):
        permissions = ROLE_PERMISSIONS.get(role_code, set())
        if ("*", "*") in permissions or (resource, action) in permissions:
            return True
    return False


def get_primary_role(session: Session, usuario_id: int) -> str:
    roles = get_user_role_codes(session, usuario_id)
    return roles[0] if roles else "STOCK"


def split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        return "", "-"
    if len(parts) == 1:
        return parts[0], "-"
    return parts[0], " ".join(parts[1:])


def register_client_user(session: Session, data: UserRegister) -> Usuario:
    repo = AuthRepository(session)
    email = normalize_login(data.email)
    nombre = data.nombre.strip()
    apellido = data.apellido.strip()

    if not nombre:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El nombre es obligatorio",
        )

    if repo.get_user_by_email_any_status(email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    try:
        with UnitOfWork(session):
            user = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                celular=data.celular.strip() if data.celular else None,
                password_hash=get_password_hash(data.password),
            )
            repo.add_usuario(user)

            if user.id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo crear el usuario",
                )

            repo.add_usuario_rol(UsuarioRol(usuario_id=user.id, rol_codigo="CLIENT"))
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from exc

    return repo.refresh_usuario(user)
