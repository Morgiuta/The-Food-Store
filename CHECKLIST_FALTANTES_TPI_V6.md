# Food Store - Checklist de Faltantes TPI v6

Este documento compara el proyecto actual contra `TPI_PROG4_FOOD_STORE_v6.md` y deja una checklist accionable para completar lo que falta.

## Regla Arquitectonica Obligatoria

Correccion del profesor:

> No deben existir consultas a la DB en la capa service.

Esto significa que:

- [x] Ningun `service.py` debe usar `select(...)`, `session.exec(...)`, queries SQLAlchemy/SQLModel ni acceder directo a tablas para leer datos.
- [x] La capa `service` solo debe orquestar reglas de negocio.
- [x] Toda consulta a DB debe estar en `repository.py`.
- [ ] Las transacciones deben manejarse con Unit of Work cuando la operacion modifique mas de una entidad.
- [ ] El flujo correcto debe ser: `router -> service -> uow/repository -> model`.
- [ ] Revisar servicios actuales que violan o pueden violar esta regla:
  - [x] `backend/app/modules/direcciones/service.py`: usa `select(...)` y `session.exec(...)` directamente.
  - [x] `backend/app/modules/auth/service.py`: usa `select(...)` directamente.
  - [x] `backend/app/modules/ventas/service.py`: usaba `select(...)` directamente.
  - [x] `backend/app/modules/admin/service.py`: parece mejor encaminado porque usa repository, pero revisar que no filtre/query directo en service.
  - [x] `backend/app/modules/pedidos/service.py`: usa repository para muchas cosas, mantener ese criterio y mover cualquier acceso directo si aparece.

## Estado General

El proyecto ya tiene una base funcional: auth con JWT por cookie, roles, productos, categorias, ingredientes, direcciones, pedidos, historial, carrito frontend, panel admin y algunas metricas.

Pero frente al documento v6 faltan integraciones grandes y hay diferencias de contrato importantes.

## Backend

### Auth, JWT, RBAC y Rate Limit

- [x] Implementar refresh token real.
  - [x] Crear funcion para generar refresh token.
  - [x] Guardar hash del refresh token en tabla `refresh_tokens`.
  - [x] Agregar expiracion de 7 dias.
  - [x] Agregar revocacion con `revoked_at`.
  - [x] Endpoint `POST /api/v1/auth/refresh`.
  - [x] Endpoint `POST /api/v1/auth/logout` debe revocar refresh token, no solo borrar cookie.
  - [x] `TokenResponse` debe incluir `access_token`, `refresh_token`, `token_type`, `expires_in`.

- [x] Implementar rate limiting en login/register.
  - [x] Maximo 5 intentos fallidos por IP.
  - [x] Ventana de 15 minutos.
  - [x] Responder `429 Too Many Requests`.
  - [x] Agregar header `Retry-After`.
  - [x] Evitar queries en service: guardar/acceder intentos desde repository o mecanismo externo.

- [ ] Revisar permisos RBAC.
  - [ ] `CLIENT` no deberia poder crear pedidos como ADMIN/STOCK/PEDIDOS.
  - [ ] `STOCK` no deberia acceder a datos financieros ni crear pedidos administrativos.
  - [ ] `PEDIDOS` no deberia gestionar productos/categorias.
  - [ ] Validar endpoints contra la matriz del documento.

### Usuarios

- [ ] Separar modulo `usuarios` o dejar documentado que vive bajo `admin/usuarios`.
- [ ] CRUD completo segun especificacion.
- [ ] Soft delete.
- [ ] Asignacion de roles con `expires_at`.
- [ ] No consultar DB desde service.
- [ ] Agregar endpoints y schemas alineados al documento.

### Direcciones

- [x] Mover consultas directas de `DireccionesService` a un repository.
  - [x] `list_by_usuario`.
  - [x] `_get_owned_or_404`.
  - [x] `_unset_principales`.
  - [x] `_has_other_principal`.
  - [x] `_assert_single_principal`.

