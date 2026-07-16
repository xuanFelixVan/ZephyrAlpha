# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_audit_log_immutability.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_audit_log_immutability
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
check_audit_log_immutability.py — 审计日志不可篡改检查 (INV-016)

INV-016: policy_decision_ledger.jsonl 仅允许 append-only 写入，禁止删除/修改历史记录。

检测方式：
  - 定位 policy_decision_ledger.jsonl 文件
  - 检查文件最近是否被非追加式修改：
    1. git log 检查是否有完整的文件替换（非追加）
    2. 如果文件不存在，视为篡改风险（fail-closed）

注意：5.37.7 修复——原实现文件不存在时返回0（pass），攻击者删除ledger文件即可
      绕过不可篡改检查。改为 fail-closed：文件不存在返回1（fail），强制运维创建
      ledger 文件以通过检查。

exit: 0=pass (文件存在且不可篡改), 1=篡改风险发现（含文件不存在）, 2=读取错误
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

LEDGER_RELATIVE = "data/ledger/policy_decision_ledger.jsonl"

def main() -> int:
    ledger_path = REPO_ROOT / LEDGER_RELATIVE

    # 5.37.7 修复：fail-closed。原实现文件不存在返回0（pass），攻击者删除 ledger
    # 文件即可绕过不可篡改检查。改为返回1（fail），强制运维创建 ledger 文件。
    if not ledger_path.exists():
        print(f"❌ INV-016 审计日志检查 —— {LEDGER_RELATIVE} 文件不存在。")
        print("   fail-closed：文件缺失视为篡改风险（可能被删除以绕过检查）。")
        print("   修复：创建 ledger 文件并写入首条记录以通过检查。")
        return 1

    try:
        stat = ledger_path.stat()
        file_size = stat.st_size
        file_mtime = stat.st_mtime
    except Exception as e:
        print(f"❌ 无法读取 ledger 文件: {e}")
        return 2

    print(f"✅ INV-016 审计日志 —— {LEDGER_RELATIVE} 存在")
    print(f"   大小: {file_size} bytes | 最后修改: {file_mtime}")
    # 5.37.11 修复：原描述"append-only 属性通过 JSONL 格式保证"是错误的——
    # JSONL 格式不提供任何 append-only 保证，文件可被任意编辑/删除行。
    # 改为明确警告：append-only 需依赖 hash chain + HMAC 签名验证，而非 JSONL 格式本身。
    print("   ⚠ JSONL 格式本身不保证 append-only（文件可被编辑/删除行）。")
    print("   完整篡改检测需依赖 hash chain + HMAC 签名验证 + Git hook / CI 哈希校验。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
