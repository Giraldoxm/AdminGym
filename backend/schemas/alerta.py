from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class AlertaResponse(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: str
    usuario_telefono: Optional[str]
    fecha_vencimiento: date
    dias_anticipacion: int
    enviada: bool
    fecha_creacion: datetime
    fecha_enviada: Optional[datetime]

    model_config = {"from_attributes": True}
