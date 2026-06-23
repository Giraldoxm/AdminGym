import json
import math
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import MarcaRM, Usuario
from schemas.marcas import MarcaRMCreate, MarcaRMResponse
from security import get_current_user

router = APIRouter(prefix="/marcas", tags=["Marcas RM"])


# Clasificación por ejercicio (debe coincidir con frontend/src/data/ejerciciosMarcas.js)
TIPOS_EJERCICIO = {
    "Back Squat": "barra",
    "Deadlift": "barra",
    "Clean": "barra",
    "Clean and Jerk": "barra",
    "Snatch": "barra",
    "Bench Press": "barra",
    "Press Militar": "barra",
    "Dominadas": "corporal_lastre",
    "Push Up": "reps",
    "Air Squat": "reps",
    "Sit Up": "reps",
    "Test de Léger": "leger",
}


def _tipo_de(ejercicio: str) -> str:
    return TIPOS_EJERCICIO.get(ejercicio.strip(), "barra")


def _calcular_1rm(peso: float, reps: int) -> float:
    if reps == 1:
        return round(peso, 1)
    # Brzycki divide por (37 - r): r >= 37 rompe (÷0 o negativo). Las fórmulas 1RM
    # tampoco son válidas con reps muy altas. El cap real (36) se valida antes en el
    # router; este clamp es defensa en profundidad para no reventar el cálculo.
    if reps >= 37:
        reps = 36
    w, r = peso, reps
    valores = [
        w * (36 / (37 - r)),                                    # Brzycki
        w * (1 + r / 30),                                        # Epley
        (100 * w) / (101.3 - 2.67123 * r),                     # Lander
        w * (1 + 0.025 * r),                                     # O'Conner
        w * (r ** 0.1),                                          # Lombardi
        (100 * w) / (52.2 + 41.9 * math.exp(-0.055 * r)),      # Mayhew
        (100 * w) / (48.8 + 53.8 * math.exp(-0.075 * r)),      # Wathen
    ]
    return round(sum(valores) / len(valores), 1)


@router.get("/", response_model=List[MarcaRMResponse])
def listar_todas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return (
        db.query(MarcaRM)
        .filter(MarcaRM.usuario_id == current_user.id)
        .order_by(MarcaRM.fecha.asc())
        .all()
    )


