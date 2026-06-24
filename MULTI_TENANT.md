# Multi-tenant SaaS — plan y estado

Objetivo: convertir JainSportBox de un sistema de un solo gimnasio a una plataforma SaaS donde un **SuperAdmin** registra múltiples gimnasios (tenants) independientes, cada uno con sus propios usuarios, datos y módulos contratados.

Este documento es el registro vivo de avance. Actualízalo cuando se cierre o se abra una fase nueva.

## Estado general

| Fase | Estado |
|---|---|
| Fase 1 — Aislamiento de datos (`gym_id`) | ✅ Completa |
| Fase 2 — Feature flags por módulo | ✅ Completa |
| Fase 3 — SuperAdmin | ✅ Completa (backend + frontend) |
| Fase 4 — Bridge biométrico multi-gym | ❌ Pendiente (requiere hardware) |
| Frontend SaaS (selector de gym, panel SuperAdmin, sidebar por módulo) | ✅ Completa |
| Resolución de gym en el login (slug) | ✅ Completa |
| Verificación end-to-end con la app corriendo | ✅ Backend verificado con uvicorn real — ver "Cómo verificar" |

## Fase 1 — Aislamiento de datos (completa)

- Modelo `Gimnasio` (`backend/models.py`) — un row por tenant: `id`, `nombre`, `slug`, `activo`.
- `gym_id` (FK a `gimnasios.id`, `NOT NULL`) agregado a **todas** las tablas de dominio: `usuarios`, `planes`, `pagos`, `wods`, `productos`, `ventas`, `asistencias`, `movimientos_financieros`, `medidas_salud`, `marcas_rm`, `alertas_membresia`, `metodos_pago`, `ejercicios`.
- Uniques globales rotos y reemplazados por compuestos `(gym_id, X)`:
  - `usuarios.email` y `usuarios.documento_identidad` → `uq_usuario_gym_email`, `uq_usuario_gym_documento`.
  - `ejercicios.nombre` → `uq_ejercicio_gym_nombre` (cada gym tiene su propio catálogo de ejercicios).
- Migraciones en `backend/main.py`: backfill de todo lo existente al gimnasio `id=1` ("Jain Sport Box"), reconstrucción de tablas donde el unique constraint cambió (`usuarios`, `ejercicios`), `ALTER TABLE ... ADD COLUMN gym_id INTEGER NOT NULL DEFAULT 1` para el resto. Verificadas contra SQLite simulando el esquema legado (backfill, aislamiento entre gyms, rechazo de duplicados dentro del mismo gym, idempotencia).
- JWT de usuario (`security.py`) ahora lleva `gym_id` además de `sub` (email). `get_current_user` filtra por `email + gym_id`, no solo email.
- Los **14 routers** de dominio quedaron filtrados por `current_user.gym_id` en cada lectura, escritura, update y delete — no solo en creación.
- Casos especiales resueltos:
  - Endpoints que aceptan tanto `X-Bridge-Secret` como JWT (`asistencia.py`, `usuarios.py` huella) validan que el `gym_id` del caller JWT coincida con el del usuario objetivo.
  - El job programado `generar_alertas` (sin `current_user`, corre en background vía APScheduler) asigna `gym_id` desde `usuario.gym_id` de cada alerta creada.

**Limitación conocida:** el login (`POST /login`) resuelve el usuario por email sin que el cliente indique a qué gimnasio pertenece — toma el primer match. Funciona mientras la base de usuarios reales no tenga el mismo email repetido entre gimnasios distintos. Hay que resolver esto antes de dar de alta un segundo gimnasio real (ver "Próximos pasos").

## Fase 2 — Feature flags por módulo (completa)

- Tablas nuevas: `modulos` (catálogo fijo: `id`, `clave`, `nombre`, `descripcion`) y `gimnasio_modulos` (puente `gym_id` ↔ `modulo_id`, con `activo` y `fecha_expiracion` opcional).
- Helper `backend/modulos.py`:
  - `gimnasio_tiene_modulo(db, gym_id, clave)` — chequeo directo, usado en endpoints que no tienen `current_user` disponible (rutas autenticadas solo con `X-Bridge-Secret`).
  - `require_modulo(clave)` — dependencia FastAPI (403 si el gym no tiene el módulo activo), usada en endpoints con JWT.
- Módulos del catálogo actual: `wods` (WODs y puntuación) y `biometria` (lector de huellas).
- Aplicación:
  - `wods.py` — gateado a nivel de router completo (`dependencies=[Depends(require_modulo("wods"))]`).
  - `asistencia.py` / `usuarios.py` (endpoints de huella) — gateados endpoint por endpoint porque mezclan auth JWT y `X-Bridge-Secret`.
