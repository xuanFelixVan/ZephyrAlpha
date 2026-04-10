---
module_id: 09_AUDIT_PROC_BLUEPRINT_DOC_HYGIENE_MASTER_20260408
version: 1.1.0
status: Active
created_date: 2026-04-08
last_updated: '2026-04-10'
owner: 文档治理系统
standard_type: 程序性总案（蓝图阶段清洁）
applicable_scope: 全库 `docs/**/*.md` 孤儿、重复池、overlap 的系统化收敛
compliance_level: 专业标准
related_documents:
  - ../../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md
  - ../../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md
  - ../../../../06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md
  - ../../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md
  - ../../../../09_AUDIT/STATE/STRICT_ORPHAN_FILES_LIST_20260408.txt
---

# 蓝图阶段：文档「彻底清洁」总执行案（2026-04-08）

> **目标**：在**不破坏可追溯性**的前提下，让蓝图阶段所依赖的文档体系达到：**可发现、单真源、链接可门禁、归档可审计**。  
> **「彻底」定义**：不是「删到篇数最少」，而是 **孤儿收敛到可接受水位、重复与 overlap 均有台账与指针、合并前 L1=0**。

---

## 1. 三条工作流（必须同时进行、分批合入）

| 工作流 | 对象 | 真源/台账 | 完成判据（阶段性） |
|--------|------|-----------|---------------------|
| **A. 严格孤儿** | `docs/**/*.md` 入度为 0（口径见报告） | [`STRICT_ORPHAN_FILES_LIST_20260408.txt`](../../../../09_AUDIT/STATE/STRICT_ORPHAN_FILES_LIST_20260408.txt) 为**人工分桶基线**；可重算对比 | A 类高价值文档均可从约定 `INDEX.md` 链达；重跑扫描后孤儿集 **下降** |
| **B. 重复（duplicates 池）** | `docs/09_ARCHIVE/duplicates/*.md` | [`CANONICAL_POINTERS.md`](../../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md) | 表中 **无未裁决 TBD**（或全部有 Owner 与截止日）；非真源已 **Superseded** 声明 |
| **C. 重叠（overlap）** | `docs/06_ARCHIVE/overlap_*.md` | [`OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md`](../../../../06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md) | 每篇有 **非真源 + canonical_path**（或登记过的 TBD） |

总册原则见：[全库孤儿与重复/重叠治理方案（Playbook）](../../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md)。

---

## 2. 基线清单 vs 自动重算（避免口径漂移）

- **基线**：`STRICT_ORPHAN_FILES_LIST_20260408.txt` + [`STRICT_ORPHAN_FILES_REPORT_20260408.md`](../../../../09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md)（含 **A/B/C 人工分桶**），用于治理任务拆分。  
- **重算**：仓库根目录执行：

  ```text
  python scripts/strict_orphan_inbound_scan.py
  ```

  默认生成 `STRICT_ORPHAN_FILES_LIST_REGEN_<日期>.txt`（**不覆盖**基线文件名）。用于合并多轮 INDEX 修补后 **验收趋势**；若需替换基线，使用 `--basename STRICT_ORPHAN_FILES_LIST_YYYYMMDD` **显式**指定。

> 说明：随着各域 `INDEX.md` 补链，**重算孤儿数应单调下降**；与 20260408 基线篇数不必完全一致（基线含当时口径与分桶）。

---

## 3. 分阶段执行（蓝图优先）

### P0 — 蓝图关键路径（必须先干净）

对下列目录 **优先**完成：A 类孤儿挂接 + 任一指向 canonical 的重复裁决（若涉及）：

- `docs/01_FRAMEWORK/`（架构与 Layer 蓝图入口）
- `docs/02_FACTOR_LIBRARY/`（因子与数据契约）
- `docs/03_TRADING_TACTICS/`（战术与策略框架）
- `docs/05_IMPLEMENTATION/`（实施与施工蓝图，尤其 `06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`）
- `docs/09_AUDIT/STANDARDS/`、`PROCEDURES/`（治理标准与程序）

**门禁**：每 PR **L1 Invalid links = 0**。

### P1 — 审计与研究支撑

- `docs/09_AUDIT/REPORTS/`：以 [`INDEX_GROUPED_REPORTS_20260408.md`](../../../../09_AUDIT/REPORTS/INDEX_GROUPED_REPORTS_20260408.md) 为枢纽，**禁止**把数百报告逐篇堆进单一 `INDEX.md`。
- `docs/07_RESEARCH/`、`docs/08_KNOWLEDGE/`：按子目录 `INDEX.md` 分批补链。

### P2 — duplicates 池「结案」

按 [`DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`](../../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) 执行 **merge_then_delete / retain_trace**；删除前必须在台账更新 **disposition** 与日期。

### P3 — overlap 全量指针

按 [`OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md`](../../../../06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md) 主题批次执行；与 P0–P1 **并行、错开 PR**。

---

## 4. 禁止事项（避免「假彻底」）

- **无台账批量删除**重复或历史报告。  
- **单次 PR 改几百个文件**（除非纯机器生成且已 L1 验证）。  
- **跳过分桶**把高价值 A 类与应归档 B 类混处理。

---

## 5. 退出标准（蓝图阶段可宣告「清洁达标」）

| 检查项 | 标准 |
|--------|------|
| 主干 INDEX | P0 目录均已挂接 Playbook 所述入口或专项目录索引 |
| L1 | 默认分支 **Invalid links = 0** |
| duplicates | `CANONICAL_POINTERS.md` 无悬空 TBD（或已全部指派） |
| overlap | `overlap_*` 无「裸奔」缺指针（或已登记豁免） |
| 孤儿趋势 | 重算 `REGEN` 清单较基线 **明显减少**（篇数随项目约定） |

---

## 6. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-04-08 | 初版：蓝图阶段三条工作流 + 分阶段 + 工具与退出标准 |
| v1.1.0 | 2026-04-10 | **真源迁至** `00_MANAGEMENT/CANON/`；`related_documents` 与文内相对链接已重算 |
