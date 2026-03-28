# 01_FRAMEWORK - 核心框架

> Layer 0-7 分层架构说明
>
> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：✅ 活跃

---

## 1. 目录说明

本目录是清风量化交易系统 4.0 的**核心框架说明**，定义了整个系统的 Layer 0-7 分层架构。

### 1.1 与其他目录的关系

```
docs/
├── 01_FRAMEWORK/            ← 📐 框架说明（本文档）
│   └── README.md            ← Layer 0-7架构定义
│
├── main/                    ← 🎯 战术模块（Layer 0-7实现）
│   └── 02_TACTICS/         ← 战术实现文档
│
├── 02_FACTOR_LIBRARY/      ← 🧬 因子库（因子定义和研究）
├── 03_TRADING_TACTICS/     ← 📊 交易策略（策略池）
└── 04_TECHNICAL_SPECS/     ← ⚙️ 技术规格（系统架构）
```

---

## 2. Layer 0-7 分层架构

清风量化交易系统采用 Layer 0-7 分层架构，将量化交易流程分解为 8 个层次：

```
┌─────────────────────────────────────────┐
│ Layer 7: 策略迭代                        │
│   - 策略评估、优化升级                    │
│   - 文档：main/02_TACTICS/07_ITERATION/ │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 6: 绩效归因                        │
│   - 收益分解、因子暴露分析                │
│   - 文档：main/02_TACTICS/06_PERFORMANCE/│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 5: 风控监控                        │
│   - 实时监控、告警、异常检测              │
│   - 文档：main/02_TACTICS/05_RISK_CONTROL/│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 4: 执行层                          │
│   - 订单生成、路由、执行算法              │
│   - 文档：main/02_TACTICS/04_EXECUTION/ │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 3: 风险层                          │
│   - 风险因子建模、组合风险管理            │
│   - 文档：main/02_TACTICS/03_RISK_MANAGEMENT/│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 2: Alpha 层                        │
│   - Alpha 因子生成、信号预测              │
│   - 文档：main/02_TACTICS/02_ALPHA_FACTORS/│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 1: 前置层                          │
│   - 市场状态识别、信号预处理              │
│   - 文档：main/02_TACTICS/01_MARKET_REGIME/│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Layer 0: 数据层                          │
│   - 数据采集、清洗、存储                  │
│   - 文档：02_FACTOR_LIBRARY/04_DATA_SOURCE/│
└─────────────────────────────────────────┘
```

---

## 3. Layer 详细说明

### Layer 0 - 数据层

| 项目 | 说明 |
|------|------|
| **功能** | 数据采集、清洗、存储 |
| **输入** | 原始市场数据（行情、财务、宏观） |
| **输出** | 标准化数据（OHLCV、财务指标、宏观指标） |
| **文档位置** | [02_FACTOR_LIBRARY/04_DATA_SOURCE/](../02_FACTOR_LIBRARY/04_DATA_SOURCE/) |

### Layer 1 - 前置层

| 项目 | 说明 |
|------|------|
| **功能** | 市场状态识别、信号预处理 |
| **输入** | 标准化数据 |
| **输出** | 市场状态标签（牛市/熊市/震荡市/妖股周期/混沌） |
| **文档位置** | [main/02_TACTICS/01_MARKET_REGIME/](../main/02_TACTICS/01_MARKET_REGIME/) |

### Layer 2 - Alpha 层

| 项目 | 说明 |
|------|------|
| **功能** | Alpha 因子生成、信号预测 |
| **输入** | 市场状态、标准化数据 |
| **输出** | Alpha 信号（预期收益率） |
| **文档位置** | [main/02_TACTICS/02_ALPHA_FACTORS/](../main/02_TACTICS/02_ALPHA_FACTORS/) |

### Layer 3 - 风险层

| 项目 | 说明 |
|------|------|
| **功能** | 风险因子建模、组合风险管理 |
| **输入** | Alpha 信号、风险因子数据 |
| **输出** | 风险调整后的预期收益 |
| **文档位置** | [main/02_TACTICS/03_RISK_MANAGEMENT/](../main/02_TACTICS/03_RISK_MANAGEMENT/) |

### Layer 4 - 组合层

| 项目 | 说明 |
|------|------|
| **功能** | 组合优化、权重分配 |
| **输入** | 风险调整后的预期收益 |
| **输出** | 目标持仓权重 |
| **文档位置** | [04_TECHNICAL_SPECS/modules/](../04_TECHNICAL_SPECS/modules/) |

### Layer 5 - 执行层

| 项目 | 说明 |
|------|------|
| **功能** | 订单生成、路由、执行算法 |
| **输入** | 目标持仓权重 |
| **输出** | 实际成交订单 |
| **文档位置** | [main/02_TACTICS/04_EXECUTION/](../main/02_TACTICS/04_EXECUTION/) |

