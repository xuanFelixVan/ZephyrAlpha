---
module_id: KE-244
status: active
title: 3.1 7 核心能力域定义
category: documentation
---

# 3.1 7 核心能力域定义

3.1 7 核心能力域定义

对标 ArchiMate Business Capability + Goldman Aladdin Capability Categories，本视图定义 ZephyrAlpha 的 7 个核心能力域：

| 能力域 | 含义 | 主承载业务层 |
|---|---|---|
| **C1 数据能力** | Market data ingestion / quality / PIT / survivorship / lineage | L00 + L01（存储基础设施）|
| **C2 因子 & 信号能力** | Alpha factor / sentiment / signal extraction / factor registry / IC-IR | L02 + L03 |
| **C3 风控能力** | Pre-trade / at-trade / post-trade / VaR-CVaR / limits / stop-loss | L04 |
| **C4 组合构建能力** | Optimization / rebalancing / backtest / strategic allocation / meta-router | L05 |
| **C5 执行 & 交易后能力** | OMS / SOR / execution / attribution / TCA / review | L06 + L07 |
| **C6 ML / AI 平台能力** | Model lifecycle / training / serving / scout / experimentation | L11 + L13 |
| **C7 治理 & 合规能力** | Compliance runtime / governance three-layer / AISG / audit trail / fitness functions | L10 + 横切 09-GOV |

**另有 3 横切支撑域**（打到 "Cross-layer" 行）：

| 横切域 | 含义 | 主承载 |
|---|---|---|
| **CC-1 人机交互 & 研究** | Human-AI interface / research notebooks / CLI | L08 + L09 |
| **CC-2 可观测性** | Metrics / logs / traces / ai_behavior | L12 |
| **CC-3 AI 自治** | D 家族 6 系统 / ai_operator 预留口子 / decision engine | 跨 D 家族 + l*_ai_operator |
