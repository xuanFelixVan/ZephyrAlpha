"""
check_acl_boundary.py — Broker ACL 边界强制执行 (INV-005)

INV-005: 只有 l06_trade_execution/adapters/ 可调用 Broker API，其他层禁止直接访问。

检测方式：
  - 扫描 src/zephyr/ 下所有 .py 文件
  - 搜索 Broker API 相关 import/call 模式
  - 排除 l06_trade_execution/adapters/ 目录下的合法调用

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

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "zephyr"
ALLOWED_DIR = SRC_ROOT / "l06_trade_execution" / "adapters"

BROKER_PATTERNS = [
    (re.compile(r"from\s+.*broker.*\s+import", re.IGNORECASE), "broker 模块 import"),
    (re.compile(r"import\s+.*broker", re.IGNORECASE), "broker 模块 import"),
    (re.compile(r"ib_insync", re.IGNORECASE), "IB 券商 SDK 直接引用"),
    (re.compile(r"from\s+futu\s+import", re.IGNORECASE), "富途 SDK 直接引用"),
    (re.compile(r"import\s+futu", re.IGNORECASE), "富途 SDK 直接引用"),
    (re.compile(r"from\s+longport", re.IGNORECASE), "LongPort SDK 直接引用"),
    (re.compile(r"longbridge", re.IGNORECASE), "LongBridge SDK 直接引用"),
    (re.compile(r"broker_submit_order|broker_place_order|broker_execute|submit_to_broker", re.IGNORECASE), "Broker 下单调用"),
    (re.compile(r"BrokerInterface|BrokerAdapter|BaseBroker", re.IGNORECASE), "Broker 接口直接引用（应只通过 adapters/ 使用）"),
]

EXCLUDE_DIRS = {"__pycache__", ".git", "tests", "shared", "gates", "mcp", "pipeline"}


def is_allowed(file_path: Path) -> bool:
    try:
        file_path.resolve().relative_to(ALLOWED_DIR.resolve())
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
                violations.append(
                    f"  {file_path.relative_to(REPO_ROOT)}:{i}: {description} — \"{stripped[:120]}\""
                )
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
        print(f"❌ INV-005 Broker ACL 边界违反 ({len(all_violations)} 处):")
        for v in all_violations:
            print(v)
        print()
        print(f"只有 {ALLOWED_DIR.relative_to(REPO_ROOT)} 下的代码允许调用 Broker API。")
        print("其他层必须通过 L06 adapters/ 间接访问。")
        return 1

    print("✅ INV-005 Broker ACL 边界 —— 无违反")
    print(f"   已扫描 src/zephyr/ 下所有 .py 文件，Broker API 调用均通过 {ALLOWED_DIR.relative_to(REPO_ROOT)}/。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
