# [BLUEPRINT] MOD-GOV-059 | scripts/governance/gateway_post_commit_ritual.py | §
# [MODULE] scripts.governance.gateway_post_commit_ritual
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.constants (EXIT_*/REPO_ROOT)
# [CONSUMERS] .pre-commit-config.yaml gateway-post-commit-ritual（post-commit 阶段）；手动批次收尾
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 未触碰 rules/contracts 特征路径时不执行任何写入；三步联动任一失败整体回滚已写产物；只写派生物（契约代码/快照/integrity DB），不改手写文件
# [MODIFY-GUARD] 联动链/特征路径变更须同步 tests/governance/test_gateway_post_commit_ritual.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=无需收尾或收尾成功 / 1=批次触碰特征路径但联动失败（已回滚）/ 2=脚本自身错误；--warn-only 恒 0
# [TESTS] tests/governance/test_gateway_post_commit_ritual.py
# [A_module] module_id=MOD-GOV-059 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""gateway_post_commit_ritual.py — 网关批次收尾仪式联动（CAND-GATEMECH-005）。

病根（#ARCH-130 实证）：ruff/codegen 批量批落码后，契约快照与 rules_integrity_db
黄金哈希不会自动跟进——C2 契约漂移与 INTEGRITY 赛跑双双滞留到下一审计周期才暴露，
批次施工者需手工记得跑 generate_contracts.py + --freeze + --register，无机制约束。

本仪式（post-commit 事件驱动）：
  1. 检测本批次是否触碰 rules/contracts 特征路径（git show HEAD 或 --files 传入）
  2. 触碰 contracts → 执行 generate_contracts.py → check_contract_code_drift.py --freeze
  3. 触碰 rules 或 contracts → 执行 validate_rules_integrity.py --register
     （ZEPHYR_RECONCILER_MODE=1 门禁令牌：本仪式即 reconciler 等价 post-commit 上下文）

三步原子联动：任一步失败 → 回滚本仪式已写入的全部派生产物（恢复执行前字节快照）
→ 整体报告失败。未触碰特征路径 → 零写入零输出噪音，恒 exit 0。

Usage:
    python scripts/governance/gateway_post_commit_ritual.py            # 检测 HEAD commit
    python scripts/governance/gateway_post_commit_ritual.py --files a.py b.yaml
    python scripts/governance/gateway_post_commit_ritual.py --check    # 只检测不执行
    python scripts/governance/gateway_post_commit_ritual.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 网关批次收尾仪式——批次触碰 rules/contracts 自动联动 C2 freeze + INTEGRITY 重钉（CAND-GATEMECH-005）
