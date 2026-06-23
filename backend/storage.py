"""
Almacenamiento de archivos subidos (fotos de perfil y de productos).

Dos backends, elegidos por entorno:
  • Object storage S3-compatible (Cloudflare R2 / AWS S3) — si S3_BUCKET está
    definido. Necesario en la nube porque el filesystem de Railway/Render es
    efímero (se borra en cada deploy).
  • Filesystem local (carpeta backend/uploads) — fallback para desarrollo.

La elección es transparente para los routers: usan guardar_archivo() y
eliminar_archivo() sin saber qué backend hay detrás.

URLs almacenadas en la BD:
  • Local: ruta relativa "/uploads/...". El backend la sirve vía StaticFiles.
  • S3/R2: URL pública absoluta "https://.../uploads/...".
eliminar_archivo() reconoce ambos formatos, así que los registros antiguos
(creados en local) se siguen pudiendo borrar tras migrar a S3.

Variables de entorno (S3/R2):
  S3_BUCKET            nombre del bucket (su sola presencia activa el modo S3)
  S3_PUBLIC_URL        base pública para construir las URLs (ej. https://pub-xxx.r2.dev
                       o un dominio propio enlazado al bucket)
  S3_ENDPOINT_URL      endpoint del servicio (R2: https://<accountid>.r2.cloudflarestorage.com;
                       AWS S3: dejar vacío)
  S3_ACCESS_KEY_ID     credencial
  S3_SECRET_ACCESS_KEY credencial
  S3_REGION            región (default "auto", válido para R2)
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

UPLOADS_DIR = Path(__file__).parent / "uploads"

S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_PUBLIC_URL = os.getenv("S3_PUBLIC_URL", "").rstrip("/")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "") or None
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "")
S3_REGION = os.getenv("S3_REGION", "auto")

USA_S3 = bool(S3_BUCKET)

_cliente_s3 = None


def _s3():
    """Cliente boto3 perezoso y cacheado."""
    global _cliente_s3
    if _cliente_s3 is None:
        import boto3
        _cliente_s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
            region_name=S3_REGION,
        )
    return _cliente_s3


def guardar_archivo(foto: UploadFile, subcarpeta: str = "") -> str:
    """Guarda el archivo subido y devuelve la URL para persistir en la BD.

    subcarpeta: prefijo opcional (ej. "productos").
    """
    extension = foto.filename.rsplit(".", 1)[-1].lower()
    nombre = f"{uuid.uuid4().hex}.{extension}"
    rel = f"{subcarpeta}/{nombre}" if subcarpeta else nombre

    if USA_S3:
        key = f"uploads/{rel}"
        _s3().upload_fileobj(
            foto.file,
            S3_BUCKET,
            key,
            ExtraArgs={"ContentType": foto.content_type or "application/octet-stream"},
        )
        return f"{S3_PUBLIC_URL}/{key}"

    destino = UPLOADS_DIR / rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("wb") as f:
        shutil.copyfileobj(foto.file, f)
    return f"/uploads/{rel}"


def eliminar_archivo(url: Optional[str]) -> None:
    """Borra el archivo apuntado por la URL almacenada. Tolera URLs de ambos
    backends para soportar registros creados antes de migrar a S3."""
    if not url:
        return

    if USA_S3 and S3_PUBLIC_URL and url.startswith(S3_PUBLIC_URL + "/"):
        key = url[len(S3_PUBLIC_URL) + 1:]
        try:
            _s3().delete_object(Bucket=S3_BUCKET, Key=key)
        except Exception:
            pass
        return

    if url.startswith("/uploads/"):
        archivo = UPLOADS_DIR / url[len("/uploads/"):]
        if archivo.exists():
            archivo.unlink()
