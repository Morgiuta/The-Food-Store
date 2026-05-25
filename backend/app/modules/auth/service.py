from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.core.unit_of_work import UnitOfWork
from app.modules.auth.models import Usuario, UsuarioRol
from app.modules.auth.schemas import UserRegister


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
    statement = select(Usuario).where(
        Usuario.deleted_at.is_(None),
        Usuario.email == login,
    )
    return session.exec(statement).first()


def get_user_by_email_any_status(session: Session, email: str) -> Usuario | None:
    statement = select(Usuario).where(Usuario.email == normalize_login(email))
    return session.exec(statement).first()


def authenticate_user(session: Session, username: str, password: str) -> Usuario | None:
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_user_role_codes(session: Session, usuario_id: int) -> list[str]:
    statement = select(UsuarioRol.rol_codigo).where(
        UsuarioRol.usuario_id == usuario_id,
        UsuarioRol.deleted_at.is_(None),
    )
    return list(session.exec(statement).all())


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
    email = normalize_login(data.email)
    nombre = data.nombre.strip()
    apellido = data.apellido.strip()

    if not nombre:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El nombre es obligatorio",
        )

    if get_user_by_email_any_status(session, email) is not None:
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
            session.add(user)
            session.flush()

            if user.id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo crear el usuario",
                )

            session.add(UsuarioRol(usuario_id=user.id, rol_codigo="CLIENT"))
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from exc

    session.refresh(user)
    return user
