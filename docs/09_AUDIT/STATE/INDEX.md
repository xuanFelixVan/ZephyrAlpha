---
module_id: 09_AUDIT_STATE_INDEX
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-13
owner: 首席文档架构师
responsibility:
  - STATE目录索引
---

---
module_id: 09_AUDIT_STATE_INDEX_STATE_001
version: 1.0.4
status: Active
created_date: 2026-04-07
last_updated: 2026-04-13
owner: 文档治理系统
responsibility:
  - 目录导航与文档索引管理与优化维护
standard_type: 索引文档
applicable_scope: 文档索引导航
compliance_level: 专业标准---


# State索引
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0.0
> **创建日期**: 2026-04-07
> **核心定位**: 文档索引导航
> **索引**: `INDEX_STATE_001`

---

## 📋 目录概览

### 统计信息

| 指标 | 数值 |
|------|------|
| **文档总数** | 3 |
| **活跃模块** | 3 |
| **更新频率** | 按需更新 |

---

## 📚 文档列表
- [稀疏目录整合指南](./sparse_directory_integration_guide_20260407_025756.md) - 实施指南文档

- [稀疏目录分析报告](./sparse_directory_analysis_20260407_030548.md) - 系统文档

- [严格孤儿文件报告 REGEN](./STRICT_ORPHAN_FILES_REPORT_REGEN_20260408.md) - 治理扫描报告

### 蓝图 D 类机器产出（候选 / 分流 / 二审队列）

> 完整流程与 Owner 裁决见办公室 [D 类蓝图重叠 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md)（**§3.5**、**§5**）；更强模型二审提示词见 [二审模板](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md)。

| 阶段 | 说明 | 示例路径（按日期轮换 `YYYYMMDD`） |
|------|------|--------------------------------------|
| 启发式候选对 | `scan_blueprint_d_overlap_candidates.py` | [`BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md`](./BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md) · [`.json`](./BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json) |
| A 档分流摘要 | `triage_blueprint_d_overlap_pairs.py` | [`BLUEPRINT_D_OVERLAP_TRIAGE_20260412.md`](./BLUEPRINT_D_OVERLAP_TRIAGE_20260412.md) · [`.json`](./BLUEPRINT_D_OVERLAP_TRIAGE_20260412.json) |
| 二审输入队列 | 同上 | [`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl`](./BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl) |

### 整仓文件治理机器产出（抽样 / 密钥抽查 / Git 路径异常）

> 任务口径与波次见办公室 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)（**§1**、**§6**、**P2～P3**）。

| 类型 | 脚本或说明 | 路径 |
|------|------------|------|
| P3 主导航可见性抽样（宽松） | `sample_docs_nav_coverage.py` | [`DOCS_NAV_COVERAGE_SAMPLE_20260410.md`](./DOCS_NAV_COVERAGE_SAMPLE_20260410.md) |
| W2 可选密钥型字面量抽查 | 等价检查记录（非 gitleaks） | [`W2_SECRET_PATTERN_SPOTCHECK_20260410.md`](./W2_SECRET_PATTERN_SPOTCHECK_20260410.md) |
| Git quotePath / 显示转义澄清 | 与索引真源对照 | [`GIT_TRACKED_PATH_ANOMALIES_20260411.md`](./GIT_TRACKED_PATH_ANOMALIES_20260411.md) |
| 目录 rollup（`quotePath=false`） | `export_repo_directory_rollup.py` | **最新（20260413）** [`REPO_DIRECTORY_ROLLUP_20260413.md`](./REPO_DIRECTORY_ROLLUP_20260413.md) · [`.json`](./REPO_DIRECTORY_ROLLUP_20260413.json)；历史 [`20260411.md`](./REPO_DIRECTORY_ROLLUP_20260411.md) · [`.json`](./REPO_DIRECTORY_ROLLUP_20260411.json) |
| 平面路径清单 UTF-8 | 导出见 REPO_WIDE §1 | [`REPO_GIT_TRACKED_FILES_20260411.txt`](./REPO_GIT_TRACKED_FILES_20260411.txt) |
| 索引健全性（零入链 · REPORTS 前缀） | `scan_index_health.py --prefix docs/09_AUDIT/REPORTS` | [`INDEX_HEALTH_ORPHAN_20260412.md`](./INDEX_HEALTH_ORPHAN_20260412.md) · [`.json`](./INDEX_HEALTH_ORPHAN_20260412.json) |
| 索引健全性（零入链 · 04_OPERATIONS 前缀） | `scan_index_health.py --prefix docs/05_IMPLEMENTATION/04_OPERATIONS` | **最新（20260411）** [`INDEX_HEALTH_ORPHAN_20260411.md`](./INDEX_HEALTH_ORPHAN_20260411.md) · [`.json`](./INDEX_HEALTH_ORPHAN_20260411.json)；历史 [`20260414.md`](./INDEX_HEALTH_ORPHAN_20260414.md) · [`.json`](./INDEX_HEALTH_ORPHAN_20260414.json) |
| 多会话接力（Cursor 排队） | 当前指针 + §7 深度 3 前缀表 | [AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md) |

---

## 🧭 严格孤儿挂载（波次：A 类剩余大头）

> 说明：本目录下报告/状态文件数量较多，避免把上百条链接塞进本页；采用“分组索引”承接入口。

- **分组入口**：[`INDEX_GROUPED_STATE_20260408.md`](./INDEX_GROUPED_STATE_20260408.md)（覆盖当前仍为严格孤儿的 95 篇 STATE 文档）
- **夜间批跑**：[`overnight_runs/INDEX.md`](./overnight_runs/INDEX.md)


### 核心文档

- Continuous Audit Workflow - `CONTINUOUS_AUDIT_WORKFLOW_001`
- Module Id Registry - `MODULE_ID_REGISTRY_001`
- Responsibility Boundary Map - `RESPONSIBILITY_BOUNDARY_MAP_001`

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
| v1.0.4 | 2026-04-11 | 整仓产出表增办公室 `AUTONOMOUS_GOVERNANCE_RUN_QUEUE` 互指 | 文档治理系统 |
| v1.0.3 | 2026-04-11 | 整仓产出表增 rollup 20260411、平面清单 20260411；Git 行改为 quotePath 澄清口径 | 文档治理系统 |
| v1.0.2 | 2026-04-11 | 增整仓治理产出表（导航抽样、W2 抽查、Git 异常路径）；内层 `module_id` 版本对齐 | 文档治理系统 |
| v1.0.0 | 2026-04-07 | 初始版本创建 | 文档治理系统 |

---

## 🔗 相关文档

- [Module ID注册表](../../09_AUDIT/STATE/MODULE_ID_REGISTRY.md)
- [职责边界地图](../../09_AUDIT/STATE/RESPONSIBILITY_BOUNDARY_MAP.md)
- [专业文档治理审计指南](../../09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)

---

**索引状态**: ✅ 活跃
**维护频率**: 按需更新
**下次更新**: 按需
