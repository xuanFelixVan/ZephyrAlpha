#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
对 SYSTEM_ENHANCEMENT_BLUEPRINT.md 做定向治理补全：
- 修复章节标题、表格字段、架构图 ASCII 残片中的“汉字?”
- 将明显破碎的 ASCII 架构图替换为可读的 mermaid（保守）
"""

from __future__ import annotations

from pathlib import Path


FP = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SYSTEM_ENHANCEMENT_BLUEPRINT.md")

PAIRS: list[tuple[str, str]] = [
    ("## 一、蓝图概?", "## 一、蓝图概述"),
    ("满足证监会要?|", "满足证监会要求 |"),
    ("**核心目标**?1.", "**核心目标**:\n1."),
    ("**量化指标**?-", "**量化指标**:\n-"),
    ("### 1.3 技术定?", "### 1.3 技术定位"),
    ("Layer 7 - AI报告?**模块类型**", "Layer 7 - AI报告\n\n**模块类型**"),
    ("### 2.1 整体架构?", "### 2.1 整体架构"),
    ("#### P0级模块（核心差距?", "#### P0级模块（核心差距）"),
    ("景分析?(ScenarioAnalyzer)", "情景分析（ScenarioAnalyzer）"),
    ("景分析报告（收益影响、风险指标、敏感度分析?-", "情景分析报告（收益影响、风险指标、敏感度分析）\n-"),
    ("压力测试报告生成?(StressTestReporter)", "压力测试报告生成（StressTestReporter）"),
    ("月度定期测?/ 市场异常时触?", "月度定期测试 / 市场异常时触发"),
    ("实时风险监控报告?(RealTimeRiskReporter)", "实时风险监控报告（RealTimeRiskReporter）"),
    ("融合宏?中观/微观三层报告", "融合宏观/中观/微观三层报告"),
    ("调用频率：日度融?", "调用频率：日度融合"),
    ("策略生命周期报告?(StrategyLifecycleReporter)", "策略生命周期报告（StrategyLifecycleReporter）"),
    ("调用频率：周度更?", "调用频率：周度更新"),
    ("监管合规报告?(RegulatoryReporter)", "监管合规报告（RegulatoryReporter）"),
    ("调用频率：季度定?/ 监管要求?", "调用频率：季度定期 / 监管要求触发"),
    ("# 准确性：采样误差<5%，满足业务需?", "# 准确性：采样误差 < 5%，满足业务需求"),
    ("适用于树模型?", "适用于树模型）"),
    ("并行计算SHAP?", "并行计算 SHAP"),
    ("计算时间 | 准确?|", "计算时间 | 准确率 |"),
    ("| 采样SHAP | 1000 | 8?|", "| 采样SHAP | 1000 | 8s |"),
    ("| 近似SHAP | 100 | 2?|", "| 近似SHAP | 100 | 2s |"),
    ("快速预?", "快速预览"),
    ("况，分析预算偏?", "情况，分析预算偏差"),
    ("预算偏差分析与预?4.", "预算偏差分析与预警\n4."),
    ("再平衡建议生?", "再平衡建议生成"),
    ("检测模型漂?", "检测模型漂移"),
    ("重训练建议生?", "重训练建议生成"),
    ("过拟合概率评?", "过拟合概率评估"),
    ("策略稳健性评?", "策略稳健性评估"),
    ("决策追?", "决策追踪"),
    ("优化执行质?", "优化执行质量"),
    ("执行质量分?2.", "执行质量分析\n2."),
    ("订单流分?4.", "订单流分析\n4."),
    ("套利信?", "套利信号"),
    ("均值回归信号监?3.", "均值回归信号监控\n3."),
    ("## 三、接口定?", "## 三、接口定义"),
    ("详细的API接口定义请参?LAYER7_API_REFERENCE.md", "详细的 API 接口定义请参考 `LAYER7_API_REFERENCE.md`"),
    ("| 多时间框架融?|", "| 多时间框架融合 |"),
    ("| 策略生命周期 |", "| 策略生命周期 |"),
    ("| 监管合规 |", "| 监管合规 |"),
    ("| 执行成本 |", "| 执行成本 |"),
    ("实施?", "实施说明"),
    ("模型稳定?|", "模型稳定性 |"),
    ("回测过拟?|", "回测过拟合 |"),
    ("核心功?", "核心功能"),
    ("依赖抽?", "依赖抽象接口"),
    ("### 4.2 数据流向?", "### 4.2 数据流向"),
    ("数据?| 更新频率", "数据层 | 更新频率"),
    ("景分析?|", "情景分析 |"),
    ("因子暴?|", "因子暴露 |"),
    ("历史行?|", "历史行情 |"),
]


def replace_architecture_block(t: str) -> str:
    # 原文在“### 2.1 整体架构?”下方有一个 ``` 包裹的破碎 ASCII 图。
    # 这里按“保守替换”策略：仅在匹配到该段代码围栏时替换为 mermaid。
    marker = "### 2.1 整体架构?\n```"
    start = t.find(marker)
    if start == -1:
        return t
    fence1 = t.find("```", start)
    if fence1 == -1:
        return t
    fence2 = t.find("```", fence1 + 3)
    if fence2 == -1:
        return t

    before = t[:start]
    after = t[fence2 + 3 :]
    mer = """### 2.1 整体架构

```mermaid
graph TB
  subgraph P0[P0 核心模块]
    SA[ScenarioAnalyzer\\n情景分析] --> FUS[MultiTimeframeReportFusion\\n多时间框架融合]
    ST[StressTestReporter\\n压力测试] --> FUS
    RR[RealTimeRiskReporter\\n实时风险] --> FUS
  end

  FUS --> HUB[ReportDistributionHub\\n统一报告分发中心]

  subgraph P1[P1 扩展模块]
    LIF[StrategyLifecycleReporter\\n策略生命周期]
    REG[RegulatoryReporter\\n监管合规]
    EXP[AIExplainabilityReporter\\n可解释性]
    EXE[ExecutionCostReporter\\n执行成本]
  end

  HUB --> LIF
  HUB --> REG
  HUB --> EXP
  HUB --> EXE
```
"""
    return before + mer + after


def main() -> int:
    t = FP.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = t
    t = replace_architecture_block(t)
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

