import models
from database import engine, SessionLocal
from sqlalchemy import text

models.Base.metadata.create_all(bind=engine)

# ── Migraciones de arranque (SOLO SQLite) ─────────────────────
# Todo este bloque usa sintaxis específica de SQLite (PRAGMA, reconstrucción
# de tablas, ALTER TABLE … ADD COLUMN sin tipo completo). En Postgres revienta
# y no hace falta: create_all() ya crea el esquema final con la nulabilidad
# correcta porque los modelos reflejan el estado final.
if engine.url.get_backend_name() == "sqlite":
    # Migraciones ligeras para columnas nuevas
    _migraciones = [
        "ALTER TABLE productos ADD COLUMN foto_url VARCHAR(300)",
        "ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20)",
        "ALTER TABLE ventas ADD COLUMN metodo_pago VARCHAR(50)",
        "ALTER TABLE usuarios ADD COLUMN documento_identidad VARCHAR(20)",
        "ALTER TABLE planes ADD COLUMN beneficios TEXT",
        "ALTER TABLE planes ADD COLUMN incluye_wods_personalizados INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN genero VARCHAR(20)",
        "ALTER TABLE usuarios ADD COLUMN plan_solicitado_id INTEGER",
        "ALTER TABLE usuarios ADD COLUMN huella_template TEXT",
        "ALTER TABLE medidas_salud ADD COLUMN cuello_cm REAL",
        "ALTER TABLE medidas_salud ADD COLUMN cadera_cm REAL",
        "ALTER TABLE wods ADD COLUMN es_personalizado INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE wods ADD COLUMN genero_destino VARCHAR(20)",
        "ALTER TABLE pagos ADD COLUMN duracion_dias INTEGER",
        "ALTER TABLE marcas_rm ADD COLUMN peso_adicional REAL",
        "ALTER TABLE marcas_rm ADD COLUMN nivel INTEGER",
        "ALTER TABLE marcas_rm ADD COLUMN palier INTEGER",
        "ALTER TABLE usuarios ADD COLUMN fecha_nacimiento DATE",
        "ALTER TABLE ejercicios ADD COLUMN descripcion TEXT",
        "ALTER TABLE wod_ejercicios ADD COLUMN rep_min INTEGER",
        "ALTER TABLE wod_ejercicios ADD COLUMN rep_max INTEGER",
        "ALTER TABLE wod_ejercicios ADD COLUMN rir INTEGER",
        "ALTER TABLE wod_ejercicios ADD COLUMN porcentaje_rm REAL",
        "ALTER TABLE wod_ejercicios ADD COLUMN tiempo_segundos INTEGER",
        "ALTER TABLE wods ADD COLUMN tipo VARCHAR(50)",
        "ALTER TABLE ejercicios ADD COLUMN categoria VARCHAR(50)",
        "ALTER TABLE marcas_rm ADD COLUMN series TEXT",
        "ALTER TABLE medidas_salud ADD COLUMN brazos_cm REAL",
    ]
    with engine.connect() as _conn:
        for _sql in _migraciones:
            try:
                _conn.execute(text(_sql))
                _conn.commit()
            except Exception:
                pass

    # Migración: reconstruir tabla wods (quitar unique en fecha, agregar activo)
    with engine.connect() as _conn:
        _cols = [row[1] for row in _conn.execute(text("PRAGMA table_info(wods)")).fetchall()]
        if "activo" not in _cols:
            _conn.execute(text("""
                CREATE TABLE wods_new (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    titulo VARCHAR(150) NOT NULL,
                    descripcion TEXT NOT NULL,
                    fecha DATE NOT NULL,
                    activo BOOLEAN NOT NULL DEFAULT 1,
                    coach_id INTEGER REFERENCES usuarios(id),
                    created_at DATETIME NOT NULL
                )
            """))
            _conn.execute(text(
                "INSERT INTO wods_new (id, titulo, descripcion, fecha, activo, coach_id, created_at) "
                "SELECT id, titulo, descripcion, fecha, 1, coach_id, created_at FROM wods"
            ))
            _conn.execute(text("DROP TABLE wods"))
            _conn.execute(text("ALTER TABLE wods_new RENAME TO wods"))
            _conn.commit()

    # Migración: hacer peso_kg, altura_cm, imc nullable en medidas_salud
    with engine.connect() as _conn:
        _info = {row[1]: row[3] for row in _conn.execute(text("PRAGMA table_info(medidas_salud)")).fetchall()}
        if _info.get("peso_kg", 0) == 1:  # notnull=1 → NOT NULL constraint activo
            _conn.execute(text("""
                CREATE TABLE medidas_salud_new (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    fecha DATE NOT NULL,
                    peso_kg REAL,
                    altura_cm REAL,
                    imc REAL,
                    cintura_cm REAL,
                    cuello_cm REAL,
                    cadera_cm REAL,
                    notas TEXT,
                    created_at DATETIME NOT NULL
                )
            """))
            _conn.execute(text(
                "INSERT INTO medidas_salud_new "
                "SELECT id, usuario_id, fecha, peso_kg, altura_cm, imc, cintura_cm, cuello_cm, cadera_cm, notas, created_at "
                "FROM medidas_salud"
            ))
            _conn.execute(text("DROP TABLE medidas_salud"))
            _conn.execute(text("ALTER TABLE medidas_salud_new RENAME TO medidas_salud"))
            _conn.commit()

    # Migración: hacer peso/repeticiones/rm_calculado nullable en marcas_rm
    # (para tipos 'reps' y 'leger' que no usan estos campos)
    with engine.connect() as _conn:
        _info_marcas = {row[1]: row[3] for row in _conn.execute(text("PRAGMA table_info(marcas_rm)")).fetchall()}
        if _info_marcas and _info_marcas.get("peso", 0) == 1:  # notnull=1 → NOT NULL aún activo
            _conn.execute(text("""
                CREATE TABLE marcas_rm_new (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    ejercicio VARCHAR(100) NOT NULL,
                    peso REAL,
                    unidad VARCHAR(5) NOT NULL DEFAULT 'kg',
                    repeticiones INTEGER,
                    rm_calculado REAL,
                    peso_adicional REAL,
                    nivel INTEGER,
                    palier INTEGER,
                    fecha DATE NOT NULL,
                    notas TEXT,
                    created_at DATETIME NOT NULL
                )
            """))
            _conn.execute(text(
                "INSERT INTO marcas_rm_new "
                "(id, usuario_id, ejercicio, peso, unidad, repeticiones, rm_calculado, peso_adicional, nivel, palier, fecha, notas, created_at) "
                "SELECT id, usuario_id, ejercicio, peso, unidad, repeticiones, rm_calculado, peso_adicional, nivel, palier, fecha, notas, created_at "
                "FROM marcas_rm"
            ))
            _conn.execute(text("DROP TABLE marcas_rm"))
            _conn.execute(text("ALTER TABLE marcas_rm_new RENAME TO marcas_rm"))
            _conn.commit()

    # Migración: hacer plan_id nullable en pagos (para pagos personalizados sin plan)
    with engine.connect() as _conn:
        _info_pagos = {row[1]: row[3] for row in _conn.execute(text("PRAGMA table_info(pagos)")).fetchall()}
        if _info_pagos.get("plan_id", 0) == 1:  # notnull=1 → NOT NULL aún activo
            _conn.execute(text("""
                CREATE TABLE pagos_new (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    plan_id INTEGER REFERENCES planes(id),
                    duracion_dias INTEGER,
                    fecha_pago DATETIME,
                    monto REAL NOT NULL,
                    metodo_pago VARCHAR(50)
                )
            """))
            _conn.execute(text(
                "INSERT INTO pagos_new (id, usuario_id, plan_id, duracion_dias, fecha_pago, monto, metodo_pago) "
                "SELECT id, usuario_id, plan_id, duracion_dias, fecha_pago, monto, metodo_pago FROM pagos"
            ))
            _conn.execute(text("DROP TABLE pagos"))
            _conn.execute(text("ALTER TABLE pagos_new RENAME TO pagos"))
            _conn.commit()

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from routers import alertas, asistencia, auth, ejercicios, finanzas, marcas, metodos_pago, pagos, planes, productos, salud, usuarios, ventas, wods
from seed import seed_planes, seed_admin