@router.get("/{ejercicio}", response_model=List[MarcaRMResponse])
def listar_por_ejercicio(
    ejercicio: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return (
        db.query(MarcaRM)
        .filter(MarcaRM.usuario_id == current_user.id, MarcaRM.ejercicio == ejercicio)
        .order_by(MarcaRM.fecha.asc())
        .all()
    )


@router.post("/", response_model=MarcaRMResponse, status_code=status.HTTP_201_CREATED)
def crear_marca(
    payload: MarcaRMCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    ejercicio = payload.ejercicio.strip()
    tipo = _tipo_de(ejercicio)

    peso = None
    unidad = payload.unidad
    reps = None
    rm = None
    peso_adicional = None
    nivel = None
    palier = None
    series_json = None

    if tipo in ("barra", "corporal_lastre"):
        if tipo == "corporal_lastre":
            peso_adicional = payload.peso_adicional

        if payload.series:
            # Ruta nueva: múltiples series — calcular 1RM de cada una, guardar la mejor
            series_calc = []
            mejor: dict | None = None
            for s in payload.series:
                rm_s = _calcular_1rm(s.peso, s.repeticiones)
                entrada = {"peso": s.peso, "repeticiones": s.repeticiones, "rm_calculado": rm_s}
                series_calc.append(entrada)
                if mejor is None or rm_s > mejor["rm_calculado"]:
                    mejor = entrada
            peso = mejor["peso"]
            reps = mejor["repeticiones"]
            rm = mejor["rm_calculado"]
            series_json = json.dumps(series_calc)
        else:
            # Ruta legacy: un solo set
            if payload.peso is None or payload.peso <= 0 or payload.repeticiones is None:
                raise HTTPException(
                    status_code=422,
                    detail="Se requiere al menos una serie con peso y repeticiones.",
                )
            if payload.repeticiones > 36:
                raise HTTPException(
                    status_code=422,
                    detail="Para estimar el 1RM usa máximo 36 repeticiones.",
                )
            peso = payload.peso
            reps = payload.repeticiones
            rm = _calcular_1rm(peso, reps)
            series_json = None

    elif tipo == "reps":
        if payload.repeticiones is None or payload.repeticiones < 1:
            raise HTTPException(status_code=422, detail="Se requiere número de repeticiones.")
        reps = payload.repeticiones

    elif tipo == "leger":
        if payload.nivel is None or payload.palier is None:
            raise HTTPException(status_code=422, detail="Se requiere nivel y palier.")
        nivel = payload.nivel
        palier = payload.palier

    marca = MarcaRM(
        usuario_id=current_user.id,
        ejercicio=ejercicio,
        peso=peso,
        unidad=unidad,
        repeticiones=reps,
        rm_calculado=rm,
        peso_adicional=peso_adicional,
        nivel=nivel,
        palier=palier,
        series=series_json,
        fecha=payload.fecha,
        notas=payload.notas,
    )
    db.add(marca)
    db.commit()
    db.refresh(marca)
    return marca


@router.patch("/{marca_id}", response_model=MarcaRMResponse)
def editar_marca(
    marca_id: int,
    payload: MarcaRMCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    marca = db.query(MarcaRM).filter(
        MarcaRM.id == marca_id,
        MarcaRM.usuario_id == current_user.id,
    ).first()
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")

    ejercicio = payload.ejercicio.strip()
    tipo = _tipo_de(ejercicio)

    if tipo in ("barra", "corporal_lastre"):
        if tipo == "corporal_lastre":
            marca.peso_adicional = payload.peso_adicional
        if payload.series:
            series_calc = []
            mejor = None
            for s in payload.series:
                rm_s = _calcular_1rm(s.peso, s.repeticiones)
                entrada = {"peso": s.peso, "repeticiones": s.repeticiones, "rm_calculado": rm_s}
                series_calc.append(entrada)
                if mejor is None or rm_s > mejor["rm_calculado"]:
                    mejor = entrada
            marca.peso = mejor["peso"]
            marca.repeticiones = mejor["repeticiones"]
            marca.rm_calculado = mejor["rm_calculado"]
            marca.series = json.dumps(series_calc)
        else:
            if payload.peso is None or payload.peso <= 0 or payload.repeticiones is None:
                raise HTTPException(status_code=422, detail="Se requiere al menos una serie con peso y repeticiones.")
            if payload.repeticiones > 36:
                raise HTTPException(status_code=422, detail="Para estimar el 1RM usa máximo 36 repeticiones.")
            marca.peso = payload.peso
            marca.repeticiones = payload.repeticiones
            marca.rm_calculado = _calcular_1rm(payload.peso, payload.repeticiones)
            marca.series = None
    elif tipo == "reps":
        if payload.repeticiones is None or payload.repeticiones < 1:
            raise HTTPException(status_code=422, detail="Se requiere número de repeticiones.")
        marca.repeticiones = payload.repeticiones
    elif tipo == "leger":
        if payload.nivel is None or payload.palier is None:
            raise HTTPException(status_code=422, detail="Se requiere nivel y palier.")
        marca.nivel = payload.nivel
        marca.palier = payload.palier

    marca.unidad = payload.unidad
    marca.fecha = payload.fecha
    marca.notas = payload.notas
    db.commit()
    db.refresh(marca)
    return marca


@router.delete("/{marca_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_marca(
    marca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    marca = db.query(MarcaRM).filter(
        MarcaRM.id == marca_id,
        MarcaRM.usuario_id == current_user.id,
    ).first()
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    db.delete(marca)
    db.commit()
