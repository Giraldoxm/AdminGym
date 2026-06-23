from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import MovimientoFinanciero, Pago, Plan, RolUsuario, TipoMovimiento, Usuario
from schemas.pago import PagoCreate, PagoResponse
from security import get_current_user

router = APIRouter(prefix="/pagos", tags=["Planes"])


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Solo admin o coach pueden realizar esta acción.")
    return current_user


@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def registrar_pago(
    payload: PagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == payload.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    plan = db.query(Plan).filter(Plan.id == payload.plan_id, Plan.activo == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado o inactivo.")

    pago = Pago(
        usuario_id=payload.usuario_id,
        plan_id=payload.plan_id,
        monto=payload.monto,
        metodo_pago=payload.metodo_pago,
    )
    db.add(pago)

    hoy = date.today()
    base = (
        usuario.fecha_vencimiento
        if (usuario.fecha_vencimiento and usuario.fecha_vencimiento >= hoy)
        else hoy
    )
    nueva_fecha = base + timedelta(days=plan.duracion_dias)
    usuario.fecha_vencimiento = nueva_fecha

    db.commit()
    db.refresh(pago)

    return PagoResponse(
        id=pago.id,
        usuario_id=pago.usuario_id,
        plan_id=pago.plan_id,
        fecha_pago=pago.fecha_pago,
        monto=pago.monto,
        metodo_pago=pago.metodo_pago,
        nueva_fecha_vencimiento=nueva_fecha,
    )


class PagoDirectoCreate(BaseModel):
    usuario_id: int
    duracion_dias: int = Field(..., ge=1, le=365)
    monto: float = Field(..., ge=0)
    metodo_pago: str = Field(..., pattern=r'^(efectivo|transferencia)$')


@router.post("/directo/", status_code=status.HTTP_201_CREATED)
def registrar_pago_directo(
    payload: PagoDirectoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == payload.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    hoy = date.today()
    base = (
        usuario.fecha_vencimiento
        if (usuario.fecha_vencimiento and usuario.fecha_vencimiento >= hoy)
        else hoy
    )
    nueva_fecha = base + timedelta(days=payload.duracion_dias)
    usuario.fecha_vencimiento = nueva_fecha

    pago = Pago(
        usuario_id=payload.usuario_id,
        plan_id=None,
        duracion_dias=payload.duracion_dias,
        monto=payload.monto,
        metodo_pago=payload.metodo_pago,
    )
    db.add(pago)

    db.commit()
    db.refresh(pago)

    return {
        "id": pago.id,
        "usuario_id": usuario.id,
        "duracion_dias": payload.duracion_dias,
        "monto": payload.monto,
        "nueva_fecha_vencimiento": nueva_fecha,
    }


class PagoUpdate(BaseModel):
    monto: Optional[float] = Field(None, ge=0)
    metodo_pago: Optional[str] = Field(None, pattern=r'^(efectivo|transferencia)$')


@router.patch("/{pago_id}")
def editar_pago(
    pago_id: int,
    payload: PagoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado.")

    cambios = payload.model_dump(exclude_unset=True)
    if not cambios:
        return {"id": pago.id, "monto": pago.monto, "metodo_pago": pago.metodo_pago}

    if "monto" in cambios:
        pago.monto = cambios["monto"]
    if "metodo_pago" in cambios:
        pago.metodo_pago = cambios["metodo_pago"]

    db.commit()
    db.refresh(pago)
    return {
        "id": pago.id,
        "usuario_id": pago.usuario_id,
        "plan_id": pago.plan_id,
        "monto": pago.monto,
        "metodo_pago": pago.metodo_pago,
    }


@router.delete("/{pago_id}", status_code=status.HTTP_204_NO_CONTENT)
def anular_pago(
    pago_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado.")

    usuario = db.query(Usuario).filter(Usuario.id == pago.usuario_id).first()
    plan = db.query(Plan).filter(Plan.id == pago.plan_id).first() if pago.plan_id else None
    dias_a_restar = plan.duracion_dias if plan else (pago.duracion_dias or 0)

    if usuario and usuario.fecha_vencimiento and dias_a_restar:
        usuario.fecha_vencimiento = usuario.fecha_vencimiento - timedelta(days=dias_a_restar)

    db.delete(pago)
    db.commit()
    return


@router.get("/usuario/{usuario_id}")
def historial_pagos(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    pagos = (
        db.query(Pago)
        .filter(Pago.usuario_id == usuario_id)
        .order_by(Pago.fecha_pago.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "plan_id": p.plan_id,
            "plan_nombre": p.plan.nombre if p.plan else (f"Personalizado ({p.duracion_dias} días)" if p.duracion_dias else "Personalizado"),
            "duracion_dias": p.duracion_dias,
            "fecha_pago": p.fecha_pago,
            "monto": p.monto,
            "metodo_pago": p.metodo_pago,
        }
        for p in pagos
    ]
