from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PagoCreate(BaseModel):
    usuario_id: int
    plan_id: int
    monto: float = Field(..., gt=0)
    metodo_pago: Literal['efectivo', 'transferencia']


class PagoResponse(BaseModel):
    id: int
    usuario_id: int
    plan_id: int
    fecha_pago: datetime
    monto: float
    metodo_pago: Optional[str]
    nueva_fecha_vencimiento: Optional[date] = None

    model_config = {"from_attributes": True}
