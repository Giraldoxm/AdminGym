"""Feature flags por gimnasio (módulos opcionales: WODs, biometría, etc.)."""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import GimnasioModulo, Modulo, Usuario
from security import get_current_user


def gimnasio_tiene_modulo(db: Session, gym_id: int, clave: str) -> bool:
    return (
        db.query(GimnasioModulo)
        .join(Modulo, Modulo.id == GimnasioModulo.modulo_id)
        .filter(
            GimnasioModulo.gym_id == gym_id,
            Modulo.clave == clave,
            GimnasioModulo.activo == True,
        )
        .first()
        is not None
    )


def require_modulo(clave: str):
    """Dependencia FastAPI: 403 si el gimnasio del usuario actual no tiene el módulo activo.
    Para endpoints autenticados solo con X-Bridge-Secret (sin JWT), usar
    gimnasio_tiene_modulo(db, usuario.gym_id, clave) directamente."""

    def _dep(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)) -> Usuario:
        if not gimnasio_tiene_modulo(db, current_user.gym_id, clave):
            raise HTTPException(
                status_code=403,
                detail=f"Tu gimnasio no tiene activo el módulo '{clave}'.",
            )
        return current_user

    return _dep
