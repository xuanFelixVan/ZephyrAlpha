---
module_id: 09_AUDIT_STANDARDS_DOC_ORPHAN_DUP_PLAYBOOK_001
version: 1.0.0
status: Active
created_date: 2026-04-08
last_updated: 2026-04-09
owner: 文档治理系统
standard_type: 治理方案（全流程）
applicable_scope: 全库 `docs/**/*.md`（孤儿与重复/重叠）
compliance_level: 专业标准
related_documents:
  - ./DUPLICATE_DOCUMENT_HANDLING_STANDARD.md
  - ../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md
  - ../STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md
  - ../STATE/STRICT_ORPHAN_FILES_LIST_20260408.txt
  - ../../06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md
  - ../../06_ARCHIVE/OVERLAP_CANONICAL_POINTER_TEMPLATE.md
  - ../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md
---

# 全库文档：孤儿与重复/重叠治理方案（Playbook）

> **目的**：用可审计、可分批、可门禁的方式，统一处理 **严格孤儿（入度=0）** 与 **重复/重叠（duplicate / overlap）**，避免「一次性改几百个文件」或「无台账的硬删」。

---

## 1. 范围与不在范围

| 项目 | 说明 |
|------|------|
| **范围** | `docs/**/*.md`（以当前仓库文档体系为准） |
| **统计口径（孤儿）** | 仅统计 Markdown **相对路径**指向的 `.md` 入链；忽略外链、锚点、非 `.md` |
| **排除入口（孤儿统计）** | 见 `STRICT_ORPHAN_FILES_REPORT_*` 中「排除入口」条款（如部分 `INDEX.md` / `README.md` / 指定枢纽文） |
| **不在范围** | 源码树、生成物、二进制；若需治理代码内文档，另立规范 |

---

## 2. 概念对齐

### 2.1 孤儿（Orphan）

- **严格孤儿**：没有任何其他 `docs` 内 Markdown 以相对链接指向该文件（**inbound = 0**）。  
- **治理意义**：不一定是「垃圾」——可能是高价值但未挂入口；需 **分桶** 再动作。

### 2.2 重复与重叠

- **重复（duplicate）**：同题多份、多版本并存，需要 **canonical 裁决**（见专门标准）。  
- **重叠（overlap）**：合并/迁移产生的副本或中间产物（常见命名 `overlap_*`），**默认非真源**，需 **canonical 指针** 与可追溯说明。

### 2.3 真源（canonical）

- 每个主题 **对外只认一条权威正文**；索引与对外引用 **优先指向 canonical**。  
- 细则见：[重复文档处理标准（canonical 裁决）](./DUPLICATE_DOCUMENT_HANDLING_STANDARD.md)。

---

## 3. 总原则（机构常用）

1. **先止血、后整形**：先保证 **可发现 + 不误导**（入口、非真源声明），再合并/重写/删除。  
2. **单一真源**：重复类问题必须产出 **明确 canonical** 或经批准的 `TBD` + 台账。  
3. **小批迭代**：按 **业务域/主题** 分批，每批可评审、可回滚、可跑门禁。  
4. **台账优先**：裁决与处置写入 **台账或索引**，避免口头约定。  
5. **自动化门禁**：合并前 **链接扫描**（如 L1）**无效链接为 0**（团队约定为准）。

---

## 4. 孤儿治理流程（端到端）

### 4.1 生成清单

- 使用当前版本的 **严格孤儿报告** 与 **清单文本**（示例：`STRICT_ORPHAN_FILES_REPORT_20260408.md`、`STRICT_ORPHAN_FILES_LIST_20260408.txt`）。  
- **周期**：里程碑或每月；重大合并/迁移后 **加跑一次**。

### 4.2 分桶（与报告一致）