### Layer 6 - 风控监控层

| 项目 | 说明 |
|------|------|
| **功能** | 实时监控、告警、异常检测 |
| **输入** | 实际成交订单、市场数据 |
| **输出** | 风险告警、异常报告 |
| **文档位置** | [main/02_TACTICS/05_RISK_CONTROL/](../main/02_TACTICS/05_RISK_CONTROL/) |

### Layer 7 - 绩效归因与策略迭代层

| 项目 | 说明 |
|------|------|
| **功能** | 绩效归因、策略评估、优化升级 |
| **输入** | 交易记录、市场数据 |
| **输出** | 绩效报告、策略优化建议 |
| **文档位置** | [main/02_TACTICS/06_PERFORMANCE/](../main/02_TACTICS/06_PERFORMANCE/) + [main/02_TACTICS/07_ITERATION/](../main/02_TACTICS/07_ITERATION/) |

---

## 4. 战术模块导航

实际的战术实现文档位于 `main/02_TACTICS/` 目录：

| Layer | 模块 | 文档路径 | 状态 |
|-------|------|----------|------|
| Layer 1 | 市场状态识别 | [main/02_TACTICS/01_MARKET_REGIME/](../main/02_TACTICS/01_MARKET_REGIME/) | ✅ 活跃 |
| Layer 2 | Alpha 因子 | [main/02_TACTICS/02_ALPHA_FACTORS/](../main/02_TACTICS/02_ALPHA_FACTORS/) | ✅ 活跃 |
| Layer 3 | 风险管理 | [main/02_TACTICS/03_RISK_MANAGEMENT/](../main/02_TACTICS/03_RISK_MANAGEMENT/) | ✅ 活跃 |
| Layer 4 | 执行优化 | [main/02_TACTICS/04_EXECUTION/](../main/02_TACTICS/04_EXECUTION/) | ✅ 活跃 |
| Layer 5 | 风控监控 | [main/02_TACTICS/05_RISK_CONTROL/](../main/02_TACTICS/05_RISK_CONTROL/) | ✅ 活跃 |
| Layer 6 | 绩效归因 | [main/02_TACTICS/06_PERFORMANCE/](../main/02_TACTICS/06_PERFORMANCE/) | ✅ 活跃 |
| Layer 7 | 策略迭代 | [main/02_TACTICS/07_ITERATION/](../main/02_TACTICS/07_ITERATION/) | ✅ 活跃 |

---

## 5. 代码状态

本目录为**框架说明文档**，不包含具体实现代码。

实际战术实现代码位于 `main/02_TACTICS/` 目录，状态如下：

| 目录 | 代码状态 | 说明 |
|------|----------|------|
| main/02_TACTICS/01_MARKET_REGIME/ | [STUDY_ONLY] | 市场状态识别战术，待回测验证 |
| main/02_TACTICS/02_ALPHA_FACTORS/ | [STUDY_ONLY] | Alpha 因子战术，待回测验证 |
| main/02_TACTICS/03_RISK_MANAGEMENT/ | [STUDY_ONLY] | 风险管理战术，待回测验证 |
| main/02_TACTICS/04_EXECUTION/ | [STUDY_ONLY] | 交易执行战术，待回测验证 |
| main/02_TACTICS/05_RISK_CONTROL/ | [STUDY_ONLY] | 风控监控战术，待回测验证 |
| main/02_TACTICS/06_PERFORMANCE/ | [STUDY_ONLY] | 绩效归因战术，待回测验证 |
| main/02_TACTICS/07_ITERATION/ | [STUDY_ONLY] | 策略迭代战术，待回测验证 |

> ⚠️ **当前所有代码均为 [STUDY_ONLY] 状态，不可直接运行**
> 详见：[CODE_STATUS.md](../CODE_STATUS.md)

---

## 6. 相关文档

| 文档 | 说明 |
|------|------|
| [SPEC.md](../SPEC.md) | 主规格文档 |
| [CODE_STATUS.md](../CODE_STATUS.md) | 代码状态规范 |
| [main/02_TACTICS/](../main/02_TACTICS/) | 战术模块实现 |
| [02_FACTOR_LIBRARY/](../02_FACTOR_LIBRARY/) | 因子库 |
| [03_TRADING_TACTICS/](../03_TRADING_TACTICS/) | 交易策略 |
| [04_TECHNICAL_SPECS/](../04_TECHNICAL_SPECS/) | 技术规格 |

---

## 7. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，定义 Layer 0-7 架构 |
| v4.0.1 | 2026-03-28 | 目录重组，分离框架说明与战术实现 |