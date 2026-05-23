from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.core.security import create_access_token
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import UserPublic
from app.modules.auth.service import authenticate_user, get_primary_role, get_user_role_codes

router = APIRouter()


@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbSession,
    response: Response,
) -> dict[str, str]:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "roles": get_user_role_codes(session, user.id)}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False,
    )
    return {"mensaje": "Login exitoso. Sesión iniciada."}


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"mensaje": "Sesión cerrada exitosamente"}


@router.get("/me", response_model=UserPublic)
def read_users_me(
    current_user: Annotated[Usuario, Depends(get_current_active_user)],
    session: DbSession,
) -> UserPublic:
    return UserPublic(
        id=current_user.id or 0,
        email=current_user.email,
        nombre=current_user.nombre,
        apellido=current_user.apellido,
        full_name=current_user.full_name,
        role=get_primary_role(session, current_user.id or 0),
        is_active=current_user.is_active,
    )
