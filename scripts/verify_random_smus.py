# ruff: noqa
"""Verification script reconstructing domain models for 1000 sampled SMUs."""

import random
import sqlite3
import sys
from pathlib import Path

from backend.domain import (
    ChemicalProperties,
    DatasetMetadata,
    EnvironmentalContext,
    HydraulicProperties,
    HydrologicContext,
    LandLimitations,
    LayerMeasurements,
    PhysicalProperties,
    SoilTexture,
)

DB_PATH = Path("../data/output/hwsd.db")


def main():
    if not DB_PATH.exists():
        print("Error: Database missing.")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 1. Fetch all distinct HWSD2_SMU_ID
    cursor.execute(
        "SELECT DISTINCT HWSD2_SMU_ID FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID IS NOT NULL"
    )
    smu_ids = [r[0] for r in cursor.fetchall()]

    # Randomly sample 1000 SMUs
    random.seed(42)
    sample_smus = random.sample(smu_ids, min(1000, len(smu_ids)))

    print(f"Sampling {len(sample_smus)} SMUs for end-to-end domain model validation...")

    success_count = 0
    for smu_id in sample_smus:
        # Query layers for this SMU
        cursor.execute(
            "SELECT * FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID = ? "
            "ORDER BY SEQUENCE, TOPDEP",
            (smu_id,),
        )
        rows = cursor.fetchall()

        # Get column names
        cursor.execute("PRAGMA table_info(HWSD2_LAYERS)")
        cols = [r[1] for r in cursor.fetchall()]

        # Check SMU summary climate zone
        cursor.execute("SELECT KOPPEN FROM HWSD2_SMU WHERE HWSD2_SMU_ID = ?", (smu_id,))
        smu_row = cursor.fetchone()
        koppen = smu_row[0] if smu_row else None

        try:
            # Construct EnvironmentalContext
            env = EnvironmentalContext(koppen_climate=koppen)

            # Group rows by sequence
            seq_rows = {}
            for row in rows:
                row_dict = dict(zip(cols, row))
                seq = row_dict["SEQUENCE"]
                if seq not in seq_rows:
                    seq_rows[seq] = []
                seq_rows[seq].append(row_dict)

            for seq, l_rows in seq_rows.items():
                first_row = l_rows[0]

                # Construct HydrologicContext
                drainage = first_row["DRAINAGE"]
                if drainage in (None, -9, "-9", ""):
                    drainage = None
                swr = first_row["SWR"]
                if swr in (None, -9, "-9", ""):
                    swr = None
                il = first_row["IL"]
                if il in (None, -9, "-9", ""):
                    il = None
                hydro = HydrologicContext(
                    drainage=drainage, water_regime=swr, impermeable_layer=il
                )

                # Construct LandLimitations
                root_d = first_row["ROOT_DEPTH"]
                if root_d in (None, -9, "-9", ""):
                    root_d = None
                roots = first_row["ROOTS"]
                if roots in (None, -9, "-9", ""):
                    roots = None
                phase1 = first_row["PHASE1"]
                if phase1 in (None, -9, "-9", ""):
                    phase1 = None
                phase2 = first_row["phase2"] if "phase2" in first_row else None
                # Check case for PHASE2
                if phase2 is None and "PHASE2" in first_row:
                    phase2 = first_row["PHASE2"]
                if phase2 in (None, -9, "-9", ""):
                    phase2 = None
                add_prop = first_row["ADD_PROP"]
                if add_prop in (None, -9, "-9", ""):
                    add_prop = None
                limits = LandLimitations(
                    root_depth=root_d,
                    root_obstacles=roots,
                    phase1=phase1,
                    phase2=phase2,
                    additional_property=add_prop,
                )

                # Validate properties for each layer
                for r_dict in l_rows:
                    # Construct SoilTexture
                    usda = r_dict["TEXTURE_USDA"]
                    if usda in (None, -9, "-9", ""):
                        usda = None
                    soter = r_dict["TEXTURE_SOTER"]
                    if soter in (None, -9, "-9", ""):
                        soter = None
                    texture = SoilTexture(usda_texture=usda, soter_texture=soter)

                    # Construct PhysicalProperties
                    sand = r_dict["SAND"]
                    if sand is not None and sand < 0:
                        sand = None
                    silt = r_dict["SILT"]
                    if silt is not None and silt < 0:
                        silt = None
                    clay = r_dict["CLAY"]
                    if clay is not None and clay < 0:
                        clay = None
                    coarse = r_dict["COARSE"]
                    if coarse is not None and coarse < 0:
                        coarse = None
                    bulk = r_dict["BULK"]
                    if bulk is not None and bulk < 0:
                        bulk = None
                    ref_bulk = r_dict["REF_BULK"]
                    if ref_bulk is not None and ref_bulk < 0:
                        ref_bulk = None
                    phys = PhysicalProperties(
                        sand=sand,
                        silt=silt,
                        clay=clay,
                        coarse_fragments=coarse,
                        bulk_density=bulk,
                        ref_bulk_density=ref_bulk,
                    )

                    # Construct ChemicalProperties
                    ph = r_dict["PH_WATER"]
                    if ph is not None and ph < 0:
                        ph = None
                    oc = r_dict["ORG_CARBON"]
                    if oc is not None and oc < 0:
                        oc = None
                    n = r_dict["TOTAL_N"]
                    if n is not None and n < 0:
                        n = None
                    cn = r_dict["CN_RATIO"]
                    if cn is not None and cn < 0:
                        cn = None
                    cec = r_dict["CEC_SOIL"]
                    if cec is not None and cec < 0:
                        cec = None
                    cec_clay = r_dict["CEC_CLAY"]
                    if cec_clay is not None and cec_clay < 0:
                        cec_clay = None
                    ecec = r_dict["CEC_EFF"]
                    if ecec is not None and ecec < 0:
                        ecec = None
                    teb = r_dict["TEB"]
                    if teb is not None and teb < 0:
                        teb = None
                    bsat = r_dict["BSAT"]
                    if bsat is not None and bsat < 0:
                        bsat = None
                    asat = r_dict["ALUM_SAT"]
                    if asat is not None and asat < 0:
                        asat = None
                    esp = r_dict["ESP"]
                    if esp is not None and esp < 0:
                        esp = None
                    caco3 = r_dict["TCARBON_EQ"]
                    if caco3 is not None and caco3 < 0:
                        caco3 = None
                    gypsum = r_dict["GYPSUM"]
                    if gypsum is not None and gypsum < 0:
                        gypsum = None
                    ec = r_dict["ELEC_COND"]
                    if ec is not None and ec < 0:
                        ec = None
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

                    # Construct HydraulicProperties
                    awc = r_dict["AWC"]
                    if awc is not None and awc < 0:
                        awc = None
                    hyd = HydraulicProperties(available_water_capacity=awc)

                    # Construct LayerMeasurements
                    measure = LayerMeasurements(
                        physical=phys, chemical=chem, hydraulic=hyd
                    )

            success_count += 1
        except Exception as e:
            print(f"Failed at SMU {smu_id}: {e}")
            conn.close()
            sys.exit(1)

    print(
        f"Verification completed. Successfully constructed domain objects "
        f"for {success_count}/{len(sample_smus)} sampled SMUs with ZERO errors."
    )
    conn.close()


if __name__ == "__main__":
    main()
