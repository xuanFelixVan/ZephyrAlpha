# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/check_ssot_gate.py | §ssot_gate
# [MODULE] scripts.governance.check_ssot_gate
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.capability_lookup
# [CONSUMERS] pre-commit GATE-SSOT hook; GitCommitGateway._check_ssot_canonical（主防线）
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 真源是文件头部 [MODULE] 字段；fail-open（capability_lookup 不可用时放行）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS, exit 1=BLOCK, exit 2=ERROR
# [TESTS] tests/test_ssot_gate.py
# [TTL] permanent
"""GATE-SSOT: SSoT 创建门禁（pre-commit hook 双保险）。

检测 staged 新增 .py 文件是否违反 SSoT（四层硬阻断）：
  硬层 1（check_ssot_conflicts）：同 module_path 硬碰撞——[MODULE] 头字段精确匹配。
  硬层 2（check_capability_duplicates）：basename 撞 capability_id/alias →
    conflicting/sibling duplicate（同能力多实现，B 方案：所有信号皆阻断）。
  硬层 3（check_module_id_conflicts）：同 module_id 多文件——[A_module] 全局唯一
    （P0-2 防再生：阻断 AI 跨域复刻后忘记改 module_id）。
  硬层 4（check_module_domain_consistency）：[MODULE] 声明域 ≠ 物理路径域
    （P0-3 防再生：阻断 AI 跨域复刻后忘记改 module_path）。

真源是文件头部 [MODULE]/[A_module] 字段 + capability_lookup 派生的 duplicates 状态，
反查通过 capability_lookup 实时扫描磁盘。

L2/L3 共享检测逻辑（治本 2a）：检测核心收拢到 capability_lookup 的
check_ssot_conflicts / check_capability_duplicates / check_module_id_conflicts /
check_module_domain_consistency，本脚本只负责获取 staged
新增 .py 和格式化输出。B 方案去掉软层 advisory（软层 TP≈0 且 advisory 不阻断
=死数据），L2/L3 行为一致——所有 check_capability_duplicates 返回的信号皆阻断。

GitCommitGateway.commit() 内嵌的 _check_ssot_canonical 是主防线
（GitCommitGateway 用 --no-verify 绕过 pre-commit）。
本脚本是双保险——当有人不用 GitCommitGateway 而是直接 git commit 时拦截。

已知边界:
    git commit --no-verify 能绕过本 hook（git 固有设计，无法技术阻止）。
    依赖 GATE-COMMIT-GW 规则约束（全项目 git commit 必须经 GitCommitGateway）。
    L2 GitCommitGateway._check_ssot_canonical 是主防线——即使用 --no-verify 绕过
    pre-commit，gateway 内嵌检测逻辑仍生效（但绕过 gateway 直接 git commit 则无保护）。

Exit codes:
    0 = PASS（无冲突或无新增 .py 文件）
    1 = BLOCK（检测到 module_path 冲突 / 能力重复 / module_id 冲突 / 域不一致）
    2 = ERROR（脚本异常）
"""
from __future__ import annotations