dimensions:
- D11
priority: P1
timeout_seconds: 120
warn_only: false
"""

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402

__all__: Final = ["RitualResult", "detect_batch_signals", "run_ritual", "main"]

# rules/contracts 特征路径（批次触碰即触发收尾仪式）
_CONTRACT_PREFIXES: Final = (
    "architecture_model/contracts/",
    "src/zephyr/shared/contracts/",
)
_RULES_PREFIXES: Final = (
    "docs/01_policies_and_standards/rules/",
    "scripts/governance/_shared/thresholds.yaml",
    "scripts/governance/meta/",
    "scripts/governance/quickstart.md",
    "scripts/governance/quality_standard.md",
    "AGENTS.md",
)

_GENERATE_CONTRACTS: Final = "scripts/governance/d5_architecture/generators/generate_contracts.py"
_CONTRACT_FREEZE: Final = "scripts/governance/d5_architecture/checkers/check_contract_code_drift.py"
_INTEGRITY_REGISTER: Final = "scripts/governance/meta/validate_rules_integrity.py"


def _step_timeout() -> int:
    """单步超时（秒），从 thresholds.yaml gateway_ritual.step_timeout_seconds 读取。"""
    from _shared.thresholds import get as _get_threshold

    return int(_get_threshold("gateway_ritual.step_timeout_seconds", 300))


@dataclass
class RitualResult:
    """收尾仪式执行结果。"""

    triggered: bool
    steps: list[tuple[str, int]] = field(default_factory=list)  # (步骤名, exit_code)
    rolled_back: bool = False

    @property
    def ok(self) -> bool:
        return all(rc == 0 for _, rc in self.steps)


def detect_batch_signals(files: list[str]) -> tuple[bool, bool]:
    """检测批次是否触碰特征路径。返回 (touched_contracts, touched_rules)。"""
    normalized = [f.replace("\\", "/") for f in files]
    touched_contracts = any(f.startswith(_CONTRACT_PREFIXES) for f in normalized)
    touched_rules = any(f.startswith(_RULES_PREFIXES) for f in normalized)
    return touched_contracts, touched_rules


def _head_commit_files(root: Path) -> list[str]:
    """取 HEAD commit 变更文件清单。git 失败返回空（不触发仪式）。"""
    result = run_subprocess_hidden(
        ["git", "show", "--name-only", "--format=", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(root),
        timeout=30,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _backup_outputs(root: Path) -> dict[Path, bytes | None]:
    """备份仪式将写入的派生产物（字节快照；None=执行前不存在，回滚时删除）。"""
    contracts_dir = root / "src" / "zephyr" / "shared" / "contracts"
    targets: list[Path] = []
    if contracts_dir.is_dir():
        targets.extend(sorted(contracts_dir.glob("*.py")))
        targets.append(contracts_dir / "_codegen_snapshot.txt")
    targets.append(root / "scripts" / "governance" / "meta" / "rules_integrity_db.json")
    backup: dict[Path, bytes | None] = {}
    for path in targets:
        try:
            backup[path] = path.read_bytes() if path.exists() else None
        except OSError:
            backup[path] = None
    return backup


def _restore_outputs(root: Path, backup: dict[Path, bytes | None]) -> None:
    """回滚：恢复执行前字节快照；仪式新建的文件（不在备份键中）删除。"""
    known = set(backup)
    contracts_dir = root / "src" / "zephyr" / "shared" / "contracts"
    current: set[Path] = set()
    if contracts_dir.is_dir():
        current |= set(contracts_dir.glob("*.py"))
        current.add(contracts_dir / "_codegen_snapshot.txt")
    for path in current - known:
        try:
            path.unlink()
        except OSError:
            pass
    for path, data in backup.items():
        try:
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_bytes(data)
        except OSError:
            pass


def _run_step(cmd: list[str], root: Path, env: dict[str, str]) -> int:
    """执行单步，返回 exit code。启动异常返回 EXIT_ERROR。"""
    try:
        result = run_subprocess_hidden(cmd, cwd=str(root), env=env, timeout=_step_timeout(), capture_output=False)
    except (OSError, subprocess.TimeoutExpired):
        return EXIT_ERROR
    return result.returncode


def run_ritual(root: Path, files: list[str], check_only: bool = False) -> RitualResult:
    """检测批次信号并执行三步原子联动（任一失败整体回滚派生产物）。"""
    touched_contracts, touched_rules = detect_batch_signals(files)
    if not touched_contracts and not touched_rules:
        return RitualResult(triggered=False)
    if check_only:
        return RitualResult(triggered=True)

    backup = _backup_outputs(root)
    env = dict(os.environ)
    env["ZEPHYR_RECONCILER_MODE"] = "1"  # post-commit 仪式 = reconciler 等价上下文
    result = RitualResult(triggered=True)

    plan: list[tuple[str, list[str]]] = []
    if touched_contracts:
        plan.append(("generate_contracts", [sys.executable, _GENERATE_CONTRACTS]))
        plan.append(("contract_freeze", [sys.executable, _CONTRACT_FREEZE, "--freeze"]))
    plan.append(("integrity_register", [sys.executable, _INTEGRITY_REGISTER, "--register"]))

    for name, cmd in plan:
        rc = _run_step(cmd, root, env)
        result.steps.append((name, rc))
        if rc != 0:
            _restore_outputs(root, backup)
            result.rolled_back = True
            break
    return result


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="网关批次收尾仪式（CAND-GATEMECH-005）")
    parser.add_argument("--files", nargs="*", default=None, help="批次文件清单（缺省取 HEAD commit）")
    parser.add_argument("--check", action="store_true", help="只检测是否触碰特征路径，不执行联动")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    try:
        files = args.files if args.files is not None else _head_commit_files(REPO_ROOT)
        result = run_ritual(REPO_ROOT, files, check_only=args.check)
    except OSError as exc:
        print(f"[RITUAL] ERROR: 执行失败（{type(exc).__name__}）", file=sys.stderr)
        return EXIT_ERROR

    if not result.triggered:
        print("[RITUAL] 本批次未触碰 rules/contracts 特征路径，无需收尾", file=sys.stderr)
        return EXIT_PASS

    if args.check:
        print("[RITUAL] 批次触碰 rules/contracts 特征路径——需要收尾仪式", file=sys.stderr)
        return EXIT_FINDINGS

    for name, rc in result.steps:
        tag = "✅" if rc == 0 else "🔴"
        print(f"[RITUAL] {tag} {name} (exit={rc})", file=sys.stderr)

    if result.ok:
        print("[RITUAL] 收尾仪式完成（契约重生成 + 快照冻结 + INTEGRITY 重钉）", file=sys.stderr)
        return EXIT_PASS

    print(
        f"[RITUAL] 🔴 联动失败，已回滚派生产物（rolled_back={result.rolled_back}）。"
        "修复失败步骤后手动重跑本仪式，或手工执行 generate_contracts → --freeze → --register",
        file=sys.stderr,
    )
    return EXIT_PASS if args.warn_only else EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
