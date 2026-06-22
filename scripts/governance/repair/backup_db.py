# D:\ZephyrAlpha\scripts\governance\repair\backup_db.py
import shutil
import sys
import time
from pathlib import Path

DBDIR = Path(r"D:\ZephyrAlpha\data\databases")
DBS = ["depgraph.db", "governance.db", "task_cards.db"]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "manual"
    ts = time.strftime("%Y%m%dT%H%M%S")
    out = DBDIR / "_repair_backups" / f"{tag}_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    for db in DBS:
        src = DBDIR / db
        if src.exists():
            shutil.copy2(src, out / db)
            print(f"[BACKUP] {db} -> {out / db}")
    print(f"[BACKUP] DONE tag={tag} dir={out}")


if __name__ == "__main__":
    main()
