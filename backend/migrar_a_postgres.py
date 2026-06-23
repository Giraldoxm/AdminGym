"""
Migración de datos SQLite → PostgreSQL (Capa 2 del despliegue).

Corrida única para llevar los datos actuales de producción (usuarios, pagos,
marcas, etc.) desde el SQLite local hacia el Postgres de la nube.

Uso:
    # 1. Define el destino Postgres (mismo formato que DATABASE_URL en prod):
    #    PowerShell:  $env:DATABASE_URL = "postgresql+psycopg://user:pass@host:5432/db"
    #    bash:        export DATABASE_URL="postgresql+psycopg://user:pass@host:5432/db"
    # 2. Ejecuta desde la carpeta backend/:
    #    python migrar_a_postgres.py
    #
    # Origen SQLite por defecto: ./crossfit.db (override con SQLITE_URL).

Qué hace:
    1. create_all() en Postgres (crea el esquema final).
    2. Dos engines: lee de SQLite, escribe en Postgres a nivel core
       (los type-processors convierten fechas/booleanos/enums correctamente).
    3. Copia las tablas respetando el orden de claves foráneas
       (Base.metadata.sorted_tables ya viene topológicamente ordenado).
    4. Resetea las secuencias de IDs (setval) al final.

Es idempotente solo si el destino está vacío: vuelve a insertar y fallaría por
PK duplicada. Pensado para correrse UNA vez sobre un Postgres fresco.
"""

import os
import sys

from sqlalchemy import create_engine, insert, select, func

import models
from models import Base

SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///crossfit.db")
DEST_URL = os.getenv("DATABASE_URL", "")

if DEST_URL.startswith("postgres://"):
    DEST_URL = DEST_URL.replace("postgres://", "postgresql+psycopg://", 1)


def main() -> None:
    if not DEST_URL:
        sys.exit("❌ Define DATABASE_URL con la URL del Postgres destino.")
    if DEST_URL.startswith("sqlite"):
        sys.exit("❌ DATABASE_URL apunta a SQLite. Debe ser un Postgres destino.")

    src_engine = create_engine(SQLITE_URL)
    dst_engine = create_engine(DEST_URL)

    print(f"Origen : {SQLITE_URL}")
    print(f"Destino: {dst_engine.url.render_as_string(hide_password=True)}\n")

    # 1. Esquema final en Postgres
    Base.metadata.create_all(bind=dst_engine)

    # 2-3. Copia tabla por tabla en orden de dependencias de FK
    total = 0
    with src_engine.connect() as src, dst_engine.begin() as dst:
        for table in Base.metadata.sorted_tables:
            filas = [dict(row) for row in src.execute(select(table)).mappings()]
            if not filas:
                print(f"  · {table.name}: 0 filas")
                continue
            dst.execute(insert(table), filas)
            total += len(filas)
            print(f"  ✓ {table.name}: {len(filas)} filas")

    # 4. Resetear las secuencias de IDs en Postgres
    print("\nReseteando secuencias de IDs…")
    with dst_engine.begin() as dst:
        for table in Base.metadata.sorted_tables:
            if "id" not in table.c:
                continue
            max_id = dst.execute(select(func.max(table.c.id))).scalar()
            if max_id is None:
                continue
            dst.execute(
                select(func.setval(
                    func.pg_get_serial_sequence(table.name, "id"),
                    max_id,
                ))
            )
            print(f"  ✓ {table.name}: secuencia → {max_id}")

    print(f"\n✅ Migración completa. {total} filas copiadas.")


if __name__ == "__main__":
    main()
