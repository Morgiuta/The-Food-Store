from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.base_model import utcnow
from app.modules.direcciones.models import Direccion
from app.modules.direcciones.schemas import (
    DireccionCreate,
    DireccionPublic,
    DireccionUpdate,
)


class DireccionesService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_usuario(self, usuario_id: int) -> list[DireccionPublic]:
        direcciones = self.session.exec(
            select(Direccion)
            .where(
                Direccion.usuario_id == usuario_id,
                Direccion.deleted_at.is_(None),
            )
            .order_by(Direccion.es_principal.desc(), Direccion.id)
        ).all()
        return [DireccionPublic.model_validate(direccion) for direccion in direcciones]

    def create(self, usuario_id: int, data: DireccionCreate) -> DireccionPublic:
        if data.es_principal:
            self._unset_principales(usuario_id)

        direccion = Direccion(usuario_id=usuario_id, **data.model_dump())
        self.session.add(direccion)
        self.session.commit()
        self.session.refresh(direccion)
        self._assert_single_principal(usuario_id)
        return DireccionPublic.model_validate(direccion)

    def update(
        self,
        usuario_id: int,
        direccion_id: int,
        data: DireccionUpdate,
    ) -> DireccionPublic:
        direccion = self._get_owned_or_404(usuario_id, direccion_id)

        if data.es_principal and self._has_other_principal(usuario_id, direccion_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene una direccion principal",
            )

        for field, value in data.model_dump().items():
            setattr(direccion, field, value)

        self.session.add(direccion)
        self.session.commit()
        self.session.refresh(direccion)
        self._assert_single_principal(usuario_id)
        return DireccionPublic.model_validate(direccion)

    def mark_principal(self, usuario_id: int, direccion_id: int) -> DireccionPublic:
        direccion = self._get_owned_or_404(usuario_id, direccion_id)
        self._unset_principales(usuario_id)
        direccion.es_principal = True
        self.session.add(direccion)
        self.session.commit()
        self.session.refresh(direccion)
        self._assert_single_principal(usuario_id)
        return DireccionPublic.model_validate(direccion)

    def soft_delete(self, usuario_id: int, direccion_id: int) -> None:
        direccion = self._get_owned_or_404(usuario_id, direccion_id)
        direccion.deleted_at = utcnow()
        direccion.es_principal = False
        self.session.add(direccion)
        self.session.commit()

    def _get_owned_or_404(self, usuario_id: int, direccion_id: int) -> Direccion:
        direccion = self.session.exec(
            select(Direccion).where(
                Direccion.id == direccion_id,
                Direccion.usuario_id == usuario_id,
                Direccion.deleted_at.is_(None),
            )
        ).first()
        if direccion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Direccion no encontrada",
            )
        return direccion

    def _unset_principales(self, usuario_id: int) -> None:
        direcciones = self.session.exec(
            select(Direccion).where(
                Direccion.usuario_id == usuario_id,
                Direccion.deleted_at.is_(None),
                Direccion.es_principal.is_(True),
            )
        ).all()
        for direccion in direcciones:
            direccion.es_principal = False
            self.session.add(direccion)

    def _has_other_principal(self, usuario_id: int, direccion_id: int) -> bool:
        return (
            self.session.exec(
                select(Direccion).where(
                    Direccion.usuario_id == usuario_id,
                    Direccion.id != direccion_id,
                    Direccion.deleted_at.is_(None),
                    Direccion.es_principal.is_(True),
                )
            ).first()
            is not None
        )

    def _assert_single_principal(self, usuario_id: int) -> None:
        principales = self.session.exec(
            select(Direccion).where(
                Direccion.usuario_id == usuario_id,
                Direccion.deleted_at.is_(None),
                Direccion.es_principal.is_(True),
            )
        ).all()
        if len(principales) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario solo puede tener una direccion principal",
            )
