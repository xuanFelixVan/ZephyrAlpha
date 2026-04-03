---
module_id: TACTICS_README_001
version: 4.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# main/02_TACTICS - 战术模块

> Layer 0-11 战术实现文档
>
> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：✅ 活跃

---

## 1. 概述

本目录是清风量化交易系统 4.0 的**战术实现模块**，包含 Layer 0-11 分层架构中各层的具体战术实现文档。

### 1.1 与框架的关系

```
01_FRAMEWORK/README.md    ← 📐 框架说明（Layer 0-11 架构定义）
      ↓
main/02_TACTICS/          ← 🎯 战术实现（具体实现文档）
```

---

## 2. 模块概览

| 目录 | Layer | 描述 | 战术数 | 状态 |
|------|-------|------|--------|------|
| 01_MARKET_REGIME | Layer 1 | 市场状态识别 | 5 | ✅ 活跃 |
| 02_ALPHA_FACTORS | Layer 2 | Alpha 因子战术 | 20+ | ✅ 活跃 |
| 03_RISK_MANAGEMENT | Layer 3 | 风险管理 | 2 | ✅ 活跃 |
| 04_EXECUTION | Layer 4-5 | 交易执行 | 7 | ✅ 活跃 |
| 05_RISK_CONTROL | Layer 6 | 风控监控 | 2 | ✅ 活跃 |
| 06_PERFORMANCE | Layer 7 | 绩效归因 | 1 | ✅ 活跃 |
| 07_ITERATION | Layer 7 | 策略迭代 | 1 | ✅ 活跃 |

---

## 3. 目录结构

```
main/02_TACTICS/
├── README.md                        # 本文档
│
├── 01_MARKET_REGIME/               # Layer 1: 市场状态识别
│   ├── README.md
│   ├── T.00.MR001.市场趋势识别.md
│   ├── T.00.MR002.量能周期体系.md
│   ├── T.00.MR003.市场结构博弈.md
│   ├── T.00.MR004.宏观策略量化.md
│   └── T.00.MR005.指数与行业分析.md
│
├── 02_ALPHA_FACTORS/               # Layer 2: Alpha 因子战术
│   ├── README.md
│   ├── 01_趋势跟踪/
│   │   ├── README.md
│   │   ├── T.01.TR001.双均线趋势跟踪.md
│   │   └── T.01.TR002.技术指标协同.md
│   ├── 02_均值回归/
│   │   └── README.md
│   ├── 03_价值投资/
│   │   ├── README.md
│   │   └── T.01.VA001.估值分析.md
│   ├── 04_成长投资/
│   │   └── README.md
│   ├── 05_质量因子/
│   │   └── README.md
│   ├── 06_动量战术/
│   │   └── README.md
│   └── 07_情绪量化/
│       ├── README.md
│       ├── T.01.SN001.资金流向.md
│       ├── T.01.SN002.龙虎榜跟庄.md
│       └── T.01.SN003.筹码峰分析.md
│
├── 03_RISK_MANAGEMENT/             # Layer 3: 风险管理
│   ├── README.md
│   ├── T.03.RM001.行业敞口控制.md
│   └── T.03.RM002.波动率目标管理.md
│
├── 04_EXECUTION/                   # Layer 4-5: 交易执行
│   ├── README.md
│   ├── T.04.EX002.TWAP 执行.md
│   ├── T.04.EX004.盘前计划与买入模式.md
│   ├── T.04.EX005.开盘竞价信号.md
│   ├── T.04.EX006.A 股交易规则.md
│   ├── T.04.EX007.做 T 策略量化.md
│   └── T.04.EX008.分时图分析.md
│
├── 05_RISK_CONTROL/                # Layer 6: 风控监控
│   ├── README.md
│   ├── T.05.RC001.实时风险监控.md
│   └── T.05.RC002.风险控制量化体系.md
│
├── 06_PERFORMANCE/                 # Layer 7: 绩效归因
│   ├── README.md
│   └── T.06.PF001.Brinson 归因.md
│
└── 07_ITERATION/                   # Layer 7: 策略迭代
    ├── README.md
    └── T.07.IT001.策略绩效评估.md
```

---

## 4. Layer 分层说明

