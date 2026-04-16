---
charter_id: 09_AUDIT_CHARTER
version: 1.0.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
review_cycle: monthly
owner: 审计负责人
---

# 09_AUDIT 文件夹宪章

> **定位**: 全库审计与治理中枢
> **当前规模**: ~1172个文件（治理成本最高目录）
> **负责人**: 审计负责人
> **紧急事项**: 必须严格执行TTL，减少文件数量至<300

---

## 1. 核心职责

本目录是 **ZephyrAlpha 治理体系的执行中枢**，负责：

- **合规审计**: 全库文件合规性检查（命名、放置、元数据）
- **质量监控**: 链接健康、重复检测、孤儿文件识别
- **状态记录**: 每日/每周/每月审计快照
- **治理标准**: 20个正式标准文档（已合并自34个）

---

## 2. 内容边界

### 允许存放的文件类型

| 类型 | 模式 | 示例 | 存放位置 |
|------|------|------|----------|
| 治理标准 | `*_standard.md` | `doc-governance-mechanism.md` | `STANDARDS/` |
| 审计报告 | `*_report_*.md` | `sentinel-l1-scan-20260416.md` | `STATE/` 或 `REPORTS/` |
| 状态快照 | `*_YYYYMMDD.json` | `SENTINEL_L1_SCAN_20260416.json` | `STATE/` |
| 审计程序 | `*_procedures.md` | `audit-execution-procedures.md` | `PROCEDURES/` |
| 工作流 | `*_workflow.md` | `new-directory-creation-workflow.md` | `WORKFLOWS/` |
| 表单模板 | `*_template.md` | `session-log-template.md` | `FORM_STANDARDS/` |

### 禁止存放的文件类型

| 类型 | 原因 | 应放置位置 |
|------|------|------------|
| 设计蓝图 | 非审计内容 | `01_FRAMEWORK/` 或 `03_BLUEPRINTS/` |
| 实施文档 | 非审计内容 | `05_IMPLEMENTATION/` |
| 知识案例 | 非审计内容 | `08_KNOWLEDGE/` |
| 临时草稿（超过30天）| 已过期 | 删除或归档至 `06_ARCHIVE/` |
| 过程日志（超过14天）| 已过期 | 删除 |

---

## 3. 二级目录结构规范

```
docs/09_AUDIT/
├── STANDARDS/              # 治理标准（20个，已合并）
│   └── INDEX.md           # 标准索引（已更新v2.0.0）
├── STATE/                  # 状态快照（TTL严格管理）
│   ├── DAILY/             # 每日快照（TTL: 30天）
│   ├── WEEKLY/            # 每周汇总（TTL: 90天）
│   ├── MILESTONE/         # 里程碑（永久保留）
│   └── overnight_runs/    # 夜间运行（TTL: 14天）
├── REPORTS/                # 审计报告（按类别分类）
│   ├── GOVERNANCE/        # 治理报告
│   ├── QUALITY/           # 质量报告
│   ├── COMPLIANCE/        # 合规报告
│   ├── INCIDENT/          # 事件报告
│   └── PERIODIC/          # 周期性报告
├── FORM_STANDARDS/         # 表单模板
├── PROCEDURES/             # 审计程序
├── WORKFLOWS/              # 工作流文档
├── CONFIG/                 # 审计配置
├── AUTOMATION/             # 自动化脚本
├── DECISION_RECORDS/       # 决策记录
├── RESEARCH_MEMOS/         # 研究备忘录
└── INDEX.md               # 本目录索引
```

---

## 4. 容量限制（严格执行）

| 指标 | 当前值 | 目标值 | 上限 | 状态 |
|------|--------|--------|------|------|
| 总文件数 | ~1172 | <300 | 500 | 🔴 严重超标 |
| STATE/ 文件 | ~567 | <100 | 200 | 🔴 需清理 |
| REPORTS/ 文件 | ~503 | <150 | 300 | 🔴 需分类+清理 |
| STANDARDS/ 文件 | 20+1 | 20 | 30 | 🟢 达标 |

