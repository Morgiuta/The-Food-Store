## Ejecución local

### 1) Crear entorno virtual (se desactiva con: deactivate)

**Linux / macOS**
python3 -m venv .venv
**Windows (PowerShell)**
py -m venv .venv

### 2) Activar entorno virtual

**Linux / macOS**
source .venv/bin/activate
**Windows (PowerShell)**
.\.venv\Scripts\Activate.ps1
**Windows (CMD)**
.\.venv\Scripts\activate.bat

### 3) Actualizar pip e instalar dependencias

python -m pip install --upgrade pip
pip install -r requirements.txt

### 4) Ejecutar Servidor

python -m fastapi dev app/main.py

# Team Hero API

Ejemplo de arquitectura backend con FastAPI + SQLModel siguiendo el patrón
**Router → Service → Unit of Work → Repository**.

## Estructura del proyecto

```
team_hero/
├── main.py                        # Entrypoint FastAPI
├── seed.py                        # Datos de prueba
├── requirements.txt
├── .env.example
├── app/
│   ├── core/
│   │   ├── config.py              # Settings (pydantic-settings)
│   │   ├── database.py            # Engine, Session, get_session
│   │   ├── repository.py          # BaseRepository genérico (CRUD base)
│   │   └── unit_of_work.py        # UnitOfWork base (__enter__/__exit__)
│   └── modules/
│       ├── heroes/
│       │   ├── models.py          # Tabla Hero + schemas (Create/Update/Public)
│       │   ├── repository.py      # HeroRepository (queries específicas)
│       │   ├── unit_of_work.py    # HeroUnitOfWork (expone repos)
│       │   ├── service.py         # HeroService (lógica de negocio)
│       │   └── router.py          # Endpoints HTTP (thin layer)
│       └── teams/
│           ├── models.py
│           ├── repository.py
│           ├── unit_of_work.py    # TeamUnitOfWork (teams + heroes, 1 transacción)
│           ├── service.py
│           └── router.py
└── tests/
    ├── conftest.py                # SQLite en memoria + dependency_overrides
    ├── test_heroes.py
    └── test_teams.py
```

## Responsabilidades por capa

| Capa           | Responsabilidad                                      | Conoce a            |
| -------------- | ---------------------------------------------------- | ------------------- |
| **Router**     | HTTP: deserializar, delegar, responder               | Service             |
| **Service**    | Lógica de negocio, orquestar, levantar HTTPException | UoW                 |
| **UnitOfWork** | Gestionar transacción (commit/rollback)              | Repository, Session |
| **Repository** | Queries SQL, acceso a datos                          | Session, SQLModel   |
| **Models**     | Tabla + schemas de entrada/salida                    | —                   |

## Flujo de una request POST /heroes/

```
CLIENT
  │  POST /heroes/  { name, alias, power_level }
  ▼
ROUTER  (router.py)
  │  deserializa HeroCreate
  │  llama svc.create(data)
  ▼
SERVICE  (service.py)
  │  valida alias único
  │  with HeroUnitOfWork(session) as uow:
  ▼
UNIT OF WORK  (unit_of_work.py)
  │  __enter__: expone uow.heroes = HeroRepository(session)
  │  ...
  │  __exit__: commit() si no hay excepción
  │            rollback() si hay excepción
  ▼
REPOSITORY  (repository.py)
  │  session.add(hero)
  │  session.flush()   ← obtiene ID sin commit
  ▼
POSTGRES
```

## Puntos clave del diseño

**`flush()` vs `commit()`**
El repositorio solo llama a `flush()` — escribe en la transacción en memoria
pero no persiste. El commit real lo hace exclusivamente el UoW en `__exit__`.
Esto garantiza atomicidad: si el servicio hace dos operaciones (crear hero +
asignar rol), o se guardan ambas o ninguna.

**PATCH parcial con `exclude_unset`**

```python
patch = data.model_dump(exclude_unset=True)
for field, value in patch.items():
    setattr(hero, field, value)
```

Solo actualiza los campos que el cliente envió explícitamente.

**Soft delete**
Los registros nunca se borran físicamente. Se marca `is_active = False`.
Las queries de listado filtran por `is_active == True`.

**Cross-module en una transacción**
`TeamUnitOfWork` expone tanto `teams` como `heroes`. El servicio puede
modificar ambas entidades y el UoW garantiza que se guardan juntas o ninguna.

**Tests con SQLite en memoria**
`conftest.py` sobreescribe `get_session` con `dependency_overrides`.
El UoW y los repositorios no saben que están usando SQLite — la abstracción funciona.

## Setup rápido

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # ajustar DATABASE_URL

python seed.py                     # carga datos de prueba
fastapi dev main.py                # http://localhost:8000/docs

# tests
pip install pytest httpx
pytest tests/ -v
```
