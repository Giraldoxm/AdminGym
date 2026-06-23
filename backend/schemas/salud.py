from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class MedidaPorTipoCreate(BaseModel):
    fecha: date
    valor: float = Field(..., gt=0)
    notas: Optional[str] = None


class MedidaResponse(BaseModel):
    id: int
    usuario_id: int
    fecha: date
    peso_kg: Optional[float]
    altura_cm: Optional[float]
    imc: Optional[float]
    cintura_cm: Optional[float]
    cuello_cm: Optional[float]
    cadera_cm: Optional[float]
    brazos_cm: Optional[float]
    notas: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
