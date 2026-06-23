import json
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class SerieCreate(BaseModel):
    """Una serie individual dentro de una sesión de entrenamiento."""
    peso: float = Field(..., gt=0)
    repeticiones: int = Field(..., ge=1, le=36)


class MarcaRMCreate(BaseModel):
    """Payload flexible que cubre los 4 tipos de ejercicio.

    - barra:           series[] con peso+reps, o peso+repeticiones legacy
    - corporal_lastre: igual que barra (peso ya convertido por el frontend)
    - reps:            solo repeticiones
    - leger:           nivel + palier
    """
    ejercicio: str = Field(..., min_length=1, max_length=100)
    fecha: date
    notas: Optional[str] = None
    unidad: str = Field("kg", pattern="^(kg|lbs)$")
    # barra / corporal_lastre — nueva ruta: lista de series
    series: Optional[list[SerieCreate]] = None
    # barra / corporal_lastre — ruta legacy (un solo set)
    peso: Optional[float] = Field(None, ge=0)
    # reps puede ser alto (AMRAP de Air Squat/Sit Up); el cap para 1RM se valida en el router
    repeticiones: Optional[int] = Field(None, ge=1, le=1000)
    # corporal_lastre
    peso_adicional: Optional[float] = Field(None, ge=0)
    # leger
    nivel: Optional[int] = Field(None, ge=1, le=23)
    palier: Optional[int] = Field(None, ge=1, le=20)


class MarcaRMResponse(BaseModel):
    id: int
    usuario_id: int
    ejercicio: str
    peso: Optional[float]
    unidad: str
    repeticiones: Optional[int]
    rm_calculado: Optional[float]
    peso_adicional: Optional[float]
    nivel: Optional[int]
    palier: Optional[int]
    series: Optional[list[Any]] = None
    fecha: date
    notas: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("series", mode="before")
    @classmethod
    def _parse_series(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