- [ ] Validar que solo exista una direccion principal por usuario.
- [ ] Mantener `PATCH /principal`.
- [ ] Revisar permisos: normalmente solo propietario o ADMIN.

### Categorias

- [ ] Revisar contrato contra documento.
  - [ ] `GET /api/v1/categorias`.
  - [ ] `GET /api/v1/categorias/tree`.
  - [ ] Crear/editar/borrar soft delete.

- [ ] Cloudinary para imagen de categoria.
  - [ ] Campo `imagen_url` ya existe.
  - [ ] Falta upload real.
  - [ ] Falta endpoint para actualizar imagen segun contrato.

- [ ] Jerarquia.
  - [ ] Validar que no permita ciclos.
  - [ ] Si el documento exige CTE recursiva, implementar consulta en repository.

### Productos

- [ ] Agregar entidad `UnidadMedida`.
  - [ ] Modelo `UnidadMedida`.
  - [ ] Migration.
  - [ ] Repository.
  - [ ] Router CRUD/listado si corresponde.
  - [ ] Seed obligatorio: `kg`, `g`, `L`, `ml`, `ud`, `porciones`.

- [ ] Agregar `unidad_venta_id` en `Producto`.
  - [ ] FK hacia `UnidadMedida`.
  - [ ] Incluir en schemas create/update/read.
  - [ ] Mostrar simbolo en frontend.

- [ ] Revisar imagenes.
  - [ ] Actualmente hay `imagen_url` e `imagenes_url`.
  - [ ] Definir si se mantiene compatibilidad o se usa solo `imagenes_url`.
  - [ ] Agregar `PATCH /api/v1/productos/{id}/imagenes`.
  - [ ] Integrar con `/uploads`.

- [ ] Revisar endpoints.
  - [ ] Documento pide `PUT /productos/{id}` para actualizar; proyecto usa `PATCH`.
  - [ ] Documento pide `GET /productos/{id}/ingredientes`.
  - [ ] Documento pide `POST /productos/{id}/ingredientes`.

- [ ] Stock.
  - [ ] Mantener `PATCH /stock`.
  - [ ] Validar permisos ADMIN/STOCK.
  - [ ] Validar que `disponible` sea independiente del stock, salvo regla explicita.

### Ingredientes

- [ ] Alinear modelo con documento.
  - [ ] Documento pide `stock_cantidad`.
  - [ ] Proyecto usa `stock_actual`.
  - [ ] Documento pide `UnidadMedida`.
  - [ ] Proyecto usa `unidad` string.

- [ ] ProductoIngrediente.
  - [ ] Documento pide `cantidad`.
  - [ ] Proyecto usa `cantidad_requerida`.
  - [ ] Documento pide `unidad_medida_id`.
  - [ ] Agregar FK a `UnidadMedida`.
  - [ ] Mantener `es_removible`.
  - [ ] Revisar si `es_opcional` queda como extra o se elimina.

### Pedidos y FSM

- [x] Corregir maquina de estados a 5 estados.
  - [x] Eliminar `EN_CAMINO`.
  - [x] Estados validos: `PENDIENTE`, `CONFIRMADO`, `EN_PREP`, `ENTREGADO`, `CANCELADO`.
  - [x] Transicion `EN_PREP -> ENTREGADO`.
  - [x] `ENTREGADO` y `CANCELADO` terminales.

- [x] Corregir seed de estados.
  - [x] Quitar `EN_CAMINO`.
  - [x] Ordenar estados segun documento.

- [x] Revisar endpoints.
  - [x] Documento pide `PATCH /api/v1/pedidos/{id}/estado`.
  - [x] Documento pide `GET /api/v1/pedidos/{id}/historial`.
  - [x] Documento pide `DELETE /api/v1/pedidos/{id}` para cancelar propio.
  - [x] Proyecto tiene `PATCH /cancelar`; decidir si se mantiene como extra o se alinea.

