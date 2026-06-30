"""MDB Reader component for accessing Access database files."""

import csv
import logging
import re
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CREATE_TABLE_REGEX = (
    r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?'
    r'["\'](\w+)["\']\s*\n?\s*\((.*?)\)\s*;'
)


class MDBReader:
    """Clean, reusable interface to read Microsoft Access database (.mdb) files."""

    def __init__(self, mdb_path: Path | str) -> None:
        """Initialize the MDBReader with the path to the MDB file.

        Args:
            mdb_path: Path to the .mdb file.
        """
        self.mdb_path = Path(mdb_path)
        if not self.mdb_path.exists():
            raise FileNotFoundError(f"MDB file not found: {self.mdb_path}")
        self.primary_keys: dict[str, str] = {}
        self._schema = self._parse_schema()


    def _parse_schema(self) -> dict[str, dict[str, str]]:
        """Parse database schema dynamically using mdb-schema."""
        schema: dict[str, dict[str, str]] = {}
        try:
            proc = subprocess.run(
                ["mdb-schema", str(self.mdb_path), "postgres"],
                capture_output=True,
                text=True,
                check=True,
            )
            blocks = re.findall(
                CREATE_TABLE_REGEX,
                proc.stdout,
                re.DOTALL | re.IGNORECASE,
            )
            for table_name, col_text in blocks:
                tname = table_name.lower()
                cols = {}
                for raw_line in col_text.splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    col_match = re.match(r'["\'](\w+)["\']\s+(\w+)', line)
                    if col_match:
                        cname = col_match.group(1).lower()
                        ctype = col_match.group(2).lower()
                        cols[cname] = ctype
                schema[tname] = cols

            # Parse primary keys
            pk_regex = (
                r'ALTER TABLE\s+["\'](\w+)["\']\s+ADD\s+CONSTRAINT\s+["\']\w+["\']\s+'
                r'PRIMARY\s+KEY\s*\(\s*["\'](\w+)["\']\s*\)\s*;'
            )
            pks = re.findall(pk_regex, proc.stdout, re.IGNORECASE)
            for tname, pk_col in pks:
                self.primary_keys[tname.lower()] = pk_col.lower()

        except Exception as e:
            logger.warning(
                "Failed to parse database schema: %s. Defaulting to strings.", e
            )
        return schema


    def list_tables(self) -> list[str]:
        """List all tables available in the MDB database.

        Returns:
            A list of table name strings.
        """
        try:
            proc = subprocess.run(
                ["mdb-tables", "-1", str(self.mdb_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            tables = [
                line.strip()
                for line in proc.stdout.splitlines()
                if line.strip()
            ]
            return tables
        except Exception as e:
            raise OSError(f"Failed to list tables in MDB: {e}") from e

    def read_table(self, table_name: str) -> list[dict[str, Any]]:
        """Read a table from the MDB database into memory, preserving datatypes.

        Args:
            table_name: Name of the table to read.

        Returns:
            A list of dicts, mapping column names to values.
        """
        try:
            proc = subprocess.Popen(
                ["mdb-export", "-0", "NULL", str(self.mdb_path), table_name],
                stdout=subprocess.PIPE,
                text=True,
            )

            assert proc.stdout is not None
            reader = csv.DictReader(proc.stdout)
            rows = []
            table_schema = self._schema.get(table_name.lower(), {})

            for row in reader:
                parsed_row: dict[str, Any] = {}
                for col_name, val_str in row.items():
                    cname = col_name.lower()
                    if val_str is None or val_str in {"NULL", ""}:
                        parsed_row[col_name] = None
                    else:
                        col_type = table_schema.get(cname, "")
                        if "int" in col_type or col_type in {"long", "short"}:
                            try:
                                parsed_row[col_name] = int(val_str)
                            except ValueError:
                                parsed_row[col_name] = val_str
                        elif (
                            "double" in col_type
                            or "float" in col_type
                            or "numeric" in col_type
                            or "real" in col_type
                        ):
                            try:
                                parsed_row[col_name] = float(val_str)
                            except ValueError:
                                parsed_row[col_name] = val_str
                        else:
                            parsed_row[col_name] = val_str
                rows.append(parsed_row)

            proc.wait()
            if proc.returncode != 0:
                raise OSError(f"mdb-export failed with code {proc.returncode}")
            return rows
        except Exception as e:
            raise OSError(f"Failed to read table '{table_name}': {e}") from e
