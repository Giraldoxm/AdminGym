# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JainSportBox is a CrossFit Box Management System with a Python/FastAPI backend and Vue.js 3 frontend. It handles members, memberships, attendance (via fingerprint sensor), WODs, finances, health metrics, personal records (1RM), and a product shop.

## Development Commands

### Launcher (recomendado)

Desde la raíz del repo:
```powershell
.\start-dev.ps1                # backend + frontend + bridge en ventanas separadas
.\start-dev.ps1 -NoBridge      # si el bridge ya corre via Task Scheduler
.\start-dev.ps1 -NoFrontend    # solo backend + bridge
```
O doble-clic a `start-dev.cmd`. El launcher activa el `venv/`, detecta si el bridge ya está corriendo (no relanza) y dispara UAC solo cuando hace falta. Ver logs del bridge en vivo: `servicio_biometrico\ver-logs.cmd`.

### Estación de recepción (producción, PC del gym)

`start-estacion.ps1` sirve el build de producción del frontend localmente apuntando al backend cloud (resuelve el bloqueo *mixed content* de la PWA). Ver Capa 6 en `DEPLOYMENT.md`.
```powershell
.\start-estacion.ps1 -ApiUrl https://api.tudominio.com   # build + vite preview en http://localhost:80 + bridge
.\start-estacion.ps1 -ApiUrl https://api.tudominio.com -Port 8080 -SkipBuild
```

### Backend
```bash
# From project root
cd backend
pip install -r requirements.txt          # or: pip install -r ../requirements.txt

# Create .env from template (required before first run)
cp .env.example .env

# Start backend (auto-creates DB tables and seeds admin on startup)
uvicorn main:app --reload --port 8000

# Or fromuvicorn backend.main:app --reload --port 8000 project root:

```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Dev server at http://localhost:5173 (strictPort)
npm run build    # Production build → dist/
npm run preview  # Preview production build
```

There are no test commands — no test suite exists in this project.

## Architecture

**Three-process stack:**
- Backend: FastAPI on port 8000, SQLite database (`backend/crossfit.db`)
- Frontend: Vue 3 SPA on port 5173, talks to backend via Axios
- Bridge: `servicio_biometrico/` — .NET 4.8 Windows app for DigitalPersona U.are.U 4500 fingerprint reader

**Backend layout:**
- `backend/main.py` — FastAPI app creation, CORS config, router registration. Runs SQLite migrations on startup (ALTER TABLE in try/except; table reconstruction for nullability changes via PRAGMA table_info). Mounts `backend/uploads/` as `/uploads` for static files (user profile photos). Starts APScheduler with two jobs: alerts job (9 AM Bogotá + on startup) and `_job_reset_gym` (every 3 minutes, resets `esta_en_gym = False` for users whose last entry exceeds `MINUTOS_SESION`).
- `backend/models.py` — All SQLAlchemy models (13 tables): `usuarios`, `planes`, `pagos`, `wods`, `resultados_wod`, `productos`, `ventas`, `asistencias`, `movimientos_financieros`, `medidas_salud`, `marcas_rm`, `alertas_membresia`, `metodos_pago`
- `backend/database.py` — SQLite session factory
- `backend/security.py` — BCrypt password hashing, JWT creation/validation (HS256, 7-day expiry)
- `backend/routers/` — One file per domain: `auth`, `usuarios`, `pagos`, `planes`, `productos`, `ventas`, `wods`, `asistencia`, `finanzas`, `salud`, `alertas`, `marcas`, `metodos_pago`
- `backend/schemas/` — Pydantic request/response models; one file per domain except `planes` (schemas defined inline in router): `asistencia`, `alerta`, `finanza`, `pago`, `producto`, `venta`, `wod`, `usuario`, `salud`, `marcas`
- `backend/seed.py` — Creates default plans and admin user (runs on app startup via `main.py`)

**Frontend layout:**
- `frontend/src/main.js` — Vue app init; Axios interceptor adds `Authorization: Bearer {token}` from `localStorage`
- `frontend/src/api.js` — Axios instance with `baseURL: http://127.0.0.1:8000`
- `frontend/src/router/index.js` — Route guards using `meta.requiresAuth` and `meta.roles`; clients default to `/home`, admin to `/usuarios`, coach to `/home`. `pendiente` → forzado a `/planes`. Clientes con membresía vencida (`membresiaVencidaFor`) solo acceden a `RUTAS_CLIENTE_VENCIDO = ['/home', '/planes', '/']`.
- `frontend/src/composables/useAuth.js` — Reactive role helpers: `isAdmin`, `isCoach`, `isCliente`, `canManage`
- `frontend/src/composables/useSessionMarca.js` — Composable de sesión de Marcas (legacy, ya no usado por `MarcasEjercicioView`). Se mantiene para que `Dashboard.vue` pueda limpiar el localStorage en logout (`cancelarSesion()`).
- `frontend/src/views/` — One large SFC per page: `LoginView`, `UsuariosView`, `UsuarioPerfilView`, `HomeView`, `TiendaView`, `WodsView`, `WodsPersonalizadosView`, `FinanzasView`, `PlanesView`, `AlertasView`, `SaludView`, `SaludMedidaView`, `MarcasView`, `MarcasEjercicioView`, `SesionesView`, `MiPerfilView`. (`MonitorAccesoView.vue` exists but is not registered in the router.)
- `frontend/src/components/Dashboard.vue` — Main layout shell (sidebar + navigation). Does NOT show membership status in the sidebar — that info lives in `HomeView`. Sidebar organizado en tres secciones: **Gestión** (admin+coach), **Contenido** (todos), **Mi Box** (coach+cliente). Ver sección de sidebar más abajo.
- `frontend/src/components/BloqueCard.vue` — Acordeón reutilizable de bloque horario (usado por `SesionesView`). Header clicable muestra hora del bloque + badge de personas; al expandir muestra la lista completa de asistentes con hora exacta de entrada.
- `frontend/src/data/` — Shared config files: `saludTipos.js` (6 measurement configs), `ejerciciosMarcas.js` (12 fixed exercises)

## Key Patterns

**Auth flow:** POST `/login` returns a JWT → stored in `localStorage.token` → injected via Axios interceptor → backend validates via `get_current_user()` dependency → user role checked per-route.

**Role-based access:**
- Roles: `admin`, `coach`, `cliente`, `pendiente` (enum `RolUsuario` in `models.py`)
- Backend: route-level `Depends(_require_admin_or_coach)` or `Depends(_require_admin)` pattern in each router
- Frontend: `meta.roles` on routes + `useAuth` composable in components
- `pendiente` users are redirected to `/planes` by the router guard

