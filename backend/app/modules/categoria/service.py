from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.core.utils import utcnow
from app.modules.categoria.models import Categoria
from app.modules.categoria.schemas import (
    CategoriaCreate,
    CategoriaList,
    CategoriaPublic,
    CategoriaTree,
    CategoriaUpdate,
)
from app.modules.categoria.unit_of_work import CategoriaUnitOfWork


class CategoriaService(BaseService):
    def _get_or_404(self, uow: CategoriaUnitOfWork, categoria_id: int) -> Categoria:
        categoria = uow.categorias.get_active_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )
        return categoria

    def _assert_nombre_unique(
        self,
        uow: CategoriaUnitOfWork,
        nombre: str,
        current_id: int | None = None,
    ) -> None:
        categoria = uow.categorias.get_by_nombre(nombre)
        if categoria and categoria.id != current_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoria con nombre '{nombre}'",
            )

    def _validate_parent(
        self,
        uow: CategoriaUnitOfWork,
        parent_id: int | None,
        current_id: int | None = None,
    ) -> None:
        if parent_id is None:
            return
        if current_id is not None and parent_id == current_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Una categoria no puede ser su propio padre",
            )
        parent = uow.categorias.get_active_by_id(parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria padre con id={parent_id} no encontrada",
            )

    def create(self, data: CategoriaCreate) -> CategoriaPublic:
        with CategoriaUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)
            self._validate_parent(uow, data.parent_id)
            categoria = Categoria.model_validate(data)
            uow.categorias.add(categoria)
            result = CategoriaPublic.model_validate(categoria)
        return result

    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        parent_id: int | None = None,
        filter_parent: bool = False,
    ) -> CategoriaList:
        with CategoriaUnitOfWork(self._session) as uow:
            categorias = uow.categorias.list_active(
                offset=offset,
                limit=limit,
                parent_id=parent_id,
                filter_parent=filter_parent,
            )
            total = uow.categorias.count_active(
                parent_id=parent_id,
                filter_parent=filter_parent,
            )
            result = CategoriaList(
                data=[CategoriaPublic.model_validate(categoria) for categoria in categorias],
                total=total,
            )
        return result

    def get_tree(self) -> list[CategoriaTree]:
        with CategoriaUnitOfWork(self._session) as uow:
            categorias = uow.categorias.get_all_active()

        tree_nodes = {
            cat.id: CategoriaTree.model_validate(cat)
            for cat in categorias
        }

        roots: list[CategoriaTree] = []
        for cat in categorias:
            node = tree_nodes[cat.id]
            if cat.parent_id is None:
                roots.append(node)
            else:
                parent_node = tree_nodes.get(cat.parent_id)
                if parent_node:
                    parent_node.children.append(node)
                else:
                    roots.append(node)

        return roots

    def get_by_id(self, categoria_id: int) -> CategoriaPublic:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            result = CategoriaPublic.model_validate(categoria)
        return result

    def update(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaPublic:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            patch = data.model_dump(exclude_unset=True)

            if "nombre" in patch:
                self._assert_nombre_unique(uow, patch["nombre"], current_id=categoria.id)
            if "parent_id" in patch:
                self._validate_parent(uow, patch["parent_id"], current_id=categoria.id)

            for field, value in patch.items():
                setattr(categoria, field, value)

            categoria.updated_at = utcnow()
            uow.categorias.add(categoria)
            result = CategoriaPublic.model_validate(categoria)
        return result

    def soft_delete(self, categoria_id: int) -> None:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            if uow.categorias.has_active_products(categoria_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "No se puede eliminar la categoria porque tiene "
                        "productos activos asociados"
                    ),
                )
            categoria.deleted_at = utcnow()
            categoria.updated_at = utcnow()
            uow.categorias.add(categoria)
