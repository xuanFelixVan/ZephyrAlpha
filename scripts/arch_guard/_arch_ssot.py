# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/_arch_ssot.py | §
# [MODULE] scripts.arch_guard._arch_ssot
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""arch_guard 共享：仓库根路径、capacity_slo / invariants / contracts 装载。"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

ARCH_GUARD_ROOT = Path(__file__).resolve().parent
_GOV_DIR = ARCH_GUARD_ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

# 治本（2026-06-30）：使用 _REPO_ROOT 别名，使 REPO_ROOT 不出现在本模块命名空间中。
# 原因：若 _arch_ssot 导出 REPO_ROOT，IDE organize imports 会自动在 arch_guard 文件中
# 加回 `from _arch_ssot import REPO_ROOT`，覆盖 SSoT 源（_shared.constants）。
# 别名使 `from _arch_ssot import REPO_ROOT` 直接 ImportError，阻断 IDE 副作用。
from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402

CAPACITY_SLO_PATH = _REPO_ROOT / "config" / "capacity_slo.yaml"
INVARIANTS_PATH = _REPO_ROOT / (
    "architecture_model/cross_cutting/invariants.yaml"
)
CONTRACTS_PATH = _REPO_ROOT / (
    "architecture_model/contracts/cross_layer_contracts.yaml"
)
RISK_PARAMS_PATH = _REPO_ROOT / "config" / "risk_params.yaml"
SURVIVORSHIP_POLICY_PATH = _REPO_ROOT / "config" / "survivorship_policy.yaml"
OCP_MANIFEST_PATH = _REPO_ROOT / ("src/zephyr/shared/contracts/_frozen_signatures/ocp-manifest.json")


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def first_ms_in_text(text: str) -> int | None:
    m = re.search(r"<\s*(\d+)\s*ms", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"（<\s*(\d+)\s*ms）", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*ms", text)
    if m:
        return int(m.group(1))
    return None


def get_inv_numeric_targets_by_id(invariants_data: dict[str, Any]) -> dict[str, int]:
    """从 invariants.yaml 抽取与延迟相关的毫秒数（INV-001 语句、INV-015 note）。"""
    out: dict[str, int] = {}
    for inv in invariants_data.get("invariants") or []:
        iid = inv.get("id")
        if iid == "INV-001":
            st = inv.get("statement") or ""
            ms = first_ms_in_text(st)
            if ms is not None:
                out["INV-001"] = ms
        elif iid == "INV-015":
            note = inv.get("note") or ""
            ms = first_ms_in_text(note)
            if ms is not None:
                out["INV-015"] = ms
    return out
