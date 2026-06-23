# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/import_linter/layer_boundary_check.py | §
# [MODULE] scripts.arch_guard.import_linter.layer_boundary_check
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.import_linter.__init__
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
"""
layer_boundary_check.py — 层依赖方向强制执行 (INV-008)

INV-008: 跨层依赖方向——低层不得 import 高层（L00 不得 import L04+），依赖只能向上。

检测方式：
  - 扫描 src/zephyr/ 下所有 .py 文件的 import 语句
  - 解析 from zephyr.lNN_xxx import ... 格式的跨层引用
  - 提取层号，检查低层是否引用了高层：
    例：L02 (alpha factor) import L05 (portfolio construction) → 违规
    L00 < L02 < L03 < L04 < L05 < L06 < L07 < ... < L13
  - 合法的跨层引用：shared/ 基础设施层（被所有层共享）
  - 排除：tests/, docs/, __pycache__/

exit: 0=pass, 1=violation found
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src" / "zephyr"

LAYER_IMPORT_RE = re.compile(
    r"from\s+zephyr\.(l\d{2})_"
    r"|import\s+zephyr\.(l\d{2})_"
    r"|from\s+zephyr\.shared\s+import"
    r"|import\s+zephyr\.shared",
)

LAYER_NUM_RE = re.compile(r"l(\d{2})")

SHARED_MODULES = {
    "shared",
    "gates",
    "core",
    "db",
    "kb",
    "orchestrator",
    "pipeline",
    "mcp",
    "feedback-loop",
    "vector-memory",
    "llm-security",
    "context-engine",
}

EXCLUDE_DIRS = {"__pycache__", ".git", "tests", "docs", "shared", "gates"}


def extract_layer_number(dir_name: str) -> int | None:
    m = LAYER_NUM_RE.match(dir_name)
    if m:
        return int(m.group(1))
    return None


def check_file(file_path: Path, source_layer: int) -> list[str]:
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        for match in LAYER_NUM_RE.finditer(stripped):
            target_layer = int(match.group(1))
            if source_layer < target_layer:
                violations.append(
                    f"  {file_path.relative_to(REPO_ROOT)}:{i}: "
                    f"L{source_layer:02d} → L{target_layer:02d}（低层引用高层） "
                    f'— "{stripped[:100]}"'
                )
                break
    return violations


def main() -> int:
    if not SRC_ROOT.exists():
        print("src/zephyr/ 目录不存在")
        return 2

    all_violations: list[str] = []
    checked = 0

    for src_file in SRC_ROOT.rglob("*.py"):
        if any(excl in src_file.parts for excl in EXCLUDE_DIRS):
            continue

        source_dir = None
        for part in src_file.parts:
            if part.startswith("l") and LAYER_NUM_RE.match(part):
                source_dir = part
                break

        if source_dir is None:
            continue

        source_layer = extract_layer_number(source_dir)
        if source_layer is None:
            continue

        checked += 1
        violations = check_file(src_file, source_layer)
        all_violations.extend(violations)

    if all_violations:
        print(f"❌ INV-008 层依赖方向违反 ({len(all_violations)} 处):")
        for v in all_violations:
            print(v)
        print()
        print("14 层架构核心约束：低层不得 import 高层，依赖只能向上。")
        print("合法路径：通过 shared/contracts/ 契约间接依赖。")
        return 1

    print(f"✅ INV-008 层依赖方向 —— 无违反（已检查 {checked} 个层文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
