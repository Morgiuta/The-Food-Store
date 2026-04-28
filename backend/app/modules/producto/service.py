from collections import defaultdict

from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.core.utils import utcnow
from app.modules.producto.models import Producto
from app.modules.producto.schemas import (
    ProductoCategoriaLink,
    ProductoCreate,
    ProductoIngredienteLink,
    ProductoList,
    ProductoPublic,
    ProductoUpdate,
)
from app.modules.producto_categoria.models import ProductoCategoria
from app.modules.producto_ingrediente.models import ProductoIngrediente
from app.modules.producto.unit_of_work import ProductoUnitOfWork


class ProductoService(BaseService):
    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.productos.get_active_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    def _apply_stock_rule(self, producto: Producto) -> None:
        producto.disponible = producto.stock_cantidad > 0

    def _assert_categoria_exists(self, uow: ProductoUnitOfWork, categoria_id: int) -> None:
        if not uow.categorias.get_active_by_id(categoria_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )

    def _assert_ingrediente_exists(self, uow: ProductoUnitOfWork, ingrediente_id: int) -> None:
        if not uow.ingredientes.get_by_id(ingrediente_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )

    def _validate_categorias(self, categorias: list[ProductoCategoriaLink]) -> None:
        seen_ids: set[int] = set()
        principal_count = 0
        for categoria in categorias:
            if categoria.categoria_id in seen_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La categoria no puede repetirse dentro del mismo producto",
                )
            seen_ids.add(categoria.categoria_id)
            if categoria.es_principal:
                principal_count += 1

        if principal_count > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El producto no puede tener mas de una categoria principal",
            )

    def _validate_ingredientes(self, ingredientes: list[ProductoIngredienteLink]) -> None:
        seen_ids: set[int] = set()
        for ingrediente in ingredientes:
            if ingrediente.ingrediente_id in seen_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El ingrediente no puede repetirse dentro del mismo producto",
                )
            seen_ids.add(ingrediente.ingrediente_id)

    def _sync_categorias(
        self,
        uow: ProductoUnitOfWork,
        producto_id: int,
        categorias: list[ProductoCategoriaLink],
    ) -> None:
        self._validate_categorias(categorias)
        existentes = {
            link.categoria_id: link
            for link in uow.producto_categorias.list_by_producto(producto_id)
        }
        incoming_ids: set[int] = set()

        for categoria in categorias:
            self._assert_categoria_exists(uow, categoria.categoria_id)
            incoming_ids.add(categoria.categoria_id)
            link = existentes.get(categoria.categoria_id)
            if link is None:
                link = ProductoCategoria(
                    producto_id=producto_id,
                    categoria_id=categoria.categoria_id,
                    es_principal=categoria.es_principal,
                )
            else:
                link.es_principal = categoria.es_principal
            uow.producto_categorias.add(link)

        for categoria_id, link in existentes.items():
            if categoria_id not in incoming_ids:
                uow.producto_categorias.session.delete(link)

        uow.producto_categorias.session.flush()

    def _sync_ingredientes(
        self,
        uow: ProductoUnitOfWork,
        producto_id: int,
        ingredientes: list[ProductoIngredienteLink],
    ) -> None:
        self._validate_ingredientes(ingredientes)
        existentes = {
            link.ingrediente_id: link
            for link in uow.producto_ingredientes.list_by_producto(producto_id)
        }
        incoming_ids: set[int] = set()

        for ingrediente in ingredientes:
            self._assert_ingrediente_exists(uow, ingrediente.ingrediente_id)
            incoming_ids.add(ingrediente.ingrediente_id)
            link = existentes.get(ingrediente.ingrediente_id)
            if link is None:
                link = ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ingrediente.ingrediente_id,
                    es_removible=ingrediente.es_removible,
                    es_opcional=ingrediente.es_opcional,
                )
            else:
                link.es_removible = ingrediente.es_removible
                link.es_opcional = ingrediente.es_opcional
            uow.producto_ingredientes.add(link)

        for ingrediente_id, link in existentes.items():
            if ingrediente_id not in incoming_ids:
                uow.producto_ingredientes.session.delete(link)

        uow.producto_ingredientes.session.flush()

    def _to_public(
        self,
        producto: Producto,
        categorias: list[ProductoCategoria],
        ingredientes: list[ProductoIngrediente],
    ) -> ProductoPublic:
        return ProductoPublic(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base,
            imagen_url=producto.imagen_url,
            imagenes_url=producto.imagenes_url,
            stock_cantidad=producto.stock_cantidad,
            tiempo_prep_min=producto.tiempo_prep_min,
            disponible=producto.disponible,
            categorias=[
                ProductoCategoriaLink(
                    categoria_id=link.categoria_id,
                    es_principal=link.es_principal,
                )
                for link in categorias
            ],
            ingredientes=[
                ProductoIngredienteLink(
                    ingrediente_id=link.ingrediente_id,
                    es_removible=link.es_removible,
                    es_opcional=link.es_opcional,
                )
                for link in ingredientes
            ],
        )

    def create(self, data: ProductoCreate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto_data = data.model_dump(exclude={"categorias", "ingredientes"})
            producto = Producto.model_validate(producto_data)
            self._apply_stock_rule(producto)
            uow.productos.add(producto)
            self._sync_categorias(uow, producto.id, data.categorias)
            self._sync_ingredientes(uow, producto.id, data.ingredientes)
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto.id),
                uow.producto_ingredientes.list_by_producto(producto.id),
            )
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoList:
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.list_active(offset=offset, limit=limit)
            total = uow.productos.count_active()
            producto_ids = [producto.id for producto in productos if producto.id is not None]
            categorias_map: dict[int, list[ProductoCategoria]] = defaultdict(list)
            ingredientes_map: dict[int, list[ProductoIngrediente]] = defaultdict(list)

            for link in uow.producto_categorias.list_by_producto_ids(producto_ids):
                categorias_map[link.producto_id].append(link)

            for link in uow.producto_ingredientes.list_by_producto_ids(producto_ids):
                ingredientes_map[link.producto_id].append(link)

            result = ProductoList(
                data=[
                    self._to_public(
                        producto,
                        categorias_map.get(producto.id, []),
                        ingredientes_map.get(producto.id, []),
                    )
                    for producto in productos
                ],
                total=total,
            )
        return result

    def get_by_id(self, producto_id: int) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                uow.producto_ingredientes.list_by_producto(producto_id),
            )
        return result

    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            patch = data.model_dump(exclude_unset=True)
            patch.pop("categorias", None)
            patch.pop("ingredientes", None)
            categorias_payload = data.categorias if "categorias" in data.model_fields_set else None
            ingredientes_payload = (
                data.ingredientes if "ingredientes" in data.model_fields_set else None
            )

            for field, value in patch.items():
                setattr(producto, field, value)

            self._apply_stock_rule(producto)
            producto.updated_at = utcnow()
            uow.productos.add(producto)

            if categorias_payload is not None:
                self._sync_categorias(uow, producto_id, categorias_payload)

            if ingredientes_payload is not None:
                self._sync_ingredientes(uow, producto_id, ingredientes_payload)

            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                uow.producto_ingredientes.list_by_producto(producto_id),
            )
        return result

    def soft_delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.deleted_at = utcnow()
            producto.updated_at = utcnow()
            uow.productos.add(producto)
