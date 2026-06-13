# Guía de Estudio y Defensa: Backend FastAPI

Esta guía está diseñada para que puedas defender de forma oral y técnica el proyecto de backend (Catálogo de Productos y Pedidos) frente a una mesa evaluadora. 

---

## 1. Resumen general del proyecto

* **Problema que resuelve:** Es el sistema backend para la gestión de un catálogo de productos, inventario de ingredientes, carrito/pedidos de clientes y administración.
* **Entidades principales:** `Usuario`, `Producto`, `Categoria`, `Ingrediente`, `Pedido`, `DetallePedido`, `DireccionEntrega`.
* **Funcionalidades:** ABM (Alta, Baja, Modificación) de productos con categorías e ingredientes, gestión de stock, roles de usuario, carrito de compras (pedidos) y autenticación.
* **Arquitectura:** Arquitectura en capas limpia (Clean Architecture/N-Tier) guiada por el Dominio (Modular).
* **Tecnologías:** Python, FastAPI, SQLModel (SQLAlchemy + Pydantic), PostgreSQL, JWT (Passlib/Bcrypt), Alembic.
* **Patrones de diseño:** Dependency Injection (nativo de FastAPI), Service Pattern, Repository Pattern, Unit of Work (UoW).

---

## 2. Estructura del repositorio

El backend está organizado de forma **Modular por Dominio** dentro de `app/modules/`.

* `backend/main.py`: Punto de entrada de la aplicación. Configura CORS, Lifespan y monta el router principal.
* `backend/alembic/`: Archivos de configuración y versiones de migraciones de la base de datos.
* `backend/app/core/`: Componentes transversales de infraestructura y abstracciones base (`base_model.py`, `base_repository.py`, `config.py`, `database.py`, `security.py`, `unit_of_work.py`).
* `backend/app/shared/`: Utilidades o dependencias compartidas (`dependencies.py`).
* `backend/app/api/router.py`: Router principal que agrupa e incluye todos los sub-routers de cada módulo.
* `backend/app/modules/`: **El corazón del sistema.** Está dividido por entidades del negocio (ej. `auth`, `producto`, `categoria`, `pedidos`, `ventas`).
    * Dentro de cada módulo (ej. `producto/`) encontramos:
        * `models.py`: Entidades SQLAlchemy (SQLModel).
        * `schemas.py`: DTOs / Pydantic models para Request y Response.
        * `repository.py`: Interacción con la BD de ese dominio.
        * `service.py`: Lógica de negocio.
        * `router.py`: Endpoints expuestos de FastAPI.
        * `unit_of_work.py`: Controlador transaccional para el módulo.

**¿Por qué esta estructura?** 
Favorece la **Cohesión**: todo lo relacionado con "Producto" está en la misma carpeta. Si el proyecto crece, es mucho más fácil dividirlo en microservicios.

---

## 3. Arquitectura del backend

El proyecto utiliza una **Arquitectura en Capas**.
* **Capa de Presentación / API:** `Routers` de FastAPI.
* **Capa de Lógica de Negocio:** `Services`.
* **Capa de Acceso a Datos:** `Repositories` y `Unit of Work`.
* **Capa de Dominio / Infra:** `Models` (SQLModel).

**Flujo de una petición HTTP:**
1. **Request HTTP** llega al `Router` (ej. `POST /productos`).
2. **FastAPI** valida el body usando un `Schema` (ej. `ProductoCreate`) y usa Inyección de Dependencias (`Depends`) para obtener el `Service`.
3. El `Router` llama al método del `Service` (ej. `svc.create(data)`).
4. El `Service` instancia el `Unit of Work`, abre la transacción y ejecuta la **Lógica de Negocio** (validar reglas, stock, etc.).
5. El `Service` llama al `Repository` correspondiente dentro del UoW para interactuar con la Base de Datos.
6. El `Repository` usa el `Model SQLAlchemy` y traduce objetos a SQL.
7. El `Service` confirma (Commit) o revierte (Rollback) la transacción vía el UoW.
8. El `Service` convierte el `Model` en un `Schema` de respuesta y lo devuelve al `Router`.
9. **FastAPI** envía la **Response JSON** al Cliente.

**Ventajas:** Facilita el Testing (podes mockear el Repository para probar el Service), respeta el Principio de Responsabilidad Única (SOLID) y permite cambiar la DB sin tocar las reglas de negocio.
**Riesgos si no existieran Services/Repos:** El Router tendría lógica SQL mezclada con validaciones HTTP. Sería inMantenible, inTesteable y vulnerable a errores.

