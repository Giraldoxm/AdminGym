from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import Gimnasio, GimnasioModulo, Modulo, RolUsuario, Usuario
from security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_superadmin,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/superadmin", tags=["SuperAdmin"])


@router.post("/login")
def login_superadmin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from models import SuperAdmin

    email_norm = (form_data.username or "").strip().lower()
    admin = db.query(SuperAdmin).filter(SuperAdmin.email == email_norm).first()
    if not admin or not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": admin.email, "scope": "superadmin"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


class GimnasioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-z0-9-]+$")
    admin_nombre: str = Field(..., min_length=2, max_length=120)
    admin_email: str = Field(..., min_length=3, max_length=120)
    admin_password: str = Field(..., min_length=6)
    admin_documento: str = Field(..., min_length=3, max_length=20)
    admin_telefono: Optional[str] = Field(None, max_length=20)
    modulos: List[str] = Field(default=[])


class GimnasioResponse(BaseModel):
    id: int
    nombre: str
    slug: str
    activo: bool

    class Config:
        from_attributes = True


class GimnasioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    activo: Optional[bool] = None


@router.get("/gimnasios", response_model=List[GimnasioResponse])
def listar_gimnasios(
    db: Session = Depends(get_db),
    _: "object" = Depends(get_current_superadmin),
):
    return db.query(Gimnasio).order_by(Gimnasio.id).all()


@router.post("/gimnasios", response_model=GimnasioResponse, status_code=status.HTTP_201_CREATED)
def crear_gimnasio(
    payload: GimnasioCreate,
    db: Session = Depends(get_db),
    _: "object" = Depends(get_current_superadmin),
):
    if db.query(Gimnasio).filter(Gimnasio.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Ya existe un gimnasio con ese slug.")

    gimnasio = Gimnasio(nombre=payload.nombre, slug=payload.slug, activo=True)
    db.add(gimnasio)
    db.flush()

    admin_email = payload.admin_email.strip().lower()
    admin = Usuario(
        gym_id=gimnasio.id,
        nombre=payload.admin_nombre,
        email=admin_email,
        password_hash=get_password_hash(payload.admin_password),
        documento_identidad=payload.admin_documento.strip(),
        telefono=payload.admin_telefono,
        rol=RolUsuario.ADMIN,
    )
    db.add(admin)

    for clave in payload.modulos:
        modulo = db.query(Modulo).filter(Modulo.clave == clave).first()
        if not modulo:
            raise HTTPException(status_code=422, detail=f"Módulo '{clave}' no existe en el catálogo.")
        db.add(GimnasioModulo(gym_id=gimnasio.id, modulo_id=modulo.id, activo=True))

    db.commit()
    db.refresh(gimnasio)
    return gimnasio


@router.patch("/gimnasios/{gym_id}", response_model=GimnasioResponse)
def actualizar_gimnasio(
    gym_id: int,
    payload: GimnasioUpdate,
    db: Session = Depends(get_db),
    _: "object" = Depends(get_current_superadmin),
):
    gimnasio = db.query(Gimnasio).filter(Gimnasio.id == gym_id).first()
    if not gimnasio:
        raise HTTPException(status_code=404, detail="Gimnasio no encontrado.")
    if payload.nombre is not None:
        gimnasio.nombre = payload.nombre
    if payload.activo is not None:
        gimnasio.activo = payload.activo
    db.commit()
    db.refresh(gimnasio)
    return gimnasio


class ModuloResponse(BaseModel):
    id: int
    clave: str
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/modulos", response_model=List[ModuloResponse])
def listar_modulos(
    db: Session = Depends(get_db),
    _: "object" = Depends(get_current_superadmin),
):
    return db.query(Modulo).order_by(Modulo.clave).all()


class GimnasioModuloResponse(BaseModel):
    modulo_id: int
    clave: str
    nombre: str
    activo: bool


@router.get("/gimnasios/{gym_id}/modulos", response_model=List[GimnasioModuloResponse])
def listar_modulos_de_gimnasio(
    gym_id: int,
    db: Session = Depends(get_db),
    _: "object" = Depends(get_current_superadmin),
):
    if not db.query(Gimnasio).filter(Gimnasio.id == gym_id).first():
        raise HTTPException(status_code=404, detail="Gimnasio no encontrado.")
    activos = {
        gm.modulo_id: gm.activo
        for gm in db.query(GimnasioModulo).filter(GimnasioModulo.gym_id == gym_id).all()
    }
    return [
        GimnasioModuloResponse(
            modulo_id=m.id,
            clave=m.clave,
            nombre=m.nombre,
            activo=activos.get(m.id, False),
        )
        for m in db.query(Modulo).order_by(Modulo.clave).all()
    ]


class ToggleModuloPayload(BaseModel):
    activo: bool


@router.patch("/gimnasios/{gym_id}/modulos/{modulo_id}", response_model=GimnasioModuloResponse)
def activar_o_desactivar_modulo(
    gym_id: int,
    modulo_id: int,
    payload: ToggleModuloPayload,
    db: Session = Depends(get_db),
    _: "object" = Depends(get_current_superadmin),
):
    if not db.query(Gimnasio).filter(Gimnasio.id == gym_id).first():
        raise HTTPException(status_code=404, detail="Gimnasio no encontrado.")
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Módulo no encontrado.")

    gm = db.query(GimnasioModulo).filter(
        GimnasioModulo.gym_id == gym_id, GimnasioModulo.modulo_id == modulo_id
    ).first()
    if not gm:
        gm = GimnasioModulo(gym_id=gym_id, modulo_id=modulo_id, activo=payload.activo)
        db.add(gm)
    else:
        gm.activo = payload.activo
    db.commit()
    return GimnasioModuloResponse(modulo_id=modulo.id, clave=modulo.clave, nombre=modulo.nombre, activo=gm.activo)
