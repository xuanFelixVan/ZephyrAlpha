# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_acl_boundary.py | §
# [MODULE] scripts.arch_guard.check_acl_boundary
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.__init__
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
check_acl_boundary.py — Broker ACL 边界强制执行 (INV-005)

INV-005: 只有 ex_core/adapters/ 可调用 Broker API，其他层禁止直接访问。

检测方式：
  - 扫描 src/zephyr/ 下所有 .py 文件
  - 搜索 Broker API 相关 import/call 模式
  - 排除 ex_core/adapters/ 目录、broker_interface.py 与 l06/__init__.py（公开重导出，无 SDK）

Broker API 特征模式（匹配以下任一即标记）：
  - from .*broker.* import ...
  - import .*broker.*
  - broker_submit_order / broker_place_order / broker_execute
  - 直接 import ib_insync / futu / longport SDK

exit: 0=pass, 1=violation found
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

SRC_ROOT = REPO_ROOT / "src" / "zephyr"
EX_CORE_ROOT = SRC_ROOT / "ex_core"
# INV-005：仅 adapters/ 可直接触达券商 SDK；OCP 接口定义文件不含 SDK 调用，免检
ADAPTERS_DIR = EX_CORE_ROOT / "adapters"
EX_CORE_SDK_EXEMPT_FILES = frozenset(
    {
        EX_CORE_ROOT / "broker_interface.py",
        EX_CORE_ROOT / "__init__.py",
    }
)

BROKER_PATTERNS = [
    (re.compile(r"from\s+.*broker.*\s+import", re.IGNORECASE), "broker 模块 import"),
    (re.compile(r"import\s+.*broker", re.IGNORECASE), "broker 模块 import"),
    (re.compile(r"ib_insync", re.IGNORECASE), "IB 券商 SDK 直接引用"),
    (re.compile(r"from\s+futu\s+import", re.IGNORECASE), "富途 SDK 直接引用"),
    (re.compile(r"import\s+futu", re.IGNORECASE), "富途 SDK 直接引用"),
    (re.compile(r"from\s+longport", re.IGNORECASE), "LongPort SDK 直接引用"),
    (re.compile(r"longbridge", re.IGNORECASE), "LongBridge SDK 直接引用"),
    (
        re.compile(r"broker_submit_order|broker_place_order|broker_execute|submit_to_broker", re.IGNORECASE),
        "Broker 下单调用",
    ),
    (
        re.compile(r"BrokerInterface|BrokerAdapter|BaseBroker", re.IGNORECASE),
        "Broker 接口直接引用（应只通过 adapters/ 使用）",
    ),
]

EXCLUDE_DIRS = {"__pycache__", ".git", "tests", "shared", "gates", "mcp", "pipeline"}

def is_allowed(file_path: Path) -> bool:
    resolved = file_path.resolve()
    if resolved in {p.resolve() for p in EX_CORE_SDK_EXEMPT_FILES}:
        return True
    try:
        resolved.relative_to(ADAPTERS_DIR.resolve())
        return True
    except ValueError:
        return False

def check_file(file_path: Path) -> list[str]:
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for pattern, description in BROKER_PATTERNS:
            if pattern.search(stripped):
                violations.append(f'  {file_path.relative_to(REPO_ROOT)}:{i}: {description} — "{stripped[:120]}"')
                break
    return violations

def main() -> int:
    if not SRC_ROOT.exists():
        print("src/zephyr/ 目录不存在")
        return 2

    all_violations: list[str] = []
    for py_file in SRC_ROOT.rglob("*.py"):
        if any(excl in py_file.parts for excl in EXCLUDE_DIRS):
            continue
        if is_allowed(py_file):
            continue
        violations = check_file(py_file)
        all_violations.extend(violations)

    if all_violations:
        print(f"[FAIL] INV-005 Broker ACL 边界违反 ({len(all_violations)} 处):")
        for v in all_violations:
            print(v)
        print()
        print(f"只有 {ADAPTERS_DIR.relative_to(REPO_ROOT)}/ 下的代码允许调用 Broker API。")
        print("其他层必须通过 D_EXECUTION_CORE adapters/ 间接访问。")
        return 1

    print("[OK] INV-005 Broker ACL 边界 —— 无违反")
    print(f"   已扫描 src/zephyr/ 下所有 .py 文件，Broker API 调用均位于 {ADAPTERS_DIR.relative_to(REPO_ROOT)}/。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