- [ ] Audit trail append-only.
  - [x] Verificar que ninguna capa haga UPDATE/DELETE sobre `HistorialEstadoPedido`.
  - [ ] Agregar tests.
  - [x] Documentar regla.

- [x] Snapshot.
  - [x] `nombre_snapshot` OK.
  - [x] `precio_snapshot` OK.
  - [x] Revisar nombre `subtotal_snapshot` vs documento `subtotal_snap`.
  - [x] Confirmar que no se recalcula luego de creado.

- [x] Personalizacion.
  - [x] Documento pide lista de IDs de ingredientes removidos.
  - [x] Proyecto usa JSON/dict.
  - [x] Alinear schema backend y tipos frontend.

- [ ] WebSocket post-commit.
  - [ ] Al cambiar estado exitosamente, emitir evento despues del commit.
  - [ ] No emitir dentro de la transaccion.

### Pagos y MercadoPago

- [ ] Crear modulo `pagos`.
  - [ ] `backend/app/modules/pagos/router.py`.
  - [ ] `backend/app/modules/pagos/service.py`.
  - [ ] `backend/app/modules/pagos/repository.py`.
  - [ ] `backend/app/modules/pagos/schemas.py`.
  - [ ] No hacer queries desde service.

- [ ] Agregar dependencia backend.
  - [ ] `mercadopago`.
  - [ ] Variables `.env`: `MP_ACCESS_TOKEN`, `MP_PUBLIC_KEY`, `MP_NOTIFICATION_URL`.

- [ ] Endpoint `POST /api/v1/pagos/crear`.
  - [ ] Recibir pedido o datos necesarios.
  - [ ] Crear preferencia/pago en MercadoPago.
  - [ ] Guardar registro `Pago`.
  - [ ] Generar `idempotency_key`.
  - [ ] Usar `external_reference` con referencia del pedido.
  - [ ] Retornar datos necesarios al frontend.

- [ ] Endpoint `POST /api/v1/pagos/webhook`.
  - [ ] Validar firma si se implementa.
  - [ ] Consultar estado del pago en MercadoPago.
  - [ ] Actualizar `Pago.mp_status`.
  - [ ] Actualizar pedido a `CONFIRMADO` si pago aprobado.
  - [ ] Cancelar/rechazar segun corresponda.
  - [ ] Emitir WebSocket post-commit.

- [ ] Endpoint `GET /api/v1/pagos/{pedido_id}`.
  - [ ] Solo propietario o ADMIN.
  - [ ] Devolver pago asociado.

- [ ] Seed de formas de pago.
  - [x] `MERCADOPAGO`.
  - [x] `EFECTIVO`.
  - [x] `TRANSFERENCIA`.
  - [x] Corregir actual `TARJETA` si no corresponde.

### Uploads y Cloudinary

- [ ] Crear modulo `uploads`.
  - [ ] `backend/app/modules/uploads/router.py`.
  - [ ] `backend/app/modules/uploads/service.py`.
  - [ ] `backend/app/modules/uploads/schemas.py`.

- [ ] Agregar dependencia backend.
  - [ ] `cloudinary`.
  - [ ] Variables `.env`: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.

- [ ] Endpoint `POST /api/v1/uploads/imagen`.
  - [ ] Recibir `multipart/form-data`.
  - [ ] Validar MIME: jpg, jpeg, png, webp.
  - [ ] Validar maximo 5 MB.
  - [ ] Subir a Cloudinary.
  - [ ] Devolver `secure_url`, `public_id`, `width`, `height`, `format`, `resource_type`.

- [ ] Endpoint `DELETE /api/v1/uploads/imagen/{public_id}`.
  - [ ] Eliminar por `public_id`.
  - [ ] URL encode/decode correcto.
  - [ ] Solo ADMIN.

### WebSocket

- [ ] Crear `backend/app/core/ws_manager.py`.
  - [ ] Pool de conexiones.
  - [ ] Canal admin/pedidos.
  - [ ] Broadcast por pedido.
  - [ ] Manejo de desconexiones.

