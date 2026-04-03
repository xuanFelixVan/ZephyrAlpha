---
standard_type: 系统索引
applicable_scope: 全系统
compliance_level: 顶级标准
parent_document: ../README.md
implementation_status: 活跃维护
owner: 系统架构师
version: 1.0.0
module_id: DOC_INDEX_ROOT
created_date: 2026-04-02
last_updated: 2026-04-02
---

# 清风量化系统文档索引

> **版本**: v5.1  
> **架构**: 三级时间框架融合架构  
> **最后更新**: 2026-04-03  
> **维护者**: 系统架构师

---

## 🎯 快速导航

### 核心文档入口

| 文档类型 | 文档名称 | 说明 | 路径 |
|---------|---------|------|------|
| **系统蓝图** | [实施蓝图](./05_IMPLEMENTATION/BLUEPRINT.md) | 系统总体实施蓝图 | 核心架构 |
| **架构文档** | [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | 三级时间框架融合架构 | 架构设计 |
| **因子库** | [因子库系统清单](./02_FACTOR_LIBRARY/System_Manifest.md) | 因子库系统清单 | 因子管理 |
| **交易战术** | [交易战术索引](./03_TRADING_TACTICS/INDEX.md) | 交易策略和战术索引 | 策略设计 |
| **审计标准** | [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) | 专业文档治理审计标准 | 审计规范 |

---

## 📚 文档体系架构

### 一级目录结构

```
docs/
├── 00_OVERVIEW/          # 系统概览
├── 00_RESOURCES/         # 资源文档
├── 01_FRAMEWORK/         # 框架设计
├── 02_FACTOR_LIBRARY/    # 因子库
├── 03_TRADING_TACTICS/   # 交易战术
├── 04_EXECUTION/         # 执行层
├── 05_IMPLEMENTATION/    # 实施层
├── 06_ARCHIVE/           # 归档文档
├── 07_RESEARCH/          # 研究支持
├── 09_AUDIT/             # 审计系统
└── 10_AI_WORKFLOW/       # AI工作流
```

---

## 🏗️ 三级时间框架融合架构

### 架构概览

| 时间框架 | 层级 | 核心职责 | 关键文档 |
|---------|------|---------|---------|
| **宏观配置层** | Macro | 投资原则、风险预算、策略配置 | [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) |
| **中观策略层** | Meso | 因子计算、信号生成、组合优化 | [因子库系统清单](./02_FACTOR_LIBRARY/System_Manifest.md) |
| **微观执行层** | Micro | 订单执行、风险控制、实时监控 | [交易战术索引](./03_TRADING_TACTICS/INDEX.md) |

### 架构文档

| 文档名称 | 说明 | 路径 |
|---------|------|------|
| **专业多时间框架架构** | 三级时间框架融合架构设计 | [PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) |
| **专业实施蓝图** | 专业量化机构实施蓝图 | [PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md](./01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) |
| **架构迁移计划** | 从Layer 0-8迁移到三级时间框架 | [ARCHITECTURE_MIGRATION_PLAN.md](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md) |

---

## 📖 核心模块文档

### 1. 框架设计 (01_FRAMEWORK)

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | 三级时间框架融合架构 | ⭐⭐⭐⭐⭐ |
| [专业实施蓝图](./01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) | 专业量化机构实施蓝图 | ⭐⭐⭐⭐⭐ |
| [架构迁移计划](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md) | 架构迁移计划 | ⭐⭐⭐⭐ |
| [技术栈](./01_FRAMEWORK/TECH_STACK.md) | 技术栈选择 | ⭐⭐⭐⭐ |

### 2. 因子库 (02_FACTOR_LIBRARY)

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [系统清单](./02_FACTOR_LIBRARY/System_Manifest.md) | 因子库系统清单 | ⭐⭐⭐⭐⭐ |
| [因子注册表](./02_FACTOR_LIBRARY/01_METHODOLOGY/FACTOR_REGISTRY.md) | 因子注册表 | ⭐⭐⭐⭐⭐ |
| [因子计算框架](./02_FACTOR_LIBRARY/01_METHODOLOGY/FACTOR_CALCULATION_FRAMEWORK.md) | 因子计算框架 | ⭐⭐⭐⭐ |
| [数据源接口](./02_FACTOR_LIBRARY/04_DATA_SOURCE/README.md) | 数据源接口文档 | ⭐⭐⭐⭐ |

### 3. 交易战术 (03_TRADING_TACTICS)

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [交易战术索引](./03_TRADING_TACTICS/INDEX.md) | 交易战术总索引 | ⭐⭐⭐⭐⭐ |
| [策略框架](./03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/overview.md) | 策略框架概览 | ⭐⭐⭐⭐ |
| [风险规则](./03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md) | 风险规则引擎 | ⭐⭐⭐⭐ |

### 4. 实施层 (05_IMPLEMENTATION)

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [实施蓝图](./05_IMPLEMENTATION/BLUEPRINT.md) | 系统实施蓝图 | ⭐⭐⭐⭐⭐ |
| [开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md) | 开发标准 | ⭐⭐⭐⭐ |
| [测试标准](./05_IMPLEMENTATION/02_DEVELOPMENT/TESTING_STANDARD.md) | 测试标准 | ⭐⭐⭐⭐ |

### 5. 审计系统 (09_AUDIT)

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) | 专业文档治理审计指南 | ⭐⭐⭐⭐⭐ |
| [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md) | 审计检查清单 | ⭐⭐⭐⭐ |
| [审计标准](./09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) | 审计标准 | ⭐⭐⭐⭐ |

---

## 🔍 按角色导航

### 系统架构师

**核心文档**：
1. [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)
2. [专业实施蓝图](./01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)
3. [架构迁移计划](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md)

