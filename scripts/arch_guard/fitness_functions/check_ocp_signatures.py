# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_ocp_signatures.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_ocp_signatures
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.fitness_functions.__init__
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
"""
check_ocp_signatures.py — OCP 冻结契约指纹校验 (INV-009)

  - 读取 src/zephyr/shared/contracts/_frozen_signatures/ocp-manifest.json
  - 对 cross_layer_contracts.yaml 中 frozen=true 且路径在 shared/contracts 下的文件重算 sha256

exit: 0=pass, 1=drift, 2=missing manifest
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import CONTRACTS_PATH, OCP_MANIFEST_PATH, load_yaml  # noqa: E402

def main() -> int:
    if not OCP_MANIFEST_PATH.is_file():
        print("FAIL: 缺少 ocp-manifest.json — 运行: python scripts/arch_guard/_tools/build_ocp_manifest.py")
        return 2

    manifest = json.loads(OCP_MANIFEST_PATH.read_text(encoding="utf-8"))
    stored = manifest.get("fingerprints") or {}
    if not isinstance(stored, dict) or not stored:
        print("FAIL: ocp_manifest 无 fingerprints")
        return 2

    cdata = load_yaml(CONTRACTS_PATH)
    contracts = cdata.get("contracts") or []
    expected_ids: dict[str, str] = {}
    for c in contracts:
        if not isinstance(c, dict) or not c.get("frozen"):
            continue
        rel = c.get("physical_path") or ""
        if not isinstance(rel, str) or not rel.startswith("src/zephyr/shared/contracts/"):
            continue
        cid = str(c.get("id", rel))
        p = (REPO_ROOT / rel).resolve()
        if not p.is_file():
            print(f"FAIL: 契约文件缺失 {rel}")
            return 1
        expected_ids[cid] = hashlib.sha256(p.read_bytes()).hexdigest()

    if set(expected_ids) != set(stored):
        only_exp = set(expected_ids) - set(stored)
        only_sto = set(stored) - set(expected_ids)
        print(f"FAIL: manifest 与契约集合不一致 only_in_repo={only_exp} only_in_manifest={only_sto}")
        return 1

    for cid, h in expected_ids.items():
        if stored.get(cid) != h:
            print(f"FAIL: 指纹漂移 {cid}: manifest={stored.get(cid)[:16]}... current={h[:16]}...")
            return 1

    print(f"OK: {len(expected_ids)} 条冻结契约指纹一致（INV-009）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
