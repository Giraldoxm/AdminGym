from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class VentaCreate(BaseModel):
    producto_id: int
    usuario_id: Optional[int] = None
    cantidad: int = Field(1, ge=1)
    metodo_pago: Literal['efectivo', 'transferencia']


class VentaResponse(BaseModel):
    id: int
    producto_id: int
    usuario_id: Optional[int]
    cantidad: int
    precio_unitario: float
    total: float
    metodo_pago: Optional[str]
    fecha_venta: datetime

    model_config = {"from_attributes": True}
