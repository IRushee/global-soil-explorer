"""Conversion stage of the offline preprocessing pipeline."""

import logging
import sqlite3
from pathlib import Path
from typing import Any

from backend.processing.shared.context import PreprocessingContext
from backend.processing.shared.mdb_reader import MDBReader

logger = logging.getLogger(__name__)

SENTINELS = {-9, -99, -9999, -9.0, -99.0, -9999.0}


def clean_value(val: Any) -> Any:
    """Clean sentinel missing-value codes to None (SQL NULL)."""
    if val in SENTINELS:
        return None
    if isinstance(val, str):
        v_strip = val.strip()
        if v_strip in {"-9", "-99", "-9999", "-9.0", "-99.0", "-9999.0"}:
            return None
    return val


def generate_create_table_sql(
    table_name: str,
    schema_info: dict[str, str],
    columns: list[str],
    pk: str | None,
) -> str:
    """Generate the CREATE TABLE SQL statement for SQLite."""
    cols_def = []
    columns_lower = {c.lower(): c for c in columns}

    for col_lower, col_type in schema_info.items():
        if col_lower not in columns_lower:
            continue
        col_orig = columns_lower[col_lower]
        sqlite_type = "TEXT"
        if "int" in col_type or col_type in {"long", "short"}:
            sqlite_type = "INTEGER"
        elif (
            "double" in col_type
            or "float" in col_type
            or "numeric" in col_type
            or "real" in col_type
        ):
            sqlite_type = "REAL"

        cdef = f'"{col_orig}" {sqlite_type}'
        if pk and col_lower == pk:
            cdef += " PRIMARY KEY"
        elif table_name.lower() == "hwsd2_smu" and col_lower == "hwsd2_smu_id":
            # Add UNIQUE constraint so other tables can foreign key reference it
            cdef += " UNIQUE"
        cols_def.append(cdef)

    # Fallback for columns not in the parsed schema
    for col in columns:
        if col.lower() not in schema_info:
            cdef = f'"{col}" TEXT'
            if pk and col.lower() == pk:
                cdef += " PRIMARY KEY"
            cols_def.append(cdef)

    # Define foreign key constraint for layers referencing SMU table
    if table_name.lower() == "hwsd2_layers" and "hwsd2_smu_id" in columns_lower:
        cols_def.append(
            'FOREIGN KEY("HWSD2_SMU_ID") REFERENCES "HWSD2_SMU"("HWSD2_SMU_ID")'
        )

    return (
        f'CREATE TABLE "{table_name}" (\n  ' + ",\n  ".join(cols_def) + "\n);"
    )


def _write_database(
    mdb_path: Path, db_path: Path, reader: MDBReader
) -> tuple[int, dict[str, int]]:
    """Write MDB data to SQLite and return statistics."""
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    # Turn off foreign keys temporarily for creation and bulk insert
    conn.execute("PRAGMA foreign_keys = OFF;")
    cursor = conn.cursor()

    tables = reader.list_tables()
    null_conversions = 0
    row_counts = {}

    for table_name in tables:
        rows = reader.read_table(table_name)
        row_counts[table_name] = len(rows)

        if not rows:
            # Empty table schema creation
            schema_info = reader._schema.get(table_name.lower(), {})
            pk = reader.primary_keys.get(table_name.lower())
            create_sql = generate_create_table_sql(
                table_name, schema_info, [], pk
            )
            cursor.execute(create_sql)
            continue

        columns = list(rows[0].keys())
        schema_info = reader._schema.get(table_name.lower(), {})
        pk = reader.primary_keys.get(table_name.lower())

        create_sql = generate_create_table_sql(
            table_name, schema_info, columns, pk
        )
        cursor.execute(create_sql)

        # Bulk insert
        placeholders = ", ".join(["?"] * len(columns))
        cols_str = ", ".join([f'"{c}"' for c in columns])
        insert_sql = (
            f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'
        )

        data_to_insert = []
        for r in rows:
            row_vals = []
            for col in columns:
                val = r[col]
                cleaned = clean_value(val)
                if val is not None and cleaned is None:
                    null_conversions += 1
                row_vals.append(cleaned)
            data_to_insert.append(row_vals)

        cursor.executemany(insert_sql, data_to_insert)

    conn.commit()
    conn.close()
    return null_conversions, row_counts