- Seed automático (`backend/seed.py: seed_modulos()`): crea el catálogo y activa ambos módulos para el gimnasio `id=1` — la instalación actual no pierde acceso a nada al migrar a multi-tenant.

## Fase 3 — SuperAdmin (completa en backend)

- Modelo `SuperAdmin` (`backend/models.py`) — separado de `Usuario`/`RolUsuario` a propósito: no pertenece a ningún `gym_id`.
- JWT propio con `scope=superadmin` en vez de `gym_id`. `security.py: get_current_superadmin` lo valida (rechaza tokens de usuario normal y viceversa).
- `backend/routers/superadmin.py` (prefix `/superadmin`):
  - `POST /superadmin/login`
  - `GET /superadmin/gimnasios`, `POST /superadmin/gimnasios` (crea el gym + su admin inicial en una transacción), `PATCH /superadmin/gimnasios/{id}` (activar/desactivar, renombrar)
  - `GET /superadmin/modulos` (catálogo)
  - `GET /superadmin/gimnasios/{id}/modulos`, `PATCH /superadmin/gimnasios/{id}/modulos/{modulo_id}` (activar/desactivar un módulo para un gym)
- Seed opcional (`backend/seed.py: seed_superadmin()`): solo crea el primer SuperAdmin si `SUPERADMIN_EMAIL`/`SUPERADMIN_PASSWORD` están en el entorno — instalaciones de un solo gimnasio sin panel de SuperAdmin no necesitan definirlas.

## Trabajo completado en esta iteración (web SaaS)

### 1. Resolución de gimnasio en el login ✅
- `POST /login` acepta un campo de formulario opcional `gym_slug`. Si viene, el login se acota a ese gimnasio (`Usuario.email + gym_id`); si el slug no existe → 401. Sin slug se conserva el fallback legacy "primer match por email" (compat. con instalaciones de un solo tenant).
- Endpoint público `GET /gimnasios` (en `auth.py`) lista los gimnasios activos (`slug` + `nombre`) para alimentar el selector del login.
- `LoginView.vue` carga `GET /gimnasios` al montar y muestra un `<select>` de gimnasio **solo si hay más de uno**; manda `gym_slug` en el POST de login.

### 2. Frontend — panel de SuperAdmin ✅
- Rutas top-level `/superadmin/login` y `/superadmin` (fuera del `Dashboard.vue` de gym), con guard propio en `router/index.js` basado en `localStorage.superToken` (token separado del de gym, scopes mutuamente excluyentes).
- `superApi.js`: instancia axios dedicada que inyecta `superToken`.
- `SuperAdminLoginView.vue` (login) y `SuperAdminView.vue` (listado de gimnasios, alta con admin inicial + módulos, activar/desactivar gym, toggle de módulos por gym). Consume `routers/superadmin.py`.

### 4. Catálogo de módulos ampliado ✅
- `MODULOS_DEFAULT` en `seed.py` pasó de 2 a **10 módulos**: `usuarios`, `finanzas`, `tienda`, `wods`, `biometria` (huella + huellero), `salud`, `marcas`, `sesiones`, `alertas`, `ejercicios`. `seed_modulos()` ahora también actualiza nombre/descripción de módulos ya existentes (idempotente) y activa todos para el gym 1.
- **Gating backend (`require_modulo` a nivel router):** `wods`, `finanzas`, `tienda` (productos + ventas), `salud`, `marcas`, `alertas`, + `biometria` (endpoint-level, ya existía).
- **Gating solo-frontend** (routers no gateados a propósito por ser base/cross-dep): `usuarios` (login/perfil/admin dependen de él), `sesiones` (asistencia la usa el bridge con `X-Bridge-Secret`), `ejercicios` (el editor de WODs necesita `GET /ejercicios` aunque el gym no gestione el catálogo).
- Cross-dep `salud`↔`marcas`: la vista de Dominadas pide `GET /salud/peso` dentro de un try/catch silencioso, así que si `salud` está off pero `marcas` on, simplemente cae al input manual de peso corporal (sin error).
- El panel SuperAdmin muestra automáticamente los 10 módulos (lee del catálogo) — sin cambios extra.

### Selector de gym en el login: eliminado
Cada cuenta es única (email + contraseña) y el backend resuelve el `gym_id` desde la credencial, así que el login **no** muestra selector de gimnasio. El parámetro `gym_slug` en `POST /login` y `GET /gimnasios` se conservan en el backend (útiles para subdominios a futuro) pero el frontend ya no los usa.

