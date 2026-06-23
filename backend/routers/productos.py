from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from models import Producto, RolUsuario, Usuario
from schemas.producto import ProductoCreate, ProductoResponse, ProductoUpdate
from security import get_current_user
from storage import guardar_archivo, eliminar_archivo

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

router = APIRouter(prefix="/productos", tags=["Productos"])


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Solo admin o coach pueden realizar esta acción.")
    return current_user


@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    solo_activos: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Clientes solo ven activos, admin/coach pueden ver todos
    if current_user.rol == RolUsuario.CLIENTE:
        solo_activos = True
    q = db.query(Producto)
    if solo_activos:
        q = q.filter(Producto.activo == True)
    return q.order_by(Producto.nombre).all()


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return producto


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(
    payload: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    nuevo = Producto(**payload.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{producto_id}", response_model=ProductoResponse)
def editar_producto(
    producto_id: int,
    payload: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.post("/{producto_id}/foto", response_model=ProductoResponse)
def subir_foto(
    producto_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    if foto.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa JPG, PNG o WEBP.")
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    if producto.foto_url:
        eliminar_archivo(producto.foto_url)

    producto.foto_url = guardar_archivo(foto, "productos")
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    # Soft delete para preservar historial de ventas
    producto.activo = False
    db.commit()
