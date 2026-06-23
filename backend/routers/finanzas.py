from datetime import date, datetime, timedelta
from typing import List, Optional
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import MovimientoFinanciero, Pago, Plan, RolUsuario, TipoMovimiento, Usuario, Venta
from schemas.finanza import BalanceResponse, MovimientoCreate
from security import get_current_user

router = APIRouter(prefix="/finanzas", tags=["Finanzas"])


def _require_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Solo el administrador puede acceder al módulo financiero.")
    return current_user


def _apply_date_filter(query, model_fecha_col, desde: Optional[date], hasta: Optional[date]):
    if desde:
        query = query.filter(model_fecha_col >= datetime.combine(desde, datetime.min.time()))
    if hasta:
        query = query.filter(model_fecha_col <= datetime.combine(hasta, datetime.max.time()))
    return query


@router.get("/balance", response_model=BalanceResponse)
def balance(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin),
):
    # ── Ingresos de membresías (tabla pagos) ──
    q_pagos = db.query(Pago)
    q_pagos = _apply_date_filter(q_pagos, Pago.fecha_pago, fecha_desde, fecha_hasta)
    pagos = q_pagos.all()
    total_membresias = sum(p.monto for p in pagos)

    # ── Ingresos de tienda (tabla ventas) ──
    q_ventas = db.query(Venta)
    q_ventas = _apply_date_filter(q_ventas, Venta.fecha_venta, fecha_desde, fecha_hasta)
    ventas = q_ventas.all()
    total_ventas = sum(v.total for v in ventas)

    # ── Movimientos manuales ──
    q_mov = db.query(MovimientoFinanciero)
    q_mov = _apply_date_filter(q_mov, MovimientoFinanciero.fecha, fecha_desde, fecha_hasta)
    movimientos = q_mov.all()

    # Ingresos manuales (pagos directos + ingresos varios)
    ingresos_manuales = defaultdict(float)
    for m in movimientos:
        if m.tipo == TipoMovimiento.INGRESO:
            ingresos_manuales[m.categoria] += m.monto

    # Egresos manuales
    egresos_por_categoria = defaultdict(float)
    for m in movimientos:
        if m.tipo == TipoMovimiento.EGRESO:
            egresos_por_categoria[m.categoria] += m.monto

    total_ingresos_manuales = sum(ingresos_manuales.values())
    total_egresos = sum(egresos_por_categoria.values())

    ingresos_por_categoria = {
        "mensualidad": total_membresias + ingresos_manuales.get("mensualidad", 0),
        "venta_tienda": total_ventas,
        "ingreso_varios": ingresos_manuales.get("ingreso_varios", 0),
    }
    # Add any other manual ingreso categories
    for cat, val in ingresos_manuales.items():
        if cat not in ingresos_por_categoria:
            ingresos_por_categoria[cat] = val

    total_ingresos = total_membresias + total_ventas + total_ingresos_manuales

    return BalanceResponse(
        ingresos_total=round(total_ingresos, 2),
        total_membresias=round(total_membresias + ingresos_manuales.get("mensualidad", 0), 2),
        total_tienda=round(total_ventas, 2),
        egresos_total=round(total_egresos, 2),
        balance_neto=round(total_ingresos - total_egresos, 2),
        ingresos_por_categoria={k: round(v, 2) for k, v in ingresos_por_categoria.items() if v > 0},
        egresos_por_categoria={k: round(v, 2) for k, v in egresos_por_categoria.items()},
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/movimientos")
def listar_movimientos(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    tipo: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin),
):
    items = []

    # ── Pagos de membresías ──
    if tipo in (None, "ingreso"):
        q = db.query(Pago).join(Plan, isouter=True).join(
            Usuario, Pago.usuario_id == Usuario.id, isouter=True
        )
        q = _apply_date_filter(q, Pago.fecha_pago, fecha_desde, fecha_hasta)
        for p in q.order_by(Pago.fecha_pago.desc()).all():
            plan_nombre = p.plan.nombre if p.plan else "Personalizado"
            usuario_nombre = p.usuario.nombre if p.usuario else None
            items.append({
                "id": f"pago_{p.id}",
                "tipo": "ingreso",
                "concepto": f"Membresía – {usuario_nombre or 'Anónimo'} ({plan_nombre})",
                "categoria": "mensualidad",
                "monto": p.monto,
                "fecha": p.fecha_pago,
                "metodo_pago": p.metodo_pago,
                "usuario_nombre": usuario_nombre,
                "fuente": "pago_membresia",
                "es_eliminable": False,
            })

        # ── Ventas de tienda ──
        q2 = db.query(Venta).join(Usuario, Venta.usuario_id == Usuario.id, isouter=True)
        q2 = _apply_date_filter(q2, Venta.fecha_venta, fecha_desde, fecha_hasta)
        for v in q2.order_by(Venta.fecha_venta.desc()).all():
            items.append({
                "id": f"venta_{v.id}",
                "tipo": "ingreso",
                "concepto": f"Venta tienda – {v.producto.nombre if v.producto else 'Producto'} ×{v.cantidad}",
                "categoria": "venta_tienda",
                "monto": v.total,
                "fecha": v.fecha_venta,
                "metodo_pago": v.metodo_pago,
                "usuario_nombre": v.usuario.nombre if v.usuario else None,
                "fuente": "venta_tienda",
                "es_eliminable": False,
            })

    # ── Movimientos manuales ──
    q3 = db.query(MovimientoFinanciero)
    q3 = _apply_date_filter(q3, MovimientoFinanciero.fecha, fecha_desde, fecha_hasta)
    if tipo in ("ingreso", "egreso"):
        q3 = q3.filter(MovimientoFinanciero.tipo == TipoMovimiento(tipo))
    for m in q3.order_by(MovimientoFinanciero.fecha.desc()).all():
        items.append({
            "id": f"mov_{m.id}",
            "tipo": m.tipo.value,
            "concepto": m.concepto,
            "categoria": m.categoria,
            "monto": m.monto,
            "fecha": m.fecha,
            "metodo_pago": m.metodo_pago,
            "usuario_nombre": m.usuario.nombre if m.usuario else None,
            "fuente": m.fuente,
            "es_eliminable": True,
        })

    # Ordenar por fecha desc y limitar
    items.sort(key=lambda x: x["fecha"], reverse=True)
    return items[:limit]