__manifest__ = """
args: []
description: 'GATE-SSOT: SSoT 创建门禁（pre-commit hook 双保险）。'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.capability_lookup import CapabilityLookup  # noqa: E402
# 治本(2026-06-30): REPO_ROOT 真源来自 zephyr.shared.io.paths (SSoT), 消除路径派生对 parents[N] 的依赖
from zephyr.shared.io.paths import REPO_ROOT as _REPO_ROOT  # noqa: E402


def main() -> int:
    # 获取 staged 新增的 .py 文件（diff-filter=A 只看新增）
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )
    if result.returncode != 0:
        print(f"GATE-SSOT: git diff 失败: {result.stderr}", file=sys.stderr)
        return 2

    new_files = [
        f.strip() for f in result.stdout.strip().split("\n")
        if f.strip().startswith("src/zephyr/") and f.strip().endswith(".py")
    ]

    if not new_files:
        return 0  # 无新增 .py 文件，放行

    try:
        lookup = CapabilityLookup()
    except Exception as e:
        # fail-open：capability_lookup 不可用时不阻断
        # GitCommitGateway 内嵌门禁是主防线
        print(f"GATE-SSOT: capability_lookup 不可用，跳过: {e}", file=sys.stderr)
        return 0

    # 构造 (abs_path, rel_path) 列表——L3 特有：跳过已从磁盘删除的 staged 文件
    new_py_files: list[tuple[str, str]] = []
    for rel_path in new_files:
        abs_path = _REPO_ROOT / rel_path
        if not abs_path.exists():
            continue
        new_py_files.append((str(abs_path), rel_path))

    # 检测逻辑调用共享函数（唯一真源：capability_lookup.check_ssot_conflicts）
    # L3 只负责获取 staged 新增 .py（上方 git diff）和格式化输出（下方），
    # 检测核心（解析头 + 反查 + 排除自己）收拢到 check_ssot_conflicts，L2 共用。
    conflicts = lookup.check_ssot_conflicts(new_py_files)
    if conflicts:
        print("GATE-SSOT: SSoT 冲突——新增文件声明了已有 module_path:", file=sys.stderr)
        for c in conflicts:
            print(
                f"  {c.rel_path} 声明 module_path={c.module_path}"
                f" 与已有文件冲突: {', '.join(c.conflicts)}",
                file=sys.stderr,
            )
        print("  修复指令：删除上述新增文件，扩展对应的已有文件后重新 commit（RULE-EIGHT 扩展优先于新建）", file=sys.stderr)
        print("  查已有 canonical：python -m zephyr.governance.capability_lookup --find <关键词>", file=sys.stderr)
        return 1

    # 硬层 2：能力重复（basename 撞 capability_id/alias → duplicate）
    # 治本（2a 共享方法）：检测逻辑唯一真源收拢到
    # capability_lookup.check_capability_duplicates，L2 gateway 已调用同一方法。
    # B 方案：所有信号皆阻断（去掉软层 advisory），L3 与 L2 行为一致。
    dups = lookup.check_capability_duplicates(new_py_files)
    if dups:
        from zephyr.governance.capability_lookup import CAPABILITY_DUPLICATE_FIX_HINT
        print("GATE-SSOT: 能力重复——新增文件与已有能力构成同能力多实现:", file=sys.stderr)
        for d in dups:
            print(f"  {d.rel_path}: {d.detail}", file=sys.stderr)
        print(f"  {CAPABILITY_DUPLICATE_FIX_HINT}", file=sys.stderr)
        return 1

    # 硬层 3：module_id 全局唯一（P0-2 防再生门禁）
    id_conflicts = lookup.check_module_id_conflicts(new_py_files)
    if id_conflicts:
        print("GATE-SSOT: module_id 冲突——新增文件声明的 module_id 已被其他文件占用:", file=sys.stderr)
        for c in id_conflicts:
            print(
                f"  {c.rel_path} 声明 module_id={c.module_id}"
                f" 与已有文件冲突: {', '.join(c.conflicts)}",
                file=sys.stderr,
            )
        print("  修复指令：为新增文件分配新的 module_id，或删除新增文件复用已有文件", file=sys.stderr)
        return 1

    # 硬层 4：MODULE 声明域与物理路径域一致（P0-3 防再生门禁）
    domain_mismatches = lookup.check_module_domain_consistency(new_py_files)
    if domain_mismatches:
        print("GATE-SSOT: 域不一致——[MODULE] 声明域与物理路径域不符（疑似跨域复刻）:", file=sys.stderr)
        for m in domain_mismatches:
            print(
                f"  {m.rel_path} 物理在 {m.physical_domain}/ 但 [MODULE] 声明"
                f" {m.module_path}（声明域={m.declared_domain}）",
                file=sys.stderr,
            )
        print("  修复指令：修正 [MODULE] module_path 使其与物理路径一致，或将文件移到正确域", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
