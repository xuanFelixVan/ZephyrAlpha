# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_blind_spot_status.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_blind_spot_status
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
GATE-BS: Blind Spot Reality Check
=================================
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

# 每次跑门禁时,对 session_logs/index.yaml 中所有 status=open 的盲点
# 执行自动对账--检查代码现实是否已经解决.
# 发现"已解决但忘改状态"的盲点时,输出警告并要求手动确认.
# 此脚本不自动修改 index.yaml,只报告.

__manifest__ = {
    "args": [],
    "description": "Blind Spot Reality Check - open blinds vs actual code status",
    "dimensions": ["D5"],
    "priority": "P2",
    "timeout_seconds": 60,
    "warn_only": False,
}

import hashlib
import os
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml


def _read_yaml(path: Path) -> dict[str, Any]:
    """_read_yaml implementation."""
    with open(path, encoding="utf-8", errors="replace") as f:
        return yaml.safe_load(f) or {}


def load_open_blind_spots(index_path: Path) -> list[dict[str, Any]]:
    """load_open_blind_spots implementation."""
    data = _read_yaml(index_path)
    spots = data.get("blind_spot_timeline", [])
    return [s for s in spots if s.get("status") == "open"]


# -- Reality Check Functions -------------------------------------------
# Each function takes blind_spot_id, returns (resolved: bool, detail: str)

CheckFn = Callable[[str, Path], tuple[bool, str]]


def check_var_cvar(_repo: Path) -> tuple[bool, str]:
    """BLIND-L04-VAR-CVAR-MISSING: D_RISK 是否已有 VaR/CVaR 实现"""
    risk_dir = _repo / "src" / "zephyr" / "risk"
    if not risk_dir.exists():
        return False, "D_RISK 目录不存在"

    evidence: list[str] = []
    for py_file in risk_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pattern in [r"(?i)\bVaR\b", r"(?i)\bCVaR\b", r"(?i)value_at_risk", r"(?i)expected_shortfall"]:
            if re.search(pattern, content):
                evidence.append(str(py_file.relative_to(_repo)))
                break

    if evidence:
        return True, f"VaR/CVaR 已存在于 {len(evidence)} 个文件中: {', '.join(sorted(set(evidence)))}"
    return False, "未找到 VaR/CVaR 相关代码"


def check_channel_fallback(_repo: Path) -> tuple[bool, str]:
    """BLIND-L08-CHANNEL-FALLBACK: D_FRONTEND 是否有多渠道 fallback"""
    frontend = _repo / "src" / "zephyr" / "frontend"
    if not frontend.exists():
        return False, "D_FRONTEND 目录不存在"

    fallback_names = ["fallback", "failover", "retry", "channel_chain", "escalation"]
    evidence: list[str] = []
    for py_file in frontend.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for keyword in fallback_names:
            if keyword in content.lower():
                evidence.append(f"{py_file.relative_to(_repo)}: {keyword}")
                break

    if evidence:
        return True, f"多渠道 fallback 代码已存在: {', '.join(sorted(set(e.split(': ')[0] for e in evidence)))}"
    return False, "D_FRONTEND 中未发现 fallback/failover/retry/channel_chain 相关代码"


def check_historical_backfill(_repo: Path) -> tuple[bool, str]:
    """BLIND-L09-HISTORICAL-BACKFILL: D_RESEARCH 是否有历史回填逻辑"""
    research = _repo / "src" / "zephyr" / "research"
    if not research.exists():
        return False, "D_RESEARCH 目录不存在"

    backfill_names = ["backfill", "historical", "replay", "historical_data"]
    for py_file in research.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for keyword in backfill_names:
            if keyword in content.lower():
                return True, f"历史回填代码已存在于 {py_file.relative_to(_repo)}"
    return False, "D_RESEARCH 中未发现 backfill/historical/replay 相关代码"


def check_base_event_in_all(_repo: Path) -> tuple[bool, str]:
    """BLIND-D-BASE-EVENT-MISSING: BaseEvent 是否在 shared/contracts/__all__ 中"""
    init_file = _repo / "src" / "zephyr" / "shared" / "contracts" / "__init__.py"
    if not init_file.exists():
        return False, "shared/contracts/__init__.py 不存在"

    try:
        content = init_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False, "无法读取 __init__.py"

    has_in_all = bool(re.search(r"__all__\s*=\s*\[.*\bBaseEvent\b", content, re.DOTALL))
    has_in_all_single = '"BaseEvent"' in content or "'BaseEvent'" in content

    if has_in_all or has_in_all_single:
        return True, "BaseEvent 已在 __all__ 中"
    return False, "BaseEvent 未在 __all__ 列表中"


