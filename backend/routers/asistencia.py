import os
from collections import defaultdict
from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Asistencia, RolUsuario, Usuario
from schemas.asistencia import (
    AsistenciaCreate, AsistenciaResponse,
    AsistenteBloqueItem, BloqueHorario, SesionesPorBloqueResponse,
)
from security import get_current_user

router = APIRouter(prefix="/asistencia", tags=["Asistencia"])


def _require_admin_or_coach(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Solo admin o coach pueden realizar esta acción.")
    return current_user


def _autorizar_bridge_o_admin(request: Request, db: Session) -> None:
    bridge_secret = os.environ.get("BRIDGE_SECRET", "")
    x_secret = request.headers.get("X-Bridge-Secret", "")
    if bridge_secret and x_secret == bridge_secret:
        return
    from jose import jwt as jose_jwt
    from security import ALGORITHM, SECRET_KEY
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload_jwt = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload_jwt.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Not authenticated")
    caller = db.query(Usuario).filter(Usuario.email == email).first()
    if not caller or caller.rol not in (RolUsuario.ADMIN, RolUsuario.COACH):
        raise HTTPException(status_code=403, detail="Sin permisos.")


MINUTOS_SESION = 65  # tiempo máximo de una sesión; usado por el job de reset en main.py


def _registrar(usuario: Usuario, db: Session) -> AsistenciaResponse:
    # La palanquera solo controla la ENTRADA. No se registran salidas:
    # cada marcación de huella es una entrada y enciende esta_en_gym.
    # El flag vuelve a False solo por tiempo (job _job_reset_gym en main.py).
    asistencia = Asistencia(usuario_id=usuario.id, tipo="entrada")
    db.add(asistencia)
    usuario.esta_en_gym = True
    db.commit()
    db.refresh(asistencia)
    return AsistenciaResponse(
        id=asistencia.id,
        usuario_id=asistencia.usuario_id,
        tipo=asistencia.tipo,
        fecha_hora=asistencia.fecha_hora,
        nombre_usuario=usuario.nombre,
    )


@router.post("/", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
def registrar_asistencia(payload: AsistenciaCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.huella_id == payload.huella_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con esa huella.")
    return _registrar(usuario, db)


@router.post("/por-usuario/{usuario_id}", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
def registrar_asistencia_por_id(usuario_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Registra una entrada dado el usuario_id directamente.
    Usado por el bridge DigitalPersona (X-Bridge-Secret) o por admin/coach (JWT).
    Valida que la membresía esté vigente antes de permitir el acceso.
    """
    _autorizar_bridge_o_admin(request, db)
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Toda marcación es una entrada → siempre se valida la membresía.
    if not usuario.fecha_vencimiento or usuario.fecha_vencimiento < date.today():
        raise HTTPException(
            status_code=403,
            detail=f"Membresía vencida o sin plan activo para {usuario.nombre}.",
        )

    return _registrar(usuario, db)


@router.get("/mi-historial")
def mi_historial(
    meses: int = Query(4, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    hoy = date.today()
    mes = hoy.month
    anio = hoy.year
    for _ in range(meses - 1):
        mes -= 1
        if mes == 0:
            mes = 12
            anio -= 1
    desde = datetime(anio, mes, 1)

    asistencias = (
        db.query(Asistencia)
        .filter(
            Asistencia.usuario_id == current_user.id,
            Asistencia.tipo == "entrada",
            Asistencia.fecha_hora >= desde,
        )
        .order_by(Asistencia.fecha_hora)
        .all()
    )

    fechas = sorted(set(a.fecha_hora.date().isoformat() for a in asistencias))
    return {"fechas": fechas, "total": len(fechas)}


@router.get("/historial/{usuario_id}")
def historial_usuario(
    usuario_id: int,
    meses: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    hoy = date.today()
    mes = hoy.month
    anio = hoy.year
    for _ in range(meses - 1):
        mes -= 1
        if mes == 0:
            mes = 12
            anio -= 1
    desde = datetime(anio, mes, 1)

    asistencias = (
        db.query(Asistencia)
        .filter(
            Asistencia.usuario_id == usuario_id,
            Asistencia.tipo == "entrada",
            Asistencia.fecha_hora >= desde,
        )
        .order_by(Asistencia.fecha_hora)
        .all()
    )

    fechas = sorted(set(a.fecha_hora.date().isoformat() for a in asistencias))
    return {"fechas": fechas, "total": len(fechas)}


@router.get("/en-gym")
def usuarios_en_gym(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    """Usuarios con esta_en_gym=True, con su última entrada y tiempo restante de sesión."""
    usuarios = db.query(Usuario).filter(Usuario.esta_en_gym == True).all()
    ahora = datetime.utcnow()
    resultado = []
    for u in usuarios:
        ultima = (
            db.query(Asistencia)
            .filter(Asistencia.usuario_id == u.id, Asistencia.tipo == "entrada")
            .order_by(Asistencia.fecha_hora.desc())
            .first()
        )
        if not ultima:
            continue
        minutos_transcurridos = (ahora - ultima.fecha_hora).total_seconds() / 60
        resultado.append({
            "usuario_id": u.id,
            "nombre": u.nombre,
            "foto_url": u.foto_url,
            "entrada_desde": ultima.fecha_hora.isoformat(),
            "minutos_transcurridos": round(minutos_transcurridos, 1),
            "minutos_restantes": round(max(0, MINUTOS_SESION - minutos_transcurridos), 1),
            "minutos_sesion": MINUTOS_SESION,
        })
    resultado.sort(key=lambda x: x["minutos_transcurridos"], reverse=True)
    return resultado


_BOGOTA = ZoneInfo("America/Bogota")


@router.get("/sesiones-por-bloque", response_model=SesionesPorBloqueResponse)
def sesiones_por_bloque(
    desde: date = Query(..., description="Fecha inicio YYYY-MM-DD"),
    hasta: date = Query(..., description="Fecha fin YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(_require_admin_or_coach),
):
    if desde > hasta:
        raise HTTPException(status_code=422, detail="'desde' debe ser anterior o igual a 'hasta'.")
    if (hasta - desde).days > 31:
        raise HTTPException(status_code=422, detail="El rango no puede superar 31 días.")

    desde_utc = datetime(desde.year, desde.month, desde.day, 0, 0, 0)
    hasta_utc = datetime(hasta.year, hasta.month, hasta.day, 23, 59, 59)

    asistencias = (
        db.query(Asistencia)
        .options(joinedload(Asistencia.usuario))
        .filter(
            Asistencia.tipo == "entrada",
            Asistencia.fecha_hora >= desde_utc,
            Asistencia.fecha_hora <= hasta_utc,
        )
        .all()
    )

    # Ordenar por fecha_hora para conservar la primera entrada en caso de duplicado
    asistencias.sort(key=lambda a: a.fecha_hora)

    vistos: dict[tuple, set[int]] = defaultdict(set)
    bloques: dict[tuple, list[AsistenteBloqueItem]] = defaultdict(list)
    for a in asistencias:
        hora_local = a.fecha_hora.replace(tzinfo=ZoneInfo("UTC")).astimezone(_BOGOTA)
        key = (hora_local.date().isoformat(), hora_local.hour)
        if a.usuario_id in vistos[key]:
            continue  # ya registrado en este bloque, ignorar entradas repetidas
        vistos[key].add(a.usuario_id)
        bloques[key].append(
            AsistenteBloqueItem(
                usuario_id=a.usuario_id,
                nombre=a.usuario.nombre,
                hora_exacta=hora_local.strftime("%H:%M"),
            )
        )

    resultado = [
        BloqueHorario(
            fecha=fecha_str,
            bloque=f"{h:02d}:00–{(h + 1) % 24:02d}:00",
            hora_inicio=h,
            total=len(v),
            asistentes=sorted(v, key=lambda x: x.hora_exacta),
        )
        for (fecha_str, h), v in sorted(bloques.items())
    ]

    return SesionesPorBloqueResponse(
        desde=desde.isoformat(),
        hasta=hasta.isoformat(),
        bloques=resultado,
    )
