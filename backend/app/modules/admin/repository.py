from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.core.utils import utcnow
from app.modules.auth.models import Rol, Usuario, UsuarioRol


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

    def get_active_by_id(self, usuario_id: int) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(
                Usuario.id == usuario_id,
                Usuario.deleted_at.is_(None),
            )
        ).first()

    def get_by_email_any_status(self, email: str) -> Usuario | None:
        return self.session.exec(select(Usuario).where(Usuario.email == email)).first()

    def get_rol_by_nombre(self, rol_nombre: str) -> Rol | None:
        normalized = rol_nombre.strip()
        return self.session.exec(
            select(Rol).where(
                Rol.deleted_at.is_(None),
                or_(
                    func.lower(Rol.nombre) == normalized.lower(),
                    func.upper(Rol.codigo) == normalized.upper(),
                )
            )
        ).first()

    def list_active(
        self,
        offset: int,
        limit: int,
        rol_nombre: str | None = None,
    ) -> list[Usuario]:
        statement = select(Usuario).where(Usuario.deleted_at.is_(None))

        if rol_nombre:
            normalized = rol_nombre.strip()
            statement = (
                statement.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id)
                .join(Rol, Rol.codigo == UsuarioRol.rol_codigo)
                .where(
                    UsuarioRol.deleted_at.is_(None),
                    Rol.deleted_at.is_(None),
                    or_(
                        func.lower(Rol.nombre) == normalized.lower(),
                        func.upper(Rol.codigo) == normalized.upper(),
                    )
                )
            )

        return list(
            self.session.exec(
                statement.order_by(Usuario.id).offset(offset).limit(limit)
            ).all()
        )

    def count_active(self, rol_nombre: str | None = None) -> int:
        statement = select(func.count(Usuario.id)).where(Usuario.deleted_at.is_(None))

        if rol_nombre:
            normalized = rol_nombre.strip()
            statement = (
                select(func.count(func.distinct(Usuario.id)))
                .select_from(Usuario)
                .join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id)
                .join(Rol, Rol.codigo == UsuarioRol.rol_codigo)
                .where(
                    Usuario.deleted_at.is_(None),
                    UsuarioRol.deleted_at.is_(None),
                    Rol.deleted_at.is_(None),
                    or_(
                        func.lower(Rol.nombre) == normalized.lower(),
                        func.upper(Rol.codigo) == normalized.upper(),
                    ),
                )
            )

        return int(self.session.exec(statement).one())

    def list_roles_by_usuario(self, usuario_id: int) -> list[Rol]:
        return list(
            self.session.exec(
                select(Rol)
                .join(UsuarioRol, UsuarioRol.rol_codigo == Rol.codigo)
                .where(
                    UsuarioRol.usuario_id == usuario_id,
                    UsuarioRol.deleted_at.is_(None),
                    or_(UsuarioRol.expires_at.is_(None), UsuarioRol.expires_at > utcnow()),
                    Rol.deleted_at.is_(None),
                )
                .order_by(Rol.codigo)
            ).all()
        )

    def list_role_assignments_by_usuario(self, usuario_id: int) -> list[tuple[Rol, UsuarioRol]]:
        return list(
            self.session.exec(
                select(Rol, UsuarioRol)
                .join(Rol, UsuarioRol.rol_codigo == Rol.codigo)
                .where(
                    UsuarioRol.usuario_id == usuario_id,
                    UsuarioRol.deleted_at.is_(None),
                    or_(UsuarioRol.expires_at.is_(None), UsuarioRol.expires_at > utcnow()),
                    Rol.deleted_at.is_(None),
                )
                .order_by(UsuarioRol.rol_codigo)
            ).all()
        )

    def replace_usuario_rol(
        self,
        usuario_id: int,
        rol_codigo: str,
        expires_at=None,
        asignado_por_id: int | None = None,
    ) -> None:
        current_roles = self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.deleted_at.is_(None)
            )
        ).all()
        for current_role in current_roles:
            self.session.delete(current_role)

        self.session.flush()
        self.session.add(
            UsuarioRol(
                usuario_id=usuario_id,
                rol_codigo=rol_codigo,
                expires_at=expires_at,
                asignado_por_id=asignado_por_id,
            )
        )
        self.session.flush()
