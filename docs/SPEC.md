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
docs/
├── SPEC.md                    # ⭐ 统一入口文档（本文档）
├── CODE_STATUS.md             # 代码状态标记规范
├── README.md                  # 项目README
│
├── technical-specs/           # 技术规格（系统架构）
│   ├── architecture/          # 系统架构
│   ├── modules/              # 核心模块
│   ├── trading-rules/        # 交易规则
│   └── ai-optimization/      # AI优化
│
├── trading-tactics/          # 交易战术
│   ├── strategy-pool/        # 策略池
│   └── tactics/             # 战术库
│
├── factor-library/           # 因子库（独立模块）
│   ├── 00_INDEX/            # 索引导航
│   ├── 01_METHODOLOGY/       # 研究方法论
│   ├── 02_ALPHA_FACTORS/    # Alpha因子
│   ├── 03_RISK_FACTORS/    # 风险因子
│   ├── 04_DATA_SOURCE/      # 数据源
│   ├── 05_BACKTEST/         # 回测报告
│   ├── 06_ARCHIVE/         # 归档
│   └── 10_MANUAL/          # 手册
│
├── main/                     # ⚠️ 旧版框架（保留参考）
│   ├── 01_FRAMEWORK/       # 旧版框架
│   ├── 02_TACTICS/         # 旧版战术
│   └── 03_ARCHIVE/         # 旧版归档
│
└── archive/                  # 统一归档
    ├── 技术文档_v1.0.md
    ├── 系统增强手册_v1.0.md
    ├── 策略池_v1.0.md
    └── 战术手册_v1.0.md
```

---

## 3. Layer 0-7 分层架构

| Layer | 名称 | 功能 | 状态 |
|-------|------|------|------|
| Layer 0 | 数据层 | 数据采集、清洗、存储 | 研究阶段 |
| Layer 1 | 前置层 | 市场状态识别、信号预处理 | 研究阶段 |
| Layer 2 | Alpha层 | Alpha因子生成、预测 | 研究阶段 |
| Layer 3 | 风险层 | 风险因子建模、归因 | 研究阶段 |
| Layer 4 | 组合层 | 组合优化、权重分配 | 研究阶段 |
| Layer 5 | 执行层 | 订单生成、路由、执行 | 回测阶段 |
| Layer 6 | 监控层 | 实时监控、告警 | 回测阶段 |
| Layer 7 | 归因层 | 绩效归因、分析 | 回测阶段 |

---

## 4. 模块说明

### 4.1 technical-specs（技术规格）

> 系统级技术文档，描述**如何构建系统**

| 目录 | 内容 | 状态 |
|------|------|------|
| architecture/ | 系统架构设计 | 框架设计 |
| modules/ | 核心功能模块 | 框架设计 |
| trading-rules/ | A股交易规则 | 参考文档 |
| ai-optimization/ | AI参数优化 | 框架设计 |

### 4.2 trading-tactics（交易战术）

> 策略级业务文档，描述**做什么策略**

| 目录 | 内容 | 状态 |
|------|------|------|
| strategy-pool/ | 策略池管理 | 研究阶段 |
| tactics/ | 战术库 | 研究阶段 |

### 4.3 factor-library（因子库）

> 独立模块，专注于因子研究

详见：[factor-library/00_INDEX/README.md](./factor-library/00_INDEX/README.md)

### 4.4 main（旧版框架）

> ⚠️ **已废弃，仅保留参考**
>
> 本目录包含旧版（v3.x）框架文档，已被新架构取代。
> 新开发请使用 technical-specs 和 trading-tactics。

---

## 5. 代码状态管理

### 5.1 三种代码状态

| 状态 | 标记 | 含义 |
|------|------|------|
| 待实现 | `{# TODO: 回测阶段实现}` | 逻辑已设计，代码待实现 |
| 示例代码 | `{# EXAMPLE: 研究阶段示例}` | 用于说明逻辑，不可运行 |
| 可执行 | `{# EXECUTABLE: 已验证可运行}` | 代码已验证，可执行 |

### 5.2 当前状态

| 目录 | 代码状态 | 说明 |
|------|----------|------|
| technical-specs/ | 框架代码 | 系统架构说明 |
| trading-tactics/ | 示例代码 | 策略逻辑示例 |
| factor-library/01_METHODOLOGY/ | 参考代码 | 方法论参考 |

> ⚠️ **当前所有代码均为示例代码，不可直接运行**

详见：[CODE_STATUS.md](./CODE_STATUS.md)

---

## 6. 核心规格

### 6.1 策略池规格

详见：[trading-tactics/strategy-pool/index.md](./trading-tactics/strategy-pool/index.md)

### 6.2 风险管理规格

详见：[technical-specs/modules/risk-management.md](./technical-specs/modules/risk-management.md)

### 6.3 接口规格

详见：[technical-specs/architecture/json-schemas.md](./technical-specs/architecture/json-schemas.md)

---

## 7. 相关文档索引

| 类型 | 文档 | 说明 |
|------|------|------|
| **入门** | [README.md](./README.md) | 项目简介 |
| **规范** | [CODE_STATUS.md](./CODE_STATUS.md) | 代码状态规范 |
| **策略** | [trading-tactics/strategy-pool/index.md](./trading-tactics/strategy-pool/index.md) | 策略池 |
| **因子** | [factor-library/00_INDEX/README.md](./factor-library/00_INDEX/README.md) | 因子库 |
| **架构** | [technical-specs/architecture/json-schemas.md](./technical-specs/architecture/json-schemas.md) | 技术架构 |

---

## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 增加代码状态说明，明确开发阶段，更新目录结构 |
| v3.2 | 2026-03-26 | 因子库手册v3.2 |
| v3.1 | 2026-03-01 | 因子分类体系建立 |
