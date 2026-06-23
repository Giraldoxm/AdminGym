import os
from dotenv import load_dotenv

load_dotenv()

from database import SessionLocal
from models import Plan, Usuario, RolUsuario
from security import get_password_hash

import json as _json

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
            plan = db.query(Plan).filter(Plan.nombre == datos["nombre"]).first()
            if not plan:
                db.add(Plan(**datos))
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
        admin = db.query(Usuario).filter(Usuario.email == cfg["email"]).first()
        if not admin:
            admin = Usuario(
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


if __name__ == "__main__":
    print("Sembrando planes por defecto...")
    seed_planes()
    print("Sembrando usuario admin...")
    seed_admin()
    print("Listo.")
