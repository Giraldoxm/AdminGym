# Plan de Despliegue — JainSportBox

Despliegue de JainSportBox como **página web pública (PWA instalable)** con **estación de huella local** en el gym.

**Escenario elegido:**
- **Alcance:** Mixto — clientes entran por internet + estación de huella/recepción en la PC del gym.
- **Hosting backend:** Nube gestionada (Railway / Render / Fly).
- **Base de datos:** Migración de SQLite → PostgreSQL.

---

## Arquitectura objetivo

```
┌─────────────────────────┐         ┌──────────────────────────────┐
│  Clientes (celular/web) │  HTTPS  │  Frontend PWA (Vercel/Netlify)│
│  instalan la PWA        │────────▶│  app.tudominio.com            │
└─────────────────────────┘         └───────────────┬──────────────┘
                                                     │ HTTPS (axios)
                                                     ▼
                                     ┌──────────────────────────────┐
                                     │  Backend FastAPI (Railway)    │
                                     │  api.tudominio.com + Postgres │
                                     └───────────────▲──────────────┘
                                                     │ HTTPS
                       ┌─────────────────────────────┴───────────────┐
                       │  PC del gym (recepción)                       │
                       │  • Bridge .NET (huella + Arduino) → cloud API │
                       │  • Frontend LOCAL en http://localhost (huella)│
                       └───────────────────────────────────────────────┘
```

**Razón del diseño "doble entrega" del frontend:** un navegador con página `https://` **no puede** llamar a `http://localhost:8001` (bloqueo *mixed content*). La estación de huella corre una copia **local** del frontend en `http://localhost`, que sí puede hablar con el bridge (`http://localhost` → `http://localhost`) y con el backend cloud (`http://localhost` → `https://api`, permitido). Los clientes usan la PWA en la nube y nunca tocan el bridge.

---

## Capa 1 — Base de datos (PostgreSQL)

Base de todo lo demás. Se hace y prueba en local con Postgres en Docker antes de subir nada.

### 1.1 `backend/database.py` — leer `DATABASE_URL` del entorno
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///crossfit.db")
# Railway entrega "postgres://"; SQLAlchemy 2.x exige "postgresql+psycopg://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 1.2 `backend/requirements.txt`
- Añadir `psycopg[binary]`.

### 1.3 `backend/main.py` — guard de migraciones SQLite
Las migraciones de arranque son 100% SQLite (`PRAGMA`, reconstrucción de tablas, `ALTER TABLE … ADD COLUMN`). En Postgres revientan. Envolver **todo el bloque**:
```python
if engine.url.get_backend_name() == "sqlite":
    # ... todo el bloque actual de ALTER TABLE + PRAGMA + reconstrucción ...
```
En Postgres fresco no hace falta: `Base.metadata.create_all()` ya crea el esquema final con la nulabilidad correcta (los modelos reflejan el estado final).

### 1.4 (Opcional, recomendado) Alembic
Para cambios de esquema **futuros** en Postgres, introducir Alembic en vez de seguir con el patrón de `ALTER TABLE` en el arranque.

**Entregable de la capa:** backend corriendo local contra Postgres en Docker, esquema creado, login admin funcional.

---

## Capa 2 — Migración de datos (SQLite → Postgres)

Script Python de una sola corrida:
1. `create_all()` en Postgres.
2. Dos sesiones SQLAlchemy: lee de SQLite, escribe en Postgres.
3. Copiar tablas respetando el orden de claves foráneas.
4. Resetear las secuencias de IDs (`setval`) al final.

> ~60 líneas. Se ejecuta una sola vez para llevar los datos de producción actuales.

**Entregable de la capa:** datos actuales (usuarios, pagos, marcas, etc.) visibles en Postgres.

---

## Capa 3 — Backend en la nube (Railway)

### 3.1 CORS por entorno — `backend/main.py`
```python
import os
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
# Railway: CORS_ORIGINS=https://app.tudominio.com,http://localhost:5173,http://localhost:4173
```

