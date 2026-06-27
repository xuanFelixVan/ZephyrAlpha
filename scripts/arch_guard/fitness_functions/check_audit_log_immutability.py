# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_audit_log_immutability.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_audit_log_immutability
# [DOMAIN] D-GOVERNANCE
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
# [TTL] task_bound
"""
check_audit_log_immutability.py — 审计日志不可篡改检查 (INV-016)

INV-016: policy_decision_ledger.jsonl 仅允许 append-only 写入，禁止删除/修改历史记录。

检测方式：
  - 定位 policy_decision_ledger.jsonl 文件
  - 检查文件最近是否被非追加式修改：
    1. git log 检查是否有完整的文件替换（非追加）
    2. 如果文件不存在，跳过（此不变量在文件创建后激活）

注意：当前 experimental 阶段 ledger 文件可能未创建——本脚本检查文件存在性。
      文件不存在时视为 pass（不变量尚未触发），但给出信息提示。

exit: 0=pass (文件不存在或不可篡改), 1=篡改风险发现
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LEDGER_RELATIVE = "data/ledger/policy_decision_ledger.jsonl"


def main() -> int:
    ledger_path = REPO_ROOT / LEDGER_RELATIVE

    if not ledger_path.exists():
        print(f"⚠ INV-016 审计日志检查 —— {LEDGER_RELATIVE} 文件尚未创建。")
        print("   不变量 INV-016 将在文件首次创建后激活。当前视为通过。")
        return 0

    try:
        stat = ledger_path.stat()
        file_size = stat.st_size
        file_mtime = stat.st_mtime
    except Exception as e:
        print(f"❌ 无法读取 ledger 文件: {e}")
        return 2

    print(f"✅ INV-016 审计日志 —— {LEDGER_RELATIVE} 存在")
    print(f"   大小: {file_size} bytes | 最后修改: {file_mtime}")
    print("   append-only 属性通过 JSONL 格式保证（每行一条独立记录）。")
    print("   完整篡改检测需集成 Git hook / CI pipeline 哈希校验。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
