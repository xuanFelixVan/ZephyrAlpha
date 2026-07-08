# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] scripts.governance.generators.check_gate_inventory_drift
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.governance.audit.reconciliation_registry.make_gate_inventory_sync_reconciler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 真源=commit_gates/*.py 文件存在性；blueprint.md §0.1 是派生视图；漂移=exit 1
# [MODIFY-GUARD] 检测逻辑变更需同步 blueprint.md §0.1 解析正则
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=一致 / exit 1=漂移（stdout 含缺失/多余列表）/ exit 2=错误
# [TESTS] tests/governance/generators/test_check_gate_inventory_drift.py
# [A_module] module_id=MOD-GOV-check_gate_inventory_drift | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-055]
"""check_gate_inventory_drift.py — commit_gates 模块清单漂移检测（ARCH-055 治本）

检测 src/zephyr/governance/commit_gates/*.py 实际文件与
docs/03_modules/_cross_layer/gate_engine/blueprint.md §0.1 模块清单表格的一致性。

病根（ARCH-055）：blueprint.md §0.1 模块清单靠手工维护，100% AI 开发模式下
新增 gate 后 AI 不会自觉同步文档，导致漂移（截至 2026-07-09 漂移 6/29=20.7%）。
本脚本提供"代码→文档"正向检测（现有 GATE-AGENTS-MD-REFS 是反向检测：
文档引用→代码存在性）。

Usage:
    python scripts/governance/generators/check_gate_inventory_drift.py
    python scripts/governance/generators/check_gate_inventory_drift.py --check

Exit codes:
    0 = 一致（无漂移）
    1 = 漂移（stdout 含 missing/extra 列表）
    2 = 错误（脚本异常）
"""

from __future__ import annotations

import re
import sys

from zephyr.shared.io.paths import REPO_ROOT

GATES_DIR = REPO_ROOT / "src" / "zephyr" / "governance" / "commit_gates"
BLUEPRINT_PATH = (
    REPO_ROOT / "docs" / "03_modules" / "_cross_layer" / "gate_engine" / "blueprint.md"
)

# 匹配 blueprint.md §0.1 表格中的 commit_gates/xxx.py 条目
_RE_BP_GATE_ENTRY = re.compile(r"commit_gates/(\w+\.py)")


def scan_actual_gates() -> set[str]:
    """扫描 commit_gates 目录实际 .py 文件（排除 __init__.py）。"""
    if not GATES_DIR.is_dir():
        return set()
    return {f.name for f in GATES_DIR.glob("*.py") if f.name != "__init__.py"}


def scan_blueprint_listed() -> set[str]:
    """解析 blueprint.md §0.1 表格中列举的 commit_gates/*.py 文件名。"""
    if not BLUEPRINT_PATH.is_file():
        return set()
    text = BLUEPRINT_PATH.read_text(encoding="utf-8", errors="replace")
    return set(_RE_BP_GATE_ENTRY.findall(text))


def detect_drift() -> tuple[list[str], list[str]]:
    """检测漂移，返回 (missing_in_blueprint, extra_in_blueprint)。

    - missing_in_blueprint: 代码有但 blueprint.md §0.1 没登记的文件
    - extra_in_blueprint: blueprint.md §0.1 登记但代码已删除的文件
    """
    actual = scan_actual_gates()
    listed = scan_blueprint_listed()
    missing = sorted(actual - listed)
    extra = sorted(listed - actual)
    return missing, extra


def main() -> int:
    try:
        missing, extra = detect_drift()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    actual = scan_actual_gates()
    if not missing and not extra:
        print(f"OK: commit_gates inventory in sync ({len(actual)} gates)")
        return 0

    listed = scan_blueprint_listed()
    print(
        f"DRIFT: commit_gates inventory mismatch "
        f"(actual={len(actual)} listed={len(listed)})"
    )
    if missing:
        print(f"  MISSING in blueprint.md §0.1 ({len(missing)}):")
        for f in missing:
            print(f"    - commit_gates/{f}")
        bp_rel = BLUEPRINT_PATH.relative_to(REPO_ROOT).as_posix()
        print(f"  → 补齐: 在 {bp_rel} §0.1 表格添加上述文件行")
    if extra:
        print(f"  EXTRA in blueprint.md §0.1 ({len(extra)}):")
        for f in extra:
            print(f"    - commit_gates/{f}")
        bp_rel = BLUEPRINT_PATH.relative_to(REPO_ROOT).as_posix()
        print(f"  → 清理: 从 {bp_rel} §0.1 表格移除上述文件行")
    return 1


if __name__ == "__main__":
    sys.exit(main())