### 3.2 Comando de arranque
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3.3 Variables de entorno en Railway
| Variable | Origen |
|---|---|
| `DATABASE_URL` | inyectada por el addon Postgres |
| `SECRET_KEY` | generar valor seguro |
| `ADMIN_NOMBRE`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_TELEFONO`, `ADMIN_DOCUMENTO` | seed admin |
| `BRIDGE_SECRET` | clave compartida con el bridge |
| `CORS_ORIGINS` | dominios del frontend |

### 3.4 Almacenamiento de `/uploads` (fotos de perfil) — ✅ RESUELTO: Object storage (R2/S3)
El filesystem de Railway/Render es **efímero** (se borra en cada deploy → se pierden las fotos). Se eligió **almacenamiento de objetos S3-compatible** (Cloudflare R2 / AWS S3).

Implementado en `backend/storage.py`: abstracción `guardar_archivo()` / `eliminar_archivo()` usada por los routers `usuarios`, `auth` (registro) y `productos`. Si `S3_BUCKET` está definido sube al bucket vía boto3; si no, cae al filesystem local (dev). `eliminar_archivo()` tolera URLs de ambos backends, así que los registros viejos (creados en local) se siguen pudiendo borrar tras migrar.

Variables de entorno S3/R2 (ver `backend/.env.example`): `S3_BUCKET`, `S3_PUBLIC_URL`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_REGION`.

### 3.5 Archivos de despliegue (raíz del repo)
- `railway.toml` — builder nixpacks + `startCommand` (entra a `backend/`).
- `Procfile` — fallback con el mismo comando de arranque.
- `.python-version` — fija Python 3.13.

**Entregable de la capa:** `https://api.tudominio.com/docs` accesible, login funcional contra Postgres en la nube.

---

## Capa 4 — Frontend web + PWA (Vercel/Netlify)

### 4.1 Base URL por entorno — `frontend/src/api.js`
```js
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
})
```
- `.env.production` (build cloud): `VITE_API_URL=https://api.tudominio.com`
- `.env.local` (estación de huella): `VITE_API_URL=https://api.tudominio.com`

### 4.2 Configuración del host (Vercel/Netlify)
- Build command: `npm run build`
- Output dir: `dist/`
- **Rewrite SPA:** todas las rutas → `index.html` (para que el router de Vue no rompa al recargar).

### 4.3 PWA — `vite-plugin-pwa`
```js
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [vue(), VitePWA({
    registerType: 'autoUpdate',
    includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
    manifest: {
      name: 'JainSportBox', short_name: 'JainBox',
      theme_color: '#dc2626', background_color: '#ffffff',
      display: 'standalone', start_url: '/',
      icons: [
        { src: 'pwa-192.png', sizes: '192x192', type: 'image/png' },
        { src: 'pwa-512.png', sizes: '512x512', type: 'image/png' },
        { src: 'pwa-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    workbox: {
      navigateFallback: '/index.html',
      runtimeCaching: [{
        urlPattern: ({ url }) => url.origin === 'https://api.tudominio.com',
        handler: 'NetworkFirst',           // datos frescos, fallback offline
        options: { cacheName: 'api', networkTimeoutSeconds: 5 },
      }],
    },
  })],
})
```

### 4.4 Consideraciones PWA para esta app
- **No cachear** `/login` ni respuestas con token → usar `NetworkFirst`, nunca `CacheFirst` en la API.
- La PWA solo es **instalable sobre HTTPS** (por eso el frontend cloud va con dominio + TLS).
- Generar íconos `pwa-192.png`, `pwa-512.png`, `apple-touch-icon.png`.
- (Opcional) Botón "Instalar app" capturando el evento `beforeinstallprompt`.

### 4.5 Estado — ✅ IMPLEMENTADO
- `frontend/src/api.js` — `baseURL` por `VITE_API_URL` + helper `mediaUrl()` (resuelve fotos: absolutas de S3/R2 tal cual, locales con base del backend). Aplicado en `TiendaView`, `UsuariosView`, `UsuarioPerfilView`.
- `frontend/vite.config.js` — `vite-plugin-pwa` (autoUpdate). El origin del API se lee con `loadEnv` y se hornea como RegExp en el SW (NetworkFirst, no CacheFirst). Verificado en build: `registerRoute(/^https:\/\/api…/, NetworkFirst)`.
- Íconos generados en `frontend/public/`: `pwa-192.png`, `pwa-512.png`, `apple-touch-icon.png`, `favicon.ico` (rojo de marca).
- `index.html` — favicon, apple-touch-icon, theme-color, título.
- Config de host: `frontend/vercel.json` (rewrite SPA) y `netlify.toml` (base/publish + redirect SPA).
- `frontend/.env.example` documenta `VITE_API_URL`. Valores reales en el dashboard del host o `.env.production`/`.env.local` (gitignored).

**Pendiente (acción externa):** setear `VITE_API_URL` con el dominio real del API en Vercel/Netlify una vez exista (decisión de dominio aún abierta).

**Entregable de la capa:** `https://app.tudominio.com` instalable como app en Android/iOS, conectada al backend cloud.

---

