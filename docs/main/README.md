# main - 战术模块

> Layer 0-7 战术实现
>
> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：✅ 活跃

---

## 1. 概述

`main/` 目录是清风量化交易系统 4.0 的**战术实现模块**，包含 Layer 0-7 分层架构中各层的具体战术实现文档。

---

## 2. 目录结构

```
main/
└── 02_TACTICS/          # 战术手册（Layer 0-7 实现）
    ├── README.md
    ├── 01_MARKET_REGIME/    # Layer 1: 市场状态
    ├── 02_ALPHA_FACTORS/   # Layer 2: Alpha 因子
    ├── 03_RISK_MANAGEMENT/ # Layer 3: 风险管理
    ├── 04_EXECUTION/        # Layer 4-5: 执行
    ├── 05_RISK_CONTROL/     # Layer 6: 风控监控
    ├── 06_PERFORMANCE/      # Layer 7: 绩效归因
    └── 07_ITERATION/       # Layer 7: 策略迭代
```

---

## 3. 与框架的关系

```
docs/01_FRAMEWORK/README.md   ← 📐 框架说明（Layer 0-7 架构定义）
      ↓
docs/main/02_TACTICS/         ← 🎯 战术实现（具体实现文档）
```

- **01_FRAMEWORK**: 定义 Layer 0-7 分层架构的职责和输入输出
- **main/02_TACTICS**: 提供各 Layer 的具体战术实现文档

---

## 4. 模块导航

| 模块 | Layer | 描述 | 战术数 | 状态 |
|------|-------|------|--------|------|
| [02_TACTICS/01_MARKET_REGIME/](./02_TACTICS/01_MARKET_REGIME/) | Layer 1 | 市场状态识别 | 5 | ✅ 活跃 |
| [02_TACTICS/02_ALPHA_FACTORS/](./02_TACTICS/02_ALPHA_FACTORS/) | Layer 2 | Alpha 因子战术 | 20+ | ✅ 活跃 |
| [02_TACTICS/03_RISK_MANAGEMENT/](./02_TACTICS/03_RISK_MANAGEMENT/) | Layer 3 | 风险管理 | 2 | ✅ 活跃 |
| [02_TACTICS/04_EXECUTION/](./02_TACTICS/04_EXECUTION/) | Layer 4-5 | 交易执行 | 7 | ✅ 活跃 |
| [02_TACTICS/05_RISK_CONTROL/](./02_TACTICS/05_RISK_CONTROL/) | Layer 6 | 风控监控 | 2 | ✅ 活跃 |
| [02_TACTICS/06_PERFORMANCE/](./02_TACTICS/06_PERFORMANCE/) | Layer 7 | 绩效归因 | 1 | ✅ 活跃 |
| [02_TACTICS/07_ITERATION/](./02_TACTICS/07_ITERATION/) | Layer 7 | 策略迭代 | 1 | ✅ 活跃 |

---

## 5. 关联文档

| 文档 | 说明 |
|------|------|
| [../SPEC.md](../SPEC.md) | 主规格文档 |
| [../01_FRAMEWORK/README.md](../01_FRAMEWORK/README.md) | Layer 0-7 框架说明 |
| [../02_FACTOR_LIBRARY/](../02_FACTOR_LIBRARY/) | 因子库 |
| [../03_TRADING_TACTICS/](../03_TRADING_TACTICS/) | 交易策略池 |
| [../04_TECHNICAL_SPECS/](../04_TECHNICAL_SPECS/) | 技术规格 |

---

## 6. 版本信息

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，基于 Layer 0-7 架构 |
| v4.0.1 | 2026-03-28 | 目录重组，从 01_FRAMEWORK 迁移战术模块 |