from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import MetodoPago, RolUsuario, Usuario
from security import get_current_user

router = APIRouter(prefix="/metodos-pago", tags=["MetodosPago"])


def _require_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Solo el administrador puede realizar esta acción.")
    return current_user


class MetodoPagoCreate(BaseModel):
    banco: str = Field(..., min_length=1, max_length=80)
    tipo_cuenta: str = Field(..., min_length=1, max_length=40)
    numero_cuenta: str = Field(..., min_length=1, max_length=50)


class MetodoPagoUpdate(BaseModel):
    banco: Optional[str] = Field(None, min_length=1, max_length=80)
    tipo_cuenta: Optional[str] = Field(None, min_length=1, max_length=40)
    numero_cuenta: Optional[str] = Field(None, min_length=1, max_length=50)
    orden: Optional[int] = None
    activo: Optional[bool] = None


def _serializar(m: MetodoPago) -> dict:
    return {
        "id": m.id,
        "banco": m.banco,
        "tipo_cuenta": m.tipo_cuenta,
        "numero_cuenta": m.numero_cuenta,
        "orden": m.orden,
        "activo": m.activo,
    }


@router.get("/")
def listar_metodos_pago(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista métodos de pago activos en orden secuencial. Visible para cualquier usuario autenticado."""
    metodos = (
        db.query(MetodoPago)
        .filter(MetodoPago.activo == True)
        .order_by(MetodoPago.orden, MetodoPago.id)
        .all()
    )
    return [_serializar(m) for m in metodos]


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_metodo_pago(
    payload: MetodoPagoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_admin),
):
    # Asignar orden al final.
    max_orden = db.query(MetodoPago).order_by(MetodoPago.orden.desc()).first()
    siguiente = (max_orden.orden + 1) if max_orden else 0
    metodo = MetodoPago(
        banco=payload.banco.strip(),
        tipo_cuenta=payload.tipo_cuenta.strip(),
        numero_cuenta=payload.numero_cuenta.strip(),
        orden=siguiente,
    )
    db.add(metodo)
    db.commit()
    db.refresh(metodo)
    return _serializar(metodo)


@router.patch("/{metodo_id}")
def actualizar_metodo_pago(
    metodo_id: int,
    payload: MetodoPagoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_admin),
):
    metodo = db.query(MetodoPago).filter(MetodoPago.id == metodo_id).first()
    if not metodo:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado.")
    if payload.banco is not None:
        metodo.banco = payload.banco.strip()
    if payload.tipo_cuenta is not None:
        metodo.tipo_cuenta = payload.tipo_cuenta.strip()
    if payload.numero_cuenta is not None:
        metodo.numero_cuenta = payload.numero_cuenta.strip()
    if payload.orden is not None:
        metodo.orden = payload.orden
    if payload.activo is not None:
        metodo.activo = payload.activo
    db.commit()
    db.refresh(metodo)
    return _serializar(metodo)


@router.delete("/{metodo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_metodo_pago(
    metodo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_admin),
):
    metodo = db.query(MetodoPago).filter(MetodoPago.id == metodo_id).first()
    if not metodo:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado.")
    db.delete(metodo)
    db.commit()