## Capa 5 — Bridge biométrico (.NET, PC del gym)

### 5.1 Apuntar al backend cloud — ✅ IMPLEMENTADO
`ApiBase` y `BridgeSecret` estaban hardcodeados en `FingerprintCapture.cs` y `HttpApi.cs`. Se centralizaron en **`servicio_biometrico/BridgeConfig.cs`**, que los lee de variables de entorno con default local:
```csharp
public static readonly string ApiBase =
    (Environment.GetEnvironmentVariable("JSB_API_BASE") ?? "http://localhost:8000").TrimEnd('/');
public static readonly string BridgeSecret =
    Environment.GetEnvironmentVariable("BRIDGE_SECRET") ?? "jain_bridge_secret_2024";
```
Ambos archivos ahora referencian `BridgeConfig.*` (fuente única, sin riesgo de desincronizar el secreto). Compila OK (verificado vía `dotnet build`).

**Configurar en la PC del gym** (env vars de máquina, requieren reabrir la sesión/proceso):
```powershell
setx JSB_API_BASE "https://api.tudominio.com" /M
setx BRIDGE_SECRET "<mismo valor que el backend>" /M
```

### 5.2 Notas
- El bridge sigue exponiendo `localhost:8001` (HTTP API) y `localhost:8765` (WebSocket) para la estación local.
- El header `X-Bridge-Secret` viaja igual contra el cloud → **debe ser HTTPS** para no mandar el secreto en claro (por eso `JSB_API_BASE` debe ser `https://`).
- El bridge sigue corriendo como Administrador (acceso al driver USB) en la PC del gym.
- Recompilar requiere detener el bridge en ejecución (bloquea `bin\Debug\net48\HuelleroBridge.exe`).

**Entregable de la capa:** enrolamiento y verificación de huella funcionando contra el backend cloud.

---

## Capa 6 — Estación de huella local (recepción) — ✅ IMPLEMENTADO

Resuelve el bloqueo *mixed content*: una página `http://localhost` sí puede llamar al bridge (`http://localhost:8001`, mismo esquema) y al backend cloud (`http→https` permitido). Los clientes usan la PWA en la nube y nunca tocan esta ruta.

**Launcher `start-estacion.ps1`** (raíz; wrapper `start-estacion.cmd`):
```powershell
.\start-estacion.ps1 -ApiUrl https://api.tudominio.com
```
Hace: `npm install` (si falta) → `npm run build` con `VITE_API_URL` → sirve `dist/` con `vite preview` en `http://localhost:80` (fallback SPA incluido) → arranca el bridge si no corre.

Flags: `-Port <n>` (default 80; 80 requiere admin), `-SkipBuild` (sirve el `dist/` existente), `-NoBridge`. Si `VITE_API_URL` no es HTTPS, avisa (el `X-Bridge-Secret` viajaría en claro).

Verificado: `vite preview` sirve `/`, deep routes (`/usuarios` → 200 vía fallback SPA), `sw.js` y `manifest.webmanifest`.

- El recepcionista abre `http://localhost` en el navegador de la PC del gym.
- Los URLs del bridge (`localhost:8001`, `ws://localhost:8765`) ya están fijados a local en el frontend; el resto de llamadas van al API cloud (`VITE_API_URL`).

**Entregable de la capa:** flujo completo de recepción (marcar huella → abre palanquera → registra asistencia en cloud) operativo.

---

## Orden de ejecución recomendado

| # | Capa | Depende de |
|---|---|---|
| 1 | Base de datos (Postgres) | — |
| 2 | Migración de datos | Capa 1 |
| 3 | Backend en la nube | Capas 1–2 |
| 4 | Frontend web + PWA | Capa 3 |
| 5 | Bridge biométrico | Capa 3 |
| 6 | Estación de huella local | Capas 4–5 |

---

## Decisiones pendientes

1. ~~**Fotos de perfil (`/uploads`):**~~ ✅ RESUELTO → object storage R2/S3 (ver Capa 3.4).
2. **Dominio:** ¿dominio propio, o subdominios gratis de Railway/Vercel al inicio?
3. **Alembic:** ¿introducirlo ahora (capa 1.4) o dejar el patrón actual de migraciones?

---

## Notas de seguridad

- Forzar **HTTPS** en backend y frontend (TLS automático en Railway/Vercel).
- `BRIDGE_SECRET` y `SECRET_KEY` solo en variables de entorno, nunca en el repo.
- Revisar que CORS no quede en `*` en producción.
- El bridge habla con el cloud por HTTPS para proteger `X-Bridge-Secret`.