@router.post("/movimientos", status_code=status.HTTP_201_CREATED)
def crear_movimiento(
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin),
):
    if payload.usuario_id:
        if not db.query(Usuario).filter(Usuario.id == payload.usuario_id).first():
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    mov = MovimientoFinanciero(
        tipo=TipoMovimiento(payload.tipo),
        concepto=payload.concepto,
        categoria=payload.categoria,
        monto=payload.monto,
        fecha=payload.fecha,
        metodo_pago=payload.metodo_pago,
        usuario_id=payload.usuario_id,
        notas=payload.notas,
        fuente="manual",
        created_by=current_user.id,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return {"id": f"mov_{mov.id}", "mensaje": "Movimiento registrado correctamente."}


@router.delete("/movimientos/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin),
):
    mov = db.query(MovimientoFinanciero).filter(
        MovimientoFinanciero.id == movimiento_id,
        MovimientoFinanciero.fuente == "manual",
    ).first()
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado o no es eliminable.")
    db.delete(mov)
    db.commit()


@router.get("/usuarios/buscar")
def buscar_usuarios(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin),
):
    term = f"%{q}%"
    usuarios = (
        db.query(Usuario)
        .filter((Usuario.nombre.ilike(term)) | (Usuario.email.ilike(term)))
        .limit(10)
        .all()
    )
    return [{"id": u.id, "nombre": u.nombre, "email": u.email} for u in usuarios]
