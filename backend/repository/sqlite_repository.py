"""SQLite concrete implementation of the SoilObservationRepository."""

import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from backend.contracts.repository import SoilObservationRepository
from backend.domain import (
    ChemicalProperties,
    Coordinate,
    DatasetMetadata,
    EnvironmentalContext,
    HydraulicProperties,
    HydrologicContext,
    LandLimitations,
    LayerMeasurements,
    PhysicalProperties,
    PropertyType,
    SoilClassification,
    SoilLayer,
    SoilObservation,
    SoilProfile,
    SoilProperty,
    SoilTexture,
    Unit,
)


def _clean_numeric(val: Any) -> float | None:
    """Standardize missing/sentinel database values to None for floats."""
    if val is None or val in ("", -9, -9.0, "-9", "-9.0"):
        return None
    try:
        f_val = float(val)
        if f_val < 0.0:
            return None
        return f_val
    except (ValueError, TypeError):
        return None


def _clean_int(val: Any) -> int | None:
    """Standardize missing/sentinel database values to None for integers."""
    if val is None or val in ("", -9, "-9"):
        return None
    try:
        i_val = int(val)
        if i_val < 0:
            return None
        return i_val
    except (ValueError, TypeError):
        return None


def _clean_str(val: Any) -> str | None:
    """Clean string values and handle hyphen sentinels."""
    if val is None:
        return None
    s_val = str(val).strip()
    if s_val in ("", "-9", "-"):
        return None
    return s_val