| 分桶 | 含义 | 建议动作 |
|------|------|----------|
| **A · 应挂入口** | 高价值、仍属现行体系 | 在对应域 **`INDEX.md` / 分组索引** 增加链接（只索引，不大改正文） |
| **B · 应归档** | 历史/重叠/重复池候选 | 移入 `06_ARCHIVE/` 或 `09_ARCHIVE/` 等，并 **更新索引与 canonical 台账** |
| **C · 需人工判定** | 边界模糊 | Owner 裁决后转入 A 或 B；必要时先标 `TBD` |

### 4.3 执行顺序（推荐）

1. **业务主干目录优先**：`01_FRAMEWORK` → `03_TRADING_TACTICS` → `05_IMPLEMENTATION` → `09_AUDIT/REPORTS` 等（可按你们系统重要性调整）。  
2. **每批体量**：单次 PR 建议 **20～50 条链接** 或 **单域一节**，避免大爆炸。  
3. **验收**：本批涉及路径 **L1 无新增无效链接**；必要时抽样点击验证。

### 4.4 与「排除入口」的关系

- 被统计规则 **排除** 的文件不参与「孤儿」计数，但仍可能需要在 **父级导航** 中暴露——以报告定义为准，避免重复劳动。

---

## 5. 重复 / 重叠治理流程（端到端）

### 5.1 发现

- 审计脚本、人工评审、合并冲突、`duplicates` 池、`overlap_*` 命名等。

### 5.2 canonical 裁决

- 遵循：[重复文档处理标准](./DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) 中的 **优先级与输出要求**。  
- **台账**：`docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`（或团队指定真源台账）。

### 5.3 非真源处置

- **重复文档**：在非真源顶部增加 **Superseded + canonical 链接**（见上述标准模板）。  
- **overlap_***：使用 [`OVERLAP_CANONICAL_POINTER_TEMPLATE.md`](../../06_ARCHIVE/OVERLAP_CANONICAL_POINTER_TEMPLATE.md) 或等价声明，填写 **`canonical_path`**（暂无则 `TBD` 并在台账备注）。

### 5.4 入口收敛

- 各域 `INDEX.md`、SITEMAP、导航页 **只推荐 canonical**；非真源仅作为「追溯/历史」被索引。

### 5.5 清理窗口

- 建议 **30 / 90 / 180 天** 追溯期；到期删除或深归档须在 **索引或台账** 记录日期与理由。

### 5.6 并行排期（推荐）

- 详见：[`OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md`](../../06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md)（overlap 与孤儿 **双轨、分批**）。

---

## 6. 工具与门禁

| 工具 | 用途 |
|------|------|
| `scripts/governance/sentinel_l1_governance_scan.py`（根目录同名入口可转发） | Markdown **内链有效性**扫描；合并前 **Invalid links = 0**（团队约定） |
| 严格孤儿报告 / 清单 | 孤儿 **分桶与批量挂接** 的输入 |
| `CANONICAL_POINTERS.md` | 重复裁决 **台账** |
| overlap 模板与排期文档 | **重叠副本** 指针与批次节奏 |

---

## 7. 角色与职责（RACI 简版）

| 活动 | Owner（各域） | 治理 / 架构 | 执行人 |
|------|----------------|---------------|--------|
| 裁决 canonical | C | A | R |
| 更新 INDEX 挂接 | A | C | R |
| 维护 overlap/duplicate 台账 | C | A | R |
| 跑 L1 并修链接 | R | A | R |
| 删除/深归档 | A | C | R |

（R=执行，A=负责，C=征询）

---

## 8. 度量与退出标准（建议）

| 指标 | 说明 |
|------|------|
| **严格孤儿数量（分桶）** | A/B/C 随时间 **A 下降**（或转化为已挂接） |
| **L1 无效链接** | 长期保持 **0** |
| **无指针 overlap 数量** | `overlap_*` 中缺 **canonical 声明** 的篇数 **下降** |
| **台账覆盖率** | duplicates 条目中 **`canonical_path` 可解析比例** |

**阶段退出（示例）**：主干域 INDEX 已完成 A 类挂接；overlap 按主题批次完成指针；L1 稳定；台账无未决 `TBD` 或已全部登记 Owner。

---