---

## 4. FastAPI: routers, endpoints y dependencias

**Ejemplo de Endpoint:** `POST /productos/` (en `app/modules/producto/router.py`)
* **Método:** `POST`
* **Body esperado:** `ProductoCreate` (valida precio >=0, largo de nombre, etc).
* **Response esperado:** `ProductoPublic` (status 201).
* **Dependencias:** `_current_user = Depends(require_roles("ADMIN"))` (valida JWT y rol) y `svc: ProductoService = Depends(get_producto_service)`.
* **Lógica:** Recibe el input y delega directamente `return svc.create(data)`.

**Inyección de dependencias (`Depends`):**
FastAPI utiliza `Depends()` para resolver dependencias *antes* de entrar al endpoint. 
* Por ejemplo, `DbSession` en `get_producto_service(session: DbSession)` recibe la conexión a la base de datos automáticamente porque `DbSession` está definido como `Annotated[Session, Depends(get_session)]`.
* Esto permite reutilizar lógica (como verificar el token) y no tener que instanciar manualmente las clases.

---

## 5. Services

El **Service** es el dueño de las **Reglas de Negocio**.
Analizando `ProductoService` (`app/modules/producto/service.py`):
* **Responsabilidad:** Valida que las categorías y los ingredientes no se repitan, recalcula el stock disponible en base a los ingredientes requeridos, maneja el Soft Delete.
* **Uso de UoW:** Inicializa `with ProductoUnitOfWork(self._session) as uow:` garantizando que todas las tablas afectadas (Producto, ProductoCategoria, ProductoIngrediente) se guarden juntas o fallen juntas.
* **¿Por qué separar Service y Repository?** El Repository *solo* sabe hablar SQL (ej. "guardar esto en la tabla"). El Service entiende el negocio (ej. "si el stock llega a 0, cambiar 'disponible' a False").

---

## 6. Repositories

Analizando `ProductoRepository` (`app/modules/producto/repository.py`):
* **Hereda de:** `BaseRepository[Producto]`, lo que le da métodos gratis (`get_by_id`, `add`, `get_all`).
* **Responsabilidad:** Encapsula SQLAlchemy. Abstrae queries complejas.
* **Ejemplo:** `get_active_by_id(producto_id)` filtra explícitamente productos donde `deleted_at IS NULL`. También encapsula la búsqueda con paginación y filtros dinámicos en `list_active()`.
* **Diferencia con el Service:** El repo no lanza excepciones HTTP (como 404), solo devuelve `None` o listas vacías. El Service decide si `None` significa 404 o no.

---

## 7. Unit of Work (UoW)

Analizando `app/core/unit_of_work.py` y `ProductoUnitOfWork`:
* **¿Qué es?** Es un patrón que agrupa múltiples operaciones de repositorios bajo una única transacción de base de datos.
* **¿Para qué sirve?** Asegura consistencia (ACID). Si estoy creando un Producto, y guardando las asociaciones en la tabla intermedia `ProductoCategoria` y algo falla, el UoW hace **Rollback** automáticamente (cancelando la creación del Producto para no dejar datos huérfanos).
* **Implementación en el proyecto:** Usa los "Context Managers" de Python (`__enter__` y `__exit__`). Al usar `with ProductoUnitOfWork(self._session) as uow:`, si no hay excepciones, hace `.commit()` al salir del bloque; si hay una excepción, hace `.rollback()`.

---

## 8. Models SQLAlchemy (SQLModel)

Analizando `Producto` (`app/modules/producto/models.py`):
* Utiliza **SQLModel**, que fusiona `SQLAlchemy` (ORM) y `Pydantic` (Validación).
* **Columnas:** `id` (PK), `precio_base` (Numeric), `disponible` (Boolean), `deleted_at` (DateTime - Soft Delete).
* **CheckConstraints:** Garantiza en la base de datos (y no solo en código) que el `precio_base >= 0`.
* **Relaciones (`Relationship` y `back_populates`):**
  * `productos_categoria: list["ProductoCategoria"] = Relationship(back_populates="producto")`.
  * Sirve para vincular los objetos en memoria. Si pido `producto.productos_categoria`, SQLAlchemy va a la tabla intermedia y me trae las asociaciones.
* **¿Por qué no devolver el Model al cliente?** Evita exponer información sensible (como campos `password_hash`), y previene problemas de "Lazy Loading" (SQLAlchemy intentando consultar la base de datos después de cerrar la sesión al serializar a JSON).