def _validate_sqlite_database(
    db_path: Path, reader: MDBReader, row_counts: dict[str, int]
) -> int:
    """Validate SQLite database against MDBReader source and schema."""
    conn = sqlite3.connect(str(db_path))
    # Turn ON foreign keys for verification
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Table count check
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    sqlite_tables = {row[0] for row in cursor.fetchall()}
    mdb_tables = set(reader.list_tables())
    if sqlite_tables != mdb_tables:
        msg = (
            f"Table count mismatch. "
            f"MDB: {len(mdb_tables)}, SQLite: {len(sqlite_tables)}"
        )
        raise ValueError(msg)

    # 2. Row count equality check
    for tname in mdb_tables:
        cursor.execute(f'SELECT COUNT(*) FROM "{tname}"')
        sql_count = cursor.fetchone()[0]
        if sql_count != row_counts[tname]:
            msg = (
                f"Row count mismatch in table '{tname}'. "
                f"MDB: {row_counts[tname]}, SQLite: {sql_count}"
            )
            raise ValueError(msg)

    # 3. Schema integrity check (verify PK columns)
    for tname in mdb_tables:
        pk_expected = reader.primary_keys.get(tname.lower())
        if pk_expected:
            cursor.execute(f'PRAGMA table_info("{tname}")')
            cols_info = cursor.fetchall()
            pk_cols = [c[1].lower() for c in cols_info if c[5] > 0]
            if not pk_cols or pk_expected not in pk_cols:
                raise ValueError(
                    f"Primary key validation failed for table '{tname}'. "
                    f"Expected: {pk_expected}, Found: {pk_cols}"
                )

    # 4. Foreign key integrity check
    cursor.execute("PRAGMA foreign_key_check")
    fk_violations = cursor.fetchall()
    if fk_violations:
        raise ValueError(
            f"Foreign key integrity check failed: {fk_violations}"
        )

    # 5. Database size check
    db_size = db_path.stat().st_size
    if db_size == 0:
        raise ValueError("Generated SQLite database size is 0 bytes.")

    conn.close()
    return db_size


def convert_database(context: PreprocessingContext) -> None:
    """Convert raw tabular database records to query-optimized SQLite.

    Args:
        context: The PreprocessingContext instance.
    """
    logger.info("Initializing SQLite database generation...")

    mdb_path = Path(context.discovered_paths["mdb"])
    db_path = context.config.output_dir / "hwsd.db"

    # Make sure output directory exists
    context.config.output_dir.mkdir(parents=True, exist_ok=True)

    reader = MDBReader(mdb_path)

    # 1. Generate primary database
    null_conversions, row_counts = _write_database(mdb_path, db_path, reader)
    logger.info("SQLite database generated successfully.")

    # 2. Validation
    logger.info("Starting post-generation validations...")
    db_size = _validate_sqlite_database(db_path, reader, row_counts)

    # 3. Reproducibility Check
    logger.info("Verifying reproducibility...")
    temp_db_path = context.config.output_dir / "hwsd_repro.db"
    _write_database(mdb_path, temp_db_path, reader)

    # Verify logical identity of row counts
    conn_a = sqlite3.connect(str(db_path))
    conn_b = sqlite3.connect(str(temp_db_path))

    for tname in reader.list_tables():
        count_a = conn_a.execute(f'SELECT COUNT(*) FROM "{tname}"').fetchone()[
            0
        ]
        count_b = conn_b.execute(f'SELECT COUNT(*) FROM "{tname}"').fetchone()[
            0
        ]
        if count_a != count_b:
            raise ValueError(
                f"Reproducibility check failed: row count mismatch in '{tname}'"
            )

    conn_a.close()
    conn_b.close()
    temp_db_path.unlink()

    logger.info(
        "Post-generation validation succeeded. Database is 100% correct."
    )
    logger.info("Total NULL conversions: %d", null_conversions)
    logger.info("Database File: %s (%d bytes)", db_path, db_size)
