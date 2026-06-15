from collections import defaultdict

from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.core.utils import utcnow
from app.modules.ingrediente.models import Ingrediente
from app.modules.producto.models import Producto
from app.modules.producto.schemas import (
    ProductoCategoriaLink,
    ProductoCreate,
    ProductoDisponibilidadUpdate,
    ImagenProductoUpdate,
    ProductoIngredientePublic,
    ProductoIngredienteLink,
    ProductoList,
    ProductoPublic,
    ProductoStockUpdate,
    ProductoUpdate,
)
from app.modules.producto_categoria.models import ProductoCategoria
from app.modules.producto_ingrediente.models import ProductoIngrediente
from app.modules.producto.unit_of_work import ProductoUnitOfWork
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.unidad_medida.schemas import UnidadMedidaPublic


class ProductoService(BaseService):
    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

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

    def _assert_unidad_venta_exists(
        self,
        uow: ProductoUnitOfWork,
        unidad_venta_id: int | None,
    ) -> None:
        if unidad_venta_id is None:
            return
        if uow.unidades_medida.get_active_by_id(unidad_venta_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unidad de medida con id={unidad_venta_id} no encontrada",
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
                uow.producto_categorias.delete(link)

        uow.producto_categorias.flush()

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
                    cantidad=ingrediente.cantidad,
                    unidad_medida_id=ingrediente.unidad_medida_id,
                )
            else:
                link.es_removible = ingrediente.es_removible
                link.es_opcional = ingrediente.es_opcional
                link.cantidad = ingrediente.cantidad
                link.unidad_medida_id = ingrediente.unidad_medida_id
            uow.producto_ingredientes.add(link)

        for ingrediente_id, link in existentes.items():
            if ingrediente_id not in incoming_ids:
                uow.producto_ingredientes.delete(link)

        uow.producto_ingredientes.flush()

    def recalcular_stock(self, uow: ProductoUnitOfWork, producto: Producto) -> None:
        links = uow.producto_ingredientes.list_by_producto(producto.id)
        if not links:
            return
        
        ingredientes_by_id = self._ingredientes_by_id(uow, links)
        posibles = []
        for link in links:
            ingrediente = ingredientes_by_id.get(link.ingrediente_id)
            if ingrediente and link.cantidad > 0:
                posibles.append(int(ingrediente.stock_cantidad / link.cantidad))
        
        if posibles:
            producto.stock_cantidad = min(posibles)

    def _to_public(
        self,
        producto: Producto,
        categorias: list[ProductoCategoria],
        ingredientes: list[ProductoIngrediente],
        ingredientes_by_id: dict[int, Ingrediente] | None = None,
        unidades_by_id: dict[int, UnidadMedida] | None = None,
    ) -> ProductoPublic:
        ingredientes_by_id = ingredientes_by_id or {}
        unidades_by_id = unidades_by_id or {}
        unidad_venta = (
            unidades_by_id.get(producto.unidad_venta_id)
            if producto.unidad_venta_id is not None
            else None
        )
        return ProductoPublic(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base,
            imagen_url=producto.imagen_url,
            imagenes_url=producto.imagenes_url,
            stock_cantidad=producto.stock_cantidad,
            unidad_venta_id=producto.unidad_venta_id,
            unidad_venta=(
                UnidadMedidaPublic(
                    id=unidad_venta.id or 0,
                    codigo=unidad_venta.codigo,
                    nombre=unidad_venta.nombre,
                    simbolo=unidad_venta.simbolo,
                    descripcion=unidad_venta.descripcion,
                    created_at=unidad_venta.created_at,
                    updated_at=unidad_venta.updated_at,
                    deleted_at=unidad_venta.deleted_at,
                )
                if unidad_venta is not None
                else None
            ),
            tiempo_prep_min=producto.tiempo_prep_min,
            disponible=producto.disponible,
            created_at=producto.created_at,
            updated_at=producto.updated_at,
            deleted_at=producto.deleted_at,
            categorias=[
                ProductoCategoriaLink(
                    categoria_id=link.categoria_id,
                    es_principal=link.es_principal,
                )
                for link in categorias
            ],
            ingredientes=[
                ProductoIngredientePublic(
                    ingrediente_id=link.ingrediente_id,
                    nombre=ingredientes_by_id[link.ingrediente_id].nombre,
                    descripcion=ingredientes_by_id[link.ingrediente_id].descripcion,
                    es_alergeno=ingredientes_by_id[link.ingrediente_id].es_alergeno,
                    created_at=ingredientes_by_id[link.ingrediente_id].created_at,
                    updated_at=ingredientes_by_id[link.ingrediente_id].updated_at,
                    deleted_at=ingredientes_by_id[link.ingrediente_id].deleted_at,
                    es_removible=link.es_removible,
                    es_opcional=link.es_opcional,
                    cantidad=link.cantidad,
                    unidad_medida_id=link.unidad_medida_id,
                )
                for link in ingredientes
                if link.ingrediente_id in ingredientes_by_id
            ],
        )

    def _to_ingredientes_public(
        self,
        uow: ProductoUnitOfWork,
        ingredientes: list[ProductoIngrediente],
    ) -> list[ProductoIngredientePublic]:
        ingredientes_by_id = self._ingredientes_by_id(uow, ingredientes)
        return [
            ProductoIngredientePublic(
                ingrediente_id=link.ingrediente_id,
                nombre=ingredientes_by_id[link.ingrediente_id].nombre,
                descripcion=ingredientes_by_id[link.ingrediente_id].descripcion,
                es_alergeno=ingredientes_by_id[link.ingrediente_id].es_alergeno,
                created_at=ingredientes_by_id[link.ingrediente_id].created_at,
                updated_at=ingredientes_by_id[link.ingrediente_id].updated_at,
                deleted_at=ingredientes_by_id[link.ingrediente_id].deleted_at,
                es_removible=link.es_removible,
                es_opcional=link.es_opcional,
                cantidad=link.cantidad,
                unidad_medida_id=link.unidad_medida_id,
            )
            for link in ingredientes
            if link.ingrediente_id in ingredientes_by_id
        ]

    def _ingredientes_by_id(
        self,
        uow: ProductoUnitOfWork,
        links: list[ProductoIngrediente],
    ) -> dict[int, Ingrediente]:
        ingrediente_ids = sorted({link.ingrediente_id for link in links})
        return {
            ingrediente.id: ingrediente
            for ingrediente in uow.ingredientes.list_by_ids(ingrediente_ids)
            if ingrediente.id is not None
        }

    def _unidades_by_id(
        self,
        uow: ProductoUnitOfWork,
        productos: list[Producto],
    ) -> dict[int, UnidadMedida]:
        unidad_ids = sorted(
            {
                producto.unidad_venta_id
                for producto in productos
                if producto.unidad_venta_id is not None
            }
        )
        return {
            unidad.id: unidad
            for unidad in uow.unidades_medida.list_by_ids(unidad_ids)
            if unidad.id is not None
        }

    def create(self, data: ProductoCreate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto_data = data.model_dump(exclude={"categorias", "ingredientes"})
            self._assert_unidad_venta_exists(uow, data.unidad_venta_id)
            producto = Producto.model_validate(producto_data)
            uow.productos.add(producto)
            self._sync_categorias(uow, producto.id, data.categorias)
            self._sync_ingredientes(uow, producto.id, data.ingredientes)
            self.recalcular_stock(uow, producto)
            uow.productos.flush()
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto.id),
                ingredientes := uow.producto_ingredientes.list_by_producto(producto.id),
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result

    def get_all(
        self,
        page: int = 1,
        size: int = 10,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        q: str | None = None,
        include_deleted: bool = False,
    ) -> ProductoList:
        with ProductoUnitOfWork(self._session) as uow:
            offset = (page - 1) * size
            productos = uow.productos.list_active(
                offset=offset,
                limit=size,
                categoria_id=categoria_id,
                disponible=disponible,
                q=q,
                include_deleted=include_deleted,
            )
            total = uow.productos.count_active(
                categoria_id=categoria_id,
                disponible=disponible,
                q=q,
                include_deleted=include_deleted,
            )
            producto_ids = [producto.id for producto in productos if producto.id is not None]
            categorias_map: dict[int, list[ProductoCategoria]] = defaultdict(list)
            ingredientes_map: dict[int, list[ProductoIngrediente]] = defaultdict(list)

            for link in uow.producto_categorias.list_by_producto_ids(producto_ids):
                categorias_map[link.producto_id].append(link)

            for link in uow.producto_ingredientes.list_by_producto_ids(producto_ids):
                ingredientes_map[link.producto_id].append(link)

            ingredientes_by_id = self._ingredientes_by_id(
                uow,
                [
                    link
                    for producto_links in ingredientes_map.values()
                    for link in producto_links
                ],
            )
            unidades_by_id = self._unidades_by_id(uow, productos)

            result = ProductoList(
                items=[
                    self._to_public(
                        producto,
                        categorias_map.get(producto.id, []),
                        ingredientes_map.get(producto.id, []),
                        ingredientes_by_id,
                        unidades_by_id,
                    )
                    for producto in productos
                ],
                total=total,
                page=page,
                size=size,
                pages=max(1, (total + size - 1) // size),
            )
        return result

    def get_by_id(self, producto_id: int) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            ingredientes = uow.producto_ingredientes.list_by_producto(producto_id)
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                ingredientes,
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result

    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if producto.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede editar un producto inactivo",
                )
            patch = data.model_dump(exclude_unset=True)
            patch.pop("categorias", None)
            patch.pop("ingredientes", None)
            if "unidad_venta_id" in patch:
                self._assert_unidad_venta_exists(uow, patch["unidad_venta_id"])
            categorias_payload = data.categorias if "categorias" in data.model_fields_set else None
            ingredientes_payload = (
                data.ingredientes if "ingredientes" in data.model_fields_set else None
            )

            for field, value in patch.items():
                setattr(producto, field, value)

            producto.updated_at = utcnow()
            uow.productos.add(producto)

            if categorias_payload is not None:
                self._sync_categorias(uow, producto_id, categorias_payload)

            if ingredientes_payload is not None:
                self._sync_ingredientes(uow, producto_id, ingredientes_payload)
                
            self.recalcular_stock(uow, producto)
            uow.productos.flush()

            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                ingredientes := uow.producto_ingredientes.list_by_producto(producto_id),
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result

    def update_disponibilidad(
        self,
        producto_id: int,
        data: ProductoDisponibilidadUpdate,
    ) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if producto.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede editar un producto inactivo",
                )
            producto.disponible = data.disponible
            producto.updated_at = utcnow()
            uow.productos.add(producto)
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                ingredientes := uow.producto_ingredientes.list_by_producto(producto_id),
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result

    def get_ingredientes(self, producto_id: int) -> list[ProductoIngredientePublic]:
        with ProductoUnitOfWork(self._session) as uow:
            self._get_or_404(uow, producto_id)
            result = self._to_ingredientes_public(
                uow,
                uow.producto_ingredientes.list_by_producto(producto_id),
            )
        return result

    def update_ingredientes(
        self,
        producto_id: int,
        ingredientes: list[ProductoIngredienteLink],
    ) -> list[ProductoIngredientePublic]:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if producto.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede editar un producto inactivo",
                )
            self._sync_ingredientes(uow, producto_id, ingredientes)
            self.recalcular_stock(uow, producto)
            producto.updated_at = utcnow()
            uow.productos.add(producto)
            uow.productos.flush()
            result = self._to_ingredientes_public(
                uow,
                uow.producto_ingredientes.list_by_producto(producto_id),
            )
        return result

    def update_imagenes(
        self,
        producto_id: int,
        data: ImagenProductoUpdate,
    ) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if producto.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede editar un producto inactivo",
                )
            producto.imagenes_url = data.imagenes_url
            producto.updated_at = utcnow()
            uow.productos.add(producto)
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                ingredientes := uow.producto_ingredientes.list_by_producto(producto_id),
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result

    def update_stock(self, producto_id: int, data: ProductoStockUpdate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if producto.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede editar un producto inactivo",
            )
            producto.stock_cantidad = data.stock_cantidad
            producto.updated_at = utcnow()
            uow.productos.add(producto)
            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                ingredientes := uow.producto_ingredientes.list_by_producto(producto_id),
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result

    def soft_delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            if producto.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El producto ya se encuentra dado de baja",
                )
            producto.deleted_at = utcnow()
            producto.updated_at = utcnow()
            uow.productos.add(producto)

    def restore(self, producto_id: int) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = uow.productos.get_by_id(producto_id)
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con id={producto_id} no encontrado",
                )
            producto.deleted_at = None
            producto.updated_at = utcnow()
            self.recalcular_stock(uow, producto)
            uow.productos.add(producto)
            uow.productos.flush()

            result = self._to_public(
                producto,
                uow.producto_categorias.list_by_producto(producto_id),
                ingredientes := uow.producto_ingredientes.list_by_producto(producto_id),
                self._ingredientes_by_id(uow, ingredientes),
                self._unidades_by_id(uow, [producto]),
            )
        return result