**Financial movements:** `finanzas.py` surfaces income from three sources: rows in `pagos` (membership payments, both plan-based and personalizado), rows in `ventas` (shop sales), and rows in `movimientos_financieros` (manual entries + legacy `pago_directo` records). Pagos and ventas are NOT mirrored into `movimientos_financieros` — the finanzas listing reads from each table directly to avoid double-counting.

**Pago model:** `plan_id` is nullable. Personalizado payments have `plan_id = NULL` and `duracion_dias` set to the days purchased. The historial endpoint shows them as `"Personalizado (N días)"`.

**Email/document normalization:** All routes that write or look up `usuarios.email` apply `.strip().lower()` (login, registro, POST/PATCH usuarios, JWT subject in `get_current_user`). `documento_identidad` is `.strip()`-ed. The model has `unique=True` on both columns, but case normalization happens in code so `Foo@x.com` and `foo@x.com` are treated as the same account.

**Fingerprint integration:** see the dedicated section below.

**SQLite migrations:** `backend/main.py` runs migrations on startup. New columns use `ALTER TABLE … ADD COLUMN` inside try/except. Changing nullability requires full table reconstruction (rename → CREATE → INSERT → DROP), guarded by a `PRAGMA table_info` check to avoid re-running.

**Chart lifecycle (Vue + Chart.js):** Always call `destruirChart()` before creating a new instance. Use `watch(registros, async () => { await nextTick(); await nextTick(); renderChart() })` to ensure the canvas is in the DOM after a `v-if` renders.

**Unit normalization (1RM):** All weight comparisons (PR detection, chart, esPR preview) are done in kg using `1 kg = 2.20462 lbs`. Values are converted back to the display unit (`ultimaUnidad`) only for rendering. Never compare `rm_calculado` values from different records without normalizing first.

**Public registration:** `POST /registro` accepts `multipart/form-data` (not JSON) because it supports an optional profile photo. Use `Form(...)` for all text fields and `File(None)` for the photo. The frontend sends a `FormData` object with `Content-Type: multipart/form-data`.

## HomeView — client/coach home screen

Route `/home` (roles: `cliente`, `coach`). Shows:
- Membership status card + current plan card (clients only)
- Coach staff card (coaches only)
- Attendance calendar with month navigation (prev/next arrows, fetches 12 months once on mount)

**Loading state (membresía):** `cargandoPerfil` ref (inicia `true`, pasa a `false` en el `finally` del fetch). Mientras carga, las tarjetas de membresía y plan muestran un spinner. Esto evita el flash de "-999 días / Sin membresía activa": `diasRestantes` devuelve el centinela `-999` cuando `userData.fecha_vencimiento` aún no llegó, y sin el flag se renderizaba por un instante antes de la respuesta de `/me`.

**Attendance calendar pattern:**
- Fetch: `GET /asistencia/mi-historial?meses=12` on mount
- State: `mesOffset` ref (0 = current month, -1 = previous, min = -11)
- `calendarioActual` computed builds the single visible month from `attendedSet`
- Cell classes: `bg-emerald-500` attended, `bg-gray-800` today, `bg-gray-50` future, `bg-transparent` past not attended

## UsuarioPerfilView — admin user profile page

Route `/usuarios/:id` (roles: `admin`, `coach`). Three sections:

**Profile card:** Centered column layout — photo on top, name below (prevents mobile truncation). Shows email, document, phone, gender, fingerprint status, membership status. "Editar perfil" button in the header opens an edit modal.

**Edit modal:** Fields: nombre, email, teléfono, documento_identidad, género, fecha_nacimiento (opcional), optional password change (checkbox toggle + visibility toggle). Only sends changed fields to the backend (`PATCH /usuarios/:id`). Updates `usuario.value` reactively on success without page reload.

**Profile card:** Muestra `fecha_nacimiento` como "15 ene 1995 (30 años)" usando el helper `formatCumpleanos(f)` — calcula la edad en base a la fecha de hoy. Solo se muestra si el campo existe.

**Attendance calendar:** Same month-navigation pattern as `HomeView` but fetches `GET /asistencia/historial/:id?meses=12` (admin endpoint).

**Subscription history:** Table from `GET /pagos/usuario/:id` — date, plan name, amount, payment method, and per-row actions (edit/anular). The membership card has an "Agregar membresía" button (red) that opens a modal mirroring the "Activar Usuario" modal in `UsuariosView` (plan grid + "Personalizado (días)" option + monto + método). Confirmar dispatches to `POST /pagos/` (plan) or `POST /pagos/directo/` (personalizado).

**Edit/anular pago:**
- Edit (`PATCH /pagos/{id}`): only `monto` and `metodo_pago`. Plan changes are not allowed in-place — the UI tells the admin to anular and recreate.
- Anular (`DELETE /pagos/{id}`): subtracts `plan.duracion_dias` (or `pago.duracion_dias` for personalizado) from `usuario.fecha_vencimiento`, then deletes the `Pago`. The resulting fecha may land in the past — that's correct (membership expired by the reversal).

**Navigation:** The "ver" button in `UsuariosView` calls `router.push('/usuarios/${u.id}')` instead of opening a modal.

## Dashboard — estructura del sidebar

El sidebar está dividido en secciones semánticas según el rol:

**Usuario pendiente:** solo ve Planes.

**Sección "Gestión"** (`canManage` = admin + coach):
- Usuarios, Sesiones, Alertas WhatsApp, Ejercicios (admin + coach)
- Planes, Finanzas (solo admin)

**Sección "Contenido"** (todos los roles no pendientes):
- WODs (siempre, si membresía vigente)
- WODs Personalizados (staff o cliente con `tieneWodsPersonalizados`, si membresía vigente)
- Tienda (solo `canManage`)

**Sección "Mi Box"** (coach + cliente):
- Inicio
- Planes (solo cliente)
- Mi Salud (cliente, membresía vigente)
- Mis Marcas (coach + cliente, membresía vigente)

**Sección "Cuenta"** (todos los roles no pendientes, incluido admin):
- Mi Perfil

## MiPerfilView — autogestión de perfil

Ruta `/perfil` (roles: `admin`, `coach`, `cliente`). Permite que **cualquier usuario edite su propia cuenta** sin pasar por admin. Está en `RUTAS_CLIENTE_VENCIDO`, así que un cliente con membresía vencida también puede entrar.