| Layer | 模块 | 职责 | 战术示例 |
|-------|------|------|----------|
| Layer 1 | 01_MARKET_REGIME | 识别当前市场环境，为战术选择提供前提条件 | 市场趋势识别、量能周期、市场结构博弈 |
| Layer 2 | 02_ALPHA_FACTORS | 核心 Alpha 来源，趋势/均值回归/价值/成长/质量/动量/情绪 | 双均线趋势跟踪、资金流向、筹码峰分析 |
| Layer 3 | 03_RISK_MANAGEMENT | 组合层面风险管理，敞口控制 | 行业敞口控制、波动率目标管理 |
| Layer 4 | 04_EXECUTION | 订单执行算法，减少冲击成本 | TWAP 执行、盘前计划、做 T 策略 |
| Layer 5 | 04_EXECUTION | 交易执行细节 | A 股交易规则、分时图分析 |
| Layer 6 | 05_RISK_CONTROL | 实时风控监控，异常检测 | 实时风险监控、风险控制量化体系 |
| Layer 7 | 06_PERFORMANCE + 07_ITERATION | 收益分解，因子暴露分析，策略评估 | Brinson 归因、策略绩效评估 |

---

## 5. 战术命名规范

### 5.1 文件名格式

```
T.{Layer 编号}.{分类代码}.{序号}.{战术名称}.md
```

### 5.2 命名示例

| 战术名称 | 文件名 | 说明 |
|----------|--------|------|
| 市场趋势识别 | T.00.MR001.市场趋势识别.md | Layer 0, Market Regime, 001 |
| 双均线趋势跟踪 | T.01.TR001.双均线趋势跟踪.md | Layer 1, Trend, 001 |
| 资金流向 | T.01.SN001.资金流向.md | Layer 1, Sentiment, 001 |
| 波动率目标管理 | T.03.RM002.波动率目标管理.md | Layer 3, Risk Management, 002 |
| TWAP 执行 | T.04.EX002.TWAP 执行.md | Layer 4, Execution, 002 |
| Brinson 归因 | T.06.PF001.Brinson 归因.md | Layer 6, Performance, 001 |

### 5.3 分类代码

| 代码 | 英文 | 中文 | 所属 Layer |
|------|------|------|------------|
| MR | Market Regime | 市场状态 | Layer 1 |
| TR | Trend | 趋势跟踪 | Layer 2 |
| MR | Mean Reversion | 均值回归 | Layer 2 |
| VA | Value | 价值投资 | Layer 2 |
| GR | Growth | 成长投资 | Layer 2 |
| QL | Quality | 质量因子 | Layer 2 |
| MO | Momentum | 动量 | Layer 2 |
| SN | Sentiment | 情绪量化 | Layer 2 |
| RM | Risk Management | 风险管理 | Layer 3 |
| EX | Execution | 执行优化 | Layer 4-5 |
| RC | Risk Control | 风控监控 | Layer 6 |
| PF | Performance | 绩效归因 | Layer 7 |
| IT | Iteration | 策略迭代 | Layer 7 |

---

## 6. 代码状态

本目录中的所有战术均为**战术实现文档**，代码状态如下：

| 目录 | 代码状态 | 说明 |
|------|----------|------|
| 01_MARKET_REGIME/ | [STUDY_ONLY] | 市场状态识别战术，待回测验证 |
| 02_ALPHA_FACTORS/ | [STUDY_ONLY] | Alpha 因子战术，待回测验证 |
| 03_RISK_MANAGEMENT/ | [STUDY_ONLY] | 风险管理战术，待回测验证 |
| 04_EXECUTION/ | [STUDY_ONLY] | 交易执行战术，待回测验证 |
| 05_RISK_CONTROL/ | [STUDY_ONLY] | 风控监控战术，待回测验证 |
| 06_PERFORMANCE/ | [STUDY_ONLY] | 绩效归因战术，待回测验证 |
| 07_ITERATION/ | [STUDY_ONLY] | 策略迭代战术，待回测验证 |

> ⚠️ **当前所有代码均为 [STUDY_ONLY] 状态，不可直接运行**

---

## 7. 关联文档

| 文档 | 说明 |
|------|------|
| [../../INDEX.md](../INDEX.md) | 主规格文档 |
| [../../CHANGELOG.md](../../06_ARCHIVE/CHANGELOG.md) | 变更日志 |
| [../../01_FRAMEWORK/README.md](../../01_FRAMEWORK/README.md) | Layer 0-11 框架说明 |
| [../../02_FACTOR_LIBRARY/](../../02_FACTOR_LIBRARY/) | 因子库 |
| [../../04_EXECUTION/](../../04_EXECUTION/) | 执行引擎 |

---

## 8. 版本信息

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，基于 Layer 0-11 架构 |
| v4.0.1 | 2026-03-28 | 目录重组，从 01_FRAMEWORK 迁移到 main/ |