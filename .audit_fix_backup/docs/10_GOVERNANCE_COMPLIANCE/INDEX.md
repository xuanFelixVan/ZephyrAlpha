---
module_id: 10_GOVERNANCE_COMPLIANCE_INDEX_GOVERNANCE_COMPLIANCE_001
version: 1.0.1
status: Active
created_date: 2026-04-04
last_updated: '2026-04-11'
owner: 系统架构师
responsibility:
- 目录导航与文档索引管理与优化维护
standard_type: 专业量化机构目录索引
applicable_scope: Layer 10 - 治理与合规层
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
layer: layer_00
---


# Layer 10：治理与合规层目录索引

> **核心职责**: 目录导航和文档索引  
> **职责边界**:
> - ✅ 本文档负责：`docs/10_GOVERNANCE_COMPLIANCE/` 导航与子域门面入链
> - ❌ 本文档不负责：其他模块正文的实质性改写

> **版本**: v5.3（叙事口径）  
> **架构**: Layer 10 - 治理与合规层  
> **最后更新**: 2026-04-11

---

## 上级与接力

- [docs 根索引](../INDEX.md)
- 全仓库文件治理任务清单 §7
- 治理工具总索引
- [09_AUDIT 索引](../09_AUDIT/INDEX.md)
- [09_AUDIT STATE 索引](../09_AUDIT/STATE/INDEX.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260506.md（`scan_index_health.py --prefix docs/10_GOVERNANCE_COMPLIANCE --date 20260506`；**zero_inbound=0**；候选 md **21**；首轮 **6** 处子域门面零入链，已由本页**子域门面表**补链后复跑归零）
- **rollup（深度 3）**：../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md（JSON 真源同 stem；键 `docs/10_GOVERNANCE_COMPLIANCE` **21** 条路径）

---

## 🎯 目录职责

本目录存放 Layer 10 治理与合规层文档，包括：

- 内部控制体系  
- 合规监控系统  
- 决策审计追踪  
- 风险治理框架  
- 监管合规文档  

---

## 子域门面（INDEX / README）

| 子域 | 索引 | 概述 |
|------|------|------|
| CI_CD_INTEGRATION | [INDEX.md](12_MODULE_DESIGNS/layer_0/INDEX.md) | [README.md](./TRAINING_SYSTEM/README.md) |
| CLASSIFICATION | [INDEX.md](12_MODULE_DESIGNS/layer_0/INDEX.md) | [README.md](./TRAINING_SYSTEM/README.md) |
| GOVERNANCE_PROCESSES | [INDEX.md](12_MODULE_DESIGNS/layer_0/INDEX.md) | （本目录无 `README.md`） |
| TRAINING_SYSTEM | [INDEX.md](12_MODULE_DESIGNS/layer_0/INDEX.md) | [README.md](./TRAINING_SYSTEM/README.md) |
| KNOWLEDGE_BASE | [INDEX.md](12_MODULE_DESIGNS/layer_0/INDEX.md) | （门面见子索引） |

---

## 📚 核心文档

### 蓝图文档

| 文档名称 | 说明 | 重要度 |
|---------|------|--------|
| 治理与合规层蓝图 | Layer 10 总体架构设计 | ⭐⭐⭐⭐⭐ |

### 子模块（规划中）

| 目录名称 | 说明 | 状态 |
|---------|------|------|
| `internal_controls/` | 内部控制体系 | 🔄 规划中 |
| `compliance_monitoring/` | 合规监控系统 | 🔄 规划中 |
| `decision_audit/` | 决策审计追踪 | 🔄 规划中 |
| `risk_governance/` | 风险治理框架 | 🔄 规划中 |
| `regulatory_compliance/` | 监管合规文档 | 🔄 规划中 |

---

## 📖 快速导航

### 核心功能

1. **内部控制**: 交易授权、操作审计、风险控制  
2. **合规监控**: 监管合规检查、交易规则验证、持仓限制  
3. **决策审计**: AI 决策审计、人工决策记录、全链路追溯  
4. **风险治理**: 风险委员会、风险预算管理、风险评估  

### 技术栈

- **规则引擎**: Drools / 自研规则引擎  
- **审计系统**: 日志系统 + 区块链存证  
- **合规检查**: 自动化合规引擎  
- **风险评估**: AI 风险评估模型  

---

## 🔗 相关文档

- [统一架构 (Layer 0-11)](../01_FRAMEWORK/ARCHITECTURE.md)
- AI 决策审计蓝图
- 合规监控系统蓝图
- [审计系统](../09_AUDIT/INDEX.md)
- [战略决策层 (Layer 11)](../11_STRATEGIC_DECISION/INDEX.md)

---

## 🧭 严格孤儿挂载（波次：A 类继续清理）

- DOCUMENT_ENCODING_STANDARD
- LINK_MAINTENANCE_MECHANISM
- RESPONSIBILITY_REVIEW_MECHANISM
- SIMILARITY_THRESHOLD_OPTIMIZATION

### 子目录直链（持续合入 · 从 Layer 10 主索引）

- CI/CD 集成指南
- 文档创建流程
- 文档审查流程
- 培训体系指南

---

## 📊 文档统计

| 统计项 | 数量 |
|--------|------|
| 蓝图文档 | 1 |
| 技术文档 | 0 |
| 实施文档 | 0 |
| **总计** | **1** |

---

## 📝 维护说明

- **创建日期**: 2026-04-04  
- **最后更新**: 2026-04-11  
- **维护者**: 系统架构师  
- **更新频率**: 按需更新  
