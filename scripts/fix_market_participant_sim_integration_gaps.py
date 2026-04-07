#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对 MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md 做定向治理补全：
- 允许在示例代码/注释中替换常见断裂片段（高置信度词尾）
- 目标：显著减少“汉字?”断裂，提升可读性与可执行性
"""

from __future__ import annotations

from pathlib import Path


FP = Path(
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/"
    "MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md"
)

PAIRS: list[tuple[str, str]] = [
    ("行为模拟系?", "行为模拟系统"),
    ("审批智能?", "审批智能体"),
    ("多层次集?-", "多层次集成——"),
    ("多层次集?", "多层次集成"),
    ("详细集成架构设?", "详细集成架构设计"),
    ("## 🏗?二、详细集成架构设计", "## 🏗 二、详细集成架构设计"),
    ("分析? 之间新增", "分析层之间新增"),
    ("Alpha因子?", "Alpha因子层"),
    ("新增核心?", "新增核心层"),
    ("主力智能?", "主力智能体"),
    ("散户智能?", "散户智能体"),
    ("机器学习?", "机器学习层"),
    ("策略执行?", "策略执行层"),
    ("组合优化?", "组合优化层"),
    ("AI报告?", "AI报告层"),
    ("人机交互?", "人机交互层"),
    ("为什么需要Layer 2.5?*", "为什么需要 Layer 2.5（模拟层）"),
    ("复杂计?3.", "复杂计算。\n3."),
    ("三种形?", "三种形态"),
    ("集成方?", "集成方案"),
    ("数据? ", "数据来自 "),
    ("输?", "输出"),
    ("信?", "信号"),
    ("因?", "因子"),
    ("不平衡?", "不平衡度"),
    ("绝对值越?强度越大", "绝对值越大，强度越大"),
    ("追涨杀跌程?", "追涨杀跌程度"),
    ("绪因子", "情绪因子"),
    ("政策支持?", "政策支持强度"),
    ("市场稳定?", "市场稳定性"),
    ("持仓变?", "持仓变化"),
    ("政策信?", "政策信号"),
    ("合成最终因?", "合成最终因子"),
    ("因子库集?", "因子库集成"),
    ("初始化因?", "初始化因子"),
    ("因子标准?", "因子标准化"),
    ("信号输出层集成方?", "信号输出层集成方案"),
    ("信号生成?", "信号生成器"),
    ("交易信?", "交易信号"),
    ("整合信?", "整合信号"),
    ("提取各智能体的信?", "提取各智能体的信号"),
    ("置信?*", "置信度"),
    ("计算最终权?", "计算最终权重"),
    ("归一?", "归一化"),
    ("最终权?", "最终权重"),
    ("策略集?", "策略集成"),
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

