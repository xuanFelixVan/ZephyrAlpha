---
module_id: INDEX_001
version: 2.1
status: Active
last_updated: 2026-03-29
---

# 文档主索引

> 清风量化系统 v5.0 精简文档导航（个人开发版）
>
> **快速入口**: ⭐ 推荐阅读 [System_Manifest.md](System_Manifest.md) 了解完整系统架构

---

## 🎯 快速入口

### 我是新手
→ [00_OVERVIEW/README.md](00_OVERVIEW/README.md) - 系统总览（5分钟）

### 我要理解架构
→ [System_Manifest.md](System_Manifest.md) - 系统清单（15分钟）
→ [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md) - Layer 0-8统一架构

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
| [System_Manifest.md](System_Manifest.md) | 系统清单、架构、模块映射 | 15分钟 |
| [AI_Research_Framework.md](AI_Research_Framework.md) | AI主力模式架构决策 | 15分钟 |
| [Strategy_Spec_S001.md](Strategy_Spec_S001.md) | 策略逻辑白皮书 | 30分钟 |
| [AI_Permissions.md](AI_Permissions.md) | AI权限清单 | 10分钟 |
| [API_Contract.md](API_Contract.md) | 模块接口契约 | 15分钟 |

---

## 🤖 AI自主量化系统（终极目标）

> 核心: AI判断市场 → AI选择策略 → AI调整风控 → 人仅授权

### 开发规划

| 文档 | 用途 | 索引 |
|------|------|------|
| [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) | 阶段性开发路线图 (Phase 0-6) | DEV.001 |
| [ULTIMATE_BLUEPRINT.md](ULTIMATE_BLUEPRINT.md) | 终极蓝图 | DEV.002 |
| [AI_RESEARCH_FRAMEWORK.md](AI_RESEARCH_FRAMEWORK.md) | AI研究Agent核心架构 | AI.AGENT.001 |

### AI模块详细设计

| 模块 | 文件位置 | 状态 |
|------|----------|------|
| A01 市场状态识别 | `quant_system_v5/src/ai/market_regime.py` | 📋 规划 |
| A02 策略路由器 | `quant_system_v5/src/ai/strategy_router.py` | 📋 规划 |
| A03 动态风控 | `quant_system_v5/src/ai/dynamic_risk.py` | 📋 规划 |
| A04 策略优化器 | `quant_system_v5/src/ai/strategy_optimizer.py` | 📋 规划 |
| A05 反馈学习闭环 | `quant_system_v5/src/ai/feedback_loop.py` | 📋 规划 |
| A06 授权确认界面 | `quant_system_v5/src/ai/approval_ui.py` | 📋 规划 |

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
| [README.md](01_FRAMEWORK/README.md) | Layer 0-7架构定义 |

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
1. [System_Manifest.md](System_Manifest.md) - 系统清单
2. [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md) - 统一架构
3. [05_IMPLEMENTATION/01_QUICKSTART/](05_IMPLEMENTATION/01_QUICKSTART/) - 快速开始

### 运维
1. [05_IMPLEMENTATION/03_DEPLOYMENT/](05_IMPLEMENTATION/03_DEPLOYMENT/) - 部署指南
2. [05_IMPLEMENTATION/04_OPERATIONS/](05_IMPLEMENTATION/04_OPERATIONS/) - 运维手册
3. [FAQ.md](FAQ.md) - 常见问题

### AI研究
1. [AI_Research_Framework.md](AI_Research_Framework.md) - AI研究框架
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
| [FINAL_SYSTEM_AUDIT.md](FINAL_SYSTEM_AUDIT.md) | 最终系统审计报告 | 系统完整性检查 |
| [SYSTEM_AUDIT_REPORT.md](SYSTEM_AUDIT_REPORT.md) | 系统审计报告 | 审计记录 |
| [DOCUMENT_AUDIT_REPORT.md](DOCUMENT_AUDIT_REPORT.md) | 文档审查报告 | 文档质量检查 |
| [LEGACY_DOC_ANALYSIS.md](LEGACY_DOC_ANALYSIS.md) | 遗留文档分析 | v4迁移参考 |
| [CODE_STATUS.md](CODE_STATUS.md) | 代码状态 | 代码完整性跟踪 |
| [CODE_EXAMPLES.md](CODE_EXAMPLES.md) | 代码示例 | 开发参考 |
| [RESEARCH_PIPELINE.md](RESEARCH_PIPELINE.md) | 研究流程 | 研究方法论 |

---

## 📖 完整地图

如需完整文档结构，请查看 [SITEMAP.md](SITEMAP.md)

---

**最后更新**: 2026-03-30
**维护者**: 清风量化系统
**版本**: v5.0 个人开发精简版
