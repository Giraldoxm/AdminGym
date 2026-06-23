from datetime import datetime, date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import AlertaMembresia, RolUsuario, Usuario
from schemas.alerta import AlertaResponse
from security import get_current_user

router = APIRouter(prefix="/alertas", tags=["Alertas"])

VENTANA_DIAS = 7


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    return current_user


def generar_alertas(db: Session) -> int:
    """Crea una alerta por usuario en cuanto entra en la ventana de 7 días antes del vencimiento.
    No genera duplicados: una sola alerta pendiente por usuario. Si el usuario renovó
    (fecha_vencimiento cambió), se descartan las alertas pendientes obsoletas."""
    hoy = date.today()
    limite = hoy + timedelta(days=VENTANA_DIAS)
    creadas = 0

    # 1) Limpiar alertas pendientes obsoletas: el usuario renovó o ya salió de la ventana.
    pendientes = db.query(AlertaMembresia).filter(AlertaMembresia.enviada == False).all()
    for a in pendientes:
        u = a.usuario
        if (
            not u
            or not u.fecha_vencimiento
            or u.fecha_vencimiento != a.fecha_vencimiento
            or u.fecha_vencimiento < hoy
            or u.fecha_vencimiento > limite
        ):
            db.delete(a)

    db.flush()

    # 2) Generar alertas faltantes para usuarios dentro de la ventana.
    usuarios = (
        db.query(Usuario)
        .filter(
            Usuario.fecha_vencimiento >= hoy,
            Usuario.fecha_vencimiento <= limite,
        )
        .all()
    )

    for u in usuarios:
        ya_tiene_pendiente = db.query(AlertaMembresia).filter(
            AlertaMembresia.usuario_id == u.id,
            AlertaMembresia.enviada == False,
        ).first()
        if ya_tiene_pendiente:
            continue

        existe_para_fecha = db.query(AlertaMembresia).filter(
            AlertaMembresia.usuario_id == u.id,
            AlertaMembresia.fecha_vencimiento == u.fecha_vencimiento,
        ).first()
        if existe_para_fecha:
            continue

        dias = (u.fecha_vencimiento - hoy).days
        db.add(AlertaMembresia(
            usuario_id=u.id,
            fecha_vencimiento=u.fecha_vencimiento,
            dias_anticipacion=dias,
        ))
        creadas += 1

    db.commit()
    return creadas


@router.get("/", response_model=List[AlertaResponse])
def listar_alertas(
    solo_pendientes: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    q = db.query(AlertaMembresia)
    if solo_pendientes:
        q = q.filter(AlertaMembresia.enviada == False)
    alertas = q.order_by(AlertaMembresia.dias_anticipacion.asc(), AlertaMembresia.fecha_creacion.desc()).all()
    result = []
    for a in alertas:
        result.append(AlertaResponse(
            id=a.id,
            usuario_id=a.usuario_id,
            usuario_nombre=a.usuario.nombre if a.usuario else "—",
            usuario_telefono=a.usuario.telefono if a.usuario else None,
            fecha_vencimiento=a.fecha_vencimiento,
            dias_anticipacion=a.dias_anticipacion,
            enviada=a.enviada,
            fecha_creacion=a.fecha_creacion,
            fecha_enviada=a.fecha_enviada,
        ))
    return result


@router.get("/contar")
def contar_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    total = db.query(AlertaMembresia).filter(AlertaMembresia.enviada == False).count()
    return {"pendientes": total}


@router.post("/generar")
def generar_manualmente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    creadas = generar_alertas(db)
    return {"mensaje": f"Proceso completado. {creadas} alerta(s) nueva(s) generada(s)."}


@router.post("/{alerta_id}/marcar-enviada", status_code=status.HTTP_200_OK)
def marcar_enviada(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    alerta = db.query(AlertaMembresia).filter(AlertaMembresia.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")
    alerta.enviada = True
    alerta.fecha_enviada = datetime.utcnow()
    db.commit()
    return {"mensaje": "Alerta marcada como enviada."}


@router.delete("/{alerta_id}", status_code=status.HTTP_204_NO_CONTENT)
def descartar_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    alerta = db.query(AlertaMembresia).filter(AlertaMembresia.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")
    db.delete(alerta)
    db.commit()
