#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对 LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md 做定向治理补全：
以“高置信度词尾替换”为主，允许在示例代码/注释中替换常见断裂片段。
"""

from __future__ import annotations

from pathlib import Path


FP = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md")

PAIRS: list[tuple[str, str]] = [
    ("系统架构?", "系统架构"),
    ("核心子系统设?", "核心子系统设计"),
    ("资金数据采集子系?", "资金数据采集子系统"),
    ("最大流出比?", "最大流出比例"),
    ("检查流动性风?", "检查流动性风险"),
    ("检查维?", "检查维度"),
    ("流动性预?", "流动性预警"),
    ("监控流动?", "监控流动性"),
    ("总资?", "总资产"),
    ("周转?", "周转率"),
    ("时间?", "时间戳"),
    ("现金流预?", "现金流预测"),
    ("预测现金?", "预测现金流"),
    ("预测置信?", "预测置信度"),
    ("目标收益?", "目标收益率"),
    ("行动?", "行动项"),
    ("数据格?", "数据格式"),
    ("数据模型与存?", "数据模型与存储"),
    ("资金流水记录?", "资金流水记录表"),
    ("数据流设?", "数据流设计"),
    ("资金周转率计?", "资金周转率计算"),
    ("计算资金周转?", "计算资金周转率"),
    ("计算周期（天?", "计算周期（天）"),
    ("时间复杂?*", "时间复杂度"),
    ("空间复杂?*", "空间复杂度"),
    ("计算复杂?*", "计算复杂度"),
    ("日流?", "日流量"),
    ("预警项列?", "预警项列表"),
    ("风险级别（LOW/MEDIUM/HIGH?", "风险级别（LOW/MEDIUM/HIGH）"),
    ("预警级别（GREEN/YELLOW/RED?", "预警级别（GREEN/YELLOW/RED）"),
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