- [ ] Crear endpoint WS.
  - [ ] `WS /ws/pedidos`.
  - [ ] Autenticacion por query param `token`.
  - [ ] Solo ADMIN/PEDIDOS para feed global.

- [ ] Integrar con pedidos y pagos.
  - [ ] Cambio de estado manual.
  - [ ] Cancelacion.
  - [ ] Confirmacion de pago.
  - [ ] Emitir siempre despues del commit.

### Estadisticas

- [ ] Crear modulo `estadisticas`.
  - [ ] `router.py`.
  - [ ] `service.py`.
  - [ ] `repository.py`.
  - [ ] `schemas.py`.

- [ ] Endpoints requeridos.
  - [ ] `GET /api/v1/estadisticas/resumen`.
  - [ ] `GET /api/v1/estadisticas/ventas`.
  - [ ] `GET /api/v1/estadisticas/productos-top`.
  - [ ] `GET /api/v1/estadisticas/pedidos-por-estado`.
  - [ ] `GET /api/v1/estadisticas/ingresos`.

- [ ] Reglas.
  - [ ] Excluir `CANCELADO`.
  - [ ] Usar `subtotal_snapshot`/`subtotal_snap` para ingresos por producto.
  - [ ] Contar ingresos solo con pagos `approved`.
  - [ ] Usar `Decimal`, no float.
  - [ ] Queries solo en repository.

### API y Contratos

- [x] Evitar doble inclusion de routers.
  - [x] Actualmente hay endpoints con y sin `/api/v1`.
  - [x] Dejar solo `/api/v1` si se sigue el documento.

- [x] Paginacion.
  - [x] Documento usa `page` y `size`.
  - [x] Proyecto mezcla `page/limit` y `offset/limit`.
  - [x] Unificar.

- [ ] Errores RFC 7807.
  - [ ] Estandarizar formato `{ detail, code, field }`.
  - [ ] Usar excepciones propias si conviene.

- [ ] OpenAPI.
  - [ ] Revisar responses, status codes y schemas.

### Seed Data

- [x] Roles: `ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`.
- [x] Estados: 5 estados sin `EN_CAMINO`.
- [x] Formas de pago: `MERCADOPAGO`, `EFECTIVO`, `TRANSFERENCIA`.
- [x] Unidades de medida: `kg`, `g`, `L`, `ml`, `ud`, `porciones`.
- [x] Admin obligatorio:
  - [x] Email: `admin@foodstore.com`.
  - [x] Password: `Admin1234!`.
  - [x] Rol: `ADMIN`.

## Frontend

### Dependencias

- [ ] Agregar `@mercadopago/sdk-react`.
- [ ] Agregar libreria de graficos.
  - [ ] `recharts` o `react-chartjs-2`.
- [ ] Evaluar TanStack Form si se quiere cumplir literal con el documento.

### Auth Frontend

- [x] Adaptar `authStore` a `TokenResponse` completo.
- [x] Manejar refresh token.
- [x] Interceptor Axios debe intentar refresh antes de hacer logout.
- [ ] Revisar persistencia: documento dice persistir solo access token; proyecto persiste usuario e `isAuthenticated`.
- [ ] Alinear cookies/headers con backend.

### Carrito

- [ ] Agregar personalizaciones.
  - [ ] Ingredientes removidos.
  - [ ] Validar removibles.
  - [ ] Persistir personalizacion en localStorage.

- [ ] Validar stock antes de checkout.
- [ ] Confirmar formato enviado a backend.

### Checkout y MercadoPago

- [ ] Quitar placeholder "Proximamente".
- [ ] Usar forma de pago `MERCADOPAGO` o la que se defina en backend.
- [ ] Integrar SDK MercadoPago.
- [ ] Crear pago/preferencia llamando `POST /api/v1/pagos/crear`.
- [ ] Manejar resultado aprobado, pendiente, rechazado.
- [ ] Mostrar errores de pago.
- [ ] Consultar estado del pedido/pago despues del checkout.

