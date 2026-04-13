#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
对 RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md 做定向治理补全：
- 修复标题/表格/清单/代码注释中的“汉字?”断裂与孤立问号（高置信度）
"""

from __future__ import annotations

from pathlib import Path


FP = Path(
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/"
    "RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md"
)


PAIRS: list[tuple[str, str]] = [
    ("? 风险贡献分析蓝图", ""),
    ("核心功能实?", "核心功能实现"),
    ("开发周?*", "开发周期"),
    ("2-3?", "2-3 周"),
    ("参考开?*", "参考开源"),
    ("风控效率?", "风控效率。"),
    ("风险预算模块?", "风险预算模块）"),
    ("核心价?*", "核心价值"),
    ("业务价?*", "业务价值"),
    ("识别组合风险集中?", "识别组合风险集中度"),
    ("提升风险管理透明?", "提升风险管理透明度"),
    ("开源依?*", "开源依赖"),
    ("2-3?|", "2-3 周 |"),
    ("提供风险贡献计算能力?", "提供风险贡献计算能力。"),
    ("为其他模块提供风险贡献计划|", "为其他模块提供风险贡献计算能力 |"),
    ("简化风险预?|", "简化风险预警 |"),
    ("快速实?|", "快速实现 |"),
    ("复杂组?|", "复杂组合 |"),
    ("识别风险集中?", "识别风险集中度"),
    ("强依?|", "强依赖 |"),
    ("简化风险预算系?|", "简化风险预算系统 |"),
    ("技术依?", "技术依赖"),
    ("技术组?|", "技术组件 |"),
    ("用?|", "用途 |"),
    ("数值计?|", "数值计算 |"),
    ("## 2. 技术实?", "## 2. 技术实现"),
    ("风险贡献分析?\"\"", "风险贡献分析器\"\""),
    ("组合波动?", "组合波动率"),
    ("风险贡献百分?", "风险贡献百分比"),
    ("风险贡献阈?", "风险贡献阈值"),
    ("测试、文?|", "测试、文档 |"),
    ("状?*", "状态"),
    ("合规?*", "合规度"),
    ("变更历?", "变更历史"),
    ("首席蓝图架构?", "首席蓝图架构师"),
    ("待创?", "待创建"),
]


def main() -> int:
    t = FP.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = t
    for a, b in PAIRS:
        t = t.replace(a, b)
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