seed_planes()
seed_admin()

app = FastAPI(
    title="Jain Sport Box System",
    description="API para la gestion integral de Jain Sport Box",
    version="0.1.0",
)

# Orígenes CORS por entorno. Local (default): puertos de Vite.
# Producción: CORS_ORIGINS=https://app.tudominio.com,http://localhost:4173 (coma-separado).
_default_origins = ("http://localhost:5173,http://127.0.0.1:5173,"
                    "http://localhost:5174,http://127.0.0.1:5174")
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# ── Scheduler diario de alertas ───────────────────────────────
def _job_alertas():
    db = SessionLocal()
    try:
        from routers.alertas import generar_alertas
        creadas = generar_alertas(db)
        if creadas:
            print(f"[Scheduler] {creadas} alerta(s) de membresía generada(s).")
    finally:
        db.close()


# ── Scheduler: reset esta_en_gym para sesiones vencidas ───────
def _job_reset_gym():
    """Cada 3 minutos libera el flag esta_en_gym de usuarios cuya última
    entrada fue hace más de MINUTOS_SESION. Cubre el caso de quienes salen
    sin pasar por el torniquete."""
    from datetime import datetime as _dt
    from sqlalchemy import func
    from models import Asistencia as _Asistencia, Usuario as _Usuario
    from routers.asistencia import MINUTOS_SESION
    db = SessionLocal()
    try:
        ahora = _dt.utcnow()
        corte = ahora - __import__('datetime').timedelta(minutes=MINUTOS_SESION)

        # Subconsulta: última entrada por usuario
        ultima_entrada = (
            db.query(
                _Asistencia.usuario_id,
                func.max(_Asistencia.fecha_hora).label("ultima")
            )
            .filter(_Asistencia.tipo == "entrada")
            .group_by(_Asistencia.usuario_id)
            .subquery()
        )

        # Usuarios en gym cuya última entrada supera el tiempo de sesión
        a_resetar = (
            db.query(_Usuario)
            .join(ultima_entrada, ultima_entrada.c.usuario_id == _Usuario.id)
            .filter(_Usuario.esta_en_gym == True, ultima_entrada.c.ultima < corte)
            .all()
        )

        for u in a_resetar:
            u.esta_en_gym = False
        if a_resetar:
            db.commit()
            print(f"[Scheduler] {len(a_resetar)} usuario(s) liberado(s) del gym por sesión vencida.")
    finally:
        db.close()


_scheduler = BackgroundScheduler(timezone="America/Bogota")
# Ejecuta todos los días a las 9:00 AM
_scheduler.add_job(_job_alertas, CronTrigger(hour=9, minute=0))
# También al arrancar para no perder el día actual
_scheduler.add_job(_job_alertas, "date")
# Reset de esta_en_gym cada 3 minutos
_scheduler.add_job(_job_reset_gym, "interval", minutes=3)
_scheduler.start()


@app.on_event("shutdown")
def _shutdown():
    _scheduler.shutdown(wait=False)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Gym System Online"}


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(wods.router)
app.include_router(planes.router)
app.include_router(pagos.router)
app.include_router(asistencia.router)
app.include_router(finanzas.router)
app.include_router(salud.router)
app.include_router(marcas.router)
app.include_router(alertas.router)
app.include_router(metodos_pago.router)
app.include_router(ejercicios.router)
