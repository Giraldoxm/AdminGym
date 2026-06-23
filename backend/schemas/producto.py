from typing import Optional

from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    stock: int = Field(0, ge=0)
    categoria: Optional[str] = None


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = None
    activo: Optional[bool] = None


class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    stock: int
    categoria: Optional[str]
    activo: bool
    foto_url: Optional[str] = None

    model_config = {"from_attributes": True}
