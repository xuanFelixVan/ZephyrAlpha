# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/_tools/build_ocp_manifest.py | §
# [MODULE] scripts.arch_guard._tools.build_ocp_manifest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
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
# [TTL] permanent
"""从 cross_layer_contracts.yaml 生成 OCP 冻结契约指纹（INV-009）。"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import CONTRACTS_PATH  # noqa: E402

MANIFEST_REL = Path("src/zephyr/shared/contracts/_frozen_signatures/ocp-manifest.json")

def main() -> int:
    import yaml

    if not CONTRACTS_PATH.is_file():
        print("FAIL: contracts yaml missing")
        return 2

    data = yaml.safe_load(CONTRACTS_PATH.read_text(encoding="utf-8"))
    contracts = data.get("contracts") or []
    fingerprints: dict[str, str] = {}
    for c in contracts:
        if not isinstance(c, dict) or not c.get("frozen"):
            continue
        rel = c.get("physical_path") or ""
        if not isinstance(rel, str) or not rel.startswith("src/zephyr/shared/contracts/"):
            continue
        p = (REPO_ROOT / rel).resolve()
        if not p.is_file():
            print(f"SKIP: {rel} 不存在")
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        fingerprints[str(c.get("id", rel))] = h

    out = {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "contract_source": str(CONTRACTS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "fingerprints": dict(sorted(fingerprints.items())),
    }

    out_path = REPO_ROOT / MANIFEST_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{out_path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, out_path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"OK: wrote {len(fingerprints)} fingerprints → {MANIFEST_REL}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
