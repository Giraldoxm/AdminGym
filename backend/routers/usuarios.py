import os
from datetime import date, datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import MovimientoFinanciero, Pago, Plan, RolUsuario, TipoMovimiento, Usuario
from schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from security import get_current_user, get_password_hash
from storage import guardar_archivo, eliminar_archivo

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Solo admin o coach pueden realizar esta acción.")
    return current_user


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    email_norm = (payload.email or "").strip().lower()
    doc_norm = (payload.documento_identidad or "").strip()
    if db.query(Usuario).filter(Usuario.email == email_norm).first():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email.")
    if db.query(Usuario).filter(Usuario.documento_identidad == doc_norm).first():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese documento de identidad.")
    nuevo = Usuario(
        nombre=payload.nombre,
        email=email_norm,
        password_hash=get_password_hash(payload.password),
        documento_identidad=doc_norm,
        genero=payload.genero,
        rol=payload.rol,
        huella_id=payload.huella_id,
        telefono=payload.telefono,
        fecha_nacimiento=payload.fecha_nacimiento,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if payload.nombre is not None:
        usuario.nombre = payload.nombre

    if payload.email is not None:
        email_norm = payload.email.strip().lower()
        duplicado = (
            db.query(Usuario)
            .filter(Usuario.email == email_norm, Usuario.id != usuario_id)
            .first()
        )
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email.")
        usuario.email = email_norm

    if payload.password is not None:
        usuario.password_hash = get_password_hash(payload.password)

    if payload.telefono is not None:
        usuario.telefono = payload.telefono

    if payload.documento_identidad is not None:
        doc_norm = payload.documento_identidad.strip()
        duplicado_doc = (
            db.query(Usuario)
            .filter(Usuario.documento_identidad == doc_norm, Usuario.id != usuario_id)
            .first()
        )
        if duplicado_doc:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese documento de identidad.")
        usuario.documento_identidad = doc_norm

    if payload.genero is not None:
        usuario.genero = payload.genero

    if payload.fecha_nacimiento is not None:
        usuario.fecha_nacimiento = payload.fecha_nacimiento

    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/{usuario_id}/foto", response_model=UsuarioResponse)
def subir_foto(
    usuario_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    if foto.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa JPG, PNG o WEBP.")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if usuario.foto_url:
        eliminar_archivo(usuario.foto_url)

    usuario.foto_url = guardar_archivo(foto)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.foto_url:
        eliminar_archivo(usuario.foto_url)
    db.delete(usuario)
    db.commit()


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    return db.query(Usuario).filter(Usuario.rol != RolUsuario.PENDIENTE).all()


# IMPORTANTE: rutas estáticas ANTES de las parametrizadas con {usuario_id}.
# FastAPI matchea en orden de declaración; si /{usuario_id} se declara primero,
# captura "pendientes" como ID y falla con 422.
@router.get("/pendientes")
def listar_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    pendientes = db.query(Usuario).filter(Usuario.rol == RolUsuario.PENDIENTE).all()
    result = []
    for u in pendientes:
        plan_solicitado = None
        if u.plan_solicitado_id:
            p = db.query(Plan).filter(Plan.id == u.plan_solicitado_id).first()
            if p:
                plan_solicitado = {"id": p.id, "nombre": p.nombre, "precio": p.precio, "duracion_dias": p.duracion_dias}
        result.append({
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "telefono": u.telefono,
            "documento_identidad": u.documento_identidad,
            "genero": u.genero,
            "created_at": u.created_at,
            "plan_solicitado_id": u.plan_solicitado_id,
            "plan_solicitado": plan_solicitado,
        })
    return result


@router.get("/cumpleanos-hoy", response_model=List[UsuarioResponse])
def cumpleanos_hoy(
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_admin_or_coach),
):
    hoy = datetime.now(ZoneInfo("America/Bogota")).date()
    hoy_md = hoy.strftime("%m-%d")
    return (
        db.query(Usuario)
        .filter(
            Usuario.fecha_nacimiento.isnot(None),
            func.strftime("%m-%d", Usuario.fecha_nacimiento) == hoy_md,
            Usuario.fecha_vencimiento >= hoy,
        )
        .all()
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario


class ActivarUsuarioPayload(BaseModel):
    plan_id: int
    monto: float = Field(..., ge=0)
    metodo_pago: str = Field(..., pattern=r'^(efectivo|transferencia)$')


@router.post("/{usuario_id}/activar")
def activar_usuario(
    usuario_id: int,
    payload: ActivarUsuarioPayload,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.rol == RolUsuario.PENDIENTE).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario pendiente no encontrado.")

    plan = db.query(Plan).filter(Plan.id == payload.plan_id, Plan.activo == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")

    usuario.rol = RolUsuario.CLIENTE
    usuario.plan_solicitado_id = None
    nueva_fecha = date.today() + timedelta(days=plan.duracion_dias)
    usuario.fecha_vencimiento = nueva_fecha

    pago = Pago(
        usuario_id=usuario.id,
        plan_id=plan.id,
        monto=payload.monto,
        metodo_pago=payload.metodo_pago,
    )
    db.add(pago)

    db.commit()
    return {
        "message": f"Usuario {usuario.nombre} activado correctamente.",
        "usuario_id": usuario.id,
        "nueva_fecha_vencimiento": nueva_fecha,
    }


@router.get("/huella/{huella_id}", response_model=UsuarioResponse)
def buscar_por_huella(
    huella_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    usuario = db.query(Usuario).filter(Usuario.huella_id == huella_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con esa huella.")
    return usuario


class HuellaTemplatePayload(BaseModel):
    template: str  # base64-encoded FMD


@router.post("/{usuario_id}/huella-template", status_code=status.HTTP_200_OK)
def guardar_huella_template(
    usuario_id: int,
    payload: HuellaTemplatePayload,
    request: Request,
    db: Session = Depends(get_db),
):
    """Guarda el template de huella. Acepta JWT de admin/coach O el header X-Bridge-Secret del bridge .NET."""
    bridge_secret = os.environ.get("BRIDGE_SECRET", "")
    x_secret = request.headers.get("X-Bridge-Secret", "")
    if x_secret != bridge_secret or not bridge_secret:
        # Si no viene del bridge, exigir JWT admin/coach
        try:
            from fastapi.security import OAuth2PasswordBearer
            from security import get_current_user
            token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            from security import SECRET_KEY, ALGORITHM
            from jose import jwt as jose_jwt, JWTError
            payload_jwt = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload_jwt.get("sub")
            caller = db.query(Usuario).filter(Usuario.email == email).first()
            if not caller or caller.rol.value not in ("admin", "coach"):
                raise HTTPException(status_code=403, detail="Sin permisos.")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail="Not authenticated")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    usuario.huella_template = payload.template
    usuario.huella_id = f"dp_{usuario_id}"
    db.commit()
    return {"mensaje": f"Huella registrada para {usuario.nombre}."}


@router.get("/con-template/lista")
def listar_usuarios_con_template(
    request: Request,
    db: Session = Depends(get_db),
):
    """Devuelve id, nombre y template de todos los usuarios con huella. Acepta JWT admin/coach o X-Bridge-Secret."""
    bridge_secret = os.environ.get("BRIDGE_SECRET", "")
    x_secret = request.headers.get("X-Bridge-Secret", "")
    if not bridge_secret or x_secret != bridge_secret:
        try:
            from jose import jwt as jose_jwt, JWTError
            from security import SECRET_KEY, ALGORITHM
            token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            payload_jwt = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload_jwt.get("sub")
            caller = db.query(Usuario).filter(Usuario.email == email).first()
            if not caller or caller.rol.value not in ("admin", "coach"):
                raise HTTPException(status_code=403, detail="Sin permisos.")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail="Not authenticated")
    usuarios = (
        db.query(Usuario.id, Usuario.nombre, Usuario.huella_template)
        .filter(Usuario.huella_template.isnot(None))
        .all()
    )
    return [
        {"id": u.id, "nombre": u.nombre, "template": u.huella_template}
        for u in usuarios
    ]
