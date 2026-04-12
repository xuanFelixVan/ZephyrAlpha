---
module_id: 09_AUDIT_TEMPLATES_INDEX_TEMPLATES_001
version: 1.0.1
status: Active
created_date: 2026-04-07
last_updated: '2026-04-11'
owner: 文档治理系统
responsibility:
- 目录导航与文档索引管理与优化维护
standard_type: 索引文档
applicable_scope: 模板文档管理
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

- **零入链扫描（本批）**：../STATE/INDEX_HEALTH_ORPHAN_20260518.md（`scan_index_health.py --prefix docs/09_AUDIT/TEMPLATES --date 20260518`；首轮 **`INDEX.md`** 零入链，已由 `09_AUDIT/INDEX` 审计模板表补链后复跑 **zero_inbound=0**）
- **rollup（深度 3）**：../STATE/REPO_DIRECTORY_ROLLUP_20260414.md（JSON 真源同 stem；键 `docs/09_AUDIT/TEMPLATES` **16** 条路径）

---

# Templates索引
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0.1
> **创建日期**: 2026-04-07
> **核心定位**: 模板文档管理
> **索引**: `INDEX_TEMPLATES_001`

---

## 📋 目录概览

### 统计信息

| 指标 | 数值 |
|------|------|
| **文档总数** | 12 |
| **活跃模块** | 12 |
| **更新频率** | 按需更新 |

---

## 📚 文档列表

### 核心文档

- Adr Template - `ADR_TEMPLATE`
- Ai Document Governance Audit Prompt - `AUDIT_TPL_AI_PROMPT_001`
- Blueprint Standard Template - `AUDIT_蓝图文件标准模板_001`
- Decision Record Template - `DECISION_RECORD_TEMPLATE`
- Document Governance Audit Checklist - `AUDIT_TPL_CHECKLIST_001`
- Document Template - `DOC_TEMPLATE`
- Emergency Response Plan - `EMERGENCY_RESPONSE_PLAN`
- Module Interface Template - `MODULE_INTERFACE_TEMPLATE`
- Professional Document Governance Audit Guide - `AUDIT_TPL_GOVERNANCE_GUIDE_001`
- Research Memo Template - `RESEARCH_MEMO_TEMPLATE`
- Risk Event Template - `RISK_EVENT_TEMPLATE`
- Stress Test Template - `STRESS_TEST_TEMPLATE`

### ✅ 入口链接补齐（用于严格孤儿入度统计）

- BLUEPRINT_STANDARD_TEMPLATE
- EMERGENCY_RESPONSE_PLAN
- MODULE_INTERFACE_TEMPLATE
- MONTHLY_AUDIT_REPORT_TEMPLATE
- QUARTERLY_AUDIT_REPORT_TEMPLATE
- STRESS_TEST_TEMPLATE
- WEEKLY_AUDIT_REPORT_TEMPLATE

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
