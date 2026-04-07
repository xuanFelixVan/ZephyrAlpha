---
module_id: INDEX
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
version: 1.0.0
standard_type: 系统索引
applicable_scope: 全系?compliance_level: 顶级标准
parent_document: README.md
implementation_status: 活跃维护
owner: 系统架构?version: 1.1.1
module_id: INDEX_ROOT_001
created_date: 2026-04-02
last_updated: 2026-04-07
responsibility:
  - 风险预算核心功能、系统架构
  responsibility_layer: Layer 11
---
---
---

# 清风量化系统文档索引

> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v5.3  
> **架构**: 三级时间框架融合架构 + Layer 0-11完整架构  
> **最后更新**: 2026-04-07  
> **维护者**: 系统架构师

---

## 📋 文档职责说明

### 核心职责

本文档是**清风量化系统的导航入口文档**，负责：
- 提供快速导航和文档分类
- 推荐文档阅读路径
- 说明文档体系架构
- 为文档查找提供导航服务

### 职责边界

**负责**：
- ✅ 提供快速导航入口
- ✅ 提供文档分类和层级说明
- ✅ 推荐文档阅读路径
- ✅ 说明文档体系架构

**不负责**：
- ❌ 完整的模块清单（由System_Manifest.md负责）
- ❌ 详细的实施状态跟踪（由System_Manifest.md负责）
- ❌ 版本管理和变更历史（由System_Manifest.md负责）

### 对接文档

**相关文档**：
- [System_Manifest.md](./System_Manifest.md) - 系统清单账本（完整模块清单和实施状态）
- [SITEMAP.md](./SITEMAP.md) - 系统地图（详细文档路径）**维护?*: 系统架构?
---

## 🎯 快速导?
### 核心文档入口

