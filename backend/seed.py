import os
from dotenv import load_dotenv

load_dotenv()

from database import SessionLocal
from models import GimnasioModulo, Modulo, Plan, SuperAdmin, Usuario, RolUsuario
from security import get_password_hash

import json as _json

# TODO multi-tenant: el admin sembrado al arrancar pertenece al gimnasio por
# defecto creado en la migración de main.py (id=1). El alta de nuevos gimnasios
# y sus admins vivirá en el router de superadmin.
DEFAULT_GYM_ID = 1

PLANES_DEFAULT = [
    {
        "nombre": "1 Semana", "precio": 35000, "duracion_dias": 7,
        "descripcion": "Acceso por 7 días",
        "beneficios": _json.dumps(["Acceso al box 7 días", "Clases grupales incluidas", "Uso de equipamiento completo"]),
    },
    {
        "nombre": "15 Días", "precio": 60000, "duracion_dias": 15,
        "descripcion": "Acceso por quince días",
        "beneficios": _json.dumps(["Acceso al box 15 días", "Clases grupales incluidas", "Uso de equipamiento completo", "Seguimiento de progreso"]),
    },
    {
        "nombre": "1 Mes", "precio": 100000, "duracion_dias": 30,
        "descripcion": "Acceso por un mes",
        "beneficios": _json.dumps(["Acceso ilimitado al box", "Clases grupales incluidas", "Uso de equipamiento completo", "Seguimiento de progreso", "Asesoría nutricional básica"]),
    },
]

def _admin_config() -> dict:
    return {
        "nombre":              os.environ["ADMIN_NOMBRE"],
        "email":               os.environ["ADMIN_EMAIL"],
        "password":            os.environ["ADMIN_PASSWORD"],
        "rol":                 RolUsuario.ADMIN,
        "telefono":            os.environ["ADMIN_TELEFONO"],
        "documento_identidad": os.environ["ADMIN_DOCUMENTO"],
    }

def seed_planes():
    db = SessionLocal()
    try:
        for datos in PLANES_DEFAULT:
            plan = db.query(Plan).filter(Plan.nombre == datos["nombre"], Plan.gym_id == DEFAULT_GYM_ID).first()
            if not plan:
                db.add(Plan(**datos, gym_id=DEFAULT_GYM_ID))
                print(f"  + Plan '{datos['nombre']}' creado")
            elif not plan.beneficios:
                plan.beneficios = datos["beneficios"]
                print(f"  · Plan '{datos['nombre']}' actualizado con beneficios")
            else:
                print(f"  · Plan '{datos['nombre']}' ya existe")
        db.commit()
    finally:
        db.close()


def seed_admin():
    cfg = _admin_config()
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.email == cfg["email"], Usuario.gym_id == DEFAULT_GYM_ID).first()
        if not admin:
            admin = Usuario(
                gym_id=DEFAULT_GYM_ID,
                nombre=cfg["nombre"],
                email=cfg["email"],
                password_hash=get_password_hash(cfg["password"]),
                documento_identidad=cfg["documento_identidad"],
                rol=cfg["rol"],
                telefono=cfg["telefono"],
            )
            db.add(admin)
            db.commit()
            print(f"  + Usuario admin '{cfg['email']}' creado")
        else:
            if not admin.documento_identidad:
                admin.documento_identidad = cfg["documento_identidad"]
                db.commit()
                print(f"  · Admin actualizado con documento de identidad")
            else:
                print(f"  · Usuario admin '{cfg['email']}' ya existe")
    finally:
        db.close()


MODULOS_DEFAULT = [
    {"clave": "wods", "nombre": "WODs y puntuación", "descripcion": "Registro y puntuación de WODs (regulares y personalizados)."},
    {"clave": "biometria", "nombre": "Biometría (huella)", "descripcion": "Integración con el lector de huellas U.are.U 4500 para control de acceso."},
]


def seed_modulos():
    """Crea el catálogo fijo de módulos y los activa para el gym por defecto
    (id=1) — la instancia existente ya usa WODs y biometría, así que no debe
    perder acceso al pasar a multi-tenant. Los gimnasios nuevos los activa el
    superadmin explícitamente."""
    db = SessionLocal()
    try:
        for datos in MODULOS_DEFAULT:
            modulo = db.query(Modulo).filter(Modulo.clave == datos["clave"]).first()
            if not modulo:
                modulo = Modulo(**datos)
                db.add(modulo)
                db.flush()
                print(f"  + Módulo '{datos['clave']}' creado")

            activacion = db.query(GimnasioModulo).filter(
                GimnasioModulo.gym_id == DEFAULT_GYM_ID,
                GimnasioModulo.modulo_id == modulo.id,
            ).first()
            if not activacion:
                db.add(GimnasioModulo(gym_id=DEFAULT_GYM_ID, modulo_id=modulo.id, activo=True))
                print(f"  + Módulo '{datos['clave']}' activado para el gym {DEFAULT_GYM_ID}")
        db.commit()
    finally:
        db.close()


def seed_superadmin():
    """Crea el primer SuperAdmin de la plataforma si SUPERADMIN_EMAIL/PASSWORD
    están definidas en el entorno. Opcional a propósito: instalaciones de un
    solo gimnasio (sin panel de SuperAdmin todavía) no necesitan setearlas."""
    email = os.environ.get("SUPERADMIN_EMAIL")
    password = os.environ.get("SUPERADMIN_PASSWORD")
    if not email or not password:
        print("  · SUPERADMIN_EMAIL/PASSWORD no definidas, se omite el seed de superadmin.")
        return
    email = email.strip().lower()
    db = SessionLocal()
    try:
        admin = db.query(SuperAdmin).filter(SuperAdmin.email == email).first()
        if not admin:
            db.add(SuperAdmin(
                nombre=os.environ.get("SUPERADMIN_NOMBRE", "SuperAdmin"),
                email=email,
                password_hash=get_password_hash(password),
            ))
            db.commit()
            print(f"  + SuperAdmin '{email}' creado")
        else:
            print(f"  · SuperAdmin '{email}' ya existe")
    finally:
        db.close()


if __name__ == "__main__":
    print("Sembrando planes por defecto...")
    seed_planes()
    print("Sembrando usuario admin...")
    seed_admin()
    print("Sembrando módulos por defecto...")
    seed_modulos()
    print("Sembrando superadmin (si está configurado)...")
    seed_superadmin()
    print("Listo.")
