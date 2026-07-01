# ruff: noqa
"""Lookup table verification script auditing code coverages and references."""

import sqlite3
from pathlib import Path

DB_PATH = Path("../data/output/hwsd.db")


def analyze_lookup(cursor, lookup_table, code_col, core_cols):
    # Total lookup entries
    cursor.execute(f"SELECT COUNT(*) FROM {lookup_table}")
    total_entries = cursor.fetchone()[0]

    # Distinct codes in lookup table
    cursor.execute(f"SELECT COUNT(DISTINCT {code_col}) FROM {lookup_table}")
    distinct_codes = cursor.fetchone()[0]

    # Get lookup codes
    cursor.execute(
        f"SELECT {code_col} FROM {lookup_table} WHERE {code_col} IS NOT NULL"
    )
    lookup_codes = set(r[0] for r in cursor.fetchall())

    # Check duplicate codes in lookup table
    cursor.execute(
        f"SELECT {code_col}, COUNT(*) FROM {lookup_table} "
        f"GROUP BY {code_col} HAVING COUNT(*) > 1"
    )
    duplicates = len(cursor.fetchall())

    # Scan core references
    used_codes_set = set()
    null_count = 0
    orphan_set = set()

    for c_table, c_col in core_cols:
        cursor.execute(f"SELECT {c_col} FROM {c_table}")
        for r in cursor.fetchall():
            val = r[0]
            if val is None or val == "" or val == -9 or val == "-9":
                null_count += 1
            else:
                # Type cast check
                if lookup_codes and isinstance(list(lookup_codes)[0], int):
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                else:
                    if isinstance(val, str):
                        val = val.strip()

                if val in lookup_codes:
                    used_codes_set.add(val)
                else:
                    orphan_set.add(val)

    used_in_db = len(used_codes_set)
    unused = len(lookup_codes - used_codes_set)
    orphans = len(orphan_set)

    return {
        "table": lookup_table,
        "rows": total_entries,
        "distinct": distinct_codes,
        "used": used_in_db,
        "unused": unused,
        "duplicates": duplicates,
        "nulls": null_count,
        "orphans": orphans,
    }


def main():
    if not DB_PATH.exists():
        print(f"Error: Database missing at {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    configs = [
        ("D_KOPPEN", "CODE", [("HWSD2_SMU", "KOPPEN")]),
        (
            "D_DRAINAGE",
            "CODE",
            [("HWSD2_LAYERS", "DRAINAGE"), ("HWSD2_SMU", "DRAINAGE")],
        ),
        (
            "D_ROOT_DEPTH",
            "CODE",
            [("HWSD2_LAYERS", "ROOT_DEPTH"), ("HWSD2_SMU", "ROOT_DEPTH")],
        ),
        ("D_ROOTS", "CODE", [("HWSD2_LAYERS", "ROOTS"), ("HWSD2_SMU", "ROOTS")]),
        (
            "D_PHASE",
            "CODE",
            [
                ("HWSD2_LAYERS", "PHASE1"),
                ("HWSD2_LAYERS", "PHASE2"),
                ("HWSD2_SMU", "PHASE1"),
                ("HWSD2_SMU", "PHASE2"),
            ],
        ),
        (
            "D_ADD_PROP",
            "CODE",
            [("HWSD2_LAYERS", "ADD_PROP"), ("HWSD2_SMU", "ADD_PROP")],
        ),
        (
            "D_TEXTURE_USDA",
            "CODE",
            [("HWSD2_LAYERS", "TEXTURE_USDA"), ("HWSD2_SMU", "TEXTURE_USDA")],
        ),
        ("D_TEXTURE_SOTER", "CODE", [("HWSD2_LAYERS", "TEXTURE_SOTER")]),
        ("D_SWR", "CODE", [("HWSD2_LAYERS", "SWR")]),
        ("D_IL", "CODE", [("HWSD2_LAYERS", "IL"), ("HWSD2_SMU", "IL")]),
    ]

    print(
        "| Lookup | Rows | Distinct Codes | Used | Unused | Duplicates | NULL | Orphans | Validation |"
    )
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for table, code_col, core_cols in configs:
        res = analyze_lookup(cursor, table, code_col, core_cols)
        status = "PASS" if res["orphans"] == 0 else "FAIL"
        print(
            f"| {res['table']} | {res['rows']} | {res['distinct']} | {res['used']} | "
            f"{res['unused']} | {res['duplicates']} | {res['nulls']} | {res['orphans']} | {status} |"
        )

    conn.close()


if __name__ == "__main__":
    main()