### 3. Frontend — ocultar funcionalidad según módulo activo ✅
- `_serialize_me` en `auth.py` ahora devuelve `modulos_activos: string[]` además de `gym_id`, `gym_nombre`, `gym_slug`.
- Composable `useModulos.js`: `setModulos`/`clearModulos`/`tieneModulo(clave)` + `tieneModuloFor` para el guard. Guarda en `localStorage.modulosActivos`. **Ausencia de la clave = todos activos** (compat. hacia atrás).
- `Dashboard.vue` oculta WODs / WODs Personalizados del sidebar si falta el módulo `wods`; refresca módulos en mount y los limpia en logout.
- `router/index.js` gatea las rutas de WODs con `meta.modulo: 'wods'` (redirige si el gym no lo tiene).
- `UsuariosView.vue` / `UsuarioPerfilView.vue` ocultan los botones de huella/palanquera y la card de huella si falta el módulo `biometria`.

## Próximos pasos (en orden recomendado)

### Fase 4 — Bridge biométrico multi-gym
El bridge .NET no manda `gym_id`. Pendiente:
- `BridgeConfig.cs`: nueva env var `JSB_GYM_ID`, fijada por gimnasio al desplegar el bridge en su PC física.
- El bridge debe mandar `X-Gym-Id` (o equivalente) en sus llamadas HTTP al backend.
- Backend: `GET /usuarios/con-template/lista` y `POST /usuarios/{id}/huella-template` deben validar ese header cuando vienen autenticados por `X-Bridge-Secret` — hoy, sin JWT, no hay forma de saber a qué gym pertenece el bridge que llama, así que `con-template/lista` devuelve templates de **todos** los gimnasios (ver `TODO multi-tenant (Fase 4)` en `usuarios.py`).

### 5. Endurecer el aislamiento restante
- Decidir si `huella_id` (hoy único global) debe pasar a único por gym o se mantiene global (actualmente es seguro porque tiene forma `dp_{usuario_id}` y los IDs de usuario son globales, pero vale la pena revisar si el bridge multi-gym cambia ese esquema).
- Auditar que ningún router nuevo que se agregue a futuro olvide el filtro `gym_id` — considerar la Opción B mencionada originalmente (filtro automático vía evento `do_orm_execute` de SQLAlchemy) si el número de routers sigue creciendo y el filtrado manual se vuelve propenso a errores.

## Cómo verificar

**Backend — verificado con `uvicorn` real sobre SQLite** (iteración web SaaS). Flujos probados vía HTTP:
- `GET /gimnasios` (público) lista los gimnasios activos.
- Login del admin del gym 1 → `/me` devuelve `gym_id`, `gym_nombre`, `gym_slug` y `modulos_activos: ["wods","biometria"]`.
- SuperAdmin: `POST /superadmin/login`, `POST /superadmin/gimnasios` (crea gym 2 + admin + módulo `wods`), `GET /superadmin/gimnasios`.
- Login del admin del gym 2 con `gym_slug=crossfit-demo` → `/me` muestra `gym_id=2` y solo `["wods"]` (aislamiento de módulos OK). Slug equivocado o inexistente → 401.
- Toggle de módulo `wods` off en gym 2 → `/me` refleja `[]` y `GET /wods/` responde **403** (`require_modulo`).

**Frontend — no verificado en ejecución**: Node.js no está instalado en la máquina donde se hizo este cambio (`where node` vacío, sin `node_modules`), así que no se pudo correr `npm run build` ni `vite`. El código quedó escrito siguiendo los patrones existentes; **falta correr `npm install && npm run build` y un smoke test manual del login multi-gym, el sidebar por módulo y el panel `/superadmin`.**

Migraciones SQL críticas (gym_id en `usuarios`, reconstrucción de `ejercicios`) ya estaban validadas en iteraciones previas: backfill, aislamiento entre gyms, rechazo de duplicados dentro del mismo gym, idempotencia.

**Antes de desplegar a producción:**
1. Correr `uvicorn main:app --reload` localmente con tu `.env` real sobre una **copia** de `crossfit.db` (no la de producción) y confirmar que arranca sin errores de migración.
2. Probar login con el admin existente y confirmar que `/me`, `/usuarios/`, `/wods/` etc. siguen funcionando igual que antes (el gym `id=1` debe comportarse exactamente como la instalación de un solo tenant).
3. Si vas a probar un segundo gimnasio, usar `POST /superadmin/gimnasios` y verificar que sus usuarios no aparecen en ningún listado del gym 1 y viceversa.
