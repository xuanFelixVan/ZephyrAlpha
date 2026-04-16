---
module_id: AUDIT_SUBSYSTEM_DEDUP_20260416
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
doc_type: owner_decision_record
priority: P0
---

# 重复子系统裁决记录 (Subsystem Deduplication Decision Record)

> **背景**：2026-04-16 诊断发现仓库存在 12 对功能重复的子系统/目录。本文档记录每对的裁决决策。
> **执行前提**：每项 action 需 Owner 明确签核后方可执行（标注 `owner_sign: TBD` 的均待签核）。

---

## D1：知识库双重目录

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `docs/08_KNOWLEDGE/` |
| **废弃（Redundant）** | `docs/08_KNOWLEDGE_BASE/` |
| **判据** | 两者同处于编号 08，功能完全重叠。`08_KNOWLEDGE/` 有更完整的子目录结构（FACTOR_LIBRARY, STRATEGY_LIBRARY, BEST_PRACTICES）。|
| **行动** | 将 `docs/08_KNOWLEDGE_BASE/` 的 6 个文件逐一检查，有内容的合并至 `docs/08_KNOWLEDGE/` 对应位置，空壳直接删除，最后删除目录 |
| **优先级** | P1 |
| **owner_sign** | TBD |
| **执行时间** | Phase C（知识库整合阶段）|

---

## D2：归档区四重目录（最严重）

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `docs/06_ARCHIVE/`（716 文件） |
| **待合并 A** | `docs/09_ARCHIVE/`（63 文件）|
| **待删除 B** | `docs/07_ARCHIVED/`（1 文件，空壳）|
| **待合并 C** | `docs/99_ARCHIVE/`（81 文件）|
| **判据** | `06_ARCHIVE` 是最早建立且文件量最大的归档区。`09_ARCHIVE` 和 `99_ARCHIVE` 是后续操作产生的重复归档区。|
| **行动** | 1) 删除 `07_ARCHIVED/`（INDEX.md 可空合并）；2) 将 `09_ARCHIVE/` 全部内容迁移至 `06_ARCHIVE/` 对应子目录；3) 将 `99_ARCHIVE/` 内容迁移，检查 DEPRECATED_BLUEPRINTS/ 是否与 `06_ARCHIVE/blueprints/` 重叠 |
| **优先级** | P1 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |
| **注意** | 迁移前需运行 `scan_duplicate_file_content.py` 确认文件级去重 |

---

## D3：审计存储双重目录

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `docs/09_AUDIT/STATE/`（558 文件）|
| **待合并** | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/`（420 文件）|
| **判据** | `09_AUDIT/STATE/` 是审计系统的正式存储区。`audit_state/` 是嵌套在实现目录下的平行存储，产生混乱。规则也指向 `09_AUDIT/`。|
| **行动** | 将 `audit_state/` 中独有的报告迁移至 `09_AUDIT/STATE/`，更新任何引用 `audit_state/` 路径的文档，最后删除 `audit_state/` 目录 |
| **优先级** | P1 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |
| **风险** | 迁移前检查是否有脚本硬编码写入 `audit_state/`（需更新脚本） |

---

## D4：治理合规双重目录

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `docs/10_GOVERNANCE_COMPLIANCE/`（21 文件）|
| **待删除** | `docs/07_GOVERNANCE_COMPLIANCE/`（1 文件，空壳）|
| **判据** | `07_GOVERNANCE_COMPLIANCE` 只有 1 个 INDEX.md，是重构残留空壳。|
| **行动** | 检查 `07_GOVERNANCE_COMPLIANCE/INDEX.md` 是否有被引用，若无则直接删除目录 |
| **优先级** | P2 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |

---

## D5：施工文档双重目录

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/`（267 文件）|
| **待迁移删除** | `docs/06_CONSTRUCTION_DOCS/`（4 文件，空壳）|
| **判据** | 嵌套版本文件量远大于顶层版本。嵌套版本有完整的子目录结构和管理文档。|
| **行动** | 检查顶层 `06_CONSTRUCTION_DOCS/` 的 4 个文件是否为独有内容，若有则迁移，最后删除顶层目录 |
| **优先级** | P1 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |

---

## D6：蓝图主存储双重目录