Es una **página** (no modal ni cards): encabezado con foto + identidad, sección "Datos personales" con los campos editables inline (nombre, email, teléfono, documento, género, fecha de nacimiento), sección "Seguridad" (cambio de contraseña opcional), y barra de acciones (Descartar / Guardar) que se habilita solo si `hayCambios`. La foto se cambia con un botón sobre el avatar (`POST /me/foto`). Tras guardar nombre actualiza `localStorage.userName`.

**Backend (`routers/auth.py`):** la autogestión vive junto al login, no en `usuarios.py` (que exige admin/coach).
- `GET /me` — además de membresía/plan, devuelve `telefono`, `documento_identidad`, `fecha_nacimiento` y `foto_url`. Serializado por el helper `_serialize_me(current_user, db)`.
- `PATCH /me` — edita el perfil propio (mismos campos y validación de email/documento duplicado y normalización que `PATCH /usuarios/{id}`, pero con `get_current_user` en vez de admin/coach). Acepta `UsuarioUpdate`.
- `POST /me/foto` — sube/reemplaza la foto propia (multipart, campo `foto`). Borra la anterior con `eliminar_archivo`.

## AlertasView — WhatsApp reminders

Route `/alertas` (admin/coach). Two tabs: **Pendientes** (grouped by `dias_anticipacion`) and **Historial** (flat list, only `enviada=true`, sorted by `fecha_enviada` desc). There is no manual "Actualizar" button — `POST /alertas/generar` runs on mount and on tab switch.

**Dedup logic in `generar_alertas`:** before creating new alerts, the function deletes any pending (`enviada=False`) alert whose `fecha_vencimiento` no longer matches the user's current `fecha_vencimiento` (i.e., the user renewed) or that has fallen outside the 7-day window. Then it creates one alert per user inside the window only if no pending alert exists for that user. This prevents accumulating duplicate pending alerts when the admin extends a membership.

## Asistencia routers

**Modelo de acceso solo-entrada:** la palanquera solo controla el ingreso, así que el sistema **no registra salidas**. Cada marcación de huella crea una `Asistencia` con `tipo="entrada"` y pone `esta_en_gym=True`. El flag vuelve a `False` únicamente por tiempo (job `_job_reset_gym`), nunca por una marcación de salida. `_registrar()` en `asistencia.py` ya no alterna entrada/salida.

`backend/routers/asistencia.py` endpoints:
- `POST /asistencia/` — registra entrada por `huella_id` (bridge)
- `POST /asistencia/por-usuario/{usuario_id}` — registra entrada por ID (bridge con `X-Bridge-Secret` o admin/coach JWT); valida membresía vigente en cada marcación
- `GET /asistencia/mi-historial?meses=N` — historial propio (cualquier rol autenticado)
- `GET /asistencia/historial/{usuario_id}?meses=N` — historial de cualquier usuario (admin/coach)
- `GET /asistencia/en-gym` — usuarios con `esta_en_gym=True`, con `entrada_desde`, `minutos_transcurridos`, `minutos_restantes` y `minutos_sesion` (admin/coach)
- `GET /asistencia/sesiones-por-bloque?desde=&hasta=` — entradas agrupadas por (fecha, hora) en zona Bogotá; rango máx 31 días; deduplica por `usuario_id` dentro del mismo bloque conservando la primera entrada (admin/coach)

**Constante `MINUTOS_SESION`** (en `asistencia.py`): duración máxima de sesión usada tanto por `GET /en-gym` como por el job `_job_reset_gym` en `main.py`. Cambiar en un solo lugar.

**Auto-reset `esta_en_gym`:** el job `_job_reset_gym` (APScheduler, cada 3 min) usa un JOIN para obtener en una sola query los usuarios con `esta_en_gym=True` cuya última entrada supere `MINUTOS_SESION`, y los resetea a `False` sin crear registro de salida. Cubre el caso de usuarios que salen sin pasar por el torniquete. Implementado con subconsulta de `MAX(fecha_hora)` agrupada por `usuario_id` para evitar N+1.

**Deduplicación en sesiones-por-bloque:** los registros se ordenan por `fecha_hora` antes de agrupar. Si un usuario entró más de una vez en el mismo bloque (salió y volvió), solo aparece la primera entrada. Esto evita duplicados causados por re-entradas dentro del mismo bloque.

## SesionesView — consulta de sesiones por bloque horario

Ruta `/sesiones` (roles: `admin`, `coach`). Tres modos:

**Modo "Esta semana"** (carga automático al entrar):
- Tabs de los 7 días (Lun–Dom) con badge del total de asistentes por día
- Día de hoy resaltado en negro; día seleccionado en rojo; días sin asistencias con opacidad reducida
- Grid de `BloqueCard` del día seleccionado (cards lado a lado)
- Buscador por nombre en tiempo real

**Modo "Este mes":**
- Calendario mensual centrado (`max-w-md mx-auto`) con navegación ← → por mes (`mesOffset` ref, 0 = mes actual, no permite ir al futuro)
- Cada celda muestra número de día + badge rojo con total de asistentes (suma de `b.total` por fecha)
- Colores: hoy en negro, día seleccionado en rojo, días con datos en rojo suave, días sin datos en gris
- Clic en celda → selecciona día y muestra grid de `BloqueCard` debajo con buscador
- Clic en día ya seleccionado → lo deselecciona
- Estado: `bloquesMes`, `diaSeleccionadoMes`, `cargandoMes`, `semanaMes` (computed que construye filas de 7 celdas con nulls para relleno)
- Helper `getMesInfo(offset)` devuelve `{ year, month }` para cualquier offset

**Modo "Fecha específica":**
- Selector de fecha + botón "Ver sesiones"
- Grid de bloques del día elegido + buscador

**`BloqueCard`** (`frontend/src/components/BloqueCard.vue`) — acordeón:
- Header clicable: bloque horario + badge de personas + chevron que rota al expandir
- Body (expandido): lista completa de asistentes con nombre y hora exacta (HH:MM)
- Inicia colapsado; sin límite de asistentes visibles (todos se muestran al expandir)

## UsuariosView — paneles superiores

### Panel "Cumpleaños hoy"

`UsuariosView.vue` muestra un panel colapsable justo debajo del header cuando algún miembro activo cumple años ese día:
- Se llama `GET /usuarios/cumpleanos-hoy` al montar (`fetchCumpleaneros`)
- Solo aparece si `cumpleaneros.length > 0`
- El panel es colapsable: `cumpleanosExpandido` ref (inicia en `true`); al colapsar queda solo la barra con emoji 🎂, título y badge rojo con el count
- Cada fila muestra nombre + botón verde "Felicitar" (abre WhatsApp con mensaje pregenerado) + botón "Ver perfil"
- Helper `whatsappCumpleanos(u)`: formatea el teléfono como `57` + dígitos y genera el link `https://wa.me/...?text=...` con mensaje de felicitación y batido gratis
- El endpoint backend filtra por `strftime("%m-%d", fecha_nacimiento) == hoy` **y** `fecha_vencimiento >= hoy` — usuarios con membresía vencida no aparecen
- El endpoint `GET /usuarios/cumpleanos-hoy` debe declararse **antes** de `GET /{usuario_id}` en el router para que FastAPI no lo capture como ID

