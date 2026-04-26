from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.modules.producto_categoria.models import ProductoCategoria
from app.modules.producto_categoria.schemas import (
    ProductoCategoriaCreate,
    ProductoCategoriaList,
    ProductoCategoriaPublic,
    ProductoCategoriaUpdate,
)
from app.modules.producto_categoria.unit_of_work import ProductoCategoriaUnitOfWork


class ProductoCategoriaService(BaseService):
    def _get_link_or_404(
        self,
        uow: ProductoCategoriaUnitOfWork,
        producto_id: int,
        categoria_id: int,
    ) -> ProductoCategoria:
        link = uow.producto_categorias.get_link(producto_id, categoria_id)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Relacion producto-categoria no encontrada "
                    f"(producto_id={producto_id}, categoria_id={categoria_id})"
                ),
            )
        return link

    def _assert_producto_exists(self, uow: ProductoCategoriaUnitOfWork, producto_id: int) -> None:
        if not uow.productos.get_active_by_id(producto_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )

    def _assert_categoria_exists(self, uow: ProductoCategoriaUnitOfWork, categoria_id: int) -> None:
        if not uow.categorias.get_active_by_id(categoria_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )

    def _assert_principal_rule(
        self,
        uow: ProductoCategoriaUnitOfWork,
        producto_id: int,
        es_principal: bool,
        current_categoria_id: int | None = None,
    ) -> None:
        if not es_principal:
            return
        current = uow.producto_categorias.get_principal_for_producto(producto_id)
        if current and current.categoria_id != current_categoria_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El producto ya tiene una categoria principal",
            )

    def create(self, data: ProductoCategoriaCreate) -> ProductoCategoriaPublic:
        with ProductoCategoriaUnitOfWork(self._session) as uow:
            self._assert_producto_exists(uow, data.producto_id)
            self._assert_categoria_exists(uow, data.categoria_id)
            if uow.producto_categorias.get_link(data.producto_id, data.categoria_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La relacion producto-categoria ya existe",
                )
            self._assert_principal_rule(uow, data.producto_id, data.es_principal)
            link = ProductoCategoria.model_validate(data)
            uow.producto_categorias.add(link)
            result = ProductoCategoriaPublic.model_validate(link)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoCategoriaList:
        with ProductoCategoriaUnitOfWork(self._session) as uow:
            links = uow.producto_categorias.list_all(offset=offset, limit=limit)
            total = uow.producto_categorias.count_all()
            result = ProductoCategoriaList(
                data=[ProductoCategoriaPublic.model_validate(link) for link in links],
                total=total,
            )
        return result

    def get_by_id(self, producto_id: int, categoria_id: int) -> ProductoCategoriaPublic:
        with ProductoCategoriaUnitOfWork(self._session) as uow:
            link = self._get_link_or_404(uow, producto_id, categoria_id)
            result = ProductoCategoriaPublic.model_validate(link)
        return result

    def update(
        self,
        producto_id: int,
        categoria_id: int,
        data: ProductoCategoriaUpdate,
    ) -> ProductoCategoriaPublic:
        with ProductoCategoriaUnitOfWork(self._session) as uow:
            link = self._get_link_or_404(uow, producto_id, categoria_id)
            self._assert_principal_rule(
                uow,
                producto_id,
                data.es_principal,
                current_categoria_id=categoria_id,
            )
            link.es_principal = data.es_principal
            uow.producto_categorias.add(link)
            result = ProductoCategoriaPublic.model_validate(link)
        return result

    def delete(self, producto_id: int, categoria_id: int) -> None:
        with ProductoCategoriaUnitOfWork(self._session) as uow:
            link = self._get_link_or_404(uow, producto_id, categoria_id)
            uow.producto_categorias.session.delete(link)
            uow.producto_categorias.session.flush()
