from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.base_model import utcnow
from app.core.unit_of_work import UnitOfWork
from app.modules.auth.models import DireccionEntrega
from app.modules.direcciones.repository import DireccionesRepository
from app.modules.direcciones.schemas import (
    DireccionCreate,
    DireccionPublic,
    DireccionUpdate,
)


class DireccionesService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.direcciones = DireccionesRepository(session)

    def list_by_usuario(self, usuario_id: int) -> list[DireccionPublic]:
        direcciones = self.direcciones.list_active_by_usuario(usuario_id)
        return [self._to_public(direccion) for direccion in direcciones]

    def create(self, usuario_id: int, data: DireccionCreate) -> DireccionPublic:
        with UnitOfWork(self.session):
            if data.es_principal:
                self._unset_principales(usuario_id)

            direccion = DireccionEntrega(
                usuario_id=usuario_id,
                alias=data.alias,
                linea1=data.calle,
                linea2=data.numero,
                ciudad=data.ciudad,
                provincia=data.provincia,
                codigo_postal=data.codigo_postal,
                es_principal=data.es_principal,
            )
            self.direcciones.add(direccion)

        self.direcciones.refresh(direccion)
        self._assert_single_principal(usuario_id)
        return self._to_public(direccion)

    def update(
        self,
        usuario_id: int,
        direccion_id: int,
        data: DireccionUpdate,
    ) -> DireccionPublic:
        with UnitOfWork(self.session):
            direccion = self._get_owned_or_404(usuario_id, direccion_id)

            if data.es_principal and self._has_other_principal(usuario_id, direccion_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario ya tiene una direccion principal",
                )

            direccion.alias = data.alias
            direccion.linea1 = data.calle
            direccion.linea2 = data.numero
            direccion.ciudad = data.ciudad
            direccion.provincia = data.provincia
            direccion.codigo_postal = data.codigo_postal
            direccion.es_principal = data.es_principal
            direccion.updated_at = utcnow()

            self.direcciones.add(direccion)

        self.direcciones.refresh(direccion)
        self._assert_single_principal(usuario_id)
        return self._to_public(direccion)

    def mark_principal(self, usuario_id: int, direccion_id: int) -> DireccionPublic:
        with UnitOfWork(self.session):
            direccion = self._get_owned_or_404(usuario_id, direccion_id)
            self._unset_principales(usuario_id)
            direccion.es_principal = True
            direccion.updated_at = utcnow()
            self.direcciones.add(direccion)

        self.direcciones.refresh(direccion)
        self._assert_single_principal(usuario_id)
        return self._to_public(direccion)

    def soft_delete(self, usuario_id: int, direccion_id: int) -> None:
        with UnitOfWork(self.session):
            direccion = self._get_owned_or_404(usuario_id, direccion_id)
            direccion.deleted_at = utcnow()
            direccion.updated_at = utcnow()
            direccion.es_principal = False
            self.direcciones.add(direccion)

    def _get_owned_or_404(self, usuario_id: int, direccion_id: int) -> DireccionEntrega:
        direccion = self.direcciones.get_active_owned(usuario_id, direccion_id)
        if direccion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Direccion no encontrada",
            )
        return direccion

    def _unset_principales(self, usuario_id: int) -> None:
        direcciones = self.direcciones.list_active_principales(usuario_id)
        for direccion in direcciones:
            direccion.es_principal = False
            direccion.updated_at = utcnow()
            self.direcciones.add(direccion)

    def _has_other_principal(self, usuario_id: int, direccion_id: int) -> bool:
        return self.direcciones.has_other_principal(usuario_id, direccion_id)

    def _assert_single_principal(self, usuario_id: int) -> None:
        principales = self.direcciones.list_active_principales(usuario_id)
        if len(principales) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario solo puede tener una direccion principal",
            )

    def _to_public(self, direccion: DireccionEntrega) -> DireccionPublic:
        return DireccionPublic(
            id=direccion.id or 0,
            usuario_id=direccion.usuario_id,
            alias=direccion.alias,
            calle=direccion.linea1,
            numero=direccion.linea2 or "",
            ciudad=direccion.ciudad,
            provincia=direccion.provincia,
            codigo_postal=direccion.codigo_postal,
            es_principal=direccion.es_principal,
            deleted_at=direccion.deleted_at,
        )
