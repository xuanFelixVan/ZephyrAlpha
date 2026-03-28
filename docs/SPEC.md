# 清风量化交易系统 v4.0 - 主规格文档

> 系统核心规格与架构定义
>
> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：已完成

---

## 1. 系统概述

### 1.1 系统定位

清风量化交易系统是一套面向A股市场的多策略量化交易平台，采用Layer 0-7分层架构，支持30-50种策略的动态管理和市场状态自适应。

### 1.2 开发阶段说明

| 阶段 | 目标 | 文档状态 | 代码状态 |
|------|------|----------|----------|
| **当前：研究/策略设计** | 验证策略想法，建立方法论 | 完善中 | 框架+示例代码 |
| **下一步：回测验证** | 用历史数据验证策略 | - | 可执行代码 |
| **未来：模拟交易** | 真实环境验证 | - | 生产级代码 |
| **未来：实盘交易** | 实际资金验证 | - | 交易级代码 |

> **重要说明**：当前所有代码均为**示例代码/框架代码**，用于说明逻辑，**不可直接运行**。
> 详见：[CODE_STATUS.md](./CODE_STATUS.md)

---

## 2. 目录结构

```
清风量化交易系统4.0/
│
├── docs/                          # 📚 文档库（策略/因子/技术文档）
│   │
│   ├── SPEC.md                   # ⭐ 统一入口文档（本文档）
│   ├── README.md                 # 文档库说明
│   ├── CODE_STATUS.md            # 代码状态规范
│   │
│   ├── 00_OVERVIEW/             # 系统总览
│   │   ├── README.md
│   │   ├── DATA_FLOW.md
│   │   └── VERSION_HISTORY.md
│   │
│   ├── 01_FRAMEWORK/            # 📐 框架说明（Layer 0-7 架构定义）
│   │   └── README.md            # Layer 0-7 架构说明
│   │
│   ├── main/                    # 🎯 战术模块（Layer 0-7 实现）
│   │   ├── README.md            # 战术模块说明
│   │   └── 02_TACTICS/         # 战术实现
│   │       ├── 01_MARKET_REGIME/    # Layer 1: 市场状态
│   │       ├── 02_ALPHA_FACTORS/   # Layer 2: Alpha 因子
│   │       ├── 03_RISK_MANAGEMENT/ # Layer 3: 风险管理
│   │       ├── 04_EXECUTION/        # Layer 4-5: 执行
│   │       ├── 05_RISK_CONTROL/     # Layer 6: 风控监控
│   │       ├── 06_PERFORMANCE/      # Layer 7: 绩效归因
│   │       └── 07_ITERATION/       # Layer 7: 策略迭代
│   │
│   ├── 02_FACTOR_LIBRARY/       # 🧬 因子库（5900+因子）
│   │   ├── 00_INDEX/           # 索引导航
│   │   ├── 01_METHODOLOGY/     # 研究方法论
│   │   ├── 02_ALPHA_FACTORS/  # Alpha因子
│   │   ├── 03_RISK_FACTORS/   # 风险因子
│   │   ├── 04_DATA_SOURCE/     # 数据源
│   │   ├── 05_BACKTEST/        # 回测报告
│   │   └── 10_MANUAL/         # 手册
│   │
│   ├── 03_TRADING_TACTICS/     # 📊 交易策略池
│   │   ├── strategy-pool/      # 策略池（S001-S120）
│   │   └── tactics/            # 战术参考（游资经验）
│   │
│   ├── 04_TECHNICAL_SPECS/     # ⚙️ 技术规格（系统架构）
│   │   ├── architecture/       # 架构设计
│   │   ├── modules/            # 核心模块
│   │   ├── trading-rules/      # 交易规则
│   │   └── ai-optimization/    # AI优化
│   │
│   ├── 05_IMPLEMENTATION/      # 🔧 实施指南
│   │   ├── CODE_QUALITY.md
│   │   ├── CONFIG_STANDARD.md
│   │   ├── ERROR_HANDLING.md
│   │   ├── SECURITY.md
│   │   ├── LOGGING_STANDARD.md
│   │   ├── TESTING_STANDARD.md
│   │   └── MIGRATION_GUIDE.md
│   │
│   └── 06_ARCHIVE/             # 📦 归档（历史版本）
│       ├── README.md
│       ├── main/               # v3.x旧版框架
│       ├── factor-library/     # 因子库历史
│       ├── 技术文档_v1.0.md
│       ├── 系统增强手册_v1.0.md
│       ├── 策略池_v1.0.md
│       └── 战术手册_v1.0.md
│
├── quant_system_v4/              # 💻 代码项目（开发中）
│   ├── docs/                   # 代码项目文档
│   ├── src/                    # 源代码
│   ├── config/                 # 配置
│   └── README.md
│
└── 量化策略专业分层方案_v3.0_专业机构标准版.md  # 📝 源文档（参考）
```

---

## 3. Layer 0-7 分层架构

