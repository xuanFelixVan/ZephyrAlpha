# [BLUEPRINT] MOD-GOV-REPAIR
# [MODULE] scripts.governance.repair.backup_db
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] scripts.governance.repair.backup_depgraph
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# D:\ZephyrAlpha\scripts\governance\repair\backup_db.py
import shutil
import sys
import time
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

DBDIR = REPO_ROOT / "data" / "databases"
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
