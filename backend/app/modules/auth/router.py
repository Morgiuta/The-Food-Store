from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.core.rate_limit import auth_failure_rate_limiter, get_client_ip
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import (
    LogoutRequest,
    RefreshTokenRequest,
    Token,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.modules.auth.service import (
    authenticate_user,
    create_token_response_for_user,
    get_primary_role,
    refresh_token_response,
    register_client_user,
    revoke_refresh_token,
)

router = APIRouter()


def assert_auth_attempt_allowed(request: Request) -> str:
    client_ip = get_client_ip(request)
    auth_failure_rate_limiter.assert_allowed(client_ip)
    return client_ip


def record_auth_failure(client_ip: str) -> None:
    auth_failure_rate_limiter.record_failure(client_ip)


def reset_auth_failures(client_ip: str) -> None:
    auth_failure_rate_limiter.reset(client_ip)


def issue_login_response(user: Usuario, session: DbSession, response: Response) -> Token:
    token = create_token_response_for_user(session, user)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=token.expires_in,
        samesite="lax",
        secure=False,
    )
    return token


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserRegister,
    session: DbSession,
    request: Request,
) -> UserPublic:
    client_ip = assert_auth_attempt_allowed(request)
    try:
        user = register_client_user(session, data)
    except HTTPException:
        record_auth_failure(client_ip)
        raise

    reset_auth_failures(client_ip)
    return UserPublic(
        id=user.id or 0,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        full_name=user.full_name,
        role="CLIENT",
        is_active=user.is_active,
    )


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbSession,
    response: Response,
    request: Request,
) -> Token:
    client_ip = assert_auth_attempt_allowed(request)
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        record_auth_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reset_auth_failures(client_ip)
    return issue_login_response(user, session, response)


@router.post("/login", response_model=Token)
def login(
    data: UserLogin,
    session: DbSession,
    response: Response,
    request: Request,
) -> Token:
    client_ip = assert_auth_attempt_allowed(request)
    user = authenticate_user(session, data.email, data.password)
    if not user:
        record_auth_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reset_auth_failures(client_ip)
    return issue_login_response(user, session, response)


@router.post("/refresh", response_model=Token)
def refresh_token(
    data: RefreshTokenRequest,
    session: DbSession,
    response: Response,
) -> Token:
    token = refresh_token_response(session, data.refresh_token)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=token.expires_in,
        samesite="lax",
        secure=False,
    )
    return token


@router.post("/logout")
def logout(
    response: Response,
    session: DbSession,
    data: LogoutRequest | None = None,
) -> dict[str, str]:
    if data is not None and data.refresh_token:
        revoke_refresh_token(session, data.refresh_token)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"mensaje": "Sesion cerrada exitosamente"}


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
