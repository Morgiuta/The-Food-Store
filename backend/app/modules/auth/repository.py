from datetime import datetime

from sqlmodel import Session, select

from app.modules.auth.models import RefreshToken, Usuario, UsuarioRol


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_active_user_by_email(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(
            Usuario.deleted_at.is_(None),
            Usuario.email == email,
        )
        return self.session.exec(statement).first()

    def get_active_user_by_id(self, usuario_id: int) -> Usuario | None:
        statement = select(Usuario).where(
            Usuario.deleted_at.is_(None),
            Usuario.id == usuario_id,
        )
        return self.session.exec(statement).first()

    def get_user_by_email_any_status(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        return self.session.exec(statement).first()

    def list_role_codes_by_usuario(self, usuario_id: int) -> list[str]:
        statement = select(UsuarioRol.rol_codigo).where(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.deleted_at.is_(None),
        )
        return list(self.session.exec(statement).all())

    def add_usuario(self, usuario: Usuario) -> Usuario:
        self.session.add(usuario)
        self.session.flush()
        return usuario

    def add_usuario_rol(self, usuario_rol: UsuarioRol) -> UsuarioRol:
        self.session.add(usuario_rol)
        self.session.flush()
        return usuario_rol

    def add_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        self.session.flush()
        return refresh_token

    def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

    def revoke_refresh_token(
        self,
        refresh_token: RefreshToken,
        revoked_at: datetime,
    ) -> RefreshToken:
        refresh_token.revoked_at = revoked_at
        self.session.add(refresh_token)
        self.session.flush()
        return refresh_token

    def refresh_usuario(self, usuario: Usuario) -> Usuario:
        self.session.refresh(usuario)
        return usuario
