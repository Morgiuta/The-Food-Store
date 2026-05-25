# Food Store - Primera entrega

Proyecto con backend FastAPI y frontend React + Vite para la primera entrega del panel administrativo de Food Store.

## Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL configurado segun el archivo `backend/.env`
- Variables de seguridad configuradas en `backend/.env` segun `backend/.env.example`

## Ejecutar backend

Abrir una terminal en la raiz del proyecto y ejecutar:

```powershell
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Si el puerto `8000` esta ocupado, buscar el proceso:

```powershell
netstat -ano | findstr :8000
```

Finalizarlo reemplazando `NUMERO_PID` por el PID que aparece al final:

```powershell
taskkill /PID NUMERO_PID /F
```

O levantar el backend en otro puerto:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## Ejecutar frontend

Abrir otra terminal en la raiz del proyecto y ejecutar:

```powershell
cd frontend
$env:VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1"
npm run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

Si el backend se levanto en `8001`, usar:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8001/api/v1"
npm run dev
```

## Login demo

Credenciales disponibles:

```text
admin / 1234
stock / stock
```

El login se valida contra el backend con OAuth2 Password Flow. El backend emite un JWT con expiracion corta y el frontend lo envia en cada request como `Authorization: Bearer <token>`.

## Funcionalidades incluidas

**Seguridad y Autenticación**
- Login backend con JWT, hashing bcrypt y persistencia local del token.
- Navegación protegida y control de acceso basado en roles (`ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`).

**Módulos del Administrador (Dashboard)**
1. **Insumos / Ingredientes**: Gestión de stock y materias primas. Exportación a Excel.
2. **Categorías**: Clasificación de productos (Hamburguesas, Bebidas, etc.).
3. **Productos**: Construcción de catálogo y recetas. Permite enlazar categorías y elegir los insumos requeridos para fabricar cada producto.
4. **Gestor de Pedidos**: Tablero operativo (tipo Kanban) en tiempo real con *auto-refresco* cada 15s. Incluye un ticket de comanda detallado.
5. **Personal y Usuarios**: Panel de control para asignar roles y gestionar clientes o empleados.

**Arquitectura y UX**
- Construido con React 18, Vite y TypeScript estricto.
- Estado asíncrono gestionado robustamente mediante **React Query** (caché, invalidación y re-fetching).
- Diseño moderno con **TailwindCSS**, notificaciones (Toasts), modales y validaciones en tiempo real.
- Búsqueda, filtros y paginación en todos los módulos.

## Verificaciones utiles

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Backend:

```powershell
cd backend
python -m compileall app main.py
```
