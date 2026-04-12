---
module_id: 09_AUDIT_GUIDES_INDEX_GUIDES_001
version: 1.0.1
status: Active
created_date: 2026-04-07
last_updated: '2026-04-11'
owner: 文档治理系统
responsibility:
- 目录导航与文档索引管理与优化维护
standard_type: 索引文档
applicable_scope: 文档索引导航
compliance_level: 专业标准
layer: layer_09
---

## 上级与接力

- [09_AUDIT 总索引](../INDEX.md)
- [docs 根索引](../../INDEX.md)
- 全仓库文件治理任务清单 §7
- 治理工具总索引
- [09_AUDIT STATE 索引](12_MODULE_DESIGNS/layer_0/INDEX.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（本批）**：../STATE/INDEX_HEALTH_ORPHAN_20260520.md（`scan_index_health.py --prefix docs/09_AUDIT/GUIDES --date 20260520`；首轮 **`GUIDES/INDEX.md`** 零入链，已由 `09_AUDIT/INDEX` 显式链 `./GUIDES/INDEX.md` 与子目录表对齐后复跑 **zero_inbound=0**）
- **rollup（深度 3）**：../STATE/REPO_DIRECTORY_ROLLUP_20260414.md（JSON 键 `docs/09_AUDIT/GUIDES` **4** 条路径）

---

# Guides索引
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0.1
> **创建日期**: 2026-04-07
> **核心定位**: 文档索引导航
> **索引**: `INDEX_GUIDES_001`

---

## 📋 目录概览

### 统计信息

| 指标 | 数值 |
|------|------|
| **文档总数** | 4 |
| **活跃模块** | 4 |
| **更新频率** | 按需更新 |

---

## 📚 文档列表

### 核心文档

- Code Change Documentation Guide - `CODE_CHANGE_DOC_GUIDE`
- Scheduled Tasks Deployment Guide - `SCHEDULED_TASKS_DEPLOYMENT_GUIDE`

### ✅ 入口链接补齐（用于严格孤儿入度统计）

- AUDIT_TOOLS_USAGE_GUIDE
- CODE_CHANGE_DOCUMENTATION_GUIDE
- SCHEDULED_TASKS_DEPLOYMENT_GUIDE

---

## 🔍 维护指南

### 更新规则

1. **新增文档**: 在此目录添加新文档后，更新本文档列表
2. **删除文档**: 删除文档后，从列表中移除对应条目
3. **重命名文档**: 更新文档名称后，同步更新索引

### 质量标准

- ✅ 所有文档必须有明确的module_id
- ✅ 文档命名遵循专业量化机构标准
- ✅ 保持索引与实际文件一致

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.1 | 2026-04-11 | P5 §7：`INDEX_HEALTH_20260520` 门面；修正 YAML 闭合；统计与入口链对齐 4 篇 md | 文档治理系统 |
| v1.0.0 | 2026-04-07 | 初始版本创建 | 文档治理系统 |

---

## 🔗 相关文档

- Module ID注册表
- 职责边界地图
- 专业文档治理审计指南

---

**索引状态**: ✅ 活跃
**维护频率**: 按需更新
**下次更新**: 按需
