# Food Store - Primera entrega

Proyecto con backend FastAPI y frontend React + Vite para la primera entrega del panel administrativo de Food Store.

Video de presentacion:

```text
https://youtu.be/DEhMDTzeUyE
```

## Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL configurado segun el archivo `backend/.env`
- Variables de seguridad configuradas en `backend/.env` segun `backend/.env.example`

## Configuracion inicial

Crear el archivo de variables del backend:

```bash
cp backend/.env.example backend/.env
```

Editar `backend/.env` y configurar al menos:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=catalogo_productos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=una_clave_larga_aleatoria_de_32_bytes_o_mas
```

La base de datos PostgreSQL debe estar creada y accesible con esos datos antes de levantar el backend.

Crear e instalar el entorno Python:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd ..
```

En Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd ..
```

Instalar dependencias del frontend:

```bash
cd frontend
npm install
cd ..
```

## Ejecutar backend

Abrir una terminal en la raiz del proyecto y ejecutar:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

En Windows PowerShell:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
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

Linux/macOS:

```bash
lsof -iTCP:8000 -sTCP:LISTEN -n -P
kill NUMERO_PID
```

Windows PowerShell:

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

Linux/macOS:

```bash
cd frontend
VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1" npm run dev
```

Windows PowerShell:

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

Linux/macOS:

```bash
VITE_API_BASE_URL="http://127.0.0.1:8001/api/v1" npm run dev
```

Windows PowerShell:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8001/api/v1"
npm run dev
```

## Levantar ngrok para MercadoPago

MercadoPago necesita una URL publica para enviar las notificaciones del webhook. Con el backend corriendo en `http://127.0.0.1:8000`, abrir otra terminal y ejecutar:

```bash
ngrok http 8000
```

Copiar la URL HTTPS que muestra ngrok, por ejemplo:

```text
https://abc123.ngrok-free.app
```

Actualizar `backend/.env` con esa URL en `MP_NOTIFICATION_URL`, agregando la ruta del webhook:

```env
MP_NOTIFICATION_URL=https://abc123.ngrok-free.app/api/v1/pagos/webhook
```

Despues de cambiar `backend/.env`, reiniciar el backend.

## Login demo

Credenciales disponibles:

```text
admin@foodstore.com / Admin1234!
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