### Panel "En el box ahora"

El filtro "En el box ahora" en la tabla de usuarios usa `enGym` (ref), cargado con `GET /asistencia/en-gym` al montar y refrescado cada 10 segundos via `gymInterval`. No hay panel visual separado ni countdown — el panel de chips con temporizador fue eliminado.

## Mi Salud — health metrics

Per-measurement routing: each metric has its own page at `/salud/:tipo`. **Excluida del rol `admin`** — el router restringe `/salud` y `/salud/:tipo` a `roles: ['coach', 'cliente']`. El admin no ve esta sección en el sidebar ni puede entrar por URL directa.

**Measurement types** (defined in `frontend/src/data/saludTipos.js`):
`peso`, `altura`, `cintura`, `cuello`, `cadera`, `brazos`

Agregar una medida nueva = un objeto en `saludTipos.js` (la card en `SaludView` y la página `/salud/:tipo` se generan solas vía `v-for`/`find`) + la columna en el modelo + la migración `ALTER TABLE` en `main.py` + la entrada en `CAMPOS` (router) + el campo en `MedidaResponse` (schema).

**Backend router** (`backend/routers/salud.py`):
- `CAMPOS = { "peso": "peso_kg", "altura": "altura_cm", "cintura": "cintura_cm", "cuello": "cuello_cm", "cadera": "cadera_cm", "brazos": "brazos_cm" }`
- `GET /salud/` — all records for the current user (overview)
- `GET /salud/{tipo}` — records filtered by measurement type
- `POST /salud/{tipo}` — creates a record with only that field set
- `DELETE /salud/{medida_id}` — deletes by integer ID

**Model** (`MedidaSalud` in `backend/models.py`): all measurement columns are nullable (`Optional[float]`). The `imc` column is computed by the POST endpoint when both `peso_kg` and `altura_cm` are present.

**Views:**
- `SaludView.vue` — overview; 5 RouterLink cards + IMC banner, no modal
- `SaludMedidaView.vue` — detail per tipo; Chart.js line chart, history table with delete, add modal

## Mis Marcas — personal records

Per-exercise routing: each exercise has its own page at `/marcas/:ejercicio`. **Excluida del rol `admin`** — el router restringe `/marcas` y `/marcas/:ejercicio` a `roles: ['coach', 'cliente']`.

### Tipos de ejercicio

No todo se mide igual. La lista en `frontend/src/data/ejerciciosMarcas.js` etiqueta cada ejercicio con un `tipo`, y tanto el frontend como el backend bifurcan la lógica según ese tipo. La fuente de verdad es ese archivo del frontend; el backend duplica la clasificación en `TIPOS_EJERCICIO` dentro de `routers/marcas.py` — **mantener ambos en sincronía**.

| Tipo | Ejercicios | Métrica | Campos usados |
|---|---|---|---|
| `barra` | Back Squat, Deadlift, Clean, Clean and Jerk, Snatch, Bench Press, Press Militar | 1RM (fórmulas) | `peso`, `unidad`, `repeticiones`, `rm_calculado` |
| `corporal_lastre` | Dominadas | 1RM (fórmulas) sobre peso total | `peso` (corporal + lastre, snapshot), `peso_adicional` (lastre opcional), `repeticiones`, `rm_calculado` |
| `reps` | Push Up, Air Squat, Sit Up | Max reps | solo `repeticiones` |
| `leger` | Test de Léger | Mayor nivel (desempate por palier) | `nivel`, `palier` |

**Corporal+lastre (Dominadas):** el frontend jala el último `peso_kg` de Mi Salud (`GET /salud/peso`) como peso corporal automático. Si el usuario no tiene registros de salud, lo pide manual. El total `peso_corporal + peso_adicional` se guarda en `peso` como snapshot (no se recalcula a futuro si el usuario cambia de peso). 1RM se calcula sobre ese total.

**1RM formulas** (7 usadas, promediadas, solo para `barra` y `corporal_lastre`): Brzycki, Epley, Lander, O'Connor, Lombardi, Mayhew, Wathen. El promedio se guarda en `rm_calculado`. Helper backend: `_calcular_1rm(peso, reps)` en `routers/marcas.py`.

### Backend

**Router** (`backend/routers/marcas.py`):
- `GET /marcas/` — todos los registros del usuario actual
- `GET /marcas/{ejercicio}` — registros del ejercicio (URL-encoded)
- `POST /marcas/` — payload flexible; el router despacha según `_tipo_de(ejercicio)` y valida los campos requeridos por tipo (rechaza con 422 si faltan). Calcula `rm_calculado` solo para `barra` y `corporal_lastre`.
- `PATCH /marcas/{marca_id}` — edita un registro existente del usuario; aplica la misma lógica de validación y cálculo que POST.
- `DELETE /marcas/{marca_id}`

**Modelo** (`MarcaRM` en `models.py`): `usuario_id`, `ejercicio`, `unidad` (default `"kg"`), `fecha`, `notas`, `created_at` son siempre obligatorios. Todos los demás campos son nullable y se llenan según el tipo: `peso`, `repeticiones`, `rm_calculado`, `peso_adicional`, `nivel`, `palier`. La migración en `main.py` reconstruye la tabla para hacer nullable `peso`/`repeticiones`/`rm_calculado` (antes eran NOT NULL) y agrega las 3 columnas nuevas vía `ALTER TABLE`.

**Schema** (`schemas/marcas.py`): `MarcaRMCreate` tiene todos los campos de tipo opcional para soportar los 4 flujos. La validación dura sucede en el router.

### Frontend

**`MarcasView.vue`** — grid de los 12 ejercicios. Cada card muestra:
- `barra`/`corporal_lastre`: "Mejor 1RM" + valor + unidad (normalizado a kg para comparar entre kg/lbs)
- `reps`: "Mejor reps" + número
- `leger`: "Mejor nivel" + `nivel.palier`