| Layer | 名称 | 功能 | 文档位置 |
|-------|------|------|----------|
| Layer 0 | 数据层 | 数据采集、清洗、存储 | 02_FACTOR_LIBRARY/04_DATA_SOURCE/ |
| Layer 1 | 前置层 | 市场状态识别、信号预处理 | main/02_TACTICS/01_MARKET_REGIME/ |
| Layer 2 | Alpha 层 | Alpha 因子生成、预测 | main/02_TACTICS/02_ALPHA_FACTORS/ |
| Layer 3 | 风险层 | 风险因子建模、归因 | main/02_TACTICS/03_RISK_MANAGEMENT/ |
| Layer 4 | 组合层 | 组合优化、权重分配 | 04_TECHNICAL_SPECS/modules/ |
| Layer 5 | 执行层 | 订单生成、路由、执行 | main/02_TACTICS/04_EXECUTION/ |
| Layer 6 | 监控层 | 实时监控、告警 | main/02_TACTICS/05_RISK_CONTROL/ |
| Layer 7 | 归因层 | 绩效归因、分析 | main/02_TACTICS/06_PERFORMANCE/ + 07_ITERATION/ |

---

## 4. 文档职责划分

### 4.1 main/02_TACTICS/ - 战术模块

> 战术模块是 Layer 0-7 各层的**具体实现文档**

| 目录 | Layer | 内容 | 状态 |
|------|-------|------|------|
| 01_MARKET_REGIME/ | Layer 1 | 市场状态识别 | ✅ 活跃 |
| 02_ALPHA_FACTORS/ | Layer 2 | Alpha 因子实现 | ✅ 活跃 |
| 03_RISK_MANAGEMENT/ | Layer 3 | 风险管理 | ✅ 活跃 |
| 04_EXECUTION/ | Layer 4-5 | 交易执行 | ✅ 活跃 |
| 05_RISK_CONTROL/ | Layer 6 | 风控监控 | ✅ 活跃 |
| 06_PERFORMANCE/ | Layer 7 | 绩效归因 | ✅ 活跃 |
| 07_ITERATION/ | Layer 7 | 策略迭代 | ✅ 活跃 |

### 4.2 01_FRAMEWORK/ - 框架说明

> 框架说明是 Layer 0-7 的**架构定义文档**

| 文件 | 内容 | 状态 |
|------|------|------|
| README.md | Layer 0-7 架构说明 | ✅ 活跃 |

### 4.3 02_FACTOR_LIBRARY/ - 因子库

> 因子库是**独立研究模块**，包含5900+因子定义

详见：[02_FACTOR_LIBRARY/00_INDEX/README.md](./02_FACTOR_LIBRARY/00_INDEX/README.md)

### 4.3 03_TRADING_TACTICS/ - 交易策略

> 交易策略包含**量化策略库**和**战术参考**

| 目录 | 内容 | 状态 |
|------|------|------|
| strategy-pool/ | 策略池（S001-S120） | ✅ 活跃 |
| tactics/ | 战术参考（游资经验） | ✅ 活跃 |

### 4.4 04_TECHNICAL_SPECS/ - 技术规格

> 技术规格是**系统架构文档**，描述如何构建系统

| 目录 | 内容 | 状态 |
|------|------|------|
| architecture/ | 系统架构设计 | ✅ 活跃 |
| modules/ | 核心功能模块 | ✅ 活跃 |
| trading-rules/ | A股交易规则 | ✅ 活跃 |
| ai-optimization/ | AI参数优化 | ✅ 活跃 |

### 4.5 05_IMPLEMENTATION/ - 实施指南

> 实施指南包含**开发规范**和**迁移文档**

| 文档 | 内容 | 状态 |
|------|------|------|
| CODE_QUALITY.md | 代码质量标准 | ✅ 活跃 |
| CONFIG_STANDARD.md | 配置文件标准 | ✅ 活跃 |
| ERROR_HANDLING.md | 错误处理规范 | ✅ 活跃 |
| SECURITY.md | 安全规范 | ✅ 活跃 |
| LOGGING_STANDARD.md | 日志记录规范 | ✅ 活跃 |
| TESTING_STANDARD.md | 测试规范 | ✅ 活跃 |
| MIGRATION_GUIDE.md | 迁移指南 | ✅ 活跃 |

### 4.6 06_ARCHIVE/ - 归档

> 归档目录**仅保留历史版本**，不进行新开发

---

## 5. 编号体系

### 5.1 策略编号 (Sxxx)

```
S001 - S120  ← 量化策略池
```

| 文件 | 策略范围 |
|------|----------|
| retail-strategies-a.md | S001-S010 |
| retail-strategies-b.md | S011-S020 |
| ... | ... |
| retail-strategies-l.md | S106-S120 |

### 5.2 战术编号 (T.xx.xxx)

```
T.[Layer].[功能]_[序号]
```

