---
module_id: AUDIT_RULES_PHANTOM_MAP_20260416
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
doc_type: audit_report
priority: P0
---

# .cursor/rules 幻影引用映射表

> **背景**：.cursor/rules/ 中定义的路径约定与磁盘实际结构存在严重脱节。
> 本表记录每处幻影引用的现状、实际路径（若文件存在）以及修复动作。
> **修复原则**：优先更新规则路径指向实际位置；对规则定义了但未建的目录，在正确位置创建。

---

## 文件：audit-system.mdc

| 规则中引用路径 | 磁盘状态 | 实际路径 | 修复动作 |
|--------------|---------|---------|---------|
| `docs/01_GOVERNANCE/HANDOFF/project-office-ai-handoff.md` | 不存在（目录不存在） | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/project-office-ai-handoff.md` | 更新规则路径 |
| `docs/01_GOVERNANCE/governance-tools-index.md` | 不存在 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/governance-tools-index.md` | 更新规则路径 |
| `docs/01_GOVERNANCE/governance-documents-navigation.md` | 不存在 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/governance-documents-navigation.md` | 更新规则路径 |
| `docs/01_GOVERNANCE/STANDARDS/document-map-and-placement-governance.md` | 不存在 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/document-map-and-placement-governance.md` | 更新规则路径 |
| `docs/07_AUDIT/STANDARDS/` | 不存在（07_AUDIT 不存在） | `docs/09_AUDIT/STANDARDS/`（34 个标准文档）| 更新规则路径：07→09 |
| `docs/07_AUDIT/PROCEDURES/audit-execution-runbook.md` | 不存在 | 不存在（需创建） | 创建文件后更新路径 |
| `docs/07_AUDIT/STATE/` | 不存在 | `docs/09_AUDIT/STATE/`（558 个报告）| 更新规则路径：07→09 |
| `docs/ARCHIVE/` | 不存在 | `docs/06_ARCHIVE/`（716 文件）| 更新规则路径 |
| `scripts/governance/scan/` | 不存在（scan/ 子目录不存在）| `scripts/governance/`（脚本直接在此目录）| 更新规则路径 |
| `scripts/governance/fix/` | 不存在 | `scripts/governance/`（同上）| 更新规则路径 |
| `scripts/governance/validate/` | 不存在 | `scripts/governance/`（同上）| 更新规则路径 |
| `scripts/governance/report/` | 不存在 | `scripts/governance/`（同上）| 更新规则路径 |
| `TECHNOLOGY_BACKLOG.md`（ghost salvage 目标）| 不存在 | 需创建于 `docs/02_ARCHITECTURE/TECHNOLOGY_BACKLOG.md` | 创建文件 |
| `IDEAS_PIPELINE.md`（ghost salvage 目标）| 不存在 | 需创建或确认位置 | 待确认 |
| `audit-report-retention-standard.md`（规则引用）| 不存在 | 不存在（需创建）| 创建于 `docs/09_AUDIT/STANDARDS/` |

---

## 文件：project-conventions.mdc

