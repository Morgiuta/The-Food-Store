from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.modules.auth.models import Rol, Usuario, UsuarioRol


ROLE_PERMISSIONS: dict[str, set[tuple[str, str]]] = {
    "ADMIN": {("*", "*")},
    "STOCK": {
        ("categoria", "read"),
        ("producto", "create"),
        ("producto", "read"),
        ("producto", "update"),
        ("ingrediente", "create"),
        ("ingrediente", "read"),
        ("ingrediente", "update"),
        ("ingrediente", "restore"),
        ("pedido", "read"),
        ("pedido", "update"),
    },
    "PEDIDOS": {("pedido", "read"), ("pedido", "update")},
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


def authenticate_user(session: Session, username: str, password: str) -> Usuario | None:
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_role_by_codigo(session: Session, codigo: str) -> Rol | None:
    statement = select(Rol).where(Rol.codigo == codigo.strip().upper())
    return session.exec(statement).first()


def get_user_role_codes(session: Session, usuario_id: int) -> list[str]:
    statement = select(UsuarioRol.rol_codigo).where(UsuarioRol.usuario_id == usuario_id)
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


def ensure_demo_users(session: Session) -> None:
    roles = {
        "ADMIN": "Administrador",
        "STOCK": "Stock",
        "PEDIDOS": "Pedidos",
    }

    for codigo, nombre in roles.items():
        role = get_role_by_codigo(session, codigo)
        if role is None:
            session.add(
                Rol(
                    codigo=codigo,
                    nombre=nombre,
                    descripcion=f"Rol {nombre}",
                )
            )

    session.commit()

    demo_users = [
        {
            "email": "admin",
            "nombre": "Food Store",
            "apellido": "Admin",
            "rol_codigo": "ADMIN",
            "password": "1234",
        },
        {
            "email": "stock",
            "nombre": "Gestor",
            "apellido": "Stock",
            "rol_codigo": "STOCK",
            "password": "stock",
        },
    ]

    for demo_user in demo_users:
        user = get_user_by_username(session, demo_user["email"])
        if user is None:
            user = Usuario(
                email=demo_user["email"],
                nombre=demo_user["nombre"],
                apellido=demo_user["apellido"],
                password_hash=get_password_hash(demo_user["password"]),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        if user.id is None:
            continue

        statement = select(UsuarioRol).where(
            UsuarioRol.usuario_id == user.id,
            UsuarioRol.rol_codigo == demo_user["rol_codigo"],
        )
        if session.exec(statement).first() is None:
            session.add(
                UsuarioRol(
                    usuario_id=user.id,
                    rol_codigo=demo_user["rol_codigo"],
                )
            )

    session.commit()
