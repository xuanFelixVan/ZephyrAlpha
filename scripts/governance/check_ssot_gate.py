# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/check_ssot_gate.py | §ssot_gate
# [MODULE] scripts.governance.check_ssot_gate
# [DOMAIN] D-GOVERNANCE
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
"""GATE-SSOT: SSoT 创建门禁（pre-commit hook 双保险）。

检测 staged 新增 .py 文件是否声明了已有 module_path。
真源是文件头部 [MODULE] 字段，反查通过 capability_lookup 实时扫描磁盘。

GitCommitGateway.commit() 内嵌的 _check_ssot_canonical 是主防线
（GitCommitGateway 用 --no-verify 绕过 pre-commit）。
本脚本是双保险——当有人不用 GitCommitGateway 而是直接 git commit 时拦截。

Exit codes:
    0 = PASS（无冲突或无新增 .py 文件）
    1 = BLOCK（检测到 module_path 冲突）
    2 = ERROR（脚本异常）
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.capability_lookup import CapabilityLookup  # noqa: E402


def main() -> int:
    # 获取 staged 新增的 .py 文件（diff-filter=A 只看新增）
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True,
        text=True,
        cwd=str(_PROJECT_ROOT),
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
        abs_path = _PROJECT_ROOT / rel_path
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
        print("  复用决策（RULE-EIGHT）：扩展已有文件而非新建。", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