| 规则中引用路径 | 磁盘状态 | 实际路径 | 修复动作 |
|--------------|---------|---------|---------|
| `docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md` | **存在** ✓ | 路径正确 | 无需修复 |
| `docs/04_CONSTRUCTION/PLANS/INDEX.md` | **存在** ✓ | 路径正确 | 无需修复 |
| `docs/02_ARCHITECTURE/MODULE_INVENTORY.md` | 不存在（`02_ARCHITECTURE/` 不存在）| 需创建 | 创建目录 + 文件 |
| `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` | 不存在 | 需创建 | 创建文件 |
| `docs/02_ARCHITECTURE/DEV_ENV_SETUP.md` | 不存在 | 需创建 | 创建文件 |
| `docs/02_ARCHITECTURE/SYSTEM_PANORAMA.md` | 不存在 | 需创建 | 创建文件（可指向 01_FRAMEWORK/ARCHITECTURE.md）|
| `docs/02_ARCHITECTURE/TECHNOLOGY_BACKLOG.md` | 不存在 | 需创建 | 创建文件 |
| `docs/01_GOVERNANCE/STANDARDS/file-governance-automation-rules.md` | 不存在 | 不存在（需创建或迁移）| 创建于 `docs/01_GOVERNANCE/STANDARDS/` |
| `docs/01_GOVERNANCE/STANDARDS/configuration-management-plan.md` | 不存在 | 不存在 | 创建 |
| `docs/01_GOVERNANCE/STANDARDS/document-encoding-standard.md` | 不存在 | 不存在 | 创建 |
| `docs/01_GOVERNANCE/STANDARDS/information-architecture-standard.md` | 不存在 | 不存在（`09_AUDIT/STANDARDS/` 中有相关内容）| 可创建为指向 09_AUDIT/STANDARDS 的导航文件 |
| `docs/01_GOVERNANCE/REGISTERS/controlled-documents-register.md` | 不存在（REGISTERS/ 不存在）| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/controlled-documents-register.md` | 在 `01_GOVERNANCE/REGISTERS/` 创建 symlink-style 导航文件，或迁移 |
| `docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md` | 不存在 | 不存在（需创建）| 创建 |
| `docs/03_BLUEPRINTS/L{XX}_*/` | 不存在（整个目录树不存在）| `docs/01_FRAMEWORK/`（332 文件）| 规则更新为 `docs/01_FRAMEWORK/`（短期）；长期创建 03_BLUEPRINTS |
| `docs/06_KNOWLEDGE_BASE/` | 不存在 | `docs/08_KNOWLEDGE/`（13 文件）| 更新规则路径 |
| `docs/00_OVERVIEW/SITEMAP.md` | 不存在（实际在根目录）| `docs/SITEMAP.md` | 更新规则路径 |
| `BLUEPRINT_DOMAIN_INVENTORY.md` | 不存在（全库无此文件）| 需创建 | 创建于 `docs/02_ARCHITECTURE/` 或 `docs/01_FRAMEWORK/` |
| `docs/07_AUDIT/PROCEDURES/audit-execution-runbook.md` | 不存在 | `docs/09_AUDIT/PROCEDURES/`（目录存在但为空）| 创建文件 + 更新路径 |
| `docs/06_KNOWLEDGE_BASE/` 各索引（KMS 条目规则）| 不存在 | `docs/08_KNOWLEDGE/` | 更新路径 |
| `docs/01_GOVERNANCE/PLAYBOOKS/construction-change-impact-playbook.md` | 不存在 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/`（无此文件）| 创建于正确位置 |
| `docs/03_BLUEPRINTS/L{XX}_{LAYER}/`（蓝图写入路径锁定）| 不存在 | `docs/01_FRAMEWORK/`（暂定）| 更新路径锁定表 |

---

## 文件：code-conventions.mdc

| 规则中引用路径 | 磁盘状态 | 实际路径 | 修复动作 |
|--------------|---------|---------|---------|
| `docs/04_CONSTRUCTION/PLANS/MASTER_DEVELOPMENT_PLAN.md` | **存在** ✓ | 路径正确 | 无需修复 |
| `docs/04_CONSTRUCTION/PLANS/CONSTRUCTION_PLAN_*.md` | **存在** ✓（L00 已创建）| 路径正确 | 无需修复 |
| `docs/03_BLUEPRINTS/L{XX}/`（蓝图确认路径）| 不存在 | `docs/01_FRAMEWORK/` | 更新路径 |
| `docs/01_GOVERNANCE/PLAYBOOKS/construction-change-impact-playbook.md`（施工后参考）| 不存在 | 需创建 | 创建文件 |

---

## 修复执行计划（按优先级）

### 立即执行（不阻塞施工的修复）

1. **创建 `docs/02_ARCHITECTURE/` 目录** 及以下 5 个核心文件（空白骨架，待后续填充）：
   - `MODULE_INVENTORY.md`
   - `TECH_DECISION_RECORDS.md`
   - `DEV_ENV_SETUP.md`
   - `SYSTEM_PANORAMA.md`
   - `TECHNOLOGY_BACKLOG.md`

2. **创建 `docs/01_GOVERNANCE/` 子目录结构**：
   - `STANDARDS/INDEX.md`
   - `PLAYBOOKS/INDEX.md`
   - `REGISTERS/INDEX.md`（含 controlled-documents-register.md、lessons-learned-register.md）

3. **更新 `.cursor/rules/*.mdc`** 中的路径引用（主要是 07_AUDIT→09_AUDIT，01_GOVERNANCE/XXX→实际路径）

4. **创建缺失的高优先级文档**：
   - `docs/09_AUDIT/PROCEDURES/audit-execution-runbook.md`
   - `docs/09_AUDIT/STANDARDS/blueprint-lifecycle-standard.md`（Phase B）

### 短期执行（Phase D，需 Owner 签核）

5. 更新规则中的蓝图路径：`docs/03_BLUEPRINTS/L{XX}/` → `docs/01_FRAMEWORK/`（过渡期）
6. 更新 `docs/06_KNOWLEDGE_BASE/` → `docs/08_KNOWLEDGE/`

---

## 幻影引用统计

| 类别 | 数量 |
|------|------|
| 路径错误（文件存在，路径不对）| 8 |
| 文件不存在（需新建）| 12 |
| 目录结构不存在（需建目录）| 5 |
| **合计幻影引用** | **25** |
| 路径正确（无需修复）| 4 |