| 前缀 | Layer | 示例 |
|------|-------|------|
| T.00. | Layer 0-1 | T.00.MR001 - 市场趋势识别 |
| T.01. | Layer 2 | T.01.TR001 - 趋势跟踪 |
| T.03. | Layer 3 | T.03.RM001 - 风险管理 |
| T.04. | Layer 5 | T.04.EX001 - 执行 |
| T.05. | Layer 6 | T.05.RC001 - 风控监控 |
| T.06. | Layer 7 | T.06.PF001 - 绩效归因 |
| T.08. | AI优化 | T.08.AI001 - AI优化 |

---

## 6. 代码状态管理

### 6.1 三种代码状态

| 状态 | 标记 | 含义 |
|------|------|------|
| 待实现 | `[PLACEHOLDER]` | 逻辑已设计，代码待实现 |
| 研究阶段 | `[STUDY_ONLY]` | 用于说明逻辑，不可运行 |
| 可执行 | `[EXECUTABLE]` | 代码已验证，可执行 |

> 详见：[CODE_STATUS.md](./CODE_STATUS.md) - 标记格式已更新为更清晰的格式

### 6.2 当前状态

| 目录 | 代码状态 | 说明 |
|------|----------|------|
| 01_FRAMEWORK/ | 示例代码 | 战术逻辑示例 |
| 02_FACTOR_LIBRARY/ | 参考代码 | 方法论参考 |
| 03_TRADING_TACTICS/ | 示例代码 | 策略逻辑示例 |
| 04_TECHNICAL_SPECS/ | 框架代码 | 系统架构设计 |
| quant_system_v4/src/ | 待实现 | 代码框架，待开发 |

> ⚠️ **当前所有代码均为示例代码，不可直接运行**

---

## 7. 核心规格索引

### 7.1 策略池规格

详见：[03_TRADING_TACTICS/strategy-pool/index.md](./03_TRADING_TACTICS/strategy-pool/index.md)

### 7.2 风险管理规格

详见：[main/02_TACTICS/03_RISK_MANAGEMENT/README.md](./main/02_TACTICS/03_RISK_MANAGEMENT/README.md)

### 7.3 战术规格索引

| Layer | 模块 | 索引文档 |
|-------|------|----------|
| Layer 1 | 市场状态 | [main/02_TACTICS/01_MARKET_REGIME/README.md](./main/02_TACTICS/01_MARKET_REGIME/README.md) |
| Layer 2 | Alpha 因子 | [main/02_TACTICS/02_ALPHA_FACTORS/README.md](./main/02_TACTICS/02_ALPHA_FACTORS/README.md) |
| Layer 3 | 风险管理 | [main/02_TACTICS/03_RISK_MANAGEMENT/README.md](./main/02_TACTICS/03_RISK_MANAGEMENT/README.md) |
| Layer 4-5 | 交易执行 | [main/02_TACTICS/04_EXECUTION/README.md](./main/02_TACTICS/04_EXECUTION/README.md) |
| Layer 6 | 风控监控 | [main/02_TACTICS/05_RISK_CONTROL/README.md](./main/02_TACTICS/05_RISK_CONTROL/README.md) |
| Layer 7 | 绩效归因 | [main/02_TACTICS/06_PERFORMANCE/README.md](./main/02_TACTICS/06_PERFORMANCE/README.md) |

---

## 8. 相关文档索引

| 类型 | 文档 | 说明 |
|------|------|------|
| **入口** | [README.md](./README.md) | 项目简介 |
| **规范** | [CODE_STATUS.md](./CODE_STATUS.md) | 代码状态规范 |
| **实施指南** | [05_IMPLEMENTATION/README.md](./05_IMPLEMENTATION/README.md) | 开发规范索引 |
| **策略池** | [03_TRADING_TACTICS/strategy-pool/index.md](./03_TRADING_TACTICS/strategy-pool/index.md) | 120 个策略 |
| **因子库** | [02_FACTOR_LIBRARY/00_INDEX/README.md](./02_FACTOR_LIBRARY/00_INDEX/README.md) | 5900+因子 |
| **框架说明** | [01_FRAMEWORK/README.md](./01_FRAMEWORK/README.md) | Layer 0-7 架构 |
| **战术模块** | [main/02_TACTICS/README.md](./main/02_TACTICS/README.md) | Layer 0-7 实现 |
| **技术架构** | [04_TECHNICAL_SPECS/architecture/json-schemas.md](./04_TECHNICAL_SPECS/architecture/json-schemas.md) | 系统架构 |
| **代码项目** | [../quant_system_v4/README.md](../quant_system_v4/README.md) | quant_system_v4 |

---

## 9. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0.1 | 2026-03-28 | 目录重组：分离框架说明 (01_FRAMEWORK/) 与战术实现 (main/02_TACTICS/)，解决目录结构混乱问题 |
| v4.0 | 2026-03-28 | 修正目录结构，统一编号体系，添加实施指南 |
| v3.2 | 2026-03-26 | 因子库手册 v3.2 |
| v3.1 | 2026-03-01 | 因子分类体系建立 |
