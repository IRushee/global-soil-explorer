"""SQLite concrete implementation of the SoilObservationRepository."""

import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from backend.contracts.repository import SoilObservationRepository
from backend.domain import (
    Coordinate,
    PropertyType,
    SoilClassification,
    SoilLayer,
    SoilObservation,
    SoilProfile,
    SoilProperty,
    Unit,
)


class SQLiteSoilObservationRepository(SoilObservationRepository[int]):
    """Retrieves fully constructed domain objects from the SQLite database."""

    def __init__(self, db_path: Path | str) -> None:
        """Initialize the repository and pre-load classification lookup tables.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db_path = Path(db_path)
        if not self._db_path.exists():
            raise FileNotFoundError(f"Database not found: {self._db_path}")

        # Load lookup tables for taxonomy classification mapping
        self._wrb4_lookup = self._load_lookup("D_WRB4")
        self._wrb2_lookup = self._load_lookup("D_WRB2")
        self._fao90_lookup = self._load_lookup("D_FAO90")

        self._prop_mappings = [
            (PropertyType.PH_WATER, "PH_WATER", Unit.PH),
            (PropertyType.SAND, "SAND", Unit.PERCENT),
            (PropertyType.SILT, "SILT", Unit.PERCENT),
            (PropertyType.CLAY, "CLAY", Unit.PERCENT),
            (PropertyType.COARSE_FRAGMENTS, "COARSE", Unit.PERCENT),
            (PropertyType.BULK_DENSITY, "BULK", Unit.GRAM_PER_CUBIC_CENTIMETER),
            (PropertyType.ORGANIC_CARBON, "ORG_CARBON", Unit.PERCENT),
            (
                PropertyType.CATION_EXCHANGE_CAPACITY,
                "CEC_SOIL",
                Unit.CENTIMOL_CHARGE_PER_KG,
            ),
            (PropertyType.AVAILABLE_WATER_CAPACITY, "AWC", Unit.MILLIMETER),
        ]

    def _load_lookup(self, table_name: str) -> dict[str, str]:
        """Load an SQLite lookup table into a symbol/code-to-value map."""
        mapping = {}
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            cols = [c[1].lower() for c in cursor.fetchall()]

            cursor.execute(f'SELECT * FROM "{table_name}"')
            rows = cursor.fetchall()
            for r in rows:
                row_dict = dict(zip(cols, r))
                code = row_dict.get("code") or row_dict.get("symbol")
                val = row_dict.get("value")
                if code is not None and val is not None:
                    mapping[str(code).strip().upper()] = str(val).strip()
        except Exception:
            pass
        finally:
            conn.close()
        return mapping

    def _build_classification(
        self, row_dict: dict[str, Any]
    ) -> SoilClassification:
        """Resolve database classification codes to SoilClassification."""
        wrb4_code = row_dict.get("wrb4")
        wrb2_code = row_dict.get("wrb2")
        fao90_code = row_dict.get("fao90")

        std = None
        code = None
        name = None

        if wrb4_code:
            std = "WRB 2022"
            code = str(wrb4_code).strip()
            name = self._wrb4_lookup.get(code.upper())
        elif wrb2_code:
            std = "WRB 2nd Edition"
            code = str(wrb2_code).strip()
            name = self._wrb2_lookup.get(code.upper())
        elif fao90_code:
            std = "FAO 1990"
            code = str(fao90_code).strip()
            name = self._fao90_lookup.get(code.upper())

        if not std or not code:
            std = "Unknown"
            code = "UN"
            name = "Unclassified"

        if not name:
            name = f"Unresolved classification {code}"

        return SoilClassification(
            taxonomy_standard=std, class_symbol=code, class_name=name
        )

    def get_by_key(
        self, key: int, coordinate: Coordinate | None = None
    ) -> SoilObservation:
        """Retrieve a fully constructed SoilObservation using a spatial key.

        Args:
            key: The dataset-specific spatial key (HWSD2_SMU_ID).
            coordinate: The validated Coordinate to associate (defaults to (0,0)).

        Returns:
            A fully constructed and validated SoilObservation object.
        """
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM "HWSD2_LAYERS" WHERE "HWSD2_SMU_ID" = ? '
            'ORDER BY "SEQUENCE" ASC, "TOPDEP" ASC',
            (key,),
        )
        col_names = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            raise KeyError(f"Observation key {key} not found.")

        # Group rows by SEQUENCE to build individual profiles
        seq_rows = defaultdict(list)
        for r in rows:
            row_dict = dict(zip(col_names, r))
            seq = row_dict.get("sequence")
            if seq is not None:
                seq_rows[seq].append(row_dict)

        profiles = []
        for seq in sorted(seq_rows.keys()):
            layers_data = seq_rows[seq]
            first_row = layers_data[0]

            share_val = first_row.get("share")
            share = float(share_val) if share_val is not None else 100.0
            classification = self._build_classification(first_row)

            layers = []
            for r in layers_data:
                top_dep = r.get("topdep")
                bot_dep = r.get("botdep")
                if top_dep is None or bot_dep is None:
                    continue

                properties = []
                for prop_type, col_name, unit in self._prop_mappings:
                    val = r.get(col_name.lower())
                    if val is not None:
                        properties.append(
                            SoilProperty(prop_type, float(val), unit)
                        )

                layers.append(
                    SoilLayer(
                        float(top_dep), float(bot_dep), tuple(properties)
                    )
                )

            if not layers:
                continue

            sorted_layers = sorted(layers, key=lambda layer: layer.top_depth_cm)
            profile_obj = SoilProfile(
                layers=tuple(sorted_layers),
                classification=classification,
                composition_share=share,
            )
            profiles.append(profile_obj)

        unique_profiles = []
        seen_ids = set()
        for p in profiles:
            if id(p) not in seen_ids:
                unique_profiles.append(p)
                seen_ids.add(id(p))

        obs_coordinate = (
            coordinate if coordinate is not None else Coordinate(0.0, 0.0)
        )
        return SoilObservation(
            coordinate=obs_coordinate, profiles=tuple(unique_profiles)
        )
