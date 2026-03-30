---
module_id: INDEX_001
version: 2.2
status: Active
last_updated: 2026-03-31
---

# 文档主索引

> 清风量化系统 v5.0 精简文档导航（个人开发版）
>
> **快速入口**: ⭐ 推荐阅读 [BLUEPRINT.md](BLUEPRINT.md) 了解完整系统蓝图

---

## 🎯 快速入口

### 我是新手
→ [00_OVERVIEW/README.md](00_OVERVIEW/README.md) - 系统总览（5分钟）

### 我要理解架构
→ [BLUEPRINT.md](BLUEPRINT.md) - 清风量化系统蓝图（推荐）
→ [01_FRAMEWORK/ARCHITECTURE.md](01_FRAMEWORK/ARCHITECTURE.md) - Layer 0-8统一架构

### 我要开发策略
→ [Strategy_Spec_S001.md](Strategy_Spec_S001.md) - 策略模板（30分钟）

### 我要查因子
→ [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子索引（10分钟）

### 我要部署系统
→ [05_IMPLEMENTATION/03_DEPLOYMENT/](05_IMPLEMENTATION/03_DEPLOYMENT/) - 部署指南（20分钟）

### 我遇到问题
→ [FAQ.md](FAQ.md) - 常见问题（5分钟）

---

## ⭐ 核心文档（必读）

| 文档 | 用途 | 阅读时间 |
|------|------|----------|
| [BLUEPRINT.md](BLUEPRINT.md) | ⭐ 清风量化系统蓝图（合并版） | 30分钟 |
| [System_Manifest.md](06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md) | 系统清单（归档） | - |
| [01_FRAMEWORK/ARCHITECTURE.md](01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-8统一架构 | 30分钟 |
| [AI_Permissions.md](AI_Permissions.md) | AI权限清单 | 10分钟 |
| [API_Contract.md](API_Contract.md) | 模块接口契约 | 15分钟 |
| [Strategy_Spec_S001.md](Strategy_Spec_S001.md) | 策略逻辑白皮书 | 30分钟 |

> **说明**: 7个蓝图文档已合并为 [BLUEPRINT.md](BLUEPRINT.md)，原始文档归档于 [06_ARCHIVE/main/BLUEPRINTS/](06_ARCHIVE/main/BLUEPRINTS/)

---

## 🤖 AI自主量化系统（终极目标）

> 核心: AI判断市场 → AI选择策略 → AI调整风控 → 人仅授权

### 开发规划

| 文档 | 用途 | 索引 |
|------|------|------|
| [BLUEPRINT.md](BLUEPRINT.md) | 清风量化系统蓝图 | - |
| [06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md](06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md) | 阶段性开发路线图 (Phase 0-6) | DEV.001 |
| [06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md](06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md) | AI研究Agent核心架构 | AI.AGENT.001 |

### AI模块详细设计

| 模块 | 文件位置 | 状态 |
|------|----------|------|
| A01 市场状态识别 | `src/ai/market_regime.py` | 📋 规划 |
| A02 策略路由器 | `src/ai/strategy_router.py` | 📋 规划 |
| A03 动态风控 | `src/ai/dynamic_risk.py` | 📋 规划 |
| A04 策略优化器 | `src/ai/strategy_optimizer.py` | 📋 规划 |
| A05 反馈学习闭环 | `src/ai/feedback_loop.py` | 📋 规划 |
| A06 授权确认界面 | `src/ai/approval_ui.py` | 📋 规划 |

---

## 📁 文档地图

### 00_OVERVIEW - 系统总览

| 文档 | 说明 |
|------|------|
| [README.md](00_OVERVIEW/README.md) | 系统总览 |
| [DATA_FLOW.md](00_OVERVIEW/DATA_FLOW.md) | 数据流图 |
| [VERSION_HISTORY.md](00_OVERVIEW/VERSION_HISTORY.md) | 版本历史 |

### 01_FRAMEWORK - 框架定义

| 文档 | 说明 |
|------|------|
| [README.md](01_FRAMEWORK/README.md) | 框架文档索引 |
| [ARCHITECTURE.md](01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-8统一架构 |
| [MARKET_REGIME.md](01_FRAMEWORK/MARKET_REGIME.md) | 市场状态识别 |
| [HUMAN_AI_FLOW.md](01_FRAMEWORK/HUMAN_AI_FLOW.md) | 人机协作流程 |
| [TECH_STACK.md](01_FRAMEWORK/TECH_STACK.md) | 技术栈选择 |

### 02_FACTOR_LIBRARY - 因子库 (v5.0架构)

| 目录/文档 | 说明 |
|------|------|
| [README.md](02_FACTOR_LIBRARY/README.md) | 因子库总览 |
| [00_INDEX/](02_FACTOR_LIBRARY/00_INDEX/) | 因子分类导航 |
| [01_METHODOLOGY/](02_FACTOR_LIBRARY/01_METHODOLOGY/) | 因子研究方法论 |
| [02_ALPHA_FACTORS_INDEX.md](02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) | 87个Alpha因子索引 |
| [03_RISK_FACTORS/](02_FACTOR_LIBRARY/03_RISK_FACTORS/) | 46个风险因子 |
| [04_DATA_SOURCE/](02_FACTOR_LIBRARY/04_DATA_SOURCE/) | 数据源说明 |
| [05_BACKTEST/](02_FACTOR_LIBRARY/05_BACKTEST/) | 回测报告 |
| [06_FACTOR_REGISTRY/](02_FACTOR_LIBRARY/06_FACTOR_REGISTRY/) | 因子注册 |
| [07_MONITORING/](02_FACTOR_LIBRARY/07_MONITORING/) | 监控中心 |

### 03_TRADING_TACTICS - 交易策略

| 目录/文档 | 说明 |
|------|------|
| [README.md](03_TRADING_TACTICS/README.md) | 策略池总览 |
| [INDEX.md](03_TRADING_TACTICS/INDEX.md) | 策略索引 |
| [01_STRATEGY_FRAMEWORK/](03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/) | 策略框架 |
| [03_ADVANCED_TACTICS/](03_TRADING_TACTICS/03_ADVANCED_TACTICS/) | 高级战术 |
| [04_YOUZI_STRATEGIES/](03_TRADING_TACTICS/04_YOUZI_STRATEGIES/) | 游资策略 |

### 04_EXECUTION - 执行引擎

| 目录/文档 | 说明 |
|------|------|
| [README.md](04_EXECUTION/README.md) | 执行总览 |
| [01_EVENT_ENGINE/](04_EXECUTION/01_EVENT_ENGINE/) | 事件驱动引擎 |
| [02_TRADE_EXECUTOR/](04_EXECUTION/02_TRADE_EXECUTOR/) | 交易执行 |
| [03_MONITORING/](04_EXECUTION/03_MONITORING/) | 监控模块 |

### 05_IMPLEMENTATION - 实施指南

| 目录/文档 | 说明 |
|------|------|
| [README.md](05_IMPLEMENTATION/README.md) | 实施指南总览 |
| [01_QUICKSTART/](05_IMPLEMENTATION/01_QUICKSTART/) | 快速开始（5分钟） |
| [02_DEVELOPMENT/](05_IMPLEMENTATION/02_DEVELOPMENT/) | 开发规范 |
| [03_DEPLOYMENT/](05_IMPLEMENTATION/03_DEPLOYMENT/) | 部署指南 |
| [04_OPERATIONS/](05_IMPLEMENTATION/04_OPERATIONS/) | 运维手册 |

### 06_ARCHIVE - 归档

| 目录/文档 | 说明 |
|------|------|
| [README.md](06_ARCHIVE/README.md) | 归档说明 |
| [main/v4_development/](06_ARCHIVE/main/v4_development/) | v4.0开发文档 |
| [over_engineered/](06_ARCHIVE/over_engineered/) | 过度工程化文档 |

### 07_RESEARCH - AI研究

| 目录/文档 | 说明 |
|------|------|
| [01_ENVIRONMENT/](07_RESEARCH/01_ENVIRONMENT/) | 研究环境 |
| [02_EXPLORATORY_ANALYSIS/](07_RESEARCH/02_EXPLORATORY_ANALYSIS/) | 探索性分析 |
| [03_PATTERN_RECOGNITION/](07_RESEARCH/03_PATTERN_RECOGNITION/) | 模式识别 |
| [04_EXPERIMENT_TRACKING/](07_RESEARCH/04_EXPERIMENT_TRACKING/) | 实验追踪 |

---

## 🔍 按用途查找

### 策略开发者
1. [Strategy_Spec_S001.md](Strategy_Spec_S001.md) - 策略模板
2. [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子库
3. [03_TRADING_TACTICS/](03_TRADING_TACTICS/) - 策略参考
4. [05_IMPLEMENTATION/02_DEVELOPMENT/](05_IMPLEMENTATION/02_DEVELOPMENT/) - 开发规范

### 系统构建
1. [BLUEPRINT.md](BLUEPRINT.md) - 清风量化系统蓝图
2. [01_FRAMEWORK/ARCHITECTURE.md](01_FRAMEWORK/ARCHITECTURE.md) - 统一架构
3. [05_IMPLEMENTATION/01_QUICKSTART/](05_IMPLEMENTATION/01_QUICKSTART/) - 快速开始

### 运维
1. [05_IMPLEMENTATION/03_DEPLOYMENT/](05_IMPLEMENTATION/03_DEPLOYMENT/) - 部署指南
2. [05_IMPLEMENTATION/04_OPERATIONS/](05_IMPLEMENTATION/04_OPERATIONS/) - 运维手册
3. [FAQ.md](FAQ.md) - 常见问题

### AI研究
1. [BLUEPRINT.md](BLUEPRINT.md) - AI研究框架（见第六章）
2. [07_RESEARCH/04_EXPERIMENT_TRACKING/](07_RESEARCH/04_EXPERIMENT_TRACKING/) - 实验追踪
3. [KNOWLEDGE_MANAGEMENT.md](KNOWLEDGE_MANAGEMENT.md) - 知识管理

---

## 📊 文档统计

- **总文档数**: ~100+（精简后）
- **核心文档**: 5个（必读）
- **一级目录**: 8个
- **因子数**: 133个（87 Alpha + 46 Risk）
- **策略数**: 120个（S001-S120）

---

## 📋 其他重要文档

| 文档 | 说明 | 用途 |
|------|------|------|
| [BLUEPRINT.md](BLUEPRINT.md) | 清风量化系统蓝图（合并版） | 完整蓝图参考 |
| [VERSIONING.md](VERSIONING.md) | 版本管理规范 | 版本控制参考 |
| [CODE_EXAMPLES.md](CODE_EXAMPLES.md) | 代码示例 | 开发参考 |
| [KNOWLEDGE_MANAGEMENT.md](KNOWLEDGE_MANAGEMENT.md) | 知识管理 | AI知识库管理 |

### 已归档文档

| 原文档 | 归档位置 | 说明 |
|--------|----------|------|
| System_Manifest.md | [06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md](06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md) | 已并入BLUEPRINT |
| UNIFIED_ARCHITECTURE.md | [01_FRAMEWORK/ARCHITECTURE.md](01_FRAMEWORK/ARCHITECTURE.md) | 已拆分 |
| ULTIMATE_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/01_ULTIMATE_BLUEPRINT.md](06_ARCHIVE/main/BLUEPRINTS/01_ULTIMATE_BLUEPRINT.md) | 已并入BLUEPRINT |
| DEPLOYMENT_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/02_DEPLOYMENT_BLUEPRINT.md](06_ARCHIVE/main/BLUEPRINTS/02_DEPLOYMENT_BLUEPRINT.md) | 已并入BLUEPRINT |
| SECURITY_BLUEPRINT.md | [06_ARCHIVE/main/BLUEPRINTS/03_SECURITY_BLUEPRINT.md](06_ARCHIVE/main/BLUEPRINTS/03_SECURITY_BLUEPRINT.md) | 已并入BLUEPRINT |
| AI_RESEARCH_FRAMEWORK.md | [06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md](06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md) | 已并入BLUEPRINT |
| DEVELOPMENT_ROADMAP.md | [06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md](06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md) | 已并入BLUEPRINT |
| FINAL_SYSTEM_AUDIT.md | [06_ARCHIVE/main/](06_ARCHIVE/main/) | 已归档 |
| RESEARCH_PIPELINE.md | [06_ARCHIVE/main/](06_ARCHIVE/main/) | 已归档 |

---

## 📖 完整地图

如需完整文档结构，请查看 [SITEMAP.md](SITEMAP.md)

---

**最后更新**: 2026-03-31
**维护者**: 清风量化系统
**版本**: v5.0 个人开发精简版