### Productos y Categorias

- [ ] Upload de imagenes.
  - [ ] Formulario de producto debe subir imagen a `/uploads/imagen`.
  - [ ] Guardar `secure_url` en `imagenes_url`.
  - [ ] Permitir eliminar imagen y llamar DELETE upload.

- [ ] Categorias.
  - [ ] Subir imagen de categoria.
  - [ ] Guardar `imagen_url`.

- [ ] Unidad de medida.
  - [ ] Mostrar simbolo en cards.
  - [ ] Permitir elegir unidad de venta en formulario admin.

### Pedidos

- [ ] Cambiar polling por WebSocket.
  - [ ] Crear `useOrderStatusWS`.
  - [ ] Crear `useAdminOrdersFeed`.
  - [ ] Crear `wsStore`.
  - [ ] Reconectar con backoff.
  - [ ] Invalidar React Query cuando llegue evento.

- [ ] Alinear estados.
  - [x] Quitar `EN_CAMINO`.
  - [x] Cambiar UI para `EN_PREP -> ENTREGADO`.
  - [ ] Ajustar colores y textos.

- [ ] Historial.
  - [ ] Consumir `GET /pedidos/{id}/historial` si se implementa.

### Dashboard y Estadisticas

- [ ] Dejar de calcular metricas pesadas en frontend.
- [ ] Consumir modulo `/estadisticas`.
- [ ] Agregar graficos:
  - [ ] Ventas por periodo.
  - [ ] Top productos.
  - [ ] Pedidos por estado.
  - [ ] Ingresos por forma de pago.
  - [ ] KPI cards.

### Stores Zustand

- [ ] Mantener `authStore`.
- [ ] Mantener `cartStore`.
- [ ] Agregar `wsStore`.
- [ ] Evaluar `paymentStore`.
- [ ] Evaluar `uiStore`.
- [ ] Usar selectors para evitar renders innecesarios.

## Tests

- [ ] Crear carpeta `backend/tests`.
- [ ] Crear `conftest.py`.
- [ ] Tests auth.
  - [ ] Register OK.
  - [ ] Login OK.
  - [ ] Login invalido.
  - [ ] Refresh token.
  - [ ] Logout revoca token.
  - [ ] Rate limit.

- [ ] Tests pedidos.
  - [ ] Crear pedido OK.
  - [ ] Stock insuficiente.
  - [ ] Transicion valida.
  - [ ] Transicion invalida.
  - [ ] Estado terminal no permite avanzar.
  - [ ] Cancelacion con motivo obligatorio.
  - [ ] Historial append-only.

- [ ] Tests pagos.
  - [ ] Crear pago.
  - [ ] Idempotency key.
  - [ ] Webhook aprobado confirma pedido.
  - [ ] Webhook rechazado cancela o marca rechazo.

- [ ] Tests estadisticas.
  - [ ] Excluir cancelados.
  - [ ] Usar pagos approved.
  - [ ] Top productos usa snapshot.

- [ ] Tests WebSocket.
  - [ ] Conexion autorizada.
  - [ ] Conexion rechazada por rol.
  - [ ] Broadcast al cambiar estado.

## Orden de Trabajo Recomendado

1. [x] Refactor de arquitectura: sacar queries de services y moverlas a repositories.
2. [x] Corregir contratos chicos: seed, estados, formas de pago, `/api/v1`, paginacion.
3. [x] Completar auth: refresh token, logout real, rate limit.
4. [ ] Corregir pedidos FSM e historial.
5. [x] Agregar UnidadMedida.
6. [ ] Implementar Cloudinary/uploads.
7. [ ] Implementar MercadoPago/pagos.
8. [ ] Implementar WebSocket.
9. [ ] Implementar estadisticas y dashboard con graficos.
10. [ ] Agregar tests.