| 文档类型 | 文档名称 | 说明 | 路径 |
|---------|---------|------|------|
| **系统蓝图** | [实施蓝图](./05_IMPLEMENTATION/BLUEPRINT.md) | 系统总体实施蓝图 | 核心架构 |
| **架构文档** | [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | 三级时间框架融合架构 | 架构设计 |
| **完整架构** | [统一架构 (Layer 0-11)](./01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-11完整架构体系 | 架构设计 |
| **因子?* | | 因子库系统清?| 因子管理 |
| **交易战术** | [交易战术索引](./03_TRADING_TACTICS/INDEX.md) | 交易策略和战术索?| 策略设计 |
| **审计标准** | [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) | 专业文档治理审计标准 | 审计规范 |

---

## 📚 文档体系架构

### 一级目录结?
```
docs/
├── 00_OVERVIEW/              # 系统概览
├── 00_RESOURCES/             # 资源文档
├── 01_FRAMEWORK/             # 框架设计
├── 02_FACTOR_LIBRARY/        # 因子?(Layer 2)
├── 03_TRADING_TACTICS/       # 交易战术 (Layer 3, 5)
├── 04_EXECUTION/             # 执行?(Layer 5, 6)
├── 05_IMPLEMENTATION/        # 实施?├── 06_ARCHIVE/               # 归档文档
├── 07_AI_REPORTING/          # 🆕 Layer 7: AI报告?├── 08_HUMAN_AI_INTERFACE/    # 🆕 Layer 8: 人机交互?├── 09_RESEARCH_INNOVATION/   # 🆕 Layer 9: 研究与创新层
├── 10_GOVERNANCE_COMPLIANCE/ # 🆕 Layer 10: 治理与合规层
└── 11_STRATEGIC_DECISION/    # 🆕 Layer 11: 战略决策?```

---

## 🏗?三级时间框架融合架构

### 架构概览

| 时间框架 | 层级 | 核心职责 | 关键文档 |
|---------|------|---------|---------|
| **宏观配置?* | Macro | 投资原则、风险预算、策略配?| [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) |
| **中观策略?* | Meso | 因子计算、信号生成、组合优?| |
| **微观执行?* | Micro | 订单执行、风险控制、实时监?| [交易战术索引](./03_TRADING_TACTICS/INDEX.md) |

### 架构文档

| 文档名称 | 说明 | 路径 |
|---------|------|------|
| **专业多时间框架架?* | 三级时间框架融合架构设计 | [PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) |
| **专业实施蓝图** | 专业量化机构实施蓝图 | [PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md](./01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) |
| **架构迁移计划** | 从Layer 0-11迁移到三级时间框?| [ARCHITECTURE_MIGRATION_PLAN.md](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md) |

---

## 🏛?Layer 0-11完整架构体系

### 架构层级

| Layer | 层级名称 | 核心职责 | 关键文档 |
|-------|---------|---------|---------|
| **Layer 11** | 战略决策?| 战略资产配置、风险预算分?| [战略决策层索引](./11_STRATEGIC_DECISION/INDEX.md) |
| **Layer 10** | 治理与合规层 | 内部控制、合规监?| [治理与合规层索引](./10_GOVERNANCE_COMPLIANCE/INDEX.md) |
| **Layer 9** | 研究与创新层 | AI虚拟研究实验室、创新孵化器 | [研究与创新层索引](./09_RESEARCH_INNOVATION/INDEX.md) |
| **Layer 8** | 人机交互?| 授权、监控、报?| [人机交互层索引](./08_HUMAN_AI_INTERFACE/INDEX.md) |
| **Layer 7** | AI报告?| 绩效归因、自动报?| [AI报告层索引](./07_AI_REPORTING/INDEX.md) |
| **Layer 6** | 组合优化?| 组合优化、风险模?| [统一架构](./01_FRAMEWORK/ARCHITECTURE.md) |
| **Layer 5** | 策略执行?| 策略运行、信号生?| [执行层索引](./04_EXECUTION/INDEX.md) |
| **Layer 4** | 机器学习?| AI预测、特征工?| [统一架构](./01_FRAMEWORK/ARCHITECTURE.md) |
| **Layer 3** | 舆情分析?| 新闻分析、情感分?| [统一架构](./01_FRAMEWORK/ARCHITECTURE.md) |
| **Layer 2** | Alpha因子?| 因子计算、因子库 | |
| **Layer 1** | 数据预处理层 | 数据清洗、标准化 | [统一架构](./01_FRAMEWORK/ARCHITECTURE.md) |
| **Layer 0** | 数据源层 | 数据采集、数据接?| [统一架构](./01_FRAMEWORK/ARCHITECTURE.md) |

### 顶层架构蓝图 (Layer 7-11) 🆕

| Layer | 层级名称 | 核心文档 | 重要?|
|-------|---------|---------|--------|
| **Layer 11** | 战略决策?| [战略决策层蓝图](./11_STRATEGIC_DECISION/BLUEPRINT.md) | ⭐⭐⭐⭐?|
| **Layer 10** | 治理与合规层 | [治理与合规层蓝图](./10_GOVERNANCE_COMPLIANCE/BLUEPRINT.md) | ⭐⭐⭐⭐?|
| **Layer 9** | 研究与创新层 | [研究与创新层蓝图](./09_RESEARCH_INNOVATION/BLUEPRINT.md) | ⭐⭐⭐⭐?|
| **Layer 8** | 人机交互?| [人机交互层蓝图](./01_FRAMEWORK/HUMAN_AI_INTERACTION_BLUEPRINT.md) | ⭐⭐⭐⭐?|
| **Layer 7** | AI报告?| [AI报告层蓝图](./07_AI_REPORTING/BLUEPRINT.md) | ⭐⭐⭐⭐?|

---

## 📖 核心模块文档

### 1. 框架设计 (01_FRAMEWORK)

| 文档名称 | 说明 | 重要?|
|---------|------|--------|
| [统一架构 (Layer 0-11)](./01_FRAMEWORK/ARCHITECTURE.md) | **🆕** Layer 0-11完整架构体系 | ⭐⭐⭐⭐?|
| [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | 三级时间框架融合架构 | ⭐⭐⭐⭐?|
| [专业实施蓝图](./01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) | 专业量化机构实施蓝图 | ⭐⭐⭐⭐?|
| [研究与创新层蓝图](./01_FRAMEWORK/RESEARCH_INNOVATION_LAYER_BLUEPRINT.md) | **🆕 Layer 9** AI虚拟研究实验?| ⭐⭐⭐⭐?|
| [治理与合规层蓝图](./01_FRAMEWORK/GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md) | **🆕 Layer 10** 内部控制体系 | ⭐⭐⭐⭐?|
| [战略决策层蓝图](./01_FRAMEWORK/STRATEGIC_DECISION_LAYER_BLUEPRINT.md) | **🆕 Layer 11** 战略资产配置 | ⭐⭐⭐⭐?|
| [架构迁移计划](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md) | 架构迁移计划 | ⭐⭐⭐⭐ |
| [技术栈](./01_FRAMEWORK/TECH_STACK.md) | 技术栈选择 | ⭐⭐⭐⭐ |

### 2. 因子?(02_FACTOR_LIBRARY)

| 文档名称 | 说明 | 重要?|
|---------|------|--------|
| | 因子库系统清?| ⭐⭐⭐⭐?|
| | 因子注册?| ⭐⭐⭐⭐?|
| [因子计算框架](./02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_CALCULATION_FRAMEWORK.md) | 因子计算框架 | ⭐⭐⭐⭐ |
| | 数据源接口文?| ⭐⭐⭐⭐ |

### 3. 交易战术 (03_TRADING_TACTICS)

| 文档名称 | 说明 | 重要?|
|---------|------|--------|
| [交易战术索引](./03_TRADING_TACTICS/INDEX.md) | 交易战术总索?| ⭐⭐⭐⭐?|
| [策略框架](./03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/overview.md) | 策略框架概览 | ⭐⭐⭐⭐ |
| | 风险规则引擎 | ⭐⭐⭐⭐ |

### 4. 实施?(05_IMPLEMENTATION)

| 文档名称 | 说明 | 重要?|
|---------|------|--------|
| [实施蓝图](./05_IMPLEMENTATION/BLUEPRINT.md) | 系统实施蓝图 | ⭐⭐⭐⭐?|
| [开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md) | 开发标?| ⭐⭐⭐⭐ |
| [测试标准](./05_IMPLEMENTATION/02_DEVELOPMENT/TESTING_STANDARD.md) | 测试标准 | ⭐⭐⭐⭐ |

### 5. 审计系统 (09_AUDIT)

| 文档名称 | 说明 | 重要?|
|---------|------|--------|
| [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) | 专业文档治理审计指南 | ⭐⭐⭐⭐?|
| [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md) | 审计检查清?| ⭐⭐⭐⭐ |
| [审计标准](./09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) | 审计标准 | ⭐⭐⭐⭐ |

---

## 🔍 按角色导?
### 系统架构?
**核心文档**?1. [统一架构 (Layer 0-11)](./01_FRAMEWORK/ARCHITECTURE.md)
2. [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)
3. [专业实施蓝图](./01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)
4. [架构迁移计划](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md)

### 研究与创新负责人 🆕

**核心文档**：
1. [研究与创新层蓝图](./09_RESEARCH_INNOVATION/BLUEPRINT.md)
2. 3. [因子计算框架](./02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_CALCULATION_FRAMEWORK.md)

### 治理与合规负责人 🆕

**核心文档**：
1. [治理与合规层蓝图](./10_GOVERNANCE_COMPLIANCE/BLUEPRINT.md)
2. 3. [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)

### 战略决策负责人 🆕

**核心文档**：
1. [战略决策层蓝图](./11_STRATEGIC_DECISION/BLUEPRINT.md)
2. [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)
3. ### 因子研究?
**核心文档**?1. 2. [因子计算框架](./02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_CALCULATION_FRAMEWORK.md)
3. ### 策略开发人?
**核心文档**?1. [交易战术索引](./03_TRADING_TACTICS/INDEX.md)
2. [策略框架](./03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/overview.md)
3. [开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)

### 风险管理人员

**核心文档**?1. 2. [风险规则蓝图](./03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md)
3. [风险报告](./03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md)

### 审计人员

**核心文档**?1. [文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
2. [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)
3. [审计标准](./09_AUDIT/STANDARDS/AUDIT_STANDARDS.md)
4. [文档治理长效机制](./09_AUDIT/STANDARDS/DOC_GOVERNANCE_MECHANISM.md)

---

## 📊 文档统计

### 文档数量统计

| 目录 | 文档数量 | 说明 |
|------|---------|------|
| **01_FRAMEWORK** | 20+ | 框架设计文档 |
| **02_FACTOR_LIBRARY** | 50+ | 因子库文?|
| **03_TRADING_TACTICS** | 30+ | 交易战术文档 |
| **04_EXECUTION** | 20+ | 执行层文?|
| **05_IMPLEMENTATION** | 100+ | 实施层文?|
| **09_AUDIT** | 30+ | 审计系统文档 |
| **总计** | **250+** | 全系统文?|

### 架构一致性统?
| 指标 | 数量 | 说明 |
|------|------|------|
| **三级时间框架文档** | 32?| 包含新架构关键词的文?|
| **Layer 9-11蓝图** | 3?| 新增顶层架构蓝图 |
| **归档旧架构文?* | 4?| Layer 0文档已归?|
| **架构迁移完成?* | 76% | 仍有114个文件包含旧架构残留 |

---

## 🚀 快速开?
### 📖 文档阅读路径

| 角色 | 推荐阅读路径 |
|------|-------------|
| **新用?* | 系统概览 ?架构设计 ?实施蓝图 ?开发标?|
| **系统架构?* | 统一架构 ?专业架构 ?实施蓝图 ?架构迁移计划 |
| **研究负责?* | 研究与创新层蓝图 ?因子注册??因子计算框架 |
| **治理负责?* | 治理与合规层蓝图 ?风险规则引擎 ?审计指南 |
| **战略负责?* | 战略决策层蓝??专业架构 ?风险规则引擎 |
| **因子研究?* | 因子注册??因子计算框架 ?数据源接??回测标准 |
| **策略开发人?* | 策略框架 ?开发标??测试标准 ?部署计划 |
| **风险管理人员** | 风险规则引擎 ?风险规则蓝图 ?风险报告 |
| **审计人员** | 审计指南 ?审计检查清??审计标准 |

### 新用户入门（5步快速上手）

1. **阅读系统概览**：[系统概览](00_OVERVIEW/INDEX.md)
2. **了解架构设计**：[统一架构 (Layer 0-11)](./01_FRAMEWORK/ARCHITECTURE.md)
3. **查看实施蓝图**：[实施蓝图](./05_IMPLEMENTATION/BLUEPRINT.md)
4. **配置开发环?*：5. **开始开?*：[开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)

### 开发人员快速开?
1. **环境配置**：2. **学习路径**：[学习路径](./05_IMPLEMENTATION/01_QUICKSTART/LEARNING_PATH.md)
3. **开发规?*：[开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)
4. **测试规范**：[测试标准](./05_IMPLEMENTATION/02_DEVELOPMENT/TESTING_STANDARD.md)

---

## 🔗 重要链接

### 外部资源

| 资源名称 | 说明 | 链接 |
|---------|------|------|
| **GitHub仓库** | 系统源代码仓?| [GitHub](https://github.com/your-repo) |
| **问题跟踪** | 问题跟踪系统 | [Issues](https://github.com/your-repo/issues) |
| **文档网站** | 在线文档网站 | [Docs](https://your-docs-site) |

### 内部工具

| 工具名称 | 说明 | 路径 |
|---------|------|------|
| **审计工具** | 文档审计工具 | [scripts/document_auditor.py](../scripts/document_auditor.py) |
| **链接修复** | 链接修复工具 | [scripts/link_fixer.py](../scripts/link_fixer.py) |
| **架构分析** | 架构分析工具 | [scripts/architecture_analyzer.py](../scripts/architecture_analyzer.py) |

---

## 📰 更新日志

### 2026-04-07: Layer 4文档治理修复

**修复概要**:
- 审计文档数: 145个
- 发现问题数: 353个
- 修复问题数: 179个
- 修复完成率: 60.7%

**主要修复**:
- ✅ 职责不清修复: 121个文档添加明确职责描述
- ✅ 死链接修复: 41个链接已修复
- ✅ 文件命名规范化: 11个文件重命名
- ✅ Layer归属修正: 6个文档归属已更新

**相关文档**:



---

## 📝 文档维护

### 文档更新流程

1. **创建文档**：使用[文档模板](./09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md)
2. **质量检?*：使用[文档质量门](./05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/06_CHECKLISTS/DOCUMENT_QUALITY_GATE.md)
3. **提交审核**：提交到审核流程
4. **更新索引**：更新相关索引文?
### 文档治理原则

遵循专业量化机构五大原则?1. **职责驱动原则**：每个文档只承担一种核心职?2. **索引完备性原?*：所有活跃文档必须被索引
3. **版本隔离原则**：同一内容只保留最新版?4. **文档代码对应原则**：文档必须反映实际代码状?5. **命名规范原则**：使用标准化的命名体?
---

## 📞 联系方式

| 角色 | 联系方式 | 职责 |
|------|---------|------|
| **系统架构?* | architect@example.com | 架构设计和维?|
| **文档维护?* | docs@example.com | 文档维护和更?|
| **审计人员** | audit@example.com | 文档审计和质量控?|

---

**文档版本**: v1.1.0  
**创建日期**: 2026-04-02  
**最后更?*: 2026-04-03  
**维护?*: 系统架构? 
**状?*: ?活跃维护

- [ZephyrAlpha API文档](./API_README.md) - 系统文档
