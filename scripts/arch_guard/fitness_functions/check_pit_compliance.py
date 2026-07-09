# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_pit_compliance.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_pit_compliance
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
# [TTL] task_bound
"""
check_pit_compliance.py — PIT（Point-in-Time）铁律强制执行 (INV-004)

INV-004: 回测数据禁止未来信息泄露（Look-ahead Bias 零容忍）。

检测方式：
  - 扫描 D_FACTOR Alpha Factor 相关 Python 代码
  - 搜索常见的 look-ahead bias 模式：
    1. 使用未来日期的数据引用（如 shifting with +N 而非 -N）
    2. 在时间序列上使用正向 shift / forward-fill from future
    3. 使用 close 作为当天决策价（应用滞后一日的 close）
    4. 在全样本上做标准化后再切分训练集（data leakage）

注意：这是静态代码模式检测，不替代运行时数据验证。
      完整验证需要配合实际数据 pipeline 运行。

exit: 0=pass, 1=warning patterns found
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

FACTOR_DIR = REPO_ROOT / "src" / "zephyr" / "factor"

PIT_SUSPECT_PATTERNS = [
    (re.compile(r"\.shift\(\s*\+?\d+"), "正向 shift（+N）可能存在未来信息泄露——应使用 shift(-N) 引用历史数据"),
    (re.compile(r"\.shift\(\s*1\s*\)"), "shift(1) 引用未来数据——PIT 要求只能使用已知数据"),
    (re.compile(r"pandas.*\.shift\(1\)|df\.shift\(1\)"), "pandas shift(1) 引用下一条记录——典型 look-ahead"),
    (re.compile(r"forward.?fill|bfill|\.fillna\(method=.ffill"), "forward-fill 可能引入未来信息——确认填充方向"),
    (
        re.compile(
            r"StandardScaler.*fit_transform.*full|normalize.*full.*dataset|standardize.*all.*data", re.IGNORECASE
        ),
        "全样本标准化后再切分——data leakage 风险",
    ),
    (
        re.compile(r"close.*price.*decision|decision_price.*close(?!.*shift\(-1\)|.*lag)", re.IGNORECASE),
        "使用当天收盘价做决策——应使用 lag(1) 的前一天收盘价",
    ),
]

EXCLUDE_DIRS = {"__pycache__", ".git", "tests", "docs"}

def check_file(file_path: Path) -> list[str]:
    warnings_found = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return warnings_found

    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        for pattern, explanation in PIT_SUSPECT_PATTERNS:
            if pattern.search(stripped):
                warnings_found.append(f'  {file_path.relative_to(REPO_ROOT)}:{i}: {explanation} — "{stripped[:120]}"')
                break
    return warnings_found

def main() -> int:
    if not FACTOR_DIR.exists():
        print(f"⚠ D_FACTOR 目录不存在: {FACTOR_DIR} — 跳过 PIT 检查")
        return 0

    all_warnings: list[str] = []
    for py_file in FACTOR_DIR.rglob("*.py"):
        if any(excl in py_file.parts for excl in EXCLUDE_DIRS):
            continue
        warnings_found = check_file(py_file)
        all_warnings.extend(warnings_found)

    if all_warnings:
        print(f"⚠ INV-004 PIT 铁律 —— 发现 {len(all_warnings)} 处可疑模式（需人工审查）:")
        for w in all_warnings:
            print(w)
        print()
        print("PIT 铁律：所有因子计算必须以截止日期 T 时刻的已知数据为输入。")
        print("以上模式不一定构成实际违规，但需要确认数据引用方向正确。")
        print("请检查：shift 方向 / 标准化时序 / 决策价格来源。")
        return 1

    print("✅ INV-004 PIT 铁律 —— 无可疑模式")
    print(f"   已扫描 {FACTOR_DIR.relative_to(REPO_ROOT)}/ 下所有 .py 文件。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
