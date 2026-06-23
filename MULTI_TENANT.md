# Multi-tenant SaaS — plan y estado

Objetivo: convertir JainSportBox de un sistema de un solo gimnasio a una plataforma SaaS donde un **SuperAdmin** registra múltiples gimnasios (tenants) independientes, cada uno con sus propios usuarios, datos y módulos contratados.

Este documento es el registro vivo de avance. Actualízalo cuando se cierre o se abra una fase nueva.

## Estado general

| Fase | Estado |
|---|---|
| Fase 1 — Aislamiento de datos (`gym_id`) | ✅ Completa |
| Fase 2 — Feature flags por módulo | ✅ Completa |
| Fase 3 — SuperAdmin | ✅ Completa (backend) |
| Fase 4 — Bridge biométrico multi-gym | ❌ Pendiente |
| Frontend SaaS (selector de gym, panel SuperAdmin) | ❌ Pendiente |
| Verificación end-to-end con la app corriendo | ⚠️ Parcial — ver "Cómo verificar" |

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

## Próximos pasos (en orden recomendado)

### 1. Resolución de gimnasio en el login (bloqueante para dar de alta un 2º gym real)
Hoy `POST /login` busca por email sin contexto de tenant. Antes de tener un segundo gimnasio con usuarios reales, decidir y construir uno de:
- Selector de gimnasio en el login (dropdown o input de slug) → el frontend manda `gym_slug` además de username/password.
- Subdominio por gimnasio (`boxA.tudominio.com`) → el backend resuelve `gym_id` por `Host` header.
- Mantener "primer match por email" solo como fallback de migración, deprecar luego.

### 2. Frontend — panel de SuperAdmin
No existe UI todavía. Construir un área separada (ruta `/superadmin`, login propio, fuera del `Dashboard.vue` de gym) que consuma `routers/superadmin.py`: alta de gimnasios, activar/desactivar módulos, ver listado.

### 3. Frontend — ocultar funcionalidad según módulo activo
`GET /me` no devuelve todavía qué módulos tiene activos el gym del usuario. Falta:
- Ampliar `_serialize_me` en `auth.py` con `modulos_activos: string[]`.
- `useAuth.js` (o un composable nuevo `useModulos.js`) que expone `tieneModulo(clave)`.
- `Dashboard.vue` oculta WODs/Mis Marcas/biometría del sidebar si el módulo no está activo (mismo patrón que ya usan con roles).
- Las vistas (`WodsView`, modal de huella) deben manejar el 403 de `require_modulo` con un mensaje claro en vez de un error genérico.

### 4. Fase 4 — Bridge biométrico multi-gym
El bridge .NET no manda `gym_id`. Pendiente:
- `BridgeConfig.cs`: nueva env var `JSB_GYM_ID`, fijada por gimnasio al desplegar el bridge en su PC física.
- El bridge debe mandar `X-Gym-Id` (o equivalente) en sus llamadas HTTP al backend.
- Backend: `GET /usuarios/con-template/lista` y `POST /usuarios/{id}/huella-template` deben validar ese header cuando vienen autenticados por `X-Bridge-Secret` — hoy, sin JWT, no hay forma de saber a qué gym pertenece el bridge que llama, así que `con-template/lista` devuelve templates de **todos** los gimnasios (ver `TODO multi-tenant (Fase 4)` en `usuarios.py`).

### 5. Endurecer el aislamiento restante
- Decidir si `huella_id` (hoy único global) debe pasar a único por gym o se mantiene global (actualmente es seguro porque tiene forma `dp_{usuario_id}` y los IDs de usuario son globales, pero vale la pena revisar si el bridge multi-gym cambia ese esquema).
- Auditar que ningún router nuevo que se agregue a futuro olvide el filtro `gym_id` — considerar la Opción B mencionada originalmente (filtro automático vía evento `do_orm_execute` de SQLAlchemy) si el número de routers sigue creciendo y el filtrado manual se vuelve propenso a errores.

## Cómo verificar

No se pudo correr un test end-to-end con `TestClient`/`uvicorn` real en el entorno donde se hizo este cambio (sin acceso a red para instalar `fastapi`/`sqlalchemy`). Lo que sí se validó:
- `py_compile` sobre todo `backend/` — compila limpio.
- Migraciones SQL críticas (gym_id en `usuarios`, reconstrucción de `ejercicios`) probadas contra SQLite real simulando el esquema legado: backfill, aislamiento entre gyms, rechazo de duplicados dentro del mismo gym, idempotencia en reintentos.

**Antes de desplegar a producción:**
1. Correr `uvicorn main:app --reload` localmente con tu `.env` real sobre una **copia** de `crossfit.db` (no la de producción) y confirmar que arranca sin errores de migración.
2. Probar login con el admin existente y confirmar que `/me`, `/usuarios/`, `/wods/` etc. siguen funcionando igual que antes (el gym `id=1` debe comportarse exactamente como la instalación de un solo tenant).
3. Si vas a probar un segundo gimnasio, usar `POST /superadmin/gimnasios` y verificar que sus usuarios no aparecen en ningún listado del gym 1 y viceversa.
