from datetime import datetime, date
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class MovimientoCreate(BaseModel):
    tipo: str = Field(..., pattern="^(ingreso|egreso)$")
    concepto: str = Field(..., min_length=1, max_length=200)
    categoria: str = Field(..., min_length=1, max_length=80)
    monto: float = Field(..., gt=0)
    fecha: datetime
    metodo_pago: Optional[str] = None
    usuario_id: Optional[int] = None
    notas: Optional[str] = None


class MovimientoResponse(BaseModel):
    id: str
    tipo: str
    concepto: str
    categoria: str
    monto: float
    fecha: datetime
    metodo_pago: Optional[str]
    usuario_nombre: Optional[str]
    fuente: str
    es_eliminable: bool

    model_config = {"from_attributes": True}


class BalanceResponse(BaseModel):
    ingresos_total: float
    total_membresias: float
    total_tienda: float
    egresos_total: float
    balance_neto: float
    ingresos_por_categoria: Dict[str, float]
    egresos_por_categoria: Dict[str, float]
    fecha_desde: Optional[date]
    fecha_hasta: Optional[date]