class SQLiteSoilObservationRepository(SoilObservationRepository[int]):
    """Retrieves fully constructed domain objects from the SQLite database."""

    def __init__(self, db_path: Path | str) -> None:
        """Initialize the repository and pre-load lookup dictionaries.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db_path = Path(db_path)
        if not self._db_path.exists():
            raise FileNotFoundError(f"Database not found: {self._db_path}")

        # Pre-load classification and limitation lookups
        self._wrb4_lookup = self._load_lookup("D_WRB4")
        self._wrb2_lookup = self._load_lookup("D_WRB2")
        self._fao90_lookup = self._load_lookup("D_FAO90")
        self._koppen_lookup = self._load_lookup("D_KOPPEN")
        self._drainage_lookup = self._load_lookup("D_DRAINAGE")
        self._root_depth_lookup = self._load_lookup("D_ROOT_DEPTH")
        self._roots_lookup = self._load_lookup("D_ROOTS")
        self._phase_lookup = self._load_lookup("D_PHASE")
        self._add_prop_lookup = self._load_lookup("D_ADD_PROP")
        self._usda_texture_lookup = self._load_lookup("D_TEXTURE_USDA")
        self._soter_texture_lookup = self._load_lookup("D_TEXTURE_SOTER")
        self._swr_lookup = self._load_lookup("D_SWR")
        self._il_lookup = self._load_lookup("D_IL")
        self._coverage_lookup = self._load_lookup("D_COVERAGE")
        self._wrb_phases_lookup = self._load_lookup("D_WRB_PHASES")
        self._library_lookup = self._load_library_lookup()

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

    def _load_library_lookup(self) -> dict[int, str]:
        """Load AezLibrary values from WRB_Library reference table."""
        mapping = {}
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ID_AezLibrary, AezLibrary FROM WRB_Library")
            for r in cursor.fetchall():
                if r[0] is not None and r[1] is not None:
                    mapping[int(r[0])] = str(r[1]).strip()
        except Exception:
            pass
        finally:
            conn.close()
        return mapping

    def _build_classification(self, row_dict: dict[str, Any]) -> SoilClassification:
        """Resolve database classification codes to SoilClassification."""
        wrb4_code = _clean_str(row_dict.get("wrb4"))
        wrb2_code = _clean_str(row_dict.get("wrb2"))
        fao90_code = _clean_str(row_dict.get("fao90"))
        wrb_phase_code = _clean_str(row_dict.get("wrb_phases"))
        national_classification = _clean_str(row_dict.get("nsc"))

        std = None
        code = None
        name = None

        if wrb4_code:
            std = "WRB 2022"
            code = wrb4_code
            name = self._wrb4_lookup.get(code.upper())
        elif wrb2_code:
            std = "WRB 2nd Edition"
            code = wrb2_code
            name = self._wrb2_lookup.get(code.upper())
        elif fao90_code:
            std = "FAO 1990"
            code = fao90_code
            name = self._fao90_lookup.get(code.upper())

        if not std or not code:
            std = "Unknown"
            code = "UN"
            name = "Unclassified"

        if not name:
            name = f"Unresolved classification {code}"

        # Resolve optional names
        wrb4_name = self._wrb4_lookup.get(wrb4_code.upper()) if wrb4_code else None
        wrb2_name = self._wrb2_lookup.get(wrb2_code.upper()) if wrb2_code else None
        fao90_name = self._fao90_lookup.get(fao90_code.upper()) if fao90_code else None
        wrb_phase_name = (
            self._wrb_phases_lookup.get(wrb_phase_code.upper())
            if wrb_phase_code
            else None
        )
        dominant_group_code = (
            wrb4_code[:2] if wrb4_code else (wrb2_code[:2] if wrb2_code else None)
        )

        return SoilClassification(
            taxonomy_standard=std,
            class_symbol=code,
            class_name=name,
            wrb4_code=wrb4_code,
            wrb4_name=wrb4_name,
            wrb2_code=wrb2_code,
            wrb2_name=wrb2_name,
            fao90_code=fao90_code,
            fao90_name=fao90_name,
            wrb_phase_code=wrb_phase_code,
            wrb_phase_name=wrb_phase_name,
            dominant_group_code=dominant_group_code,
            national_classification=national_classification,
        )

    def get_by_key(  # noqa: PLR0912, PLR0915
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

        # Query SMU level climate and coverage
        cursor.execute(
            'SELECT "KOPPEN", "COVERAGE", "WRB2_CODE" FROM "HWSD2_SMU" '
            'WHERE "HWSD2_SMU_ID" = ?',
            (key,),
        )
        smu_row = cursor.fetchone()
        if smu_row:
            koppen_code = _clean_str(smu_row[0])
            coverage_code = _clean_int(smu_row[1])
            wrb2_library_code = _clean_int(smu_row[2])
        else:
            # Fallback to layers table metadata if SMU details are missing
            cursor.execute(
                'SELECT "COVERAGE" FROM "HWSD2_LAYERS" '
                'WHERE "HWSD2_SMU_ID" = ? LIMIT 1',
                (key,),
            )
            layers_exist = cursor.fetchone()
            if not layers_exist:
                conn.close()
                raise KeyError(f"Observation key {key} not found.")
            koppen_code = None
            coverage_code = _clean_int(layers_exist[0])
            wrb2_library_code = None

        # Query Layers
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

            # Build HydrologicContext
            drainage = _clean_str(first_row.get("drainage"))
            swr = _clean_int(first_row.get("swr"))
            il = _clean_int(first_row.get("il"))
            hydro = HydrologicContext(
                drainage=drainage, water_regime=swr, impermeable_layer=il
            )

            # Build LandLimitations
            root_d = _clean_int(first_row.get("root_depth"))
            roots = _clean_int(first_row.get("roots"))
            phase1 = _clean_int(first_row.get("phase1"))
            phase2 = _clean_int(first_row.get("phase2"))
            add_prop = _clean_int(first_row.get("add_prop"))
            limits = LandLimitations(
                root_depth=root_d,
                root_obstacles=roots,
                phase1=phase1,
                phase2=phase2,
                additional_property=add_prop,
            )

            layers = []
            for r in layers_data:
                top_dep = r.get("topdep")
                bot_dep = r.get("botdep")
                if top_dep is None or bot_dep is None:
                    continue

                # Build properties list for backward compatibility
                properties = []
                for prop_type, col_name, unit in self._prop_mappings:
                    val = _clean_numeric(r.get(col_name.lower()))
                    if val is not None:
                        properties.append(SoilProperty(prop_type, float(val), unit))

                # Build SoilTexture
                usda_tex = _clean_int(r.get("texture_usda"))
                soter_tex = _clean_str(r.get("texture_soter"))
                texture = SoilTexture(usda_texture=usda_tex, soter_texture=soter_tex)

                # Build PhysicalProperties
                sand = _clean_numeric(r.get("sand"))
                silt = _clean_numeric(r.get("silt"))
                clay = _clean_numeric(r.get("clay"))
                coarse = _clean_numeric(r.get("coarse"))
                bulk = _clean_numeric(r.get("bulk"))
                ref_bulk = _clean_numeric(r.get("ref_bulk"))
                phys = PhysicalProperties(
                    sand=sand,
                    silt=silt,
                    clay=clay,
                    coarse_fragments=coarse,
                    bulk_density=bulk,
                    ref_bulk_density=ref_bulk,
                )

                # Build ChemicalProperties
                ph = _clean_numeric(r.get("ph_water"))
                oc = _clean_numeric(r.get("org_carbon"))
                n = _clean_numeric(r.get("total_n"))
                cn = _clean_numeric(r.get("cn_ratio"))
                cec = _clean_numeric(r.get("cec_soil"))
                cec_clay = _clean_numeric(r.get("cec_clay"))
                ecec = _clean_numeric(r.get("cec_eff"))
                teb = _clean_numeric(r.get("teb"))
                bsat = _clean_numeric(r.get("bsat"))
                asat = _clean_numeric(r.get("alum_sat"))
                esp = _clean_numeric(r.get("esp"))
                caco3 = _clean_numeric(r.get("tcarbon_eq"))
                gypsum = _clean_numeric(r.get("gypsum"))
                ec = _clean_numeric(r.get("elec_cond"))
                chem = ChemicalProperties(
                    ph=ph,
                    organic_carbon=oc,
                    total_nitrogen=n,
                    cn_ratio=cn,
                    cec_soil=cec,
                    cec_clay=cec_clay,
                    effective_cec=ecec,
                    teb=teb,
                    base_saturation=bsat,
                    aluminum_saturation=asat,
                    esp=esp,
                    calcium_carbonate=caco3,
                    gypsum=gypsum,
                    electrical_conductivity=ec,
                )

                # Build HydraulicProperties
                awc = _clean_numeric(r.get("awc"))
                hyd = HydraulicProperties(available_water_capacity=awc)

                # Consolidate LayerMeasurements
                measure = LayerMeasurements(physical=phys, chemical=chem, hydraulic=hyd)

                layers.append(
                    SoilLayer(
                        top_depth_cm=float(top_dep),
                        bottom_depth_cm=float(bot_dep),
                        properties=tuple(properties),
                        texture=texture,
                        measurements=measure,
                    )
                )

            if not layers:
                continue

            sorted_layers = sorted(layers, key=lambda layer: layer.top_depth_cm)
            profile_obj = SoilProfile(
                layers=tuple(sorted_layers),
                classification=classification,
                composition_share=share,
                hydrologic_context=hydro,
                land_limitations=limits,
                sequence_index=seq,
            )
            profiles.append(profile_obj)

        unique_profiles = []
        seen_ids = set()
        for p in profiles:
            if id(p) not in seen_ids:
                unique_profiles.append(p)
                seen_ids.add(id(p))

        obs_coordinate = coordinate if coordinate is not None else Coordinate(0.0, 0.0)

        # Build EnvironmentalContext
        env_ctx = (
            EnvironmentalContext(koppen_climate=koppen_code) if koppen_code else None
        )

        # Build DatasetMetadata
        lib_name = (
            self._library_lookup.get(wrb2_library_code)
            if wrb2_library_code is not None
            else None
        )
        cov_name = (
            self._coverage_lookup.get(str(coverage_code).upper())
            if coverage_code is not None
            else None
        )
        metadata = DatasetMetadata(
            coverage=coverage_code,
            library=lib_name,
            source=cov_name or "HWSD v2.0 Database",
            dataset_version="v2.0",
            reference_identifiers=(("HWSD2_SMU_ID", str(key)),),
        )

        return SoilObservation(
            coordinate=obs_coordinate,
            profiles=tuple(unique_profiles),
            environmental_context=env_ctx,
            metadata=metadata,
        )