**`MarcasEjercicioView.vue`** — UI condicional según `tipo`:
- Resumen: muestra "Último vs PR" según tipo (1RM, max reps, o nivel.palier). "Último 1RM" refleja el mejor del día más reciente (via `registrosPorDia`).
- Gráfica: evolución del 1RM, repeticiones, o nivel (puntos PR resaltados en oro). Para `barra`/`corporal_lastre` usa `registrosPorDia` — un punto por día con el mejor 1RM de ese día.
- Tabla rep-max y comparación de fórmulas: solo para `barra`/`corporal_lastre`
- Historial: encabezados y formato de celda cambian por tipo. Botones **editar** (lápiz azul) y **eliminar** (basurero rojo) siempre visibles en cada fila. En móvil se oculta la columna Notas.
- **Registro para `barra`/`corporal_lastre`:** panel de adición directa (ver sección abajo).
- **Registro para `reps`/`leger`:** modal con campos específicos (`reps`: solo repeticiones; `leger`: nivel + palier).
- **Editar registro:** botón lápiz en historial abre el modal precargado con los datos del registro. `guardar()` llama `PATCH /marcas/{id}` si edita, `POST /marcas/` si es nuevo.

**Helper compartido:** `tipoDe(nombre)` en `ejerciciosMarcas.js`.

### Registro directo por serie (`barra` / `corporal_lastre`)

Para ejercicios de peso, cada serie se guarda **inmediatamente** al presionar `+`. No hay sesión persistente ni localStorage.

**Panel de adición directa (inline en `MarcasEjercicioView.vue`):**
- Siempre visible debajo del resumen.
- Toggle kg/lbs, campo peso (o lastre adicional para Dominadas), campo reps, botón `+` (o Enter).
- Para `corporal_lastre`: muestra peso corporal auto (de Mi Salud) o input manual; pesoTotal = corporal + lastre.
- Al presionar `+`: POST `/marcas/` con `{ ejercicio, fecha: hoy, unidad, series: [{ peso, repeticiones }] }`. Un registro por serie.
- Mini-lista "Hoy · N series" muestra las series ya guardadas ese día (filtradas de `registros` por fecha).

**Computed `registrosPorDia`** — agrupa los registros por fecha tomando el de mayor `rm_calculado` por día. Usado exclusivamente para la gráfica y para `ultimoRM`/`ultimaUnidad`. El historial sigue mostrando cada registro individual.

## WODs — módulo completo

### Modelo `WOD` — campos relevantes

| Campo | Tipo | Descripción |
|---|---|---|
| `activo` | `Boolean` (default `True`) | `True` → aparece en "WODs Activos"; `False` → aparece en "Historial de WODs" |
| `es_personalizado` | `Boolean` (default `False`) | Distingue WODs regulares de personalizados |
| `genero_destino` | `String(20)`, nullable | `"masculino"` \| `"femenino"` — solo para personalizados |
| `tipo` | `String(50)`, nullable | Formato del WOD: `"For Time"` \| `"AMRAP"` \| `"EMOM"` \| `"Por Rondas"` \| `"Fuerza"` \| `"Otro"` |

### Separación activo / historial

El campo `activo` es la distinción principal entre secciones (NO la fecha):
- `activo=True` → sección **"WODs Activos"** (visible para todos los roles)
- `activo=False` → sección **"Historial de WODs"** (solo admin/coach)

Al hacer toggle, el WOD se mueve entre secciones instantáneamente en el frontend sin recargar.

**`GET /wods/`** acepta `activo: Optional[bool]` y `skip: int` para filtrar y paginar. Sin el parámetro `activo`, staff ve todos; clientes solo ven `activo=True`.

### WodsView — vista regular

Ruta `/wods` (todos los roles autenticados).

**Sección "WODs Activos":** fetch `GET /wods/?activo=true&limit=50`. Dark cards con badge del tipo (si existe). Staff ve botones de toggle (mover a historial), editar y eliminar.

**Sección "Historial de WODs":** solo staff. Fetch `GET /wods/?activo=false&limit=30`. Lista plana con "Última fecha" bajo el nombre, badge del tipo, buscador por nombre y chips de filtro por tipo. Paginado con "Cargar más" (skip/limit). El botón de toggle restaura el WOD a activos.

**Chips de filtro en historial:** Todos / For Time / AMRAP / EMOM / Por Rondas / Fuerza / Otro. Se combinan con el buscador de texto. "Cargar más" se oculta cuando hay filtro activo.

### WodsPersonalizadosView — vista personalizada

Ruta `/wods/personalizados` (roles: `admin`, `coach`, `cliente`). `GET /wods/personalizados` acepta `activo: Optional[bool]` para staff.

**Vista Staff (admin + coach):**
- Stats: conteo de WODs activos por género (masculino / femenino)
- Sección "WODs Personalizados Activos": dark cards con badge de género + badge de tipo
- Sección "Historial de Personalizados": lista plana con badge de género + badge de tipo, buscador y chips de filtro por tipo
- Botón "Nuevo WOD" visible para admin y coach

**Vista Cliente:** solo ve WODs activos filtrados por su género (el backend filtra). Sección "Tu WOD de Hoy" (fecha actual) + "Historial" (fechas anteriores).

El filtro de género en el frontend usa `localStorage.getItem('userGenero')`. El sidebar muestra el enlace a staff (admin/coach) y a clientes con plan que lo incluya.

**Backend:** `GET /wods/personalizados` retorna todos los WODs para `admin` o `coach`; para clientes filtra por género y `activo=True`. `POST /wods/` permite crear personalizados a admin y coach (antes era solo admin).

### WodFormView — formulario

Ruta `/wods/nuevo` y `/wods/:id/editar` (admin/coach). Soporta WODs regulares y personalizados vía `route.meta.personalizado`. Rutas de personalizados (`/wods/personalizados/nuevo`, `/wods/personalizados/:id/editar`) accesibles para admin y coach.

Campos del form: `titulo`, `fecha`, **`tipo`** (select con 6 opciones, opcional), `descripcion`, `activo` (toggle), `ejercicios` (via `WodEjerciciosEditor`). Para personalizados en modo creación: selección múltiple de género (masculino / femenino), crea un WOD por género seleccionado.

### Catálogo de ejercicios

**Modelo `Ejercicio`** — campo nuevo:
- `categoria: String(50)`, nullable — `"Cardio"` \| `"Fuerza"` \| `"Gimnasia"` \| `"Olímpico"` \| `"Otro"`

**`GET /ejercicios/`** acepta `categoria: Optional[str]` para filtrar por categoría en el backend.

**`EjerciciosView.vue`** (admin/coach):
- Chips de filtro por categoría encima del grid (se combinan con el buscador)
- Badge de color en cada card: Cardio → rojo, Fuerza → azul, Gimnasia → púrpura, Olímpico → ámbar, Otro → gris
- Campo select de categoría en el modal de crear/editar