### 因子研究员

**核心文档**：
1. [因子注册表](./02_FACTOR_LIBRARY/01_METHODOLOGY/FACTOR_REGISTRY.md)
2. [因子计算框架](./02_FACTOR_LIBRARY/01_METHODOLOGY/FACTOR_CALCULATION_FRAMEWORK.md)
3. [数据源接口](./02_FACTOR_LIBRARY/04_DATA_SOURCE/README.md)

### 策略开发人员

**核心文档**：
1. [交易战术索引](./03_TRADING_TACTICS/INDEX.md)
2. [策略框架](./03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/overview.md)
3. [开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)

### 风险管理人员

**核心文档**：
1. [风险规则引擎](./03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md)
2. [风险规则蓝图](./03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md)
3. [风险报告](./03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md)

### 审计人员

**核心文档**：
1. [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
2. [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)
3. [审计标准](./09_AUDIT/STANDARDS/AUDIT_STANDARDS.md)
4. [文档治理长效机制](./09_AUDIT/STANDARDS/DOC_GOVERNANCE_MECHANISM.md)

---

## 📊 文档统计

### 文档数量统计

| 目录 | 文档数量 | 说明 |
|------|---------|------|
| **01_FRAMEWORK** | 15+ | 框架设计文档 |
| **02_FACTOR_LIBRARY** | 50+ | 因子库文档 |
| **03_TRADING_TACTICS** | 30+ | 交易战术文档 |
| **04_EXECUTION** | 20+ | 执行层文档 |
| **05_IMPLEMENTATION** | 100+ | 实施层文档 |
| **09_AUDIT** | 30+ | 审计系统文档 |
| **总计** | **250+** | 全系统文档 |

### 架构一致性统计

| 指标 | 数值 | 说明 |
|------|------|------|
| **三级时间框架文档** | 32个 | 包含新架构关键词的文档 |
| **归档旧架构文档** | 4个 | Layer 0文档已归档 |
| **架构迁移完成度** | 76% | 仍有114个文件包含旧架构残留 |

---

## 🚀 快速开始

### 📖 文档阅读路径

| 角色 | 推荐阅读路径 |
|------|-------------|
| **新用户** | 系统概览 → 架构设计 → 实施蓝图 → 开发标准 |
| **系统架构师** | 专业架构 → 实施蓝图 → 架构迁移计划 → 审计标准 |
| **因子研究员** | 因子注册表 → 因子计算框架 → 数据源接口 → 回测标准 |
| **策略开发人员** | 策略框架 → 开发标准 → 测试标准 → 部署计划 |
| **风险管理人员** | 风险规则引擎 → 风险规则蓝图 → 风险报告 |
| **审计人员** | 审计指南 → 审计检查清单 → 审计标准 |

### 新用户入门（5步快速上手）

1. **阅读系统概览**：[系统概览](./00_OVERVIEW/README.md)
2. **了解架构设计**：[专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)
3. **查看实施蓝图**：[实施蓝图](./05_IMPLEMENTATION/BLUEPRINT.md)
4. **配置开发环境**：[开发环境配置](./05_IMPLEMENTATION/01_QUICKSTART/dev-setup.md)
5. **开始开发**：[开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)

### 开发人员快速开始

1. **环境配置**：[开发环境配置](./05_IMPLEMENTATION/01_QUICKSTART/dev-setup.md)
2. **学习路径**：[学习路径](./05_IMPLEMENTATION/01_QUICKSTART/LEARNING_PATH.md)
3. **开发规范**：[开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)
4. **测试规范**：[测试标准](./05_IMPLEMENTATION/02_DEVELOPMENT/TESTING_STANDARD.md)

---

## 🔗 重要链接

### 外部资源

| 资源名称 | 说明 | 链接 |
|---------|------|------|
| **GitHub仓库** | 系统源代码仓库 | [GitHub](https://github.com/your-repo) |
| **问题跟踪** | 问题跟踪系统 | [Issues](https://github.com/your-repo/issues) |
| **文档网站** | 在线文档网站 | [Docs](https://your-docs-site) |

### 内部工具

| 工具名称 | 说明 | 路径 |
|---------|------|------|
| **审计工具** | 文档审计工具 | [scripts/document_auditor.py](../scripts/document_auditor.py) |
| **链接修复** | 链接修复工具 | [scripts/link_fixer.py](../scripts/link_fixer.py) |
| **架构分析** | 架构分析工具 | [scripts/architecture_analyzer.py](../scripts/architecture_analyzer.py) |

---

## 📝 文档维护

### 文档更新流程

1. **创建文档**：使用[文档模板](./09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md)
2. **质量检查**：使用[文档质量门](./05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/06_CHECKLISTS/DOCUMENT_QUALITY_GATE.md)
3. **提交审核**：提交到审核流程
4. **更新索引**：更新相关索引文件

### 文档治理原则

遵循专业量化机构五大原则：
1. **职责驱动原则**：每个文档只承担一种核心职责
2. **索引完备性原则**：所有活跃文档必须被索引
3. **版本隔离原则**：同一内容只保留最新版本
4. **文档代码对应原则**：文档必须反映实际代码状态
5. **命名规范原则**：使用标准化的命名体系

---

## 📞 联系方式

| 角色 | 联系方式 | 职责 |
|------|---------|------|
| **系统架构师** | architect@example.com | 架构设计和维护 |
| **文档维护者** | docs@example.com | 文档维护和更新 |
| **审计人员** | audit@example.com | 文档审计和质量控制 |

---

**文档版本**: v1.0.0  
**创建日期**: 2026-04-02  
**最后更新**: 2026-04-02  
**维护者**: 系统架构师  
**状态**: ✅ 活跃维护
