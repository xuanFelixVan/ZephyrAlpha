# 02_TACTICS 战术库

## 概述

本目录存储量化交易的战术(Tactics)文件，与Framework层分离，采用Layer 0-7分层架构组织。

## 目录结构

```
02_TACTICS/
├── 01_MARKET_REGIME/           # 市场状态识别 (Layer 0)
├── 02_ALPHA_FACTORS/           # Alpha因子战术 (Layer 1-2)
│   ├── 01_趋势跟踪/
│   ├── 02_均值回归/
│   ├── 03_价值投资/
│   ├── 04_成长投资/
│   ├── 05_质量因子/
│   ├── 06_动量战术/
│   └── 07_情绪量化/
├── 03_RISK_MANAGEMENT/         # 风险管理 (Layer 3)
├── 04_EXECUTION/               # 执行优化 (Layer 4)
├── 05_RISK_CONTROL/             # 风险控制 (Layer 5)
├── 06_PERFORMANCE/             # 绩效归因 (Layer 6)
└── 07_ITERATION/               # 策略迭代 (Layer 7)
```

## Layer 分层说明

| Layer | 名称 | 职责 |
|-------|------|------|
| Layer 0 | 市场状态 | 识别当前市场环境，为战术选择提供前提条件 |
| Layer 1 | Alpha因子 | 核心Alpha来源，趋势/均值回归/价值/成长/质量/动量/情绪 |
| Layer 2 | 因子组合 | 多因子组合构建，权重配置 |
| Layer 3 | 风险管理 | 组合层面风险管理，敞口控制 |
| Layer 4 | 执行优化 | 订单执行算法，减少冲击成本 |
| Layer 5 | 风险控制 | 实时风控监控，异常检测 |
| Layer 6 | 绩效归因 | 收益分解，因子暴露分析 |
| Layer 7 | 策略迭代 | 策略评估，优化升级 |

## 战术命名规范

- 文件名格式: `T.{分类代码}.{战术名称}.md`
- 例如: `T.01.TR001.双均线趋势跟踪.md`

## 关联文档

- 主框架: [01_FRAMEWORK/量化策略框架_v3.1.md](../01_FRAMEWORK/量化策略框架_v3.1.md)
- 因子库: [factor-library](../../factor-library/00_INDEX/因子分类总表.md)

## 版本信息

- 版本: v1.0
- 创建日期: 2026-03-28