**`WodEjerciciosEditor.vue`** (componente de selección al crear/editar un WOD):
- Chips de filtro por categoría encima del select de ejercicios — facilita encontrar el ejercicio al armar el WOD
- Muestra la categoría del ejercicio como badge junto al nombre en la lista de ejercicios del WOD

## Métodos de Pago

Tabla `metodos_pago` — cuentas bancarias / transferencia que el admin expone en la pantalla de planes para que los usuarios sepan a dónde pagar.

**Modelo** (`MetodoPago` en `models.py`): `banco`, `tipo_cuenta` (ahorros, corriente, nequi, daviplata…), `numero_cuenta`, `orden` (int para ordenar), `activo` (bool), `created_at`.

**Router** (`backend/routers/metodos_pago.py`, prefix `/metodos-pago`):
- `GET /metodos-pago/` — lista los activos ordenados por `orden` asc. Visible para cualquier usuario autenticado.
- `POST /metodos-pago/` — crea uno nuevo; asigna `orden` al final. Solo admin.
- `PATCH /metodos-pago/{id}` — actualiza banco, tipo_cuenta, numero_cuenta, orden o activo. Solo admin.
- `DELETE /metodos-pago/{id}` — elimina. Solo admin.

Los schemas Pydantic (`MetodoPagoCreate`, `MetodoPagoUpdate`) están definidos inline en el router (no hay archivo separado en `schemas/`).

## Servicio Biométrico (Bridge .NET)

### Arrancar el bridge

Lo más simple: usar el launcher de la raíz (`start-dev.ps1`) — lanza el bridge con UAC junto con backend y frontend.

Manual:
```powershell
# Compilar
dotnet build servicio_biometrico\HuelleroBridge.csproj

# Ejecutar — DEBE correrse como Administrador (acceso al driver USB)
Start-Process -FilePath "servicio_biometrico\bin\Debug\net48\HuelleroBridge.exe" -Verb RunAs
```

**Logs en vivo:** `servicio_biometrico\ver-logs.cmd` (tail coloreado de `bridge.log`).

**A qué backend apunta:** por defecto el bridge habla con el backend de **Railway (producción)** — ver `BridgeConfig.cs`. Para apuntarlo a un backend local en dev, definir `JSB_API_BASE=http://localhost:8000` antes de arrancarlo. `ApiBase`/`BridgeSecret` son `static readonly` (se leen **una sola vez** al iniciar), así que tras cambiar la env var hay que **reiniciar el bridge**. Si el enrolamiento falla con `Excepción al guardar template: Error al enviar la solicitud` (un `HttpRequestException` de conexión, no de TLS), casi siempre es que `ApiBase` apunta a un backend que no responde — confirmar con la línea `[CONFIG] ApiBase` del log al arrancar.

### Por qué .NET y no Python

El SDK de DigitalPersona U.are.U 4500 ("One Touch for Windows .NET Edition") solo expone DLLs COM para .NET Framework x86. No hay bindings para Python.

### Requisitos críticos de arquitectura

- **`new Capture(Priority.High)`**: el SDK por defecto usa `Priority.Normal`, que solo entrega eventos cuando la ventana vinculada al hilo tiene foco. Como `BridgeForm` está oculta y nunca toma foco, con Normal **no llega ningún evento**. La propiedad `Priority` es read-only y debe pasarse por constructor (`new Capture(Priority.High)` en `FingerprintCapture.cs`). Ésta es la pieza que habilita la captura en background; sin esto ningún truco de message pump alcanza.
- **`[STAThread]` + `Application.Run(form)`**: el SDK usa COM para despachar eventos (`OnComplete`, `OnFingerTouch`, etc.) a través del message pump de Windows. Sin un hilo STA con message pump activo, los eventos nunca se entregan aunque el lector esté conectado. La solución es `[STAThread]` en `Main` y `Application.Run(new BridgeForm(...))`.
- **`BridgeForm`**: ventana invisible (off-screen a -32000,-32000, `Opacity=0`, `ShowInTaskbar=false`) que provee el HWND necesario para el message pump COM. El `FingerprintCapture` se inicializa en `OnLoad` (después de que el HWND existe). La invisibilidad es solo estética — la captura background depende de `Priority.High`, no de la posición de la ventana.
- **x86**: el proyecto está fijado a `PlatformTarget=x86` porque las DLLs del SDK son de 32 bits.

### Cosas que NO resuelven el problema de background (no agregar)

Históricamente se agregaron varios trucos buscando captura en background antes de descubrir `Priority.High`. Ya fueron eliminados de `Program.cs`. **No los re-introduzcas** salvo que tengas evidencia concreta de un problema distinto:

- `SetProcessInformation` con `PROCESS_POWER_THROTTLING_EXECUTION_SPEED` (opt-out de EcoQoS de Win11) — el throttling no era la causa.
- `Process.PriorityClass = AboveNormal` — el problema no era prioridad de proceso.
- `DeshabilitarQuickEdit` (manipular `ENABLE_QUICK_EDIT` del stdin) — irrelevante porque `FreeConsole()` libera la consola al arrancar.

Lo único conservado en `Program.cs` además del shell WinForms es `SetThreadExecutionState(ES_SYSTEM_REQUIRED)` para evitar que la PC del gym se duerma sola.

### Archivos del bridge

