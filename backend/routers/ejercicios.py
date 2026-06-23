from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Ejercicio, RolUsuario, Usuario, WODEjercicio
from schemas.ejercicio import EjercicioCreate, EjercicioResponse, EjercicioUpdate
from security import get_current_user

router = APIRouter(prefix="/ejercicios", tags=["Ejercicios"])


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Solo admin o coach pueden realizar esta acción.")
    return current_user


@router.get("/", response_model=List[EjercicioResponse])
def listar_ejercicios(
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    q = db.query(Ejercicio)
    if categoria:
        q = q.filter(Ejercicio.categoria == categoria)
    return q.order_by(Ejercicio.nombre.asc()).all()


@router.post("/", response_model=EjercicioResponse, status_code=status.HTTP_201_CREATED)
def crear_ejercicio(
    payload: EjercicioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    existe = db.query(Ejercicio).filter(Ejercicio.nombre.ilike(payload.nombre.strip())).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe un ejercicio con ese nombre.")
    ej = Ejercicio(
        nombre=payload.nombre.strip(),
        video_url=(payload.video_url or None),
        descripcion=(payload.descripcion or None),
        categoria=(payload.categoria or None),
    )
    db.add(ej)
    db.commit()
    db.refresh(ej)
    return ej


@router.put("/{ejercicio_id}", response_model=EjercicioResponse)
def actualizar_ejercicio(
    ejercicio_id: int,
    payload: EjercicioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    ej = db.query(Ejercicio).filter(Ejercicio.id == ejercicio_id).first()
    if not ej:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado.")
    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data and data["nombre"]:
        nuevo = data["nombre"].strip()
        conflicto = (
            db.query(Ejercicio)
            .filter(Ejercicio.nombre.ilike(nuevo), Ejercicio.id != ejercicio_id)
            .first()
        )
        if conflicto:
            raise HTTPException(status_code=409, detail="Ya existe un ejercicio con ese nombre.")
        ej.nombre = nuevo
    if "video_url" in data:
        ej.video_url = data["video_url"] or None
    if "descripcion" in data:
        ej.descripcion = data["descripcion"] or None
    if "categoria" in data:
        ej.categoria = data["categoria"] or None
    db.commit()
    db.refresh(ej)
    return ej


@router.delete("/{ejercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ejercicio(
    ejercicio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    ej = db.query(Ejercicio).filter(Ejercicio.id == ejercicio_id).first()
    if not ej:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado.")
    en_uso = db.query(WODEjercicio).filter(WODEjercicio.ejercicio_id == ejercicio_id).first()
    if en_uso:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el ejercicio está siendo usado en uno o más WODs.",
        )
    db.delete(ej)
    db.commit()
