# Catalogo de Productos Backend

Backend modular con FastAPI, SQLModel y PostgreSQL para el dominio Catalogo de Productos.

## Requisitos

- Python 3.11+
- PostgreSQL

## Configuracion

Crear el archivo `.env` con:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=catalogo_productos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
uvicorn main:app --reload
```

o

```bash
fastapi dev main.py
```
