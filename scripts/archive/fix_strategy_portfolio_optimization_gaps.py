#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
对 STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md 做定向治理补全：
- 修复标题/表格/清单/注释中的“汉字?”断裂与孤立问号（高置信度）
- 适度整理表格列与元信息行，保证可读性
"""

from __future__ import annotations

from pathlib import Path


FP = Path(
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/"
    "STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md"
)


PAIRS: list[tuple[str, str]] = [
    ("核心价?*", "核心价值"),
    ("业务价?*", "业务价值"),
    ("相关性建?", "相关性建模"),
    ("动态策略权重调?", "动态策略权重调整"),
    ("提升组合稳定?", "提升组合稳定性"),
    ("风险控?", "风险控制"),
    ("开源依?*", "开源依赖"),
    ("5-7?|", "5-7 天 |"),
    ("与多策略分层系统的关?", "与多策略分层系统的关系"),
    ("形成互补关系统", "形成互补关系"),
    ("策略权重优化、相关性建?|", "策略权重优化、相关性建模 |"),
    ("多策略分层管?|", "多策略分层管理 |"),
    ("协同优?|", "协同优化 |"),
    ("最优策略权?", "最优策略权重"),
    ("先实现本模块 (5-7?", "先实现本模块（5-7 天）"),
    ("再实?MULTI_STRATEGY_HIERARCHICAL_SYSTEM", "再实现 MULTI_STRATEGY_HIERARCHICAL_SYSTEM"),
    ("强依?|", "强依赖 |"),
    ("中依?|", "中依赖 |"),
    ("技术依?", "技术依赖"),
    ("技术组?|", "技术组件 |"),
    ("用?|", "用途 |"),
    ("数值计?|", "数值计算 |"),
    ("## 2. 技术实?", "## 2. 技术实现"),
    ("策略组合优化?\"\"", "策略组合优化器\"\""),
    ("最大夏普比?", "最大夏普比率"),
    ("最小方?", "最小方差"),
    ("相关性矩?", "相关性矩阵"),
    ("计算策略相关?\"\"", "计算策略相关性\"\""),
    ("Phase 1 | 策略相关性建?|", "Phase 1 | 策略相关性建模 |"),
    ("Phase 2 | 多策略优化算法实?|", "Phase 2 | 多策略优化算法实现 |"),
    ("Phase 3 | API、测试、文?|", "Phase 3 | API、测试、文档 |"),
    ("状?*", "状态"),
    ("合规?*", "合规度"),
    ("变更历?", "变更历史"),
    ("首席蓝图架构?", "首席蓝图架构师"),
    ("#### Layer 6: 组合优化?", "#### Layer 6: 组合优化"),
    ("待创?", "待创建"),
    ("职责**: Layer 6 组合优化?", "职责**: Layer 6 组合优化"),
]


def main() -> int:
    t = FP.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = t
    for a, b in PAIRS:
        t = t.replace(a, b)
    # 清理清单符号与孤立 '?'
    t = t.replace("\n?\n", "\n\n").replace("- ?", "- ")
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

