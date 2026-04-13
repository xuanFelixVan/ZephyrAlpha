#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
对 PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md 做定向治理补全（高置信度）：
- 修复“动态风险控?”、“技术目?”、“灵活?*”等断裂
- 修复代码块 docstring 的“CPPI动态调?”、“投资?”等断裂
"""

from __future__ import annotations

from pathlib import Path


FP = Path(
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/"
    "PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md"
)


PAIRS: list[tuple[str, str]] = [
    ("组合保险策略模块负责?- CPPI（固定比例组合保险）", "组合保险策略模块负责：\n- CPPI（固定比例组合保险）"),
    ("- 动态风险控?", "- 动态风险控制"),
    ("### 1.2 技术目?", "### 1.2 技术目标"),
    ("灵活?*", "灵活性"),
    ("透明?*", "透明度"),
    ("CPPI动态调?", "CPPI 动态调整"),
    ("新的风险资产投资?", "新的风险资产投资额"),
]


def main() -> int:
    t = FP.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = t
    for a, b in PAIRS:
        t = t.replace(a, b)
    if t != orig:
        if not t.endswith("\n"):
            t += "\n"
        FP.write_bytes(t.encode("utf-8-sig"))
        print("UPDATED")
    else:
        print("NO_CHANGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

