from datetime import date, datetime

from pydantic import BaseModel


class AsistenciaCreate(BaseModel):
    huella_id: str


class AsistenciaResponse(BaseModel):
    id: int
    usuario_id: int
    tipo: str
    fecha_hora: datetime
    nombre_usuario: str = ""

    model_config = {"from_attributes": True}


class AsistenteBloqueItem(BaseModel):
    usuario_id: int
    nombre: str
    hora_exacta: str  # "07:42"


class BloqueHorario(BaseModel):
    fecha: str        # "2026-05-31"
    bloque: str       # "07:00–08:00"
    hora_inicio: int
    total: int
    asistentes: list[AsistenteBloqueItem]


class SesionesPorBloqueResponse(BaseModel):
    desde: str
    hasta: str
    bloques: list[BloqueHorario]
