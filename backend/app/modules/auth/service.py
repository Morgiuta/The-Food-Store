from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.modules.auth.models import User


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username.strip().lower())
    return session.exec(statement).first()


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def ensure_demo_users(session: Session) -> None:
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
            continue

        session.add(
            User(
                username=demo_user["username"],
                full_name=demo_user["full_name"],
                role=demo_user["role"],
                hashed_password=get_password_hash(demo_user["password"]),
            )
        )

    session.commit()
