from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import get_db
from models import Gimnasio, GimnasioModulo, Modulo, Pago, Plan, RolUsuario, Usuario
from schemas.usuario import UsuarioUpdate
from security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, verify_password, get_current_user
from storage import guardar_archivo, eliminar_archivo

router = APIRouter(tags=["Auth"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

# TODO multi-tenant: hasta que exista resolución de gimnasio por subdominio/slug
# en el login y el registro público, todo usuario nuevo cae en el gym por defecto.
DEFAULT_GYM_ID = 1


@router.get("/gimnasios")
def listar_gimnasios_publicos(db: Session = Depends(get_db)):
    """Lista los gimnasios activos para el selector del login. Solo expone
    nombre y slug (datos no sensibles) para que el cliente indique a qué tenant
    quiere autenticarse cuando hay emails repetidos entre gimnasios."""
    gyms = db.query(Gimnasio).filter(Gimnasio.activo == True).order_by(Gimnasio.nombre).all()
    return [{"slug": g.slug, "nombre": g.nombre} for g in gyms]


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    gym_slug: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    email_norm = (form_data.username or "").strip().lower()

    # Resolución de tenant: si el cliente indica `gym_slug`, el login se acota a
    # ese gimnasio (necesario cuando dos gimnasios comparten un email). Sin slug,
    # se conserva el comportamiento legacy de "primer match por email".
    query = db.query(Usuario).filter(Usuario.email == email_norm)
    if gym_slug:
        gimnasio = db.query(Gimnasio).filter(Gimnasio.slug == gym_slug.strip().lower()).first()
        if not gimnasio:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gimnasio no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        query = query.filter(Usuario.gym_id == gimnasio.id)

    usuario = query.first()
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    gimnasio = db.query(Gimnasio).filter(Gimnasio.id == usuario.gym_id).first()
    if gimnasio is None or not gimnasio.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este gimnasio está suspendido. Contacta al administrador.",
        )

    access_token = create_access_token(
        data={"sub": usuario.email, "gym_id": usuario.gym_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/contacto")
def contacto_admin(db: Session = Depends(get_db)):
    from models import RolUsuario as _Rol
    admin = db.query(Usuario).filter(Usuario.rol == _Rol.ADMIN).first()
    return {"telefono": admin.telefono if admin else None}


@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registro_publico(
    nombre: str = Form(..., min_length=2, max_length=120),
    email: str = Form(..., max_length=120),
    password: str = Form(..., min_length=6),
    documento_identidad: str = Form(..., min_length=5, max_length=20),
    genero: str = Form(...),
    telefono: str = Form(..., min_length=7, max_length=20),
    gym_slug: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if genero not in ("masculino", "femenino"):
        raise HTTPException(status_code=422, detail="Género inválido.")

    # Resolución de tenant: el link de registro de cada gimnasio trae su `gym_slug`
    # (ej. /registro?gym=crossfit-demo). Sin slug, cae al gym por defecto (compat.
    # con instalaciones de un solo tenant).
    target_gym_id = DEFAULT_GYM_ID
    if gym_slug:
        gimnasio = (
            db.query(Gimnasio)
            .filter(Gimnasio.slug == gym_slug.strip().lower(), Gimnasio.activo == True)
            .first()
        )
        if not gimnasio:
            raise HTTPException(status_code=400, detail="Gimnasio no encontrado o inactivo.")
        target_gym_id = gimnasio.id

    email = (email or "").strip().lower()
    documento_identidad = (documento_identidad or "").strip()
    if db.query(Usuario).filter(Usuario.email == email, Usuario.gym_id == target_gym_id).first():
        raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese email.")
    if db.query(Usuario).filter(Usuario.documento_identidad == documento_identidad, Usuario.gym_id == target_gym_id).first():
        raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese documento de identidad.")

    nuevo = Usuario(
        gym_id=target_gym_id,
        nombre=nombre,
        email=email,
        password_hash=get_password_hash(password),
        documento_identidad=documento_identidad,
        genero=genero,
        telefono=telefono,
        rol=RolUsuario.PENDIENTE,
    )

    if foto and foto.filename:
        if foto.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Formato de foto no permitido. Usa JPG, PNG o WEBP.")
        nuevo.foto_url = guardar_archivo(foto)

    db.add(nuevo)
    db.commit()
    return {"message": "Registro exitoso. Tu cuenta está pendiente de aprobación por el administrador."}


def _serialize_me(current_user: Usuario, db: Session) -> dict:
    incluye_wods_personalizados = False
    plan_actual = None
    if current_user.rol == RolUsuario.CLIENTE:
        ultimo_pago = (
            db.query(Pago)
            .filter(Pago.usuario_id == current_user.id)
            .order_by(desc(Pago.fecha_pago))
            .first()
        )
        if ultimo_pago:
            plan = db.query(Plan).filter(Plan.id == ultimo_pago.plan_id).first()
            if plan:
                incluye_wods_personalizados = plan.incluye_wods_personalizados
                plan_actual = {
                    "id": plan.id,
                    "nombre": plan.nombre,
                    "duracion_dias": plan.duracion_dias,
                    "precio": plan.precio,
                    "beneficios": plan.beneficios,
                    "incluye_wods_personalizados": plan.incluye_wods_personalizados,
                }
    # Módulos activos del gimnasio del usuario (feature flags) — el frontend los
    # usa para ocultar secciones (WODs, biometría) que el gym no tiene contratadas.
    modulos_activos = [
        clave
        for (clave,) in (
            db.query(Modulo.clave)
            .join(GimnasioModulo, GimnasioModulo.modulo_id == Modulo.id)
            .filter(
                GimnasioModulo.gym_id == current_user.gym_id,
                GimnasioModulo.activo == True,
            )
            .all()
        )
    ]
    gimnasio = db.query(Gimnasio).filter(Gimnasio.id == current_user.gym_id).first()
    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol.value,
        "genero": current_user.genero,
        "telefono": current_user.telefono,
        "documento_identidad": current_user.documento_identidad,
        "fecha_nacimiento": current_user.fecha_nacimiento,
        "foto_url": current_user.foto_url,
        "fecha_vencimiento": current_user.fecha_vencimiento,
        "esta_en_gym": current_user.esta_en_gym,
        "plan_solicitado_id": current_user.plan_solicitado_id,
        "incluye_wods_personalizados": incluye_wods_personalizados,
        "plan_actual": plan_actual,
        "gym_id": current_user.gym_id,
        "gym_nombre": gimnasio.nombre if gimnasio else None,
        "gym_slug": gimnasio.slug if gimnasio else None,
        "modulos_activos": modulos_activos,
    }


@router.get("/me")
def me(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _serialize_me(current_user, db)


@router.patch("/me")
def actualizar_mi_perfil(
    payload: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permite a cualquier usuario autenticado editar su propio perfil."""
    if payload.nombre is not None:
        current_user.nombre = payload.nombre

    if payload.email is not None:
        email_norm = payload.email.strip().lower()
        duplicado = (
            db.query(Usuario)
            .filter(Usuario.email == email_norm, Usuario.gym_id == current_user.gym_id, Usuario.id != current_user.id)
            .first()
        )
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email.")
        current_user.email = email_norm

    if payload.password is not None:
        current_user.password_hash = get_password_hash(payload.password)

    if payload.telefono is not None:
        current_user.telefono = payload.telefono

    if payload.documento_identidad is not None:
        doc_norm = payload.documento_identidad.strip()
        duplicado_doc = (
            db.query(Usuario)
            .filter(Usuario.documento_identidad == doc_norm, Usuario.gym_id == current_user.gym_id, Usuario.id != current_user.id)
            .first()
        )
        if duplicado_doc:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese documento de identidad.")
        current_user.documento_identidad = doc_norm

    if payload.genero is not None:
        current_user.genero = payload.genero

    if payload.fecha_nacimiento is not None:
        current_user.fecha_nacimiento = payload.fecha_nacimiento

    db.commit()
    db.refresh(current_user)
    return _serialize_me(current_user, db)


@router.post("/me/foto")
def subir_mi_foto(
    foto: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permite a cualquier usuario autenticado cambiar su propia foto de perfil."""
    if foto.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa JPG, PNG o WEBP.")
    if current_user.foto_url:
        eliminar_archivo(current_user.foto_url)
    current_user.foto_url = guardar_archivo(foto)
    db.commit()
    db.refresh(current_user)
    return _serialize_me(current_user, db)
