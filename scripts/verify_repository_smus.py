# ruff: noqa
"""End-to-end repository validation script comparing observations to SQLite rows."""

import random
import sqlite3
import sys
from pathlib import Path

from backend.domain import Coordinate
from backend.repository.sqlite_repository import (
    SQLiteSoilObservationRepository,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "output" / "hwsd.db"


def _clean_val(v):
    if v in (None, "", -9, -9.0, "-9", "-9.0"):
        return None
    if isinstance(v, float) and v < 0:
        return None
    if isinstance(v, int) and v < 0:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s == "" or s == "-9" or s == "-":
            return None
        return s
    return v


def main():
    if not DB_PATH.exists():
        print(f"Error: Database missing at {DB_PATH}")
        sys.exit(1)

    repo = SQLiteSoilObservationRepository(DB_PATH)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Get distinct SMU IDs
    cursor.execute(
        "SELECT DISTINCT HWSD2_SMU_ID FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID IS NOT NULL"
    )
    smu_ids = [r[0] for r in cursor.fetchall()]

    random.seed(123)
    sample_smus = random.sample(smu_ids, min(1000, len(smu_ids)))

    print(f"Running validation on {len(sample_smus)} sampled SMUs...")

    for smu_id in sample_smus:
        # Load raw SMU row
        cursor.execute(
            "SELECT KOPPEN, COVERAGE, WRB2_CODE FROM HWSD2_SMU WHERE HWSD2_SMU_ID = ?",
            (smu_id,),
        )
        smu_row = cursor.fetchone()
        raw_koppen = smu_row[0] if smu_row else None
        raw_coverage = smu_row[1] if smu_row else None

        # Load raw layer rows
        cursor.execute(
            "SELECT * FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID = ? ORDER BY SEQUENCE, TOPDEP",
            (smu_id,),
        )
        col_names = [col[0].lower() for col in cursor.description]
        raw_layers = [dict(zip(col_names, r)) for r in cursor.fetchall()]

        # Query via repository
        coord = Coordinate(12.34, 56.78)
        obs = repo.get_by_key(smu_id, coordinate=coord)

        # 1. Verify Coordinate & Climate
        assert obs.coordinate == coord
        if raw_koppen is not None and str(raw_koppen).strip() != "":
            assert obs.environmental_context is not None
            assert (
                obs.environmental_context.koppen_climate
                == str(raw_koppen).strip().upper()
            )
        else:
            assert (
                obs.environmental_context is None
                or obs.environmental_context.koppen_climate is None
            )

        # 2. Group raw layers by sequence to check profiles
        seq_groups = {}
        for rl in raw_layers:
            seq = rl["sequence"]
            if seq not in seq_groups:
                seq_groups[seq] = []
            seq_groups[seq].append(rl)

        assert len(obs.profiles) == len(seq_groups)

        for profile in obs.profiles:
            # We don't have a direct key, but composition share and sequence order matches
            # Let's find the matching raw sequence group
            # Find sequence with the same composition share (roughly)
            matched_group = None
            for seq, l_rows in seq_groups.items():
                first_row = l_rows[0]
                raw_share = (
                    float(first_row.get("share"))
                    if first_row.get("share") is not None
                    else 100.0
                )
                if abs(profile.composition_share - raw_share) < 0.01:
                    # Check classification matches
                    wrb4 = _clean_val(first_row.get("wrb4"))
                    if wrb4:
                        if profile.classification.wrb4_code == wrb4:
                            matched_group = l_rows
                            break
                    else:
                        matched_group = l_rows
                        break

            assert matched_group is not None, (
                f"Failed to match profile sequence for SMU {smu_id}"
            )

            first_raw = matched_group[0]

            # 3. Verify HydrologicContext
            hydro = profile.hydrologic_context
            assert hydro.drainage == _clean_val(first_raw.get("drainage"))
            assert hydro.water_regime == _clean_val(first_raw.get("swr"))
            assert hydro.impermeable_layer == _clean_val(first_raw.get("il"))

            # 4. Verify LandLimitations
            limits = profile.land_limitations
            assert limits.root_depth == _clean_val(first_raw.get("root_depth"))
            assert limits.root_obstacles == _clean_val(first_raw.get("roots"))
            assert limits.phase1 == _clean_val(first_raw.get("phase1"))
            assert limits.phase2 == _clean_val(first_raw.get("phase2"))
            assert limits.additional_property == _clean_val(first_raw.get("add_prop"))

            # 5. Verify Layers
            assert len(profile.layers) == len(matched_group)
            for i, layer in enumerate(profile.layers):
                raw_lay = matched_group[i]
                assert layer.top_depth_cm == float(raw_lay.get("topdep"))
                assert layer.bottom_depth_cm == float(raw_lay.get("botdep"))

                # Texture check
                assert layer.texture.usda_texture == _clean_val(
                    raw_lay.get("texture_usda")
                )
                assert layer.texture.soter_texture == _clean_val(
                    raw_lay.get("texture_soter")
                )

                # Physical properties check
                phys = layer.measurements.physical
                assert phys.sand == _clean_val(raw_lay.get("sand"))
                assert phys.silt == _clean_val(raw_lay.get("silt"))
                assert phys.clay == _clean_val(raw_lay.get("clay"))
                assert phys.coarse_fragments == _clean_val(raw_lay.get("coarse"))
                assert phys.bulk_density == _clean_val(raw_lay.get("bulk"))
                assert phys.ref_bulk_density == _clean_val(raw_lay.get("ref_bulk"))

                # Chemical properties check
                chem = layer.measurements.chemical
                assert chem.ph == _clean_val(raw_lay.get("ph_water"))
                assert chem.organic_carbon == _clean_val(raw_lay.get("org_carbon"))
                assert chem.total_nitrogen == _clean_val(raw_lay.get("total_n"))
                assert chem.cn_ratio == _clean_val(raw_lay.get("cn_ratio"))
                assert chem.cec_soil == _clean_val(raw_lay.get("cec_soil"))
                assert chem.cec_clay == _clean_val(raw_lay.get("cec_clay"))
                assert chem.effective_cec == _clean_val(raw_lay.get("cec_eff"))
                assert chem.teb == _clean_val(raw_lay.get("teb"))
                assert chem.base_saturation == _clean_val(raw_lay.get("bsat"))
                assert chem.aluminum_saturation == _clean_val(raw_lay.get("alum_sat"))
                assert chem.esp == _clean_val(raw_lay.get("esp"))
                assert chem.calcium_carbonate == _clean_val(raw_lay.get("tcarbon_eq"))
                assert chem.gypsum == _clean_val(raw_lay.get("gypsum"))
                assert chem.electrical_conductivity == _clean_val(
                    raw_lay.get("elec_cond")
                )

                # Hydraulic properties check
                hyd = layer.measurements.hydraulic
                assert hyd.available_water_capacity == _clean_val(raw_lay.get("awc"))

    print(
        f"Validation completed. All {len(sample_smus)} observations matched SQLite records exactly with zero information loss."
    )
    conn.close()


if __name__ == "__main__":
    main()