---

## 9. Schemas Pydantic

Analizando `ProductoCreate` y `ProductoPublic` (`app/modules/producto/schemas.py`):
* **`ProductoCreate` (Entrada):** Define qué espera el backend del FrontEnd para crear. Exige `nombre` (max_length=150), oculta `id` o `created_at` porque los genera el servidor.
* **`ProductoPublic` (Salida):** Lo que devolvemos. Expone fechas e `id`.
* **Diferencia entre Model y Schema:** El *Model* interactúa con la BD. El *Schema* es el "contrato" de la API. 

---

## 10. Base de datos

* **Motor:** PostgreSQL (`postgresql://...`).
* **Manejo:** Se inicializa en `app/core/database.py`. Existe una función `create_db_and_tables()` que crea las tablas usando `SQLModel.metadata.create_all(engine)` si no existe Alembic, pero también contiene lógica de migración hardcodeada.
* **Alembic:** Es la herramienta de migraciones. Sirve para hacer seguimiento de los cambios en los modelos de base de datos (ej. agregar una columna). 
    * *Defensa:* "Usamos Alembic para control de versiones de la BD. Es como Git pero para el esquema SQL, permitiéndonos evolucionar la base de datos en producción sin perder datos."

---

## 11. Autenticación y autorización

Analizando `app/modules/auth/`:
* **Autenticación (Login):** `POST /auth/login`. Valida el hash (bcrypt). Si es correcto, invoca `create_access_token()`.
* **Tokens:** Usa **JWT (JSON Web Token)**. El token incluye el email del usuario y una lista de sus roles (`data={"sub": user.email, "roles": get_user_role_codes...}`).
* **Protección:** Se devuelve en un `HttpOnly Cookie` (para mayor seguridad contra ataques XSS en Frontends) y también en el payload.
* **Autorización (Permisos/Roles):** El endpoint usa dependencias como `_current_user=Depends(require_roles("ADMIN"))`. FastAPI rechaza la petición con un `403 Forbidden` si el rol no coincide.

---

## 12. Configuración del proyecto

Analizando `app/core/config.py`:
* **Pydantic Settings:** Carga automáticamente las variables de un archivo `.env` (Usuario, Contraseña de BD, `secret_key`).
* **Seguridad:** El `secret_key` es fundamental para firmar los JWT. Si se expone en GitHub, cualquiera podría falsificar un token con rol "ADMIN". Nunca se sube el `.env` al repo.

---

## 13. Manejo de errores

* **Excepciones controladas:** Se utiliza `HTTPException` de FastAPI.
* Ejemplo en Service: Si intento buscar un producto que no existe, el código hace `raise HTTPException(status_code=404, detail="Producto no encontrado")`. 
* Si se repite un ingrediente en la request, el Service lanza `409 Conflict`.
* **Pydantic Validation Error:** Si el Front manda un string en lugar de un precio (int/float), FastAPI automáticamente devuelve un error `422 Unprocessable Entity` diciendo qué campo falló.

---

## 14. Flujo completo de casos de uso

**Caso de Uso: Crear un Producto**
1. **Frontend** envía `POST /productos/` con un JSON (nombre, precio, ingredientes).
2. **FastAPI (Router):** Verifica que el token JWT sea válido y que tenga rol ADMIN (vía `Depends`).
3. **Pydantic:** Valida que el `precio_base` sea `>= 0`.
4. **Service (`create`):** Recibe el DTO.
5. Se abre `ProductoUnitOfWork`.
6. El **Service** convierte el DTO en Model. Establece `disponible` a `True` temporalmente.
7. El **Repository** (`uow.productos.add`) lo marca para inserción.
8. El **Service** sincroniza categorías e ingredientes (validando que existan llamando a otros repositorios). Calcula el stock final basado en el stock de los ingredientes.
9. El **UoW** hace el `.commit()` escribiendo en PostgreSQL todo el paquete.
10. Se devuelve el esquema `ProductoPublic` al **Router**, que lo pasa a JSON para el Frontend.

---

## 15. Preguntas de examen y respuestas

### Básicas
* **P: ¿Qué es FastAPI?**
  R: Es un framework de Python moderno para construir APIs web. Destaca por ser asíncrono, súper rápido, y autogenerar documentación (Swagger) gracias a Pydantic.
* **P: ¿Qué es un Endpoint?**
  R: Es la URL final a la que responde nuestra API (ej. `/productos/`) asociada a un Método HTTP (`GET`, `POST`).

