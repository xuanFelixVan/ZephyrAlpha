# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_importlinter.py | §
# [MODULE] scripts.governance.generators.generate_importlinter
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
generate_importlinter.py — .importlinter forbidden_modules 自动生成器

从 src/zephyr/ 顶层包扫描派生 .importlinter 的 [contracts].forbidden_modules 块。
对标 §6.3 静态清单自动生成铁律——手工维护的 forbidden_modules 必然与实际包结构漂移
（历史教训 2026-07-05：原配置引用 capacity_assurance/risk_engine/order_execution/ui
等不存在的包名，配置完全失效）。

治本（AI-01 S1-2，2026-08-01）：原 .importlinter forbidden_modules 43 个包手工维护，
文件头部自带"新增/重命名包时 MUST 同步"的君子协定——已失效过一次。现由本生成器从
src/zephyr/ 实际包结构派生，消除手工同步负担。

派生规则（对齐 .importlinter L7 PowerShell 维护命令）：
  扫描 src/zephyr/ 顶层目录，排除 shared（source_modules 自身，禁止自引用）/
  __开头（dunder，如 __pycache__）/ .开头（隐藏目录）/ _开头（私有约定）/
  无 __init__.py（非 Python 包）。

保留范围：本生成器仅重写 forbidden_modules 块；[importlinter] 段、[contracts] 段的
name/type/source_modules/ignore_imports 等其余字段原样保留（手工维护的契约语义不变）。

Usage:
    python scripts/governance/generators/generate_importlinter.py          # 重写 forbidden_modules 块
    python scripts/governance/generators/generate_importlinter.py --check  # 仅检测漂移，不写文件
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402

ensure_utf8_stdout()

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 10
args:
  - {flag: --check, type: bool, description: "仅检测漂移，不写文件"}
warn_only: false
description: >
  从 src/zephyr/ 顶层包扫描派生 .importlinter 的 forbidden_modules 块。
  对标 §6.3 静态清单自动生成铁律——消除手工维护 forbidden_modules 的漂移风险。
"""

IMPORTLINTER_PATH = REPO_ROOT / ".importlinter"
SRC_ZEPHYR = REPO_ROOT / "src" / "zephyr"

# forbidden_modules 块正则：从 "forbidden_modules =" 行到下一个非缩进行（注释/键/段头）前。
# 匹配 "forbidden_modules =\n" + 连续的 "    <value>\n" 行。
_FORBIDDEN_BLOCK_RE = re.compile(
    r"(forbidden_modules\s*=\s*\n)((?:[ \t]+\S[^\n]*\n)*)",
    re.MULTILINE,
)


def scan_top_level_packages() -> list[str]:
    """扫描 src/zephyr/ 顶层包，返回 sorted 的 "zephyr.<pkg>" 列表。

    排除规则（对齐 .importlinter L7 维护命令语义）：
      - shared：source_modules 自身，禁止自引用
      - __开头：dunder 约定（__pycache__ 等）
      - .开头：隐藏目录
      - _开头：私有约定
      - 无 __init__.py：非 Python 包
    """
    pkgs: list[str] = []
    if not SRC_ZEPHYR.is_dir():
        return pkgs
    for entry in sorted(SRC_ZEPHYR.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name == "shared":
            continue
        if name.startswith("__") or name.startswith(".") or name.startswith("_"):
            continue
        if not (entry / "__init__.py").exists():
            continue
        pkgs.append(f"zephyr.{name}")
    return pkgs


def build_forbidden_block(pkgs: list[str]) -> str:
    """构建 forbidden_modules 块文本（含键行 + 缩进值行）。"""
    lines = ["forbidden_modules ="]
    for pkg in pkgs:
        lines.append(f"    {pkg}")
    return "\n".join(lines) + "\n"


def extract_disk_block(content: str) -> str | None:
    """从 .importlinter 内容提取当前 forbidden_modules 块（含键行）。

    返回完整块文本（键行+值行，末尾含 \\n），未找到返回 None。
    """
    m = _FORBIDDEN_BLOCK_RE.search(content)
    if not m:
        return None
    return m.group(1) + m.group(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成/校验 .importlinter forbidden_modules 块")
    parser.add_argument(
        "--check",
        action="store_true",
        help="仅检测漂移，不写文件（drift 时 exit 1）",
    )
    parser.parse_args()

    pkgs = scan_top_level_packages()
    expected_block = build_forbidden_block(pkgs)

    if not IMPORTLINTER_PATH.exists():
        print(f"ERROR: .importlinter 不存在: {IMPORTLINTER_PATH}")
        sys.exit(EXIT_FINDINGS)

    content = IMPORTLINTER_PATH.read_text(encoding="utf-8")
    disk_block = extract_disk_block(content)

    if disk_block is None:
        print("ERROR: .importlinter 中未找到 forbidden_modules 块")
        sys.exit(EXIT_FINDINGS)

    # 归一化比对：提取值行集合（忽略顺序，防手工排序差异误报）
    def _values(block: str) -> set[str]:
        return {line.strip() for line in block.splitlines()[1:] if line.strip()}

    expected_vals = _values(expected_block)
    disk_vals = _values(disk_block)

    if expected_vals == disk_vals:
        print(f"PASS: .importlinter forbidden_modules 与 src/zephyr/ 实际包结构一致（{len(pkgs)} 个包）")
        sys.exit(EXIT_PASS)

    # 漂移
    missing = expected_vals - disk_vals
    stale = disk_vals - expected_vals
    print(f"DRIFT: .importlinter forbidden_modules 与 src/zephyr/ 实际包结构不一致")
    print(f"  期望 {len(expected_vals)} 个包，磁盘 {len(disk_vals)} 个包")
    if missing:
        print(f"  缺失（包已存在但未登记）: {sorted(missing)}")
    if stale:
        print(f"  过期（包已删除但仍登记）: {sorted(stale)}")

    if parser.parse_args().check:
        print("\nFix: python scripts/governance/generators/generate_importlinter.py")
        sys.exit(EXIT_FINDINGS)

    # 重写：替换 forbidden_modules 块，保留其余内容原样
    new_content = _FORBIDDEN_BLOCK_RE.sub(expected_block, content, count=1)
    atomic_write_safe(IMPORTLINTER_PATH, new_content)
    print(f"REGENERATED: .importlinter forbidden_modules 已更新（{len(pkgs)} 个包）")
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