| 项目 | 详情 |
|------|------|
| **长期 Canonical（目标）** | `docs/03_BLUEPRINTS/`（按 L00-L11 分层，目前不存在）|
| **当前 Canonical A** | `docs/01_FRAMEWORK/`（332 文件）|
| **当前 Canonical B** | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`（163 文件）|
| **判据** | 两处都有大量蓝图，关系不清晰。`01_FRAMEWORK/` 是历史主存储，`01_BLUEPRINTS/` 是重组阶段产生的"图纸柜"。|
| **行动（分两步）** | Step 1（Phase D）：确定两目录的职责边界，消除重叠的 163 个文件；Step 2（未来）：创建 `docs/03_BLUEPRINTS/L{XX}/` 并执行大迁移 |
| **优先级** | P1（Step 1）/ P2（Step 2）|
| **owner_sign** | TBD |
| **执行时间** | Phase D (Step 1) / 未来 Phase |

---

## D7：研究目录双重

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `docs/07_RESEARCH/`（16 文件）|
| **待审查** | `docs/09_RESEARCH_INNOVATION/`（48 文件）|
| **判据** | `09_RESEARCH_INNOVATION` 内容经检查主要是审计报告，不是研究内容，命名具有误导性。|
| **行动** | 审查 48 个文件：真正的研究文档迁移至 `07_RESEARCH/`；审计报告迁移至 `09_AUDIT/STATE/`；最后删除 `09_RESEARCH_INNOVATION/` |
| **优先级** | P2 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |

---

## D8：舆情分析空壳

| 项目 | 详情 |
|------|------|
| **待删除** | `docs/11_Sentiment_Analysis/`（1 文件）|
| **保留** | `docs/10_AI_WORKFLOW/` 中的 sentiment 相关文件 |
| **行动** | 检查 `11_Sentiment_Analysis/` 唯一文件的内容，若为空壳直接删除 |
| **优先级** | P2 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |

---

## D9：脚本功能重复

| 项目 | 详情 |
|------|------|
| **保留（Canonical）** | `scripts/audit/`（23 文件，活跃版本）|
| **清理** | `scripts/archive/`（692 文件，含多个与 audit/ 同名脚本）|
| **行动** | 列出 archive/ 中与 audit/ 同名的脚本，确认 audit/ 版本是最新的，然后删除 archive/ 中的同名旧版；archive/ 中独有的历史脚本保留 |
| **优先级** | P2 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |

---

## D10：根目录完整备份

| 项目 | 详情 |
|------|------|
| **待删除** | `.audit_fix_backup/`（根目录，~1396 文件）|
| **判据** | 这是某次 AI 批量修复操作的快照备份，已超过使用期。没有保留价值。|
| **行动** | 确认 git history 已记录该次修复操作（即 backup 已无用），然后删除整个 `.audit_fix_backup/` 目录 |
| **优先级** | P1 |
| **owner_sign** | TBD |
| **注意** | 删除前先运行 `git log --oneline -20` 确认备份对应的变更已在 git 中 |
| **执行时间** | Phase D（可立即执行） |

---

## D11：时间戳备份目录

| 项目 | 详情 |
|------|------|
| **待删除** | `docs/08_ARCHIVED_BACKUP_20260413123038/`（2 文件）|
| **行动** | 检查 2 个文件内容，合并入 `docs/06_ARCHIVE/` 后删除此目录 |
| **优先级** | P2 |
| **owner_sign** | TBD |
| **执行时间** | Phase D |

---

## D12：01_GOVERNANCE 目录状态

| 项目 | 详情 |
|------|------|
| **当前状态** | `docs/01_GOVERNANCE/` 存在但只有 2 个 .bak 文件（TASK_LISTS 子目录中）|
| **规则预期** | 此目录应包含 STANDARDS/, PLAYBOOKS/, REGISTERS/ 三个子目录及大量标准文档 |
| **实际治理文档位置** | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/`（25 文件）+ `docs/09_AUDIT/STANDARDS/`（34 文件）|
| **决策选项** |  **A（推荐）**: 在 `docs/01_GOVERNANCE/` 下创建规范的子目录结构，将现有治理文档逐步迁移至此，使规则引用与实际一致 / **B**: 更新规则，将引用路径改为实际路径（`05_IMPLEMENTATION/.../00_MANAGEMENT/`）|
| **推荐** | 选项 A：`docs/01_GOVERNANCE/` 已存在，创建子目录成本低，且规则不需要大改 |
| **行动** | Phase A: 创建 `docs/01_GOVERNANCE/STANDARDS/`、`PLAYBOOKS/`、`REGISTERS/` 目录及 INDEX 文件 |
| **优先级** | P0 |
| **owner_sign** | TBD |

---

## 执行优先级汇总

| 优先级 | 裁决项 | 预估影响文件数 |
|--------|--------|--------------|
| **立即（Phase A）** | D12（01_GOVERNANCE 目录结构） | 创建 3 个目录 + INDEX |
| **P1（Phase C/D）** | D1（知识库合并）、D10（backup 删除） | ~8 文件合并 + 1396 删除 |
| **P1（Phase D）** | D2（归档区合并）、D3（审计存储合并）、D5（施工文档）| ~140 文件迁移 |
| **P2（Phase D）** | D4、D7、D8、D9、D11 | 各 1-48 文件 |
| **长期（未来）** | D6（蓝图按层分目录） | ~495 文件大迁移 |
