"""Generic merge script for domain cleanup. Usage: python script.py <DOMAIN_ID>"""

import json
import sqlite3
import sys
from collections import defaultdict

DB_PATH = "D:/ZephyrAlpha/data/databases/depgraph.db"


def merge_domain(domain_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if domain needs merging
    cur.execute("SELECT COUNT(*) FROM nodes WHERE domain_id=? AND design_maturity='design'", (domain_id,))
    total_before = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type IN ('feature','reference','implementation')",
        (domain_id,),
    )
    fri_count = cur.fetchone()[0]

    print(f"{domain_id}: total={total_before}, FRI={fri_count}")

    if fri_count == 0 and total_before <= 80:
        print("  Already clean, skipping")
        conn.close()
        return True

    # Phase 1: Merge FRI nodes
    if fri_count > 0:
        children = cur.execute(
            "SELECT node_id, node_name, node_type, belongs_to FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type IN ('feature','reference','implementation')",
            (domain_id,),
        ).fetchall()

        merged = 0
        promoted = 0
        for child_id, child_name, child_type, belongs_to in children:
            parent_id = None
            if belongs_to and belongs_to.strip():
                parent_id = belongs_to.strip()
            else:
                prefix = child_id.rsplit("-", 1)[0] if "-" in child_id else child_id
                row = cur.execute(
                    "SELECT node_id FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type='module' AND node_id LIKE ? LIMIT 1",
                    (domain_id, prefix + "%"),
                ).fetchone()
                if row:
                    parent_id = row[0]

            if parent_id:
                parent = cur.execute("SELECT type_specific_data FROM nodes WHERE node_id=?", (parent_id,)).fetchone()
                tsd = json.loads(parent[0]) if parent and parent[0] else {}
                merge_key = "merged_" + child_type + "s"
                tsd.setdefault(merge_key, []).append(
                    {"node_id": child_id, "node_name": child_name or child_id, "original_type": child_type}
                )
                cur.execute(
                    "UPDATE nodes SET type_specific_data=? WHERE node_id=?",
                    (json.dumps(tsd, ensure_ascii=False), parent_id),
                )
                cur.execute("DELETE FROM nodes WHERE node_id=?", (child_id,))
                merged += 1
            else:
                cur.execute("UPDATE nodes SET node_type='module' WHERE node_id=?", (child_id,))
                promoted += 1

        conn.commit()
        print(f"  FRI merge: merged={merged}, promoted={promoted}")

    # Phase 2: Merge other non-module types (contract, event, aggregate, etc.)
    non_module_types = ["contract", "event", "aggregate", "prerequisite", "invariant", "decision", "gate", "blueprint"]
    for nmt in non_module_types:
        children = cur.execute(
            "SELECT node_id, node_name, node_type FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type=?",
            (domain_id, nmt),
        ).fetchall()
        if not children:
            continue

        merged = 0
        for child_id, child_name, child_type in children:
            prefix = child_id.rsplit("-", 1)[0] if "-" in child_id else child_id
            row = cur.execute(
                "SELECT node_id FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type='module' AND node_id LIKE ? LIMIT 1",
                (domain_id, prefix + "%"),
            ).fetchone()
            if row:
                parent_id = row[0]
                parent = cur.execute("SELECT type_specific_data FROM nodes WHERE node_id=?", (parent_id,)).fetchone()
                tsd = json.loads(parent[0]) if parent and parent[0] else {}
                merge_key = "merged_" + child_type + "s"
                tsd.setdefault(merge_key, []).append(
                    {"node_id": child_id, "node_name": child_name or child_id, "original_type": child_type}
                )
                cur.execute(
                    "UPDATE nodes SET type_specific_data=? WHERE node_id=?",
                    (json.dumps(tsd, ensure_ascii=False), parent_id),
                )
                cur.execute("DELETE FROM nodes WHERE node_id=?", (child_id,))
                merged += 1
            else:
                cur.execute("UPDATE nodes SET node_type='module' WHERE node_id=?", (child_id,))

        if merged > 0:
            conn.commit()
            print(f"  {nmt} merge: merged={merged}")

    # Phase 3: Merge small module groups (same prefix)
    cur.execute(
        "SELECT node_id, node_name, type_specific_data FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type='module' ORDER BY node_id",
        (domain_id,),
    )
    modules = cur.fetchall()

    if len(modules) > 80:
        groups = defaultdict(list)
        for mid, mname, mtsd in modules:
            parts = mid.split("-")
            prefix = "-".join(parts[:3]) if len(parts) >= 3 else mid
            groups[prefix].append((mid, mname, mtsd))

        merge_ops = 0
        for pfx, mods in groups.items():
            if len(mods) <= 1:
                continue
            rep_id, rep_name, rep_tsd = mods[0]
            rep_tsd = json.loads(rep_tsd) if rep_tsd else {}

            for child_id, child_name, child_tsd in mods[1:]:
                child_tsd = json.loads(child_tsd) if child_tsd else {}
                for k, v in child_tsd.items():
                    if k in rep_tsd and isinstance(rep_tsd[k], list) and isinstance(v, list):
                        rep_tsd[k].extend(v)
                    elif k in rep_tsd:
                        rep_tsd.setdefault("merged_overflow", []).append({k: v})
                    else:
                        rep_tsd[k] = v

                rep_tsd.setdefault("merged_modules", []).append(
                    {"node_id": child_id, "node_name": child_name or child_id}
                )

            cur.execute(
                "UPDATE nodes SET type_specific_data=? WHERE node_id=?",
                (json.dumps(rep_tsd, ensure_ascii=False), rep_id),
            )
            for child_id, _, _ in mods[1:]:
                cur.execute("DELETE FROM nodes WHERE node_id=?", (child_id,))
                merge_ops += 1

        if merge_ops > 0:
            conn.commit()
            print(f"  Module merge: {merge_ops} merged")

    # Final check
    cur.execute("SELECT COUNT(*) FROM nodes WHERE domain_id=? AND design_maturity='design'", (domain_id,))
    total_after = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE domain_id=? AND design_maturity='design' AND node_type IN ('feature','reference','implementation')",
        (domain_id,),
    )
    fri_after = cur.fetchone()[0]
    cur.execute(
        "SELECT node_type, COUNT(*) FROM nodes WHERE domain_id=? AND design_maturity='design' GROUP BY node_type ORDER BY COUNT(*) DESC",
        (domain_id,),
    )
    dist = {r[0]: r[1] for r in cur.fetchall()}

    print(f"  RESULT: total={total_after}, FRI={fri_after}, types={dist}")

    conn.close()
    return (5 <= total_after <= 80) and (fri_after == 0)


if __name__ == "__main__":
    import sys

    sys.exit("DEPRECATED: 此脚本已归档，depgraph.db 已迁移至 PostgreSQL 16")
    if len(sys.argv) < 2:
        print("Usage: python _phase_c_merge.py <DOMAIN_ID>")
        sys.exit(1)
    ok = merge_domain(sys.argv[1])
    sys.exit(0 if ok else 1)
