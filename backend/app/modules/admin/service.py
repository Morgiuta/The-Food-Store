from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.base_service import BaseService
from app.core.unit_of_work import UnitOfWork
from app.core.utils import utcnow
from app.modules.admin.repository import UsuarioRepository
from app.modules.admin.schemas import (
    RolPublic,
    UsuarioCreate,
    UsuarioList,
    UsuarioPublic,
    UsuarioRolUpdate,
    UsuarioUpdate,
)
from app.modules.auth.models import Usuario
from app.modules.auth.service import normalize_login
from app.core.security import get_password_hash


class UsuarioService(BaseService):
    def _repo(self) -> UsuarioRepository:
        return UsuarioRepository(self._session)

    def _get_or_404(self, repo: UsuarioRepository, usuario_id: int) -> Usuario:
        usuario = repo.get_active_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={usuario_id} no encontrado",
            )
        return usuario

    def _to_public(self, repo: UsuarioRepository, usuario: Usuario) -> UsuarioPublic:
        return UsuarioPublic(
            id=usuario.id or 0,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            roles=[
                RolPublic(
                    codigo=rol.codigo,
                    nombre=rol.nombre,
                    expires_at=usuario_rol.expires_at,
                )
                for rol, usuario_rol in repo.list_role_assignments_by_usuario(usuario.id or 0)
            ],
            is_active=usuario.is_active,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at,
        )

    def list(self, page: int = 1, size: int = 10, rol: str | None = None) -> UsuarioList:
        repo = self._repo()
        offset = (page - 1) * size
        usuarios = repo.list_active(offset=offset, limit=size, rol_nombre=rol)
        total = repo.count_active(rol_nombre=rol)
        return UsuarioList(
            items=[self._to_public(repo, usuario) for usuario in usuarios],
            total=total,
            page=page,
            size=size,
            pages=max(1, (total + size - 1) // size),
        )

    def get_by_id(self, usuario_id: int) -> UsuarioPublic:
        repo = self._repo()
        usuario = self._get_or_404(repo, usuario_id)
        return self._to_public(repo, usuario)

    def create(self, data: UsuarioCreate, asignado_por_id: int | None = None) -> UsuarioPublic:
        repo = self._repo()
        email = normalize_login(data.email)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email es obligatorio",
            )
        if repo.get_by_email_any_status(email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            )
        rol = repo.get_rol_by_nombre(data.rol_nombre)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol '{data.rol_nombre}' no encontrado",
            )

        try:
            with UnitOfWork(self._session):
                usuario = Usuario(
                    nombre=data.nombre.strip(),
                    apellido=data.apellido.strip(),
                    email=email,
                    celular=data.celular.strip() if data.celular else None,
                    password_hash=get_password_hash(data.password),
                )
                if not usuario.nombre or not usuario.apellido:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Nombre y apellido son obligatorios",
                    )
                repo.add(usuario)
                repo.replace_usuario_rol(
                    usuario.id or 0,
                    rol.codigo,
                    expires_at=data.rol_expires_at,
                    asignado_por_id=asignado_por_id,
                )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            ) from exc

        return self._to_public(repo, usuario)

    def update(self, usuario_id: int, data: UsuarioUpdate) -> UsuarioPublic:
        repo = self._repo()
        usuario = self._get_or_404(repo, usuario_id)
        patch = data.model_dump(exclude_unset=True)

        try:
            with UnitOfWork(self._session):
                if "email" in patch:
                    email = normalize_login(patch["email"])
                    if not email:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="El email es obligatorio",
                        )
                    existing = repo.get_by_email_any_status(email)
                    if existing and existing.id != usuario.id:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Ya existe un usuario con ese email",
                        )
                    usuario.email = email

                if "nombre" in patch:
                    nombre = patch["nombre"].strip()
                    if not nombre:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="El nombre es obligatorio",
                        )
                    usuario.nombre = nombre

                if "apellido" in patch:
                    apellido = patch["apellido"].strip()
                    if not apellido:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="El apellido es obligatorio",
                        )
                    usuario.apellido = apellido

                if "celular" in patch:
                    usuario.celular = patch["celular"].strip() if patch["celular"] else None

                if "password" in patch:
                    usuario.password_hash = get_password_hash(patch["password"])

                usuario.updated_at = utcnow()
                repo.add(usuario)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            ) from exc

        return self._to_public(repo, usuario)

    def soft_delete(self, usuario_id: int) -> None:
        repo = self._repo()
        usuario = self._get_or_404(repo, usuario_id)
        with UnitOfWork(self._session):
            usuario.deleted_at = utcnow()
            usuario.updated_at = utcnow()
            repo.add(usuario)

    def assign_rol(
        self,
        usuario_id: int,
        data: UsuarioRolUpdate,
        asignado_por_id: int | None = None,
    ) -> UsuarioPublic:
        repo = self._repo()
        usuario = self._get_or_404(repo, usuario_id)
        rol = repo.get_rol_by_nombre(data.rol_nombre)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol '{data.rol_nombre}' no encontrado",
            )

        with UnitOfWork(self._session):
            repo.replace_usuario_rol(
                usuario.id or 0,
                rol.codigo,
                expires_at=data.expires_at,
                asignado_por_id=asignado_por_id,
            )
            usuario.updated_at = utcnow()
            repo.add(usuario)
        return self._to_public(repo, usuario)