| Archivo | Rol |
|---|---|
| `Program.cs` | Entry point `[STAThread]`; redirige logs a `bridge.log`, suelta consola con `FreeConsole`, levanta WebSocket/HttpApi/BridgeForm. Al arrancar loguea `[CONFIG] ApiBase` y `[CONFIG] BridgeSecret` (definido/vacío) — primer log a revisar si el enrolamiento o las asistencias fallan. |
| `BridgeForm.cs` | Ventana WinForms invisible (HWND para message pump COM); crea `FingerprintCapture` en `OnLoad` |
| `BridgeConfig.cs` | Config por entorno (fuente única): `ApiBase` (env `JSB_API_BASE`, **default = backend de Railway en producción**; definir `JSB_API_BASE=http://localhost:8000` para apuntar a un backend local en dev) y `BridgeSecret` (env `BRIDGE_SECRET`, default `jain_bridge_secret_2024`). Referenciado por `FingerprintCapture` y `HttpApi`. |
| `FingerprintCapture.cs` | Implementa `DPFP.Capture.EventHandler`; instancia `new Capture(Priority.High)` para captura en background; maneja enrolamiento, verificación y acceso. Incluye cooldown de `CooldownSegundos` (4 s) por usuario en modo acceso para evitar doble-registro cuando el usuario pone el dedo varias veces seguidas. Dispara la palanquera vía `RelayController.Abrir()` cuando el backend confirma una **entrada** (no en salida). |
| `RelayController.cs` | Abre la palanquera mandando el byte `'A'` por USB-serial a un Arduino UNO. Ver sección "Palanquera (relé + Arduino)" más abajo. |
| `arduino/palanquera_rele/palanquera_rele.ino` | Sketch del Arduino UNO que controla el módulo de relé. |
| `ver-logs.ps1` / `.cmd` | Tail coloreado de `bridge.log` en vivo |
| `EnrollmentState.cs` | Estado compartido (thread-safe con `lock`) entre captura y HTTP API |
| `HttpApi.cs` | `HttpListener` en puerto 8001; endpoints REST consumidos por el frontend. Recibe el `RelayController` (vía `BridgeForm.Relay`) para la apertura manual de palanquera. |
| `WebSocketHub.cs` | Servidor WebSocket en puerto 8765 (Fleck); broadcast de eventos en tiempo real |
| `HuelleroBridge.csproj` | net48 x86; referencia DLLs SDK desde `C:\Program Files\DigitalPersona\One Touch SDK\.NET\Bin\` |

### Palanquera (relé + Arduino)

El bridge abre una palanquera/torniquete cuando un usuario válido marca **entrada**. El control físico es un **Arduino UNO** con un **módulo de relé SRD-05VDC-SL-C** (activo-bajo) conectado por USB-serial.

**División de responsabilidades — el Arduino es el dueño del tiempo de pulso:**
- El bridge solo manda un byte `'A'` cuando hay entrada aprobada. No bloquea esperando los 5 s.
- El Arduino, al recibir `'A'`, activa el relé `RELE_MS` (5000 ms) y lo cierra solo (loop no bloqueante con `millis()`). Si el bridge se cae o el PC se reinicia a mitad de pulso, la palanquera vuelve a reposo (cerrada) igual.

**Protocolo serial (9600 baud, line ending `\n`):**

| Dirección | Mensaje | Significado |
|---|---|---|
| bridge → arduino | `'A'` | Abrir palanquera (pulso de 5 s) |
| bridge → arduino | `'P'` | Ping (usado para autodetección de puerto) |
| arduino → bridge | `JSB-PALANQUERA READY` | Emitido al arrancar el sketch |
| arduino → bridge | `JSB-PALANQUERA OK` | Respuesta al ping `'P'` |

**Punto de disparo:** `FingerprintCapture.RegistrarAsistencia()` llama `_relay?.Abrir()` **solo si `tipo == "entrada"`**. En salida no se dispara. Acceso denegado (membresía vencida → HTTP no-2xx) tampoco abre.

**Detección de puerto COM:** `RelayController` lee la env var `PALANQUERA_COM` (ej. `COM3`). Si no está definida, autodetecta: abre cada puerto, manda `'P'` y toma el que responde con la firma `JSB-PALANQUERA`. Esto cubre el caso de que el número de COM cambie entre reconexiones del cable.

**Tolerante a ausencia de hardware:** si no hay Arduino conectado, el bridge arranca y registra asistencias normalmente; solo loguea `[RELE] Sin conexión al Arduino` y no abre la palanquera. La huella sigue funcionando.

**Reset-on-open del UNO:** el Arduino UNO se reinicia cada vez que se abre el puerto serial (por `DtrEnable=true`). Por eso `RelayController` espera 2 s tras abrir antes de usar el puerto, y mantiene la conexión abierta (no abre/cierra por cada acceso).

**Cableado (módulo de 1 canal):** `VCC→5V`, `GND→GND`, `IN→D7`. La palanquera va a los bornes `NO/COM` (normalmente abierto) del relé. Si tu módulo fuera activo-alto, intercambiá `RELE_ON`/`RELE_OFF` en el `.ino`.

**Subir el sketch:** abrir `arduino/palanquera_rele/palanquera_rele.ino` en el Arduino IDE, seleccionar placa "Arduino UNO" y el puerto, y cargar. El pin del relé es `PIN_RELE = 7` y el tiempo abierto `RELE_MS = 5000`.

### DLLs del SDK referenciadas

`DPFPDevNET.dll`, `DPFPEngNET.dll`, `DPFPShrNET.dll`, `DPFPVerNET.dll`
Ruta: `C:\Program Files\DigitalPersona\One Touch SDK\.NET\Bin\`

### HTTP API del bridge (`http://localhost:8001`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/status` | Estado completo: lector, enrolamiento y verificación |
| `POST` | `/enroll/{id}?nombre=X` | Inicia enrolamiento para el usuario `id` |
| `DELETE` | `/enroll` | Cancela enrolamiento en curso |
| `POST` | `/verify/start` | Carga templates del backend e inicia modo verificación |
| `DELETE` | `/verify` | Cancela verificación en curso |
| `POST` | `/access/reload` | Recarga el cache de templates del modo acceso |
| `POST` | `/palanquera/abrir` | Apertura manual de la palanquera (dispara `RelayController.Abrir()`). No registra asistencia. Responde `503` si no hay relé. |

**Apertura manual de palanquera:** botón verde "Abrir palanquera" en `UsuariosView` (admin/coach) que hace `POST http://localhost:8001/palanquera/abrir`. Pensado para cuando la huella no se reconoce o entra un invitado. El `HttpApi` recibe el `RelayController` vía `BridgeForm.Relay` (expuesto en `Program.cs`). Como llama a `localhost:8001`, **solo funciona desde la PC del gym** donde corre el bridge — no desde un celular remoto.

### Flujo de enrolamiento

1. Frontend llama `POST /enroll/{usuario_id}`
2. Bridge pone `EnrollmentState.Activo = true`
3. Usuario coloca el dedo 4 veces; `OnComplete` acumula muestras en `Enrollment`
4. Al completar 4 muestras, `Enrollment.Template` está listo
5. Bridge llama `POST /usuarios/{id}/huella-template` con header `X-Bridge-Secret`
6. Backend guarda el template Base64 en `usuarios.huella_template` y `huella_id = "dp_{id}"`
7. Frontend detecta `completado=true` via polling de `/status` y cierra el modal

### Flujo de verificación

1. Frontend llama `POST /verify/start`
2. Bridge carga templates con `GET /usuarios/con-template/lista` (header `X-Bridge-Secret`)
3. Usuario coloca el dedo; `OnComplete` extrae `FeatureSet` con `DataPurpose.Verification`
4. Bridge itera todos los templates y llama `Verification.Verify(features, template, ref result)`
5. Si `result.Verified = true` → `EnrollmentState.MarcarVerifyEncontrado(usuario)`
6. Frontend detecta resultado via polling y muestra nombre + botón "Ver perfil"