## 9. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-04-08 | 初版：孤儿 + 重复/重叠 全流程 Playbook |

---

## 10. 执行记录（运行时追加）

| 日期 | 动作 | 说明 |
|------|------|------|
| 2026-04-08 | `docs/09_AUDIT/INDEX.md` | 挂载 Playbook、严格孤儿报告、REPORTS 分组索引；根目录 7 篇补充入口链接；**L1：Invalid links = 0** |
| 2026-04-08 | [`BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md`](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | 蓝图阶段「彻底清洁」总执行案（P0–P3）；`scripts/strict_orphan_inbound_scan.py` 供孤儿清单重算 |
| 2026-04-08 | `docs/09_RESEARCH_INNOVATION/INDEX.md`、`docs/11_STRATEGIC_DECISION/INDEX.md` | 持续合入：`_archive/` / `archive/` 可点击入口（严格孤儿清单对账） |
| 2026-04-08 | `docs/10_GOVERNANCE_COMPLIANCE/INDEX.md`、`docs/04_EXECUTION/INDEX.md`、`docs/INDEX.md` | 持续合入：Layer 10 子目录直链、执行层 2 篇、`module_designs` L0_QMT 根索引入口 |
| 2026-04-08 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md` | 遗留路径 `docs/06_CONSTRUCTION_DOCS/`：从 canonical 建设索引挂 `01_BLUEPRINTS` 与 `A_STOCK_DATA_PROCESSING_BLUEPRINT`（相对路径 `../../06_CONSTRUCTION_DOCS/...`）；**L1：Invalid links = 0**；`STRICT_ORPHAN_FILES_LIST_REGEN_20260408.txt` 供与 `STRICT_ORPHAN_FILES_LIST_20260408.txt` 基线 diff |
| （既有） | `docs/01_FRAMEWORK/INDEX.md`、`docs/03_TRADING_TACTICS/INDEX.md`、`docs/05_IMPLEMENTATION/INDEX.md`、`docs/07_RESEARCH/INDEX.md` | 主干域分批挂接（见各索引内「严格孤儿」小节） |
| 2026-04-09 | `01_BLUEPRINTS/` 4 篇未入台账蓝图 | Trae GLM-5.1 自主窗口：全量对账发现 9 篇未在台账批次的蓝图，其中 4 篇补齐 §0.1 职责边界（OPENING_STRATEGY / OBJECT_STORAGE_INTEGRATION / MULTI_STRATEGY_HIERARCHICAL_SYSTEM / MULTI_PERIOD_DYNAMIC_OPTIMIZATION），5 篇已合规无需修改；**L1：Invalid links = 0**；REGEN 孤儿 532 篇 |
| 2026-04-09 | 全库治理大扫除 | Trae GLM-5.1 自主窗口续跑：DEDUP 2簇修复（FACTOR_GUIDE_001 + STRICT_ORPHAN_REPORT）→ module_id 重复=0；532 ORPHAN 全部入站链（06_ARCHIVE + 09_ARCHIVE INDEX.md 转链接格式 + STATE INDEX 补链）；401→326 NO-MID 补 module_id + 3 overnight_runs 重复修复 → dup=0；21 DIR 任务 + 4 EXT 任务完成（补 06_CONSTRUCTION_DOCS + 09_ARCHIVE INDEX.md）；**全程 L1：Invalid links = 0，dup = 0** |
| 2026-04-09 | [`TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md`](../STATE/TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md) Part B / 主清单收口 | **1062/1062** 任务全勾选；**L1：Invalid links = 0**；首道 `module_id` **重复 = 0、缺省 = 0**；双 YAML **= 0**（约 830 篇合并为单头，多轮修复）；`module_id` 登记 **3054**；REM **P1-A/B/C** + **EC-1～EC-7** 闭环；**CG3** 施工门禁块与 **SUB** 子树边界通过；**AUDIT** 全方案 **35** 批次完成（另 9 篇补 FM）；**Git tag**：`doc-milestone-20260409-partb-complete` |
