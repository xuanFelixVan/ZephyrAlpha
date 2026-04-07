---
module_id: 06_ARCHIVE_INDEX
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 06_ARCHIVE目录索引
---

﻿---
module_id: 06_ARCHIVE_INDEX_ARCHIVE_001
version: 1.0.1
status: Active
created_date: 2026-04-03
last_updated: 2026-04-04
owner: 首席文档架构?standard_type: 专业量化机构索引
responsibility:
  - 归档文档、历史版本
applicable_scope: 历史归档
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完?
---
---

# 归档目录索引
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **目录职责**: 存放历史版本文档、已废弃架构、旧版设计文?
## 📁 目录结构

| 目录 | 说明 | 归档日期 |
|------|------|---------|
| 20260404_audit_reports_archive/ | 审计报告归档（audit_state + review_reports?| 2026-04-04 |
| duplicate_documents/ | 重复文档归档 | 2026-04-03 |
| integrated_documents/ | 整合文档归档 | 2026-04-03 |
| architecture_v4/ | v4架构归档（Layer 0-11技术流水线?| 2026-04-03 |
| factor-library/ | 因子库历史版?| 2026-04-02 |
| main/ | 主系统历史文?| 2026-04-01 |

## 📂 子目录详?
### 20260404_audit_reports_archive - 审计报告归档 🆕

**归档原因**: 整理分散的审计报告，统一归档管理

| 子目?| 内容 | 文件?|
|--------|------|--------|
| audit_state/ | 审计状态报告、深度审计报?| 128 |
| technical_reviews/ | 技术审查报告、可行性评?| 98 |

**来源位置**:
- `05_IMPLEMENTATION/07_OPERATIONS/audit_state/`
- `05_IMPLEMENTATION/07_OPERATIONS/review_reports/`

### duplicate_documents - 重复文档归档

| 子目录 | 说明 |
|--------|------|
| 20260404_layer7_audit_reports/ | Layer 7审计报告重复 |

### architecture_v4 - v4架构归档

**归档原因**: 系统已迁移至"三级时间框架融合架构"，旧版Layer 0-11架构文档归档保留

| 子目?| 内容 |
|--------|------|
| module_designs/ | Layer模块设计文档 |
| └── layer_1/ | 数据预处理层模块 |
| └── layer_4/ | 特征工程层模?|
| └── layer_9/ | 模型优化层模?|
| └── layer_11/ | 自然语言接口层模?|

### factor-library - 因子库历?
| 文件 | 说明 |
|------|------|
| ifind_factors_list.md | iFind因子列表 |
| ifind_factors_raw.json | iFind因子原始数据 |

### main - 主系统历?
| 文件/目录 | 说明 |
|----------|------|
| BLUEPRINTS/ | 历史蓝图文档 |
| v4_development/ | v4开发计?|

## ⚠️ 归档说明

1. **归档文档仅供参?*，不反映当前系统状?2. **禁止修改归档文档**，如需更新请在新架构中创建
3. **引用归档文档需注明来源**

## 🔗 当前架构

- **新架构文?*: [../01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md)
- **架构迁移计划**: `../01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md`
---

*最后更? 2026-04-03*
