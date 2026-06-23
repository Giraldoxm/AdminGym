from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import MedidaSalud, Usuario
from schemas.salud import MedidaPorTipoCreate, MedidaResponse
from security import get_current_user

router = APIRouter(prefix="/salud", tags=["Salud"])

CAMPOS = {
    "peso":    "peso_kg",
    "altura":  "altura_cm",
    "cintura": "cintura_cm",
    "cuello":  "cuello_cm",
    "cadera":  "cadera_cm",
    "brazos":  "brazos_cm",
}


def _campo_o_404(tipo: str) -> str:
    campo = CAMPOS.get(tipo)
    if not campo:
        raise HTTPException(status_code=404, detail="Tipo de medida no válido.")
    return campo


# ── Resumen (overview) ─────────────────────────────────────────

@router.get("/", response_model=List[MedidaResponse])
def listar_todas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return (
        db.query(MedidaSalud)
        .filter(MedidaSalud.usuario_id == current_user.id)
        .order_by(MedidaSalud.fecha.asc())
        .all()
    )


# ── Por tipo ───────────────────────────────────────────────────

@router.get("/{tipo}", response_model=List[MedidaResponse])
def listar_por_tipo(
    tipo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    campo = _campo_o_404(tipo)
    col = getattr(MedidaSalud, campo)
    return (
        db.query(MedidaSalud)
        .filter(MedidaSalud.usuario_id == current_user.id, col.isnot(None))
        .order_by(MedidaSalud.fecha.asc())
        .all()
    )


@router.post("/{tipo}", response_model=MedidaResponse, status_code=status.HTTP_201_CREATED)
def crear_por_tipo(
    tipo: str,
    payload: MedidaPorTipoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    campo = _campo_o_404(tipo)
    medida = MedidaSalud(
        usuario_id=current_user.id,
        fecha=payload.fecha,
        **{campo: payload.valor},
        notas=payload.notas,
    )
    db.add(medida)
    db.commit()
    db.refresh(medida)
    return medida


@router.delete("/{medida_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medida(
    medida_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    medida = db.query(MedidaSalud).filter(
        MedidaSalud.id == medida_id,
        MedidaSalud.usuario_id == current_user.id,
    ).first()
    if not medida:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")
    db.delete(medida)
    db.commit()
