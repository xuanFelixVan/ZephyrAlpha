---
module_id: README
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 06_ARCHIVE说明文档
---

﻿---
module_id: ARCHIVE_ROOT_README_001
version: 5.1.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 归档文档、历史版本
  - 交易执行
  - 数据源
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行?---


# 06_ARCHIVE - 统一归档目录
> **核心职责**: 模块说明和快速入门指南
> **职责边界**: 
> - ✅ 本文档负责：模块说明和快速入门指南相关内容
> - ❌ 本文档不负责：其他模块内容


> 历史版本文档和过度工程化文档集中管理

**版本**: v5.1
**更新日期**: 2026-03-31

---

## 目录结构

```
06_ARCHIVE/
├── README.md                    # 本文?
?
├── main/                       # 主文档历史归?
?  ├── README.md
?  ├── CHANGELOG.md            # 版本变更历史
?  ├── NOZYIO_REFERENCE.md     # NozyIO参?
?  ├── quantitative_strategy_framework.md    # v3.1策略框架
?  ├── SYSTEM_AUDIT_REPORT.md  # 系统审计报告
?  ├── UPGRADE_REPORT.md       # 升级报告
?  ├── FINAL_AUDIT_REPORT_V5.md # 最终审计报告v5
?  ├── COMPLETE_DOCUMENT_AUDIT_REPORT_v2.md # 完整文档审计
?  ?
?  ├── v4_development/         # v4.0 开发文?
?  ?  ├── qingfeng_v4_draft.md   # 初始设计
?  ?  └── qingfeng_v4_development_plan.md   # 开发方?
?  ?
?  └── BLUEPRINTS/            # 原始蓝图文档(已合?
?      ├── 01_ULTIMATE_BLUEPRINT.md
?      ├── 02_DEPLOYMENT_BLUEPRINT.md
?      ├── 03_SECURITY_BLUEPRINT.md
?      ├── 04_API_INTEGRATION_BLUEPRINT.md
?      ├── 05_AI_RESEARCH_FRAMEWORK.md
?      ├── 06_DEVELOPMENT_ROADMAP.md
?      └── 07_SYSTEM_MANIFEST.md
?
├── factor-library/             # 因子库历史归?
?  ├── README.md
?  ├── ifind_factors_list.md
?  ├── ifind_factors_raw.json
?  └── ifind_indicators.json
?
├── over_engineered/            # 过度工程化文?归档)
?  ├── README.md
?  ├── METADATA_MANAGEMENT.md
?  └── STORAGE_ARCHITECTURE.md
?
├── tactics_manual.md            # v1.0战术手册
├── technical_documentation.md            # v1.0技术文?
├── strategy_pool.md             # v1.0策略?
└── system_enhancement_manual.md        # v1.0系统增强
```

---

## v5.1 归档原则

| 原则 | 说明 |
|------|------|
| **统一归档** | 所有模块的历史文档统一?06_ARCHIVE/ |
| **分类存储** | 按模块分子目?(main/, factor-library/, over_engineered/) |
| **精简保留** | 同一文档只保留最新版?必要历史版本 |
| **索引完备** | 每个归档有说明归档原?|
| **版本隔离** | v4.0 开发文档隔离到 v4_development/ |

---

## v5.1 变更记录 (2026-03-31)

### 清理冗余文件

已删除以下冗余文件：

| 删除文件 | 删除原因 |
|----------|----------|
| `old_v4_plan_archive.md` | 已废弃的计划文档 |
| `旧文档务实评估_1人AI_一个月.md` | 临时评估文档 |
| `旧文档分析报告_*.md` | 分析报告，已过期 |
| `v4_development/` 下的副本和备?| 冗余版本 |
| `FINAL_SYSTEM_AUDIT_archived.md` | 旧版本审?|
| `DOCUMENT_AUDIT_REPORT_v1.md` | 旧版本审?|
| `FINAL_DOCUMENT_AUDIT_REPORT_*.md` (2? | 旧版本审?|
| `CODE_STATUS_archived.md` | 过时状态文?|
| `TEST_PLAN_archived.md` | 过时测试计划 |
| `DEVELOPMENT_SEQUENCE_archived.md` | 过时开发序?|
| `RESEARCH_PIPELINE_archived.md` | 过时研究流程 |
| `LEGACY_DOC_ANALYSIS_archived.md` | 过时文档分析 |
| `README_v1.1_archived.md` | 极旧版本 |
| `BLUEPRINTS/00_UNIFIED_ARCHITECTURE_archived.md` | 已合并到其他蓝图 |

### 当前 v4_development 保留文件

| 文件 | 说明 |
|------|------|
| qingfeng_v4_draft.md | v4.0 初始设计 |
| qingfeng_v4_development_plan.md | v4.0 开发方?|

---

## 过度工程化文?(over_engineered/)

这些文档?*1?AI**模式来说**过于复杂**?

| 文档 | 归档原因 |
|------|----------|
| METADATA_MANAGEMENT.md | 数据血缘追踪过于复杂，AI运行不需?|
| STORAGE_ARCHITECTURE.md | 多级存储(???个人不需?|

---

## 恢复的文?

以下文档之前归档，但?*1?AI目标**评估后已恢复?

| 原归档位?| 恢复位置 | 恢复原因 |
|-----------|----------|----------|
| over_engineered/docker_setup.md | 07_RESEARCH/01_ENVIRONMENT/ | AI研究环境隔离必需 |
| over_engineered/statistical_tools.md | 07_RESEARCH/02_EXPLORATORY_ANALYSIS/ | AI统计分析基础 |
| over_engineered/candle_patterns.md | 07_RESEARCH/03_PATTERN_RECOGNITION/ | AI模式识别必需 |
| over_engineered/36_FRAMEWORK.md | 04_EXECUTION/04_AI_COMMITTEE/ | AI决策核心 |
| over_engineered/REAL_TIME_MONITORING.md | 04_EXECUTION/03_MONITORING/ | AI监控必需 |
| over_engineered/PERFORMANCE_ATTRIBUTION.md | 04_EXECUTION/03_MONITORING/ | AI报告必需 |
| over_engineered/tca.md | 04_EXECUTION/02_TRADE_EXECUTOR/ | AI执行分析 |
| POSITION_MANAGEMENT/ | 03_TRADING_TACTICS/06_POSITION_MANAGEMENT/ | 风控规则(人决? |
| ORDER_GENERATION/ | 03_TRADING_TACTICS/07_ORDER_GENERATION/ | AI执行?|
| EVENT_ENGINE/ | 04_EXECUTION/01_EVENT_ENGINE/ | 事件驱动引擎 |

---

## 归档检查清?

创建新归档前检查：

- [ ] 是否是历史版本文档？
- [ ] 当前系统是否不再使用此文档？
- [ ] 是否有更优位置放置此文档?
- [ ] 归档原因是否明确记录?
- [ ] 是否已有相同文档的更完整版本?

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v5.1 | 2026-03-31 | 清理冗余文件，精简归档目录 |
| v5.0 | 2026-03-29 | 新增 v4_development/ 目录和归档清?|
| v3.0 | 2026-03-29 | 恢复大部分文档（1?AI目标?|
| v2.0 | 2026-03-28 | 新增over_engineered/目录 |
| v1.0 | 2026-03-28 | 统一归档策略 |