def check_codegen_snapshot(_repo: Path) -> tuple[bool, str]:
    """BLIND-D-CODEGEN-SNAPSHOT-STALE: codegen snapshot SHA 是否与生成文件匹配"""
    snapshot_file = _repo / "src" / "zephyr" / "shared" / "contracts" / "_codegen_snapshot.txt"
    if not snapshot_file.exists():
        return False, "_codegen_snapshot.txt 不存在"

    try:
        content = snapshot_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False, "无法读取 snapshot"

    contract_dir = _repo / "src" / "zephyr" / "shared" / "contracts"
    py_files = sorted(contract_dir.glob("*.py"))
    if not py_files:
        return False, "contracts 目录无 .py 文件"

    sha = hashlib.sha256()
    for pf in py_files:
        sha.update(pf.read_bytes())
    current_hash = sha.hexdigest()

    if current_hash in content:
        return True, f"Snapshot SHA 与当前 {len(py_files)} 文件匹配: {current_hash[:16]}..."
    return False, f"Snapshot SHA 不匹配，需要重新校准（当前: {current_hash[:16]}...）"


def check_b_shadow(_repo: Path) -> tuple[bool, str]:
    """B-SHADOW: D_PORTFOLIO_CORE/D_EXECUTION_CORE skeleton base 文件是否被 codegen 覆盖"""
    files_to_check = [
        "src/zephyr/pf_core/strategy_base.py",
        "src/zephyr/ex_core/broker_interface.py",
    ]
    missing = []
    for f in files_to_check:
        fp = _repo / f
        if not fp.exists():
            missing.append(f)
            continue
        content = fp.read_text(encoding="utf-8", errors="replace")
        if "Shadow" not in content and "SHADOW" not in content:
            continue
    if missing:
        return False, f"缺失文件: {', '.join(missing)}"
    return True, "D_PORTFOLIO_CORE strategy_base.py 和 D_EXECUTION_CORE broker_interface.py 均存在"


# -- Blind Spot ID -> Check Function Mapping ---------------------------

BLIND_CHECK_MAP: dict[str, CheckFn] = {
    "B-SHADOW": check_b_shadow,
    "BLIND-L04-MISSING-VAR": check_var_cvar,
    "BLIND-L08-CHANNEL-FALLBACK": check_channel_fallback,
    "BLIND-D-BASE-EVENT-MISSING": check_base_event_in_all,
    "BLIND-D-CODEGEN-SNAPSHOT-STALE": check_codegen_snapshot,
}


# -- GATE-BS Entry Point -----------------------------------------------


def run_gate_bs(repo_root: Path | None = None) -> tuple[bool, list[str]]:
    """
    GATE-BS: 盲点现实对账。
    返回 (passed, errors)：
      - passed=True 表示所有 open 盲点都是真实的待办
      - passed=False 表示有 "已解决但忘改状态" 的盲点
    """
    if repo_root is None:
        repo_root = Path(os.getcwd())

    index_path = repo_root / "session_logs" / "index.yaml"
    if not index_path.exists():
        return False, [f"session_logs/index.yaml 不存在: {index_path}"]

    open_spots = load_open_blind_spots(index_path)
    if not open_spots:
        return True, []

    unresolved_issues: list[str] = []
    false_opens: list[str] = []
    no_check: list[str] = []

    for spot in open_spots:
        bid = spot.get("blind_spot_id", "?")
        desc = spot.get("description", "无描述")[:80]
        check_fn = BLIND_CHECK_MAP.get(bid)

        if check_fn is None:
            no_check.append(f"{bid}: 无自动化校验函数 → 需人工确认 ({desc})")
            continue

        resolved, detail = check_fn(repo_root)
        if resolved:
            false_opens.append(f"{bid}: 代码已解决但 status=open → {detail}")
        else:
            unresolved_issues.append(f"{bid}: 确认为真实待办 → {detail}")

    lines: list[str] = []

    if false_opens:
        lines.append(f"WARN: {len(false_opens)} 个盲点已解决但忘改状态（需手动 resolve）:")
        for fo in false_opens:
            lines.append(f"   - {fo}")

    if unresolved_issues:
        lines.append(f"INFO: {len(unresolved_issues)} 个盲点确认为真实待办:")
        for ui in unresolved_issues:
            lines.append(f"   - {ui}")

    if no_check:
        lines.append(f"UNKNOWN: {len(no_check)} 个盲点无自动化校验:")
        for nc in no_check:
            lines.append(f"   - {nc}")

    if not lines:
        lines.append("PASS: 无 open 盲点")

    passed = len(false_opens) == 0 and len(no_check) == 0
    return passed, lines


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    repo = Path(__file__).resolve().parent.parent.parent.parent
    passed, lines = run_gate_bs(repo)
    print("\n".join(lines))
    sys.exit(EXIT_PASS if passed else EXIT_FINDINGS)


if __name__ == "__main__":
    main()