### Intermedias
* **P: ¿Qué hace la Unit of Work y dónde se llama el commit?**
  R: Agrupa operaciones de base de datos. El commit se llama al finalizar el bloque `with UnitOfWork() as uow:` en la capa de *Service*. De esta forma nos aseguramos que todas las inserciones sean atómicas.
* **P: ¿Por qué hay un Model SQLModel y además un Schema (ProductoPublic)?**
  R: El Model define cómo se guarda en BD, mientras que el Schema define el contrato de la API. Separarlos nos permite ocultar datos (como contraseñas) y evitar problemas del ORM al intentar serializar al frontend.

### Avanzadas
* **P: ¿Qué es el problema N+1 y cómo lo evitarías acá?**
  R: Ocurre cuando hago 1 query para traer 10 productos, y luego, por culpa del *Lazy Loading*, el ORM hace 10 queries más para traer la categoría de cada producto. Lo solucionamos usando *Eager Loading* en SQLAlchemy (`selectinload` o `joinedload`). En este proyecto se está mitigando en parte solicitando las relaciones bulk desde el UoW en el `ProductoService.get_all()`.
* **P: ¿Cómo harías pruebas unitarias del `ProductoService`?**
  R: Usaría una librería como `pytest` y "Mockearía" el `ProductoUnitOfWork`. Le pasaría al service un UoW falso que no toca la base de datos, sino que devuelve datos en memoria, para probar exclusivamente la lógica (ej. si el precio es correcto).

---

## 16. Posibles debilidades del proyecto

*(Esto dilo como un arquitecto senior que propone mejoras continuas)*
1. **Migraciones híbridas:** En `database.py` hay código duro ejecutando ALTER TABLES y migrando datos legacy. En un entorno 100% ideal, esto debería estar *exclusivamente* en las revisiones de Alembic.
2. **Carga en memoria (N+1 parcial):** En `get_all` de `ProductoService`, para obtener los ingredientes asociados se obtienen todos los IDs y se hace un Query separado. Si la BD crece mucho, sería más óptimo usar `Eager Loading` de SQLAlchemy en el Repository.
3. **Instanciación fuerte en UoW:** `ProductoUnitOfWork` instancia los Repositories directamente. Para un Testing puramente aislado, podría aplicar una Inyección de Dependencias más estricta dentro del UoW.
4. **Falta de uso de async:** FastAPI brilla con operaciones asíncronas (`async def`). El proyecto usa `def` síncronas de SQLModel. Se podría migrar a `AsyncSession` de SQLAlchemy para manejar mayor concurrencia.

---

## 17. Testing

Si te preguntan por pruebas:
* **Faltan Tests Automatizados:** El repositorio actual (por lo observado) no contiene una suite extensiva de tests bajo `pytest`. 
* **Qué testear primero:**
  1. *Services:* Mockear base de datos y probar la regla de cálculo de Stock.
  2. *Endpoints (Integración):* Usar `TestClient` de FastAPI, crear una DB de prueba temporal de SQLite/Postgres en memoria, enviar un JSON a `/productos/` y verificar que el response de status sea 201.

---

## 18. Performance y escalabilidad

* **Positiva:** El proyecto usa Paginación por defecto (`limit` y `page`), lo cual es crucial para no tirar la base de datos al listar productos.
* **Mejora sugerida:** Si el catálogo no cambia a menudo (menú), se podría usar **Redis** como capa de caché para los endpoints `GET /productos/`. 

---

## 19. Seguridad

* **Correcto:** Usa JWT para tokens. Las contraseñas están Hasheadas con Bcrypt. Protege contra inyecciones SQL usando ORM (SQLModel). Valida entradas robustamente con Pydantic. Los tokens se envían como `HttpOnly` Cookies, previniendo ataques de scripts.
* **Precaución:** Asegurarse siempre que el archivo `.env` está en el `.gitignore`.

---

## 20. Glosario técnico (Cheat Sheet)

* **FastAPI:** Framework Python para APIs REST.
* **SQLModel:** Librería creada por el autor de FastAPI que fusiona SQLAlchemy (ORM) y Pydantic.
* **ORM:** Convierte filas de base de datos relacional en Objetos de Python.
* **Pydantic:** Librería de validación de datos basada en tipado de Python.
* **UoW (Unit of Work):** Patrón que controla transacciones de base de datos.
* **Soft Delete:** En vez de borrar una fila con `DELETE`, se le asigna la fecha actual a la columna `deleted_at`. El código ignora las filas con esa columna llena.
* **Dependency Injection:** Pasar dependencias (como sesiones a BD) a una función por parámetro, en lugar de crearlas dentro de la función.
* **JWT:** Estándar seguro para firmar y enviar datos de autenticación en la web.

