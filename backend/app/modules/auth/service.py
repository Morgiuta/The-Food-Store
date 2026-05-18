from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.modules.auth.models import Permission, Role, RolePermission, User, UserRole


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username.strip().lower())
    return session.exec(statement).first()


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_role_by_name(session: Session, name: str) -> Role | None:
    statement = select(Role).where(Role.name == name.strip().upper())
    return session.exec(statement).first()


def get_permission(session: Session, resource: str, action: str) -> Permission | None:
    statement = select(Permission).where(
        Permission.resource == resource,
        Permission.action == action,
    )
    return session.exec(statement).first()


def ensure_demo_users(session: Session) -> None:
    resources = ("categoria", "producto", "ingrediente", "pedido")
    actions = ("create", "read", "update", "delete", "restore")

    roles = {
        "ADMIN": {
            "description": "Acceso total al sistema",
            "permissions": {(resource, action) for resource in resources for action in actions},
        },
        "STOCK": {
            "description": "Gestiona catalogo y stock",
            "permissions": {
                ("categoria", "read"),
                ("producto", "create"),
                ("producto", "read"),
                ("producto", "update"),
                ("ingrediente", "create"),
                ("ingrediente", "read"),
                ("ingrediente", "update"),
                ("ingrediente", "restore"),
            },
        },
        "PEDIDOS": {
            "description": "Consulta pedidos",
            "permissions": {("pedido", "read")},
        },
    }

    for role_name, role_data in roles.items():
        role = get_role_by_name(session, role_name)
        if role is None:
            role = Role(name=role_name, description=role_data["description"])
            session.add(role)

    for resource in resources:
        for action in actions:
            permission = get_permission(session, resource, action)
            if permission is None:
                session.add(
                    Permission(
                        resource=resource,
                        action=action,
                        description=f"{action} {resource}",
                    )
                )

    session.commit()

    for role_name, role_data in roles.items():
        role = get_role_by_name(session, role_name)
        if role is None or role.id is None:
            continue

        for resource, action in role_data["permissions"]:
            permission = get_permission(session, resource, action)
            if permission is None or permission.id is None:
                continue

            statement = select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == permission.id,
            )
            if session.exec(statement).first() is None:
                session.add(
                    RolePermission(role_id=role.id, permission_id=permission.id)
                )

    demo_users = [
        {
            "username": "admin",
            "full_name": "Food Store Admin",
            "role": "ADMIN",
            "password": "1234",
        },
        {
            "username": "stock",
            "full_name": "Gestor de Stock",
            "role": "STOCK",
            "password": "stock",
        },
    ]

    for demo_user in demo_users:
        if get_user_by_username(session, demo_user["username"]):
            user = get_user_by_username(session, demo_user["username"])
        else:
            user = User(
                username=demo_user["username"],
                full_name=demo_user["full_name"],
                role=demo_user["role"],
                hashed_password=get_password_hash(demo_user["password"]),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        role = get_role_by_name(session, demo_user["role"])
        if user is None or user.id is None or role is None or role.id is None:
            continue

        statement = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
        if session.exec(statement).first() is None:
            session.add(UserRole(user_id=user.id, role_id=role.id))

    session.commit()