### Autenticación bridge ↔ backend (`X-Bridge-Secret`)

El bridge no tiene JWT. Los endpoints `POST /usuarios/{id}/huella-template` y `GET /usuarios/con-template/lista` aceptan el header `X-Bridge-Secret: <valor>` como alternativa al JWT de admin/coach.

El secreto se define en `backend/.env` como `BRIDGE_SECRET=jain_bridge_secret_2024`. Si el header no coincide, el backend exige JWT normal.

### Modelo de datos relevante (tabla `usuarios`)

| Campo | Tipo | Uso |
|---|---|---|
| `huella_id` | `String(100)`, único, nullable | Identificador de forma `dp_{usuario_id}`; se pone al registrar template |
| `huella_template` | `Text`, nullable | Template FMD en Base64 generado por el SDK |
| `esta_en_gym` | `Boolean` | `True` al marcar entrada; vuelve a `False` solo por tiempo (`_job_reset_gym`). No hay registro de salida. |
| `fecha_vencimiento` | `Date` | Validada en `POST /asistencia/por-usuario/{id}` antes de registrar entrada |
| `fecha_nacimiento` | `Date`, nullable | Cumpleaños del miembro; usada por `GET /usuarios/cumpleanos-hoy` |

### Endpoints de asistencia relevantes

- `POST /asistencia/por-usuario/{usuario_id}` — registra entrada; valida membresía vigente en cada marcación. Llamado por el bridge o admin.
- `GET /asistencia/mi-historial?meses=N` — historial propio
- `GET /asistencia/historial/{usuario_id}?meses=N` — historial de cualquier usuario (admin/coach)

### Frontend: componentes de huella

**`UsuariosView.vue`** (admin):
- Botón "Buscar por Huella" junto a "Nuevo Usuario" → modal de verificación
- Modal de enrolamiento accesible desde la tabla de usuarios

**`UsuarioPerfilView.vue`** (admin/coach):
- Card "Huella digital" muestra estado (`Registrada` / `No registrada`)
- Botón "Registrar" / "Reemplazar" al lado del estado → mismo modal de enrolamiento
- Al completar, refresca el usuario vía `GET /usuarios/{id}` sin recargar página

**Polling pattern (frontend):**
```js
const _pollStatus = async () => {
  const r    = await fetch('http://localhost:8001/status')
  const data = await r.json()
  // usar data.enrolamiento o data.verificacion según el modo
}
const _iniciarPoll = () => {
  _pollStatus()                          // primer fetch inmediato (sin esperar el delay)
  intervalo = setInterval(_pollStatus, 600)
}
```
Ejecutar `_pollStatus()` inmediatamente antes del `setInterval` es importante: sin esto la UI tarda 600 ms en reflejar el estado activo.

## Environment Variables

Copy `backend/.env.example` to `backend/.env`. Required keys:
```
SECRET_KEY=
ADMIN_NOMBRE=
ADMIN_EMAIL=
ADMIN_PASSWORD=
ADMIN_TELEFONO=
ADMIN_DOCUMENTO=
BRIDGE_SECRET=          # Clave compartida con el bridge .NET para autenticarse sin JWT
```

Opcionales (producción):
```
DATABASE_URL=           # Postgres; si falta, usa SQLite local (sqlite:///crossfit.db)
CORS_ORIGINS=           # Coma-separado; si falta, usa los puertos de Vite local
```

`SECRET_KEY` se lee con `os.environ["SECRET_KEY"]` en `security.py` (revienta si falta — siempre debe estar seteada en el host).

Frontend (`frontend/.env.example`):
```
VITE_API_URL=           # URL del backend; si falta, usa http://127.0.0.1:8000 (dev)
```

## CORS

Los orígenes se leen de la env var `CORS_ORIGINS` (coma-separado) en `backend/main.py`. Si no está definida, el default son los puertos de Vite (`localhost:5173/5174`, `127.0.0.1:5173/5174`). En producción hay que setear el dominio del frontend (ej. `CORS_ORIGINS=https://jainsportbox.netlify.app`, **sin barra final**).

## Deployment (Railway backend + Netlify frontend)

El detalle completo va en `DEPLOYMENT.md`. Setup actual: **backend en Railway** (`https://web-production-ca5df.up.railway.app`), **frontend en Netlify** (`https://jainsportbox.netlify.app`), **Postgres en Railway**.

**Backend (Railway):**
- Builder: Dockerfile explícito (`Dockerfile` en la raíz, `railway.toml` con `builder = "dockerfile"`). Es necesario porque el repo es mixto Python/.NET y nixpacks intentaba `dotnet restore`. El Dockerfile construye solo el backend FastAPI.
- El start command sale del `CMD` del Dockerfile (`sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"`). **No usar un "Custom Start Command" con `cd` en la UI de Railway** ni un `Procfile` con `cd backend && ...`: Railway los corre en modo *exec* (sin shell) y falla con `The executable cd could not be found`. Por eso no hay `Procfile` en el repo.
- Variables requeridas en Railway: las 7 de arriba (`SECRET_KEY`, `ADMIN_*`, `BRIDGE_SECRET`) + `DATABASE_URL=${{Postgres.DATABASE_URL}}` + `CORS_ORIGINS=https://jainsportbox.netlify.app`.

**Frontend (Netlify):**
- Config en `netlify.toml`: `base = "frontend"`, `command = "npm run build"`, `publish = "dist"` (relativo a base — **no** `frontend/dist`, daría `frontend/frontend/dist`). Rewrite SPA `/* → /index.html`.
- Variable en Netlify: `VITE_API_URL=https://web-production-ca5df.up.railway.app` (sin barra final).
- `frontend/node_modules` **no** debe estar trackeado en git: sus binarios (`vite`) commiteados desde Windows pierden el bit de ejecución y Netlify falla con `vite: Permission denied`. Está en `.gitignore`; Netlify hace su propio `npm install`.

**Gotchas de dependencias (diferencias dev local vs. imagen limpia):**
- `database.py` reescribe la URL de Postgres a `postgresql+psycopg://` para usar psycopg v3 (lo que está en `requirements.txt`), porque psycopg2 no está instalado. Maneja tanto `postgres://` como `postgresql://` (Railway entrega el segundo).
- `bcrypt` está fijado a `4.0.1` en `requirements.txt`: passlib 1.7.4 revienta con bcrypt ≥ 4.1 (`ValueError: password cannot be longer than 72 bytes` en la detección de backend).
