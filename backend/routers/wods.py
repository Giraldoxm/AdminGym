from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import get_db
from models import Ejercicio, Pago, Plan, RolUsuario, Usuario, WOD, WODEjercicio
from schemas.wod import WODCreate, WODUpdate, WODResponse
from security import get_current_user

router = APIRouter(prefix="/wods", tags=["WODs"])


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Solo admin o coach pueden realizar esta acción.")
    return current_user


def _require_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Solo el administrador puede realizar esta acción.")
    return current_user


def _aplicar_ejercicios(wod: WOD, items, db: Session) -> None:
    """Reemplaza los ejercicios de un WOD con la lista recibida. Valida que existan."""
    wod.ejercicios.clear()
    db.flush()
    for idx, item in enumerate(items or []):
        existe = db.query(Ejercicio).filter(Ejercicio.id == item.ejercicio_id).first()
        if not existe:
            raise HTTPException(
                status_code=422,
                detail=f"El ejercicio con id {item.ejercicio_id} no existe.",
            )
        wod.ejercicios.append(
            WODEjercicio(
                ejercicio_id=item.ejercicio_id,
                notas=(item.notas or None),
                rep_min=item.rep_min,
                rep_max=item.rep_max,
                rir=item.rir,
                porcentaje_rm=item.porcentaje_rm,
                tiempo_segundos=item.tiempo_segundos,
                orden=item.orden if item.orden is not None else idx,
            )
        )


def _tiene_plan_personalizado(usuario_id: int, db: Session) -> bool:
    ultimo_pago = (
        db.query(Pago)
        .filter(Pago.usuario_id == usuario_id)
        .order_by(desc(Pago.fecha_pago))
        .first()
    )
    if not ultimo_pago:
        return False
    plan = db.query(Plan).filter(Plan.id == ultimo_pago.plan_id).first()
    return bool(plan and plan.incluye_wods_personalizados)


@router.get("/personalizados", response_model=List[WODResponse])
def listar_wods_personalizados(
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol in (RolUsuario.ADMIN, RolUsuario.COACH):
        q = db.query(WOD).filter(WOD.es_personalizado == True)
        if activo is not None:
            q = q.filter(WOD.activo == activo)
        return q.order_by(WOD.fecha.desc(), WOD.id.desc()).all()
    if not _tiene_plan_personalizado(current_user.id, db):
        raise HTTPException(status_code=403, detail="Tu plan no incluye WODs personalizados.")
    if not current_user.genero:
        raise HTTPException(status_code=422, detail="Tu perfil no tiene género registrado. Contacta al administrador.")
    return (
        db.query(WOD)
        .filter(
            WOD.es_personalizado == True,
            WOD.genero_destino == current_user.genero,
            WOD.activo == True,
        )
        .order_by(WOD.fecha.desc(), WOD.id.desc())
        .all()
    )


@router.post("/", response_model=WODResponse, status_code=status.HTTP_201_CREATED)
def crear_wod(
    payload: WODCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    if payload.es_personalizado:
        if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
            raise HTTPException(status_code=403, detail="Solo el administrador o coach puede crear WODs personalizados.")
        if not payload.genero_destino:
            raise HTTPException(status_code=422, detail="Debes seleccionar el género para un WOD personalizado.")
    data = payload.model_dump()
    ejercicios = data.pop("ejercicios", None)
    data["coach_id"] = current_user.id
    wod = WOD(**data)
    db.add(wod)
    db.flush()
    _aplicar_ejercicios(wod, payload.ejercicios, db)
    db.commit()
    db.refresh(wod)
    return wod


@router.put("/{wod_id}", response_model=WODResponse)
def actualizar_wod(
    wod_id: int,
    payload: WODUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    wod = db.query(WOD).filter(WOD.id == wod_id).first()
    if not wod:
        raise HTTPException(status_code=404, detail="WOD no encontrado.")
    data = payload.model_dump(exclude_unset=True)
    tiene_ejercicios = "ejercicios" in data
    data.pop("ejercicios", None)
    for field, value in data.items():
        setattr(wod, field, value)
    if tiene_ejercicios:
        _aplicar_ejercicios(wod, payload.ejercicios, db)
    db.commit()
    db.refresh(wod)
    return wod


@router.patch("/{wod_id}/toggle", response_model=WODResponse)
def toggle_wod(
    wod_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    wod = db.query(WOD).filter(WOD.id == wod_id).first()
    if not wod:
        raise HTTPException(status_code=404, detail="WOD no encontrado.")
    wod.activo = not wod.activo
    db.commit()
    db.refresh(wod)
    return wod


@router.delete("/{wod_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_wod(
    wod_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    wod = db.query(WOD).filter(WOD.id == wod_id).first()
    if not wod:
        raise HTTPException(status_code=404, detail="WOD no encontrado.")
    db.delete(wod)
    db.commit()


@router.get("/hoy", response_model=List[WODResponse])
def wods_de_hoy(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    es_staff = current_user.rol in (RolUsuario.ADMIN, RolUsuario.COACH)
    q = db.query(WOD).filter(WOD.fecha == date.today(), WOD.es_personalizado == False)
    if not es_staff:
        q = q.filter(WOD.activo == True)
    return q.order_by(WOD.id).all()


@router.get("/", response_model=List[WODResponse])
def listar_wods(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    es_staff = current_user.rol in (RolUsuario.ADMIN, RolUsuario.COACH)
    q = db.query(WOD).filter(WOD.es_personalizado == False)
    if activo is not None:
        q = q.filter(WOD.activo == activo)
    elif not es_staff:
        q = q.filter(WOD.activo == True)
    return q.order_by(WOD.fecha.desc(), WOD.id.desc()).offset(skip).limit(limit).all()