**清理优先级**:
1. **P0**: `STATE/overnight_runs/`（TTL 14天，已部分清理）
2. **P0**: `STATE/` 超过30天的日常快照
3. **P1**: `REPORTS/` 按类别分类，超过保留期的删除
4. **P1**: 孤儿重复报告去重

---

## 5. 保留策略（TTL）— 严格执行

| 目录 | 内容类型 | TTL | 自动化清理 |
|------|----------|-----|------------|
| `STATE/DAILY/` | 每日健康快照 | 30天 | ✅ `purge_expired_state.py` |
| `STATE/WEEKLY/` | 每周汇总 | 90天 | ✅ `purge_expired_state.py` |
| `STATE/overnight_runs/` | 夜间运行日志 | 14天 | ✅ `purge_expired_state.py` |
| `REPORTS/GOVERNANCE/` | 治理报告 | 10份最新 | 手动 |
| `REPORTS/QUALITY/` | 质量报告 | 10份最新 | 手动 |
| `REPORTS/COMPLIANCE/` | 合规报告 | 5份最新 | 手动 |
| `REPORTS/INCIDENT/` | 事件报告 | 永久 | 手动（重要） |
| `REPORTS/PERIODIC/` | 周期性报告 | 按周期策略 | 手动 |
| `REPORTS/ARCHIVE/` | 归档中转 | 30天 | ✅ 自动删除 |

---

## 6. 自动化检查（高强度）

### Pre-commit 检查

```bash
# 标准文档登记检查
python scripts/hooks/check_standards_index_registration.py

# 文档放置位置检查
python scripts/hooks/check_document_placement.py
```

### 每日检查

```bash
# Sentinel L1 全库扫描
python scripts/audit/sentinel_l1_governance_scan.py

# TTL过期清理
python scripts/audit/purge_expired_state.py --dry-run
```

### 每周检查

```bash
# 质量报告生成
python scripts/ci_audit/generate_quality_report.py

# 项目健康仪表盘
python scripts/governance/generate_project_health_dashboard.py
```

---

## 7. 治理标准清单（20个）

参见 [STANDARDS/INDEX.md](../../09_AUDIT/STANDARDS/INDEX.md) v2.0.0，包含：

1. `adr-standard.md`
2. `audit-and-compliance-master-standard.md`（合并）
3. `continuous-improvement-process.md`（合并）
4. `decision-record-standard.md`
5. `doc-governance-mechanism.md`（合并）
6. `doc-naming-standard.md`（合并）
7. `document-classification-standard.md`（合并）
8. `document-metadata-and-versioning-standard.md`（合并）
9. `document-repository-layout-standard.md`
10. `document-responsibility-boundary-standard.md`
11. `module-interface-specification.md`
12. `orphan-duplicate-and-overlap-governance-standard.md`（合并）
13. `path-and-reference-standard.md`（合并）
14. `periodic-audit-mechanism.md`（合并）
15. `quality-standard.md`（合并）
16. `research-memo-standard.md`
17. `responsibility-description-standard-v2.md`
18. `responsibility-template-library.md`
19. `risk-management-framework.md`
20. `testing-and-defect-prevention-standard.md`（合并）

---

## 8. 已知问题与改进计划

| 问题 | 优先级 | 计划解决时间 | 解决方案 |
|------|--------|--------------|----------|
| 文件数严重超标（1172>300）| **P0** | 2026-04-20 | 执行TTL清理脚本，预计删除700+ |
| REPORTS/ 未分类 | P1 | 2026-04-18 | 执行二级目录分类 |
| 治理标准分散历史遗留 | P2 | 已完成 | 已合并至20个 |
| 部分历史报告编码损坏 | P3 | 按需修复 | 修复或删除 |

---

## 9. 变更历史

| 版本 | 日期 | 变更 | 变更人 |
|------|------|------|--------|
| v1.0.0 | 2026-04-16 | 初始创建，文件数1172，目标压缩至<300 | AI Assistant |

---

**相关链接**:
- [STANDARDS/INDEX.md](../../09_AUDIT/STANDARDS/INDEX.md)
- [purge_expired_state.py](../../../scripts/audit/purge_expired_state.py)
- [项目健康仪表盘](../../../scripts/governance/generate_project_health_dashboard.py)
