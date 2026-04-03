---
module_id: INDEX_06_ARCHIVE
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席文档架构�?standard_type: 专业量化机构索引
applicable_scope: 历史归档
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完�?---

# 归档目录索引

> **目录职责**: 存放历史版本文档、已废弃架构、旧版设计文�?
## 📁 目录结构

| 目录 | 说明 | 归档日期 |
|------|------|---------|
| [architecture_v4/](architecture_v4/) | v4架构归档（Layer 0-8技术流水线�?| 2026-04-03 |
| [factor-library/](factor-library/) | 因子库历史版�?| 2026-04-02 |
| [main/](main/) | 主系统历史文�?| 2026-04-01 |

## 📂 子目录详�?
### architecture_v4 - v4架构归档

**归档原因**: 系统已迁移至"三级时间框架融合架构"，旧版Layer 0-8架构文档归档保留

| 子目�?| 内容 |
|--------|------|
| [module_designs/](architecture_v4/module_designs/) | Layer模块设计文档 |
| └── layer_1/ | 数据预处理层模块 |
| └── layer_4/ | 特征工程层模�?|
| └── layer_9/ | 模型优化层模�?|
| └── layer_11/ | 自然语言接口层模�?|

### factor-library - 因子库历�?
| 文件 | 说明 |
|------|------|
| [ifind_factors_list.md](factor-library/ifind_factors_list.md) | iFind因子列表 |
| [ifind_factors_raw.json](factor-library/ifind_factors_raw.json) | iFind因子原始数据 |

### main - 主系统历�?
| 文件/目录 | 说明 |
|----------|------|
| [BLUEPRINTS/](main/BLUEPRINTS/) | 历史蓝图文档 |
| [v4_development/](main/v4_development/) | v4开发计�?|

## ⚠️ 归档说明

1. **归档文档仅供参�?*，不反映当前系统状�?2. **禁止修改归档文档**，如需更新请在新架构中创建
3. **引用归档文档需注明来源**

## 🔗 当前架构

- **新架构文�?*: [../01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md)
- **架构迁移计划**: [../01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md](../01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md)

---
*最后更�? 2026-04-03*