---

## 21. Explicación para defensa oral (Discurso armado)

**Inicio:** *"Buenos días. Les presento el backend del Catálogo de Productos y Pedidos. Está construido en Python 3 utilizando FastAPI y SQLModel con base de datos PostgreSQL."*
**Arquitectura:** *"Elegí una Arquitectura en Capas orientada al Dominio. Cada entidad fuerte (como Producto, Autenticación, Pedidos) es un módulo independiente que contiene sus Rutas, Lógica de Negocio y Repositorios. Esto asegura un bajo acoplamiento."*
**Decisiones Críticas:** *"Implementé el patrón Repository para abstraer las queries SQL de SQLAlchemy, y lo complementé con el patrón Unit of Work. Esto me permitió asegurar consistencia transaccional. Por ejemplo, al crear un Producto, se debe guardar en la tabla producto, pero también en las tablas puente de ingredientes y categorías. Si algo falla, el Unit of Work ejecuta un rollback automático, previniendo inconsistencias de estado."*
**Conclusión:** *"La elección de tecnologías como Pydantic nos aseguró validación estricta de payloads entrantes mitigando errores. Como mejora a futuro, evaluaría migrar las consultas hacia `async/await` nativo para soportar aún mayor carga de clientes recurrentes."*

---

## 22. Simulación de examen oral

* **Profesor:** ¿Por qué separaste Repository de Service? ¿Qué pasaría si pongo la lógica directo en el router?
* **Alumno (Tú):** *"Si lo pongo en el router, rompo el principio de Responsabilidad Única. El router debería encargarse solo del flujo HTTP. Si pongo la lógica ahí, el código se vuelve imposible de testear unitariamente sin simular peticiones HTTP. Al usar un Service, aislo las reglas de negocio; y al usar Repository, aislo la base de datos."*
* **Profesor:** Muy bien. ¿Cómo manejas las relaciones entre un Producto y un Ingrediente en la base de datos?
* **Alumno:** *"Dado que es una relación de 'Muchos a Muchos', utilizamos una tabla intermedia llamada `ProductoIngrediente`. En SQLModel/SQLAlchemy esto se modela utilizando el atributo `Relationship` apuntando a las entidades principales."*

---

## 23. Mapa mental del proyecto

```text
                  [ Frontend / Cliente ]
                           | (HTTP REST)
                 +-------------------+
                 | FastAPI (Routers) | --> Pydantic Schemas (Input/Output Validation)
                 +-------------------+
                           | (Dependency Injection / Depends)
                 +-------------------+
                 |     Services      | --> Lógica de Negocio, Validación, Stock
                 +-------------------+
                           |
                 +-------------------+
                 |   Unit of Work    | --> Manejo Transaccional (Begin, Commit, Rollback)
                 +-------------------+
                           |
                 +-------------------+
                 |   Repositories    | --> Abstracción de DB (get, add, list_active)
                 +-------------------+
                           |
                 +-------------------+
                 | SQLModel Models   | --> Mapeo a Tablas (Producto, Categoria)
                 +-------------------+
                           |
                   [ PostgreSQL DB ]
```

---

## 24. Recomendaciones finales para estudiar

1. **Estudiar primero:** Entiende la arquitectura y el diagrama anterior. Si entiendes cómo viaja el dato desde que entra hasta que se guarda, ya tienes el 70% adentro.
2. **Archivos a saber de memoria:** Estudia el flujo completo del archivo `app/modules/producto/service.py` (el método `create` es excelente para explicar) y `app/core/unit_of_work.py`.
3. **Flujos que debes saber sin mirar:** Explicar verbalmente cómo funciona la inyección de dependencias `Depends()` en el Login (cómo agarra el token, busca el usuario en el UoW, valida la contraseña y devuelve un DTO).
4. **Errores comunes a evitar:** No confundas **Pydantic** con **SQLAlchemy**. Pydantic es validación de Python, SQLAlchemy es Base de datos. *SQLModel junta ambos, pero en tu cabeza sepáralos*.

¡Mucho éxito en la defensa! Dominas la arquitectura de capas, y ese es el conocimiento más buscado en el mercado backend hoy.
