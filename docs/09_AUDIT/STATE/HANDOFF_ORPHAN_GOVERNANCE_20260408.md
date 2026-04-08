---
module_id: HANDOFF_ORPHAN_GOVERNANCE_20260408
version: 2.0.0
status: Active
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 文档治理系统
standard_type: 工作交接（整册方案）
applicable_scope: Trae（GLM-5.1）等连续长时执行 + Cursor 接力；蓝图阶段清洁至「可进入第 2 阶段（施工文档）」
compliance_level: 与 Playbook、总执行案、施工门禁、Trae 台账一致
related_documents:
  - ../STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md
  - ../STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md
  - ../STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md
  - ../PROCEDURES/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md
  - ../PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md
  - ../PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md
  - ../PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md
  - ../PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md
  - ../REPORTS/REMEDIATION_EXECUTION_CLOSURE_20260408.md
  - ../../06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md
  - ../../06_ARCHIVE/OVERLAP_CANONICAL_POINTER_TEMPLATE.md
  - ../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md
  - ./STRICT_ORPHAN_FILES_REPORT_20260408.md
  - ./STRICT_ORPHAN_FILES_LIST_20260408.txt
  - ./CONSTRUCTION_GATE_CRITERIA_20260408.md
  - ./ARCH_MODULE_GAP_REGISTER_20260408.md
  - ./TRAE_BLUEPRINT_TASK_LEDGER_20260408.md
  - ./LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md
  - ../INDEX_AUDIT.md
responsibility:
  - 向下一任执行者交代完整方案：路径、门禁、防幻觉、Git 备份、Trae 长时作业、重复与分层导航
  - 目标状态：蓝图交付（门禁 §0.1/§0.1a）+ IA 可发现，可开写施工文档（第 2 阶段）
---

# 工作交接：蓝图阶段文档清洁与接力（孤儿 / 重复 / overlap）

> **场景 A（通用）**：用户暂时离开，由另一模型**连续数小时**自主推进治理。  
> **场景 B（本版强化）**：在 **Trae** 中使用 **GLM-5.1** **连续约 8 小时、中途不向 Owner 追问**时，以本文 + `TRAE_BLUEPRINT_TASK_LEDGER_20260408.md` 为执行剧本，目标结束时达到 **蓝图交付标准**（`CONSTRUCTION_GATE` §0.1 / §0.1a），**可进入施工文档（第 2 阶段）**；**第 3 阶段（写代码）**门槛见门禁 §3，勿与本文终点混淆。  
> **仓库根**：`d:\ZephyrAlpha`（以实际 clone 路径为准；下文路径均相对仓库根）。

---

## 0. 文档目录（按阅读顺序）

| 节 | 内容 |
|----|------|
| **1** | 业务目标与禁止事项 |
| **2** | 必读路径与 `related_documents` 索引 |
| **3～8** | 孤儿口径、L1 门禁、已知坑、推荐工作顺序、沟通约定、一句话结论 |
| **9** | 可一并做的检查（脚本与方案） |
| **10** | 过时审计/STATE 处理原则 |
| **11** | 清洁阶段 checklist（P0～P3）与模块↔蓝图互链（§11.5） |
| **13** | 补救收口与门禁；IA hygiene §13.4～§13.6（含第 2 阶段前检查与终交付样貌） |
| **14** | 施工文档前专业机构清洁名目总表 |
| **15** | **Git 备份与安全合并**（长时作业强制） |
| **16** | **防 AI 幻觉与证据规则** |
| **17** | **Trae × GLM-5.1 连续 8 小时执行方案** |
| **18** | **重复文档 + Layer/子模块/蓝图互查** |
| **19** | 本文件变更记录 |

> 执行者**至少**通读：**0 → 15 → 16 → 17**，再按任务选读 §13～§14 与 §11。

---

## 1. 业务目标（勿跑偏）

| 要点 | 说明 |
|------|------|
| **机构化治理** | 严格孤儿（Markdown 相对链入度）、`duplicates`、`overlap_*`，**分批合入** |
| **禁止** | 单次 PR 或单次会话内改动「几百个文件」式大爆炸 |
| **孤儿基线** | 人工基线：`STRICT_ORPHAN_FILES_LIST_20260408.txt` |
| **进度重算** | `scripts/strict_orphan_inbound_scan.py` → `STRICT_ORPHAN_FILES_LIST_REGEN_<date>.txt`；**默认不要** `--basename` 覆盖 `20260408` 基线文件名 |

---

## 2. 必读与必用路径

| 用途 | 路径 |
|------|------|
| Playbook（含 §10 执行记录） | `docs/09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md` |
| 蓝图阶段「彻底清洁」总案 | `docs/09_AUDIT/PROCEDURES/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md` |
| overlap / orphan 并行节奏 | `docs/06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md` |
| 严格孤儿**基线**清单 | `docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_LIST_20260408.txt` |
| 严格孤儿**重算**清单 | `docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_LIST_REGEN_<date>.txt` |
| 重算脚本 | `scripts/strict_orphan_inbound_scan.py` |
| duplicates 台账 | `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md` |
| overlap canonical 模板 | `docs/06_ARCHIVE/OVERLAP_CANONICAL_POINTER_TEMPLATE.md` |
| 01_BLUEPRINTS 机器索引 | `scripts/generate_01_blueprints_index.py` → `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md` |
| STATE 分组承接（避免单页堆上百链） | `docs/09_AUDIT/STATE/INDEX_GROUPED_20260408.md` |
| 严格孤儿报告（人工分桶说明，与基线配套） | `docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md` |
| 审计门户（快速分流） | `docs/09_AUDIT/INDEX_AUDIT.md` |
| REPORTS 长列表分组 | `docs/09_AUDIT/REPORTS/INDEX_GROUPED_20260408.md` |
| 重复文档处理标准（与 Playbook 配套） | `docs/09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md` |
| 文档补救任务指令 | `docs/09_AUDIT/PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md` |
| 架构模块审计与 gap 计划 | `docs/09_AUDIT/PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md` |
| 施工门禁（先治理、后大规模编码） | `docs/09_AUDIT/STATE/CONSTRUCTION_GATE_CRITERIA_20260408.md` |
| Trae 蓝图任务台账 | `docs/09_AUDIT/STATE/TRAE_BLUEPRINT_TASK_LEDGER_20260408.md` |
| 夜间批跑（可选） | `scripts/overnight_audit_runner.py` |

### 2.1 关于「是否已收录全部相关文档」

- **已收录**：与「严格孤儿 + duplicates + overlap + 分批 INDEX 挂载 + L1 门禁」**直接相关**的主干与常见旁路（施工门禁、补救指令、重复标准、审计门户、分组索引等），见上表及 YAML `related_documents`。
- **未收录（刻意）**：全库数千篇 `docs/**/*.md` **不可能**也不应在交接中单列穷尽；具体孤儿路径以 **`STRICT_ORPHAN_FILES_LIST_REGEN_<date>.txt`** 与基线 diff 为准。
- **若总案引用其他日期戳文件**：以 `BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md` 内链接与 `09_AUDIT/PROCEDURES/`、`09_AUDIT/STATE/` 当日台账为准，按需打开。

---

## 3. 孤儿口径（与脚本一致）

- **链入来源**：仓库内**全部** `.md` 中解析出的 Markdown **内链**（标准写法为：方括号内锚文本，紧接圆括号内仓库相对路径，指向 `.md` 或其他资源）。
- **统计目标**：仅 `docs/**/*.md`。
- **排除「不算孤儿」的文件**：名为 `INDEX.md` / `README.md` / `SITEMAP.md`，以及 `docs/01_FRAMEWORK/` 下 `ARCHITECTURE.md`、`MODULE_RESPONSIBILITY_BOUNDARIES.md`、`BLUEPRINT_ARCHITECTURE_MAPPING.md`。
- 与 `scripts/sentinel_l1_governance_scan.py` 的相对路径解析规则对齐。

---

## 4. 质量门禁

每完成一批 `docs/**/*.md` 编辑：

```text
python scripts/sentinel_l1_governance_scan.py
```

- **目标**：**Invalid links = 0**。
- 若 `docs/09_AUDIT/STATE/` 下 `SENTINEL_L1_*`、`*REGEN*` 等生成物被 git 跟踪且**不打算提交**，可按惯例 `git restore` 对应文件。

---

## 5. 已知坑位（上一任已处理或踩过）

- **平行目录 `docs/06_CONSTRUCTION_DOCS/`**：与 canonical `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` 并存。canonical 侧已在 **`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md`** 增加「遗留路径」入口。
- **相对路径**：从 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md` 指向遗留树时，使用 **`../../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/...`**。多写一层 `../` 会指到**仓库根**下不存在的路径，**L1 会报无效链**。
- **基线 `20260408` 可能偏旧**：多域 `INDEX.md` 已分批挂载；以 **REGEN** 与磁盘为准做 diff，不要盲信旧清单行数与 IDE 缓存。

---

## 6. 推荐工作顺序（可循环 4～8 小时）

1. **对齐现状**  
   - 运行：`python scripts/strict_orphan_inbound_scan.py`（不加 `--basename`）。  
   - 对比：`STRICT_ORPHAN_FILES_LIST_REGEN_<date>.txt` vs `STRICT_ORPHAN_FILES_LIST_20260408.txt`。

2. **按簇小批挂载**  
   - 优先：高价值、非纯 `09_AUDIT/STATE` 流水报告、非一次性处理完的 `06_ARCHIVE/overlap_*` 大海。  
   - 动作：在**该域权威 `INDEX.md`** 增加「严格孤儿挂载」类小节，使用可点击的 Markdown 链接，目标为**真实存在的** `./子路径/文件名.md`。

3. **每 1～2 簇**  
   - 跑 L1；在 Playbook **§10** 追加一行（日期、改动文件、说明、L1 结果）。

4. **duplicates / overlap**（与总案 P 级对齐时）  
   - duplicates：更新 `CANONICAL_POINTERS.md`，**无台账勿硬删**。  
   - overlap：按 `OVERLAP_CANONICAL_POINTER_TEMPLATE.md` 补 canonical 指针块。

5. **收工**  
   - 再跑一次 REGEN；在 §10 或本文件末尾追加「与基线差异摘要」（可选）。

---

## 7. 与用户沟通约定

- 对用户说明使用**中文**；代码标识、文件名、量化术语保留**英文**。
- 未要求则**不**额外新建大篇 README；改动保持与任务同范围。

---

## 8. 一句话结论

下一任应以 **`strict_orphan_inbound_scan.py` 的 REGEN 清单** 驱动**小批 INDEX 挂载**，每批 **L1 门禁**，**Playbook §10 留痕**；并行推进 **duplicates 台账** 与 **overlap canonical 指针**，避免单次大范围文件变动。

---

## 9. 可一并做的检查（建议同一「治理批次」内跑完）

下列项**不互相替代**，但可在改完一批文档后**同一次会话**串行执行，减少「以为干净了其实漏项」：

| 检查项 | 命令或入口 | 说明 |
|--------|------------|------|
| **内链门禁** | `python scripts/sentinel_l1_governance_scan.py` | 目标：**Invalid links = 0**；报告里的 `module_id` 重复、无首道 `module_id` 等为**并列风险信号**，可按 `CONSTRUCTION_GATE` 与审计方案决定是否开独立修复批次 |
| **严格孤儿趋势** | `python scripts/strict_orphan_inbound_scan.py` | 对比 `REGEN_*` 与基线；关注**是否下降**，而非与基线篇数机械一致 |
| **01_BLUEPRINTS 索引与磁盘一致** | `python scripts/generate_01_blueprints_index.py` | 仅影响 canonical 蓝图目录索引；改完蓝图文件名后应重跑 |
| **全库文档审计阶段进度** | `docs/09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md` | 与「清洁」并行时，用该方案 **A～H**（及文中若载明的扩展阶段）对账进度，避免只修孤儿却漏审计口径 |
| **架构模块 gap** | `ARCH_MODULE_GAP_REGISTER_20260408.md` + `ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md` | 蓝图对齐、缺口登记与清洁批次可**交叉引用**（改 INDEX 时发现模块缺口则回填登记） |
| **夜间批跑（可选）** | `scripts/overnight_audit_runner.py` | 适合长时自动化汇总；产物仍须人工看结论，**不**等于豁免 L1 |

---

## 10. 「过时审计文件」能不能处理？怎么处理？

**可以处理，但默认不是「批量删除」**，而是 **可追溯收敛**，与总案「禁止无台账批量删除」一致。

| 类型 | 典型位置 | 建议动作 |
|------|----------|----------|
| **一次性扫描报告 / 中间态** | `docs/09_AUDIT/STATE/` 下大量带时间戳的报告、`SENTINEL_L1_*`、历史 FIX 报告 | **保留文件本体**优先；用 **`INDEX_GROUPED_20260408.md`**（或按日更新的分组页）承接入口；**勿**把上百篇逐链贴进单一 `INDEX.md`。若确需弱化干扰：在文首 front matter 增加 **`status: Superseded`**（或项目约定等价词）并**文字说明**替代真源路径（不强制改文件名，避免外链雪崩）。 |
| **REPORTS 长列表** | `docs/09_AUDIT/REPORTS/` | 以 **`REPORTS/INDEX_GROUPED_20260408.md`** 为枢纽；过时报告可标记「仅历史对账」并指向当前程序真源（如 Playbook、总案）。 |
| **仍约束当前行为的程序** | `PROCEDURES/*`、`STANDARDS/*`、施工门禁 | **不**因「日期旧」自动降级；若内容被取代，走 **TDR/ADR 或 Playbook 变更记录**，并在旧文顶部用**一段**说明「由哪篇接替」。 |
| **重复池 / overlap** | `09_ARCHIVE/duplicates`、`06_ARCHIVE/overlap_*` | **只**按 `DUPLICATE_DOCUMENT_HANDLING_STANDARD` 与 overlap 模板处理；删除或合并前**必须**更新 `CANONICAL_POINTERS.md` 或 overlap 台账。 |
| **生成物是否进 git** | `SENTINEL_L1_*`、`*REGEN*` | 若仓库策略为不提交：改完后 **`git restore`** 即可；若策略为提交基线：由 Owner 定夺，**交接人不擅自批量提交噪声**。 |

**结论**：「过时」多数是 **STATE/REPORTS 噪音**——用**分组索引 + 元数据声明 + 指向现行真源**解决；**不要**在无 Owner 书面确认下做「删半库审计 md」式清理。

---

## 11. 蓝图阶段「清洁」还剩什么要做？（对照总案 checklist）

以下与 `BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md` **§3 P0～P3** 与 **§5 退出标准**对齐，供接力者勾选推进（**非**要求单次会话全部完成）。

### 11.1 三条工作流（持续直到达标）

- [ ] **A. 严格孤儿**：P0 域（`01_FRAMEWORK`、`02_FACTOR_LIBRARY`、`03_TRADING_TACTICS`、`05_IMPLEMENTATION`、治理标准/程序）**高价值**文档可从约定 `INDEX.md` 链达；`REGEN` 相对基线**明显下降**。
- [ ] **B. duplicates**：`CANONICAL_POINTERS.md` 中 **无悬空 TBD**（或每条已指派 Owner/截止日）；非真源已 **Superseded** 或等价声明。
- [ ] **C. overlap**：`overlap_*` 已按模板具备 **canonical 指针**（或登记豁免）；节奏见 `OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md`。

### 11.2 分阶段（P0 → P3）

- [ ] **P0**：上述蓝图关键路径目录的 A 类孤儿挂接；每 PR **L1 = 0**。
- [ ] **P1**：`09_AUDIT/REPORTS` 坚持分组索引策略；`07_RESEARCH`、`08_KNOWLEDGE` 子目录 `INDEX.md` 分批补链。
- [ ] **P2**：duplicates 池按标准「结案」（台账先行）。
- [ ] **P3**：overlap 全量指针（与 P0～P1 **错开 PR、小批**）。

### 11.3 退出标准（总案 §5，蓝图阶段可宣告清洁达标）

- [ ] 主干 INDEX 与 Playbook 所述入口一致或等效可发现。
- [ ] 默认分支 **L1 Invalid links = 0**。
- [ ] duplicates / overlap 满足台账与指针要求。
- [ ] 孤儿重算趋势符合预期（篇数阈值由项目/Owner 约定，**非**机械清零执念）。

### 11.4 与「蓝图终稿 / 施工」的边界（避免清洁与门禁脱节）

- **文档「可发现、链接可门禁」**（本交接主战场）**不自动等于**「全库蓝图终稿已达标」。
- **蓝图终稿 + 施工前置**：以 `CONSTRUCTION_GATE_CRITERIA_20260408.md` **§0～§3** 为准（含 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD`、`03_CONSTRUCTION_PLANS/INDEX.md`、契约与 TDR 等）。
- **文档补救与执行收口（Remediation & Execution Closure）**：见 **§13**（行业通用概念与本仓库承载文件的对应关系）。

### 11.5 模块 ↔ 蓝图：要不要「互相都建索引」？

**要做能力范围内的检查，但不要求「每一个模块文档与每一份 `01_BLUEPRINTS` 蓝图都双向互链」**——否则组合爆炸、维护成本不可接受。仓库内口径如下。

| 层次 | 要求（摘要） | 真源依据 |
|------|----------------|----------|
| **权威栈互达** | `ARCHITECTURE.md`、`MODULE_RESPONSIBILITY_BOUNDARIES.md`、`BLUEPRINT_ARCHITECTURE_MAPPING.md` 与**至少**本轮 P0 相关实施蓝图之间，读者能沿 **有效相对链接** 往返（审计方案 **Q3**） | `ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md` **§六 Q3** |
| **孤儿蓝图（内容级）** | 若某长篇 `*_BLUEPRINT.md` 在总纲/边界/映射中**没有挂载点**，记为 **G4**，须在 gap 登记并补缺——这与「严格孤儿（入度）」是**不同维度**（G4 看语义挂载，入度看任意 md 链） | 同方案 **§三 G4** |
| **新增蓝图** | 新增或重命名后，应在 `BLUEPRINT_ARCHITECTURE_MAPPING.md` **或** `ARCHITECTURE.md` 的「相关文档」中 **至少一处**可点击到达 | `BLUEPRINT_ARCHITECTURE_MAPPING.md` **§4** |
| **全量列表** | `01_BLUEPRINTS/INDEX.md` 由脚本生成，承担「**全集可发现**」，**替代**「每篇蓝图再从每个模块 INDEX 指一遍」 | `generate_01_blueprints_index.py` |
| **`module_designs/`** | 与垂直切片绑定后再做**有边界**的对照；未纳入切片前**不**强行要求与全部蓝图互链 | `ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md` **§二** |
| **能力对照表（可选增强）** | 若存在如 `LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_*.md` 等台账，用于「能力 ↔ 蓝图」批量对齐，与上述栈**并列**使用，仍不替代单篇蓝图的职责/契约闭合 | 见 `ARCHITECTURE.md` 等处的引用 |

**推荐自检句式（接力时可当 checklist）**：

- [ ] 从 `ARCHITECTURE` 能否到达边界、映射、`01_BLUEPRINTS/INDEX`？  
- [ ] 从映射/边界能否回到 `ARCHITECTURE` 与关键蓝图？  
- [ ] P0 切片涉及的蓝图是否在总纲或映射中有「语义挂钩」（而不仅是文件存在于目录）？  
- [ ] 新发现的 G4/G5 是否写入 `ARCH_MODULE_GAP_REGISTER_20260408.md`？

---

## 13. 文档补救与执行收口（Remediation & Execution Closure）与施工门禁

### 13.1 行业通用术语（与门禁的关系）

在机构文档治理里，常见表述包括：

| 通用术语 | 含义 |
|----------|------|
| **文档补救（Document remediation）** | 针对已发现的缺陷（断链、元数据、重复、越权路径等）按**程序**整改，并留痕。 |
| **执行收口（Execution closure）** | 一轮补救结束后，用**核对清单 + 报告**声明「约定条目已满足」或「剩余例外已登记」。 |
| **门禁符合性（Gate attestation）** | 进入下一阶段（如编码）前，用**可复跑检查**（如链接扫描、双 YAML 列表）证明仍符合门槛。 |

**施工门禁**把这些东西写进 **`CONSTRUCTION_GATE_CRITERIA_20260408.md`**：既约束「蓝图终稿」，也约束「放行前证据是否仍然成立」。

### 13.2 本仓库中的实现载体（文件名）

- 上述程序的**具体作业说明**当前承载于 `docs/09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`（文件名含历史项目代号；**可整体重命名**，但须同步修改 `CONSTRUCTION_GATE` 的 `parent_document` 与全库引用）。
- 门禁 **§1～§3** 将 **EC-1～EC-7**（本仓库收口核对条目）、L1、双 YAML 等与「是否放行施工」挂钩。
- **§2** 引用 `REMEDIATION_EXECUTION_CLOSURE_20260408.md` 等，作为**是否重复劳动**的对照。

### 13.3 与「蓝图阶段信息卫生」的分工

- **Playbook / 清洁总案 / 严格孤儿 / duplicates / overlap**：主抓 **可发现性、单真源、台账与指针**。
- **补救与收口章节（门禁 §1～§3）**：主抓 **已承诺的整改闭环是否在放行前仍成立**（链接、双 YAML、例外清单等）。

两条线**都要满足各自门槛**，但职责不同，**不要混成一条模糊大杂烩**。

### 13.4 蓝图 / IA hygiene：目标、边界与分层（进入第 2 阶段前）

#### 13.4.1 目标（Goal）

在撰写**施工文档（门禁第 2 阶段：施工流程 / 计划 / 方案等）**之前，应达到机构里常见的 **blueprint / information architecture hygiene** 目标：

- **权威阅读路径干净、少误导**：新读者沿「主干导航」走时，能稳定到达**现行真源**（架构、契约、蓝图、核心索引），而不被过程稿、过期结论或重复副本带偏。

#### 13.4.2 边界（Boundary）——「足够干净」不是什么

「足够干净」**一般不是**「整个 `docs` 只剩蓝图和索引」，而是：

| 区域 | 期望状态 |
|------|----------|
| **权威区** | **架构**（`docs/01_FRAMEWORK/` 枢纽文）、**契约**（如 `docs/03_TRADING_TACTICS/API_Contract.md`）、**实施蓝图**（`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`）、**核心 `INDEX.md`**：尽量**清晰、终稿化**（对齐门禁 §0.1）。 |
| **过程稿 / 临时扫描报告** | **可以很多**；但必须落在 **`09_AUDIT/STATE`**、**`09_AUDIT/REPORTS`**、**归档树**（如 `06_ARCHIVE`、`09_ARCHIVE`）等约定位置，并用 **分组索引 + 状态 / 文首说明**，避免读者从**主干**误以为仍是**现行真源**（细则见本交接 §10）。 |

#### 13.4.3 分层（机构常用做法）

| 分层 | 说明 |
|------|------|
| **权威区（canonical）** | 读者默认从这里理解系统；忌未解释的 TBD、忌把一次性扫描结论写得像终态规范。 |
| **工作区 / 过程稿** | 允许大体量；靠 **分组索引承接** 与 **元数据（如 Superseded / 过程性说明）** 降噪。 |
| **归档区** | 历史、对照、重复池、overlap；与现行设计明确区分。 |

**结论**：蓝图阶段的「干净」= **信息架构与真源清晰**（该去哪读、什么已过时），≠ **物理上只留蓝图**。临时、一次性或与主干无关的过程稿，宜 **归位 + 标记 + 索引分流**，**非**无台账大规模硬删。

### 13.5 如何达到 §13.4 的目标（可执行方案）

按**批次**推进，每批结束跑 **L1**（见本交接 §4）。下列顺序可按人力压缩或并行，但**不要跳过「定义金线」**。

| 步骤 | 动作 | 产出 / 门禁 |
|------|------|-------------|
| **S1 定义权威阅读路径（金线）** | 在 `docs/INDEX.md` 与 `docs/01_FRAMEWORK/ARCHITECTURE.md` 中明确：**新人应先读哪些文档、顺序是什么**；链到 `MODULE_RESPONSIBILITY_BOUNDARIES`、`BLUEPRINT_ARCHITECTURE_MAPPING`、`01_BLUEPRINTS/INDEX.md`。 | 主干上任意一点可在 **≤3～4 次点击**内到达契约与蓝图索引。 |
| **S2 权威区终稿化** | 对门禁 §0.2 划定范围内的蓝图逐篇核对 §0.1（职责、契约指针、验收、status/version、占位闭合）。 | 未达标篇目记入 `ARCH_MODULE_GAP_REGISTER_20260408.md`，标 P0/P1。 |
| **S3 过程稿归位** | 将误放在权威树下的「纯过程」扫描/中间报告，**移动或改链**至 `09_AUDIT/STATE` 或 `REPORTS`（遵守 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD`）；**禁止**仅在主干 `INDEX` 上堆数百条报告链接。 | 新稿有明确「家」；主干 INDEX 只保留**分组入口**（如 `INDEX_GROUPED_*.md`）。 |
| **S4 状态与说明** | 对仍保留但已过时、仅供对账的过程文档：在文首或 front matter 标明 **Superseded / 过程稿 / 替代真源路径**（见 §10）。 | 读者误入时**第一眼**可知非现行规范。 |
| **S5 可发现性（非删库）** | 对 P0 域跑 `strict_orphan_inbound_scan.py`，将 **A 类高价值**孤儿挂到对应域 `INDEX.md`；全集蓝图依赖 `generate_01_blueprints_index.py` 维护的 `01_BLUEPRINTS/INDEX.md`。 | `REGEN` 相对基线**下降**；不要求篇数机械归零。 |
| **S6 duplicates / overlap** | 按台账与模板推进（本交接 §11、§14.5），与 S1～S5 **错开 PR、小批**。 | `CANONICAL_POINTERS` 无悬空 TBD；overlap 有指针或豁免。 |
| **S7 放行前核对** | 对照 `CONSTRUCTION_GATE_CRITERIA_20260408.md` **§0.1 / §0.1a**（写第 2 阶段前）；第 3 阶段另有 §0.3、§3，勿提前混用。 | Owner 可勾选「权威区 + 放置 + LAYOUT」后再开写施工文档。 |

**验收直觉**：一位不熟悉仓库的同事，只打开 `docs/INDEX.md` 与 `ARCHITECTURE.md`，能在**不打开 STATE 海**的前提下，把**当前系统设计**讲清楚；需要查某次历史扫描时，能从 **REPORTS/STATE 分组索引**下去，且不会与蓝图终稿混淆。

### 13.6 写施工文档（第 2 阶段）之前还要做什么？蓝图阶段最终交付长什么样？

> **真源**：`docs/09_AUDIT/STATE/CONSTRUCTION_GATE_CRITERIA_20260408.md` **§0**；本节为其摘要 + 与本交接其他节的交叉引用。

#### 13.6.1 门禁口径：谁挡在第 2 阶段前面？

`CONSTRUCTION_GATE` 约定：**第 2 阶段（施工流程 / 计划 / 方案）须在 §0「蓝图终稿」放行之后**才能开写。在此之前应完成的主块如下（可按团队并行，但**放行前**须整体成立）。

**A. 蓝图终稿（§0.1，对 §0.2 范围内每一篇）**

默认范围（§0.2）：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` 下除 `INDEX.md` 外全部 `*.md`，以及 `docs/01_FRAMEWORK/` 下文件名含 `BLUEPRINT` 的 `*.md`；**可选扩展**（如 `11_STRATEGIC_DECISION`、`module_designs/`）须在 §0.2 表或 §4 **书面列出**后才按同标准验收。

§0.1 五条须**同时**满足（扩展范围内的每篇亦然）：

1. **职责**：负责什么 / 不负责什么已写清。  
2. **接口**：与邻层、邻模块约定可指到 `docs/03_TRADING_TACTICS/API_Contract.md`（或等价契约）。  
3. **验收**：至少一句**可检查**的完成标准。  
4. **状态**：front matter 中 `status` 不得为 `Draft`；`version ≥ 1.0.0`。  
5. **闭合**：篇首或显著位置无未解释的 Draft/待补/TBD；已知限制须进「已知限制」并附补全计划或 §4 豁免。

**B. 放置与目录（§0.1a）**

- [ ] `docs/09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md` 已阅读并与 Owner 意图一致（冲突则改标准或登记豁免）。  
- [ ] `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/03_CONSTRUCTION_PLANS/` 已存在且含 `INDEX.md`（可与终稿并行）。  
- [ ] §0.2 范围内各篇路径与链接符合 LAYOUT（或篇内说明例外）。

**C. 文档卫生与工程习惯（与 §0 并行、强烈建议作为同一放行前提）**

- **IA / 金线 / 过程稿归位**：本交接 **§13.4～§13.5**（S1～S7）。  
- **内链门禁**：合并前 `python scripts/sentinel_l1_governance_scan.py`，目标 **Invalid links = 0**（与清洁总案、门禁 §2 精神一致）。  
- **架构缺口**：G4/G5 等宜在 `docs/09_AUDIT/STATE/ARCH_MODULE_GAP_REGISTER_20260408.md` 有记录或 P0 已闭（见 `ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md`）。

**D. 勿与第 3 阶段混淆**

`CONSTRUCTION_GATE` **§3 A～F**、双 YAML、收口核对项（EC）复跑等，主要面向 **写业务代码（第 3 阶段）**。**写施工文档（第 2 阶段）**的硬门槛在 **§0.1 + §0.1a**（外加团队约定的文档卫生）；**不必**等 §3 全勾完才开始第 2 阶段。

#### 13.6.2 蓝图阶段「最终交付」应呈现的样貌

对齐 §0 阶段表：第 1 阶段结束时应达到 **「盖哪栋楼、每层干什么、找哪份文档已说清，无大块空白」**。物化结果可按下表自检：

| 类别 | 交付物形态（读者可验证） |
|------|---------------------------|
| **总纲与分层** | `docs/01_FRAMEWORK/ARCHITECTURE.md`、`MODULE_RESPONSIBILITY_BOUNDARIES.md`、`BLUEPRINT_ARCHITECTURE_MAPPING.md` 可读、互链有效；能从总纲走到契约与蓝图入口。 |
| **契约真源** | `docs/03_TRADING_TACTICS/API_Contract.md` 为跨模块接口叙事入口；蓝图「接口」条款能指到此处（或登记的等价文档）。 |
| **实施蓝图体** | `01_BLUEPRINTS/` 内（除机器维护的 `INDEX.md`）每篇在 §0.2 范围内均满足 §0.1；`01_BLUEPRINTS/INDEX.md` 与磁盘一致（`scripts/generate_01_blueprints_index.py`）。 |
| **框架内蓝图** | `01_FRAMEWORK/` 下 `*BLUEPRINT*` 若属默认 §0.2 范围，标准同上。 |
| **扩展范围** | 若纳入其他路径，须在 §0.2 表或 §4 书面列出并按 §0.1 验收。 |
| **第 2 阶段落点** | `03_CONSTRUCTION_PLANS/INDEX.md` 已存在，作为下一阶段的索引入口（§0.1a）。 |
| **放置与命名** | 终稿蓝图路径、命名与 LAYOUT、PATH、FILE_NAMING 标准一致或有 documented 例外。 |

**一句话**：蓝图阶段结束 = **§0.2 范围内蓝图终稿化** + **总纲/边界/映射/契约形成可走通的权威阅读路径** + **施工文档目录与 INDEX 已就位**；过程稿仍可大量存在于 `STATE`/`REPORTS`，但**不得冒充**权威区现行真源（§13.4）。

---

## 14. 施工文档（「施工图纸」类交付）前的专业机构清洁名目（总清单）

> **语义对齐**：门禁 **§0** 中，**第 2 阶段**指施工流程 / 计划 / 方案等（施工文档）；口语里的「施工图纸」在此与其同属**进入编码（第 3 阶段）之前、蓝图终稿之后**的文档准备。  
> **真源**：`CONSTRUCTION_GATE_CRITERIA_20260408.md`（§0.1、§0.1a、§0.2）与 `BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md`（P0～P3、§5）。

下列名目按**专业机构常见的文档卫生分类**组织，并映射到本仓库路径或脚本（表格内路径均为仓库内相对描述，供检索）。

### 14.1 蓝图冻结类（Blueprint readiness / Content freeze）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **职责边界卫生** | 负责 / 不负责写清，避免职责漂移 | `CONSTRUCTION_GATE_CRITERIA_20260408.md` §0.1 条 1 |
| **接口与契约对齐** | 对外能力能指到统一契约真源 | §0.1 条 2 → `docs/03_TRADING_TACTICS/API_Contract.md` |
| **验收口径卫生** | 有可检查的完成定义 | §0.1 条 3 |
| **版本与状态卫生** | 非 Draft、`version ≥ 1.0.0` 等 | §0.1 条 4 |
| **占位符闭合** | TBD / 待补要么消掉，要么进「已知限制」并附计划或 §4 豁免 | §0.1 条 5 |

### 14.2 信息架构与可发现性（IA / Findability）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **导航与索引卫生** | 主干、P0 域有权威 `INDEX.md` 或等价入口 | 清洁总案 P0 目录；总案 §5「主干 INDEX」 |
| **严格孤儿收敛** | 高价值文档避免入度为 0 漂流 | `scripts/strict_orphan_inbound_scan.py`；基线与 `STRICT_ORPHAN_FILES_LIST_REGEN_*.txt` |
| **长列表分流** | 报告海不堆进单页 `INDEX.md` | `docs/09_AUDIT/REPORTS/INDEX_GROUPED_20260408.md`；`docs/09_AUDIT/STATE/INDEX_GROUPED_20260408.md` |

### 14.3 链接与引用完整性（Link integrity）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **内链门禁** | Markdown 相对链可解析、无断链 | `python scripts/sentinel_l1_governance_scan.py`，目标 Invalid links = 0 |
| **权威栈互达** | 架构、边界、映射与关键蓝图可往返 | `ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md` §六 Q3；本交接 §11.5 |

### 14.4 元数据与标识符（Metadata / Recordkeeping）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **首道 front matter 卫生** | `module_id` 等一致、可审计 | L1 报告；`CONSTRUCTION_GATE` §1「元数据风险」 |
| **双 YAML 清理** | 异常双 front matter 归零或登记豁免 | `python scripts/merge_double_yaml_frontmatter.py --list`；`docs/09_AUDIT/STATE/DOUBLE_YAML_EXCEPTIONS.md` |
| **`module_id` 去重** | 避免标识符冲突 | 门禁 §1；`scripts/dedupe_module_id_frontmatter.py`（若流程启用） |

### 14.5 权威源、重复与重叠（SSOT / Duplicates / Overlap）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **重复裁决卫生** | duplicates 池有 canonical、有处置状态 | `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`；`DUPLICATE_DOCUMENT_HANDLING_STANDARD.md` |
| **重叠声明卫生** | overlap 文稿带 canonical 指针或登记豁免 | `docs/06_ARCHIVE/overlap_*.md`；`OVERLAP_CANONICAL_POINTER_TEMPLATE.md`；并行 schedule |
| **架构「孤儿蓝图」** | 蓝图在总纲 / 映射语义上挂得住 | G4；`ARCH_MODULE_GAP_REGISTER_20260408.md` |

### 14.6 仓库形态与命名（Repository layout / Naming）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **文档放置卫生** | 类型进对树、例外有说明 | `DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md` |
| **命名与路径卫生** | 与 PATH / FILE_NAMING 一致 | `docs/05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md`；`docs/09_AUDIT/STANDARDS/FILE_NAMING_STANDARD.md` |
| **施工计划入口存在** | 第 2 阶段文档有挂载位置 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/03_CONSTRUCTION_PLANS/INDEX.md`；门禁 §0.1a |

### 14.7 治理与审计台账（Governance / Audit trail）

| 清洁名目 | 含义 | 本仓库落点 |
|----------|------|------------|
| **全库审计阶段对账** | 按既定阶段核对进度 | `FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md` 阶段 A～H（及文内扩展） |
| **补救 / 执行闭环** | 收口核对项（本仓库 EC 条目）与门禁 §2、§3 在放行前仍成立 | `OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`；`REMEDIATION_EXECUTION_CLOSURE_20260408.md`；§13 |
| **历史 STATE / REPORTS 姿态** | 过时材料可追溯、不误导为现行真源 | 本交接 §10 |

### 14.8 阶段边界（避免一锅煮）

- **进入第 2 阶段（写施工流程 / 计划 / 方案）**：以门禁 **§0.1 蓝图终稿** + **§0.1a 放置与 LAYOUT** 等为准；上表 **§14.1～14.7** 支撑「蓝图与文档体系已可审、可找、可链」。  
- **进入第 3 阶段（写业务代码）**：另有门禁 **§0.3、§3 A～F** 等（含 **收口核对项 EC 复跑**、双 YAML 等），**比「动笔写施工文档」更严一层**；勿把第 3 阶段清单提前当成「写施工文档前必须全勾」，除非 Owner 另有书面决定。

---

## 15. Git 备份与安全合并（长时作业强制）

> **目的**：8 小时内大量改文档时，**随时可回滚**、**历史可审计**，避免「改坏一整树无法恢复」。

### 15.1 开工前（Owner 或执行者第一条 Git 动作）

在仓库根执行（PowerShell 示例，路径按实际调整）：

```text
git status
git fetch
git checkout -b doc/hygiene-trae-YYYYMMDD
git add -A
git commit -m "chore(docs): baseline before Trae GLM hygiene marathon"
git tag -a doc-baseline-YYYYMMDD -m "文档清洁长跑前基线"
```

- **禁止**在未提交基线前开始大批量改文件。  
- 若使用 Trae 内置 git：**同样逻辑**——先有可识别基线提交或 tag。

### 15.2 长跑中途（建议每 45～90 分钟）

- **小步提交**：每完成「一批可独立验收的改动」（例如：一个域 `INDEX.md` + L1=0）即 `git commit`。  
- **提交信息**：`docs(<scope>): <动作>；L1=0`（或附脚本输出摘要文件名）。  
- **L1 失败**：**优先修复**；若无法快速修复，**`git revert` 该批或 `git restore` 相关文件**，勿在断链状态下继续堆改。

### 15.3 收工或阶段结束

- 再打 **annotated tag**：`doc-milestone-YYYYMMDD-HHMM`。  
- `git push` / `git push --tags` 按团队远程策略执行（无远程则保留本地 tag 亦可）。  
- **不要** `git push --force` 到共享默认分支。

---

## 16. 防 AI 幻觉与证据规则（执行者必读）

> **目标**：GLM / 任意模型在 8 小时内**不得靠记忆编造**路径、篇数、门禁状态。

| 规则 | 要求 |
|------|------|
| **路径存在性** | 任何「某文件在仓库中」的陈述，须以 **Glob / Read / `git ls-files`** 之一验证；**禁止**臆造 `docs/...` 路径。 |
| **数量与趋势** | 「严格孤儿还剩多少篇」等数字，**只引用** `python scripts/strict_orphan_inbound_scan.py` 生成的 `STRICT_ORPHAN_FILES_LIST_REGEN_*.txt` 行数或报告，**禁止**手估。 |
| **链接有效性** | 「全库无断链」须以 **`python scripts/sentinel_l1_governance_scan.py` 输出**为准（Invalid links = 0）。 |
| **重复与真源** | 多篇疑似重复时，**先打开** `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md` 与 `DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`；**禁止**未更新台账就删除「看起来像重复」的文件。 |
| **门禁状态** | 「已达蓝图终稿」须逐条对照 `docs/09_AUDIT/STATE/CONSTRUCTION_GATE_CRITERIA_20260408.md` **§0.1 / §0.2**；**禁止**用笼统「差不多了」代替勾选。 |
| **进度真源** | Trae 侧任务批次与完成摘要，须回写 **`docs/09_AUDIT/STATE/TRAE_BLUEPRINT_TASK_LEDGER_20260408.md`**（与台账 §6 约定一致），避免口头进度漂移。 |
| **不向 Owner 中途追问时的默认策略** | 遇歧义：**选保守**（少删、多挂链、多登记 gap）；**不猜** Owner 意图；**把假设写进** `ARCH_MODULE_GAP_REGISTER_20260408.md` 或台账「待 Owner 裁决」列。 |

---

## 17. Trae × GLM-5.1 连续 8 小时执行方案（对齐蓝图交付）

> **终点定义（8 小时）**：在**不向 Owner 追问**的前提下，尽量推进至：**L1 Invalid links = 0**、`REGEN` 孤儿相对基线**下降**、`CANONICAL_POINTERS` **无悬空 TBD**（或全部已指派）、**§0.2 范围内蓝图尽可能多**篇达到 **§0.1 五条**；**完全满足 §0.1 全量篇目可能超过 8 小时**，须按台账 **P0 优先**。收工时必须更新 **Trae 台账** 与 **Playbook §10**（见下表「收工」）。

### 17.1 开工第 0 小时（固定动作，约 30～45 分钟）

1. 执行 **§15.1** Git 基线。  
2. `python scripts/sentinel_l1_governance_scan.py` —— 存档或记录 Invalid 数。  
3. `python scripts/strict_orphan_inbound_scan.py` —— 得到当日 `STRICT_ORPHAN_FILES_LIST_REGEN_*.txt`。  
4. **只读**打开：`CONSTRUCTION_GATE_CRITERIA_20260408.md` §0.1～§0.2、`TRAE_BLUEPRINT_TASK_LEDGER_20260408.md`（当前批次表）。  
5. 在台账或本文件外**独立笔记**列出本 8h **P0 文件清单**（来自 Trae 台账批次，**不得臆造**）。

### 17.2 第 1～7 小时（循环批次）

每轮建议 **60～90 分钟**，每轮结构：

1. **改文**：按台账批次做 `01_BLUEPRINTS` 内 **§0.1 终稿化**（职责/契约指针/验收/status/TBD 闭合），或做 **INDEX 挂载** / **duplicates 台账一行** / **overlap 小批指针**（与总案「小 PR」精神一致，Trae 内即小 commit）。  
2. **门禁**：`sentinel_l1_governance_scan.py` → 若 Invalid ≠ 0，**本批止于修复**。  
3. **提交**：`git commit`（§15.2）。  
4. **每 2 轮**可选重跑 `strict_orphan_inbound_scan.py` 观察趋势。

**Trae 默认目录包**（与台账一致）：优先 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`；**勿**在未指派下改 `docs/01_FRAMEWORK/` 根下 `*BLUEPRINT*`（台账写明由 Cursor 侧时）。

### 17.3 第 7～8 小时（收工与冻结）

1. 再跑 **L1**、**strict orphan REGEN**。  
2. 对照 **§13.6** 自检表：已满足项打勾；未满足项写入 **gap 登记**或 Trae 台账「下一批」。  
3. 更新 `docs/09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md` **§10** 一行（日期、摘要、L1、REGEN 趋势）。  
4. 更新 `TRAE_BLUEPRINT_TASK_LEDGER_20260408.md` §6（或该台账规定的进度区）。  
5. **§15.3** tag + push（若适用）。

### 17.4 现实预期（避免幻觉式承诺）

- **8 小时无法保证**「§0.2 内每一篇蓝图 100% §0.1」——以台账 **P0 + L1 不回归** 为硬约束；余量列入下一马拉松或 Cursor 接力。  
- **第 2 阶段放行**的最终勾选权在 **Owner**；执行者交付的是 **可验证证据链**（L1 报告、REGEN、台账、git 历史）。

---

## 18. 重复文档与「Layer → 子模块 → 蓝图」快速导航

> **痛点**：重复副本多时，后续 AI/人类必须 **先找 canonical**，再沿 **Layer 与域索引**下到子模块蓝图，并在相关蓝图间跳转。

### 18.1 真源优先级（冲突时从高到低）

1. `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`（**重复池裁决**；未裁决前**不删**）。  
2. `docs/01_FRAMEWORK/ARCHITECTURE.md`（Layer 总纲）。  
3. `docs/01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md`（谁做什么）。  
4. `docs/01_FRAMEWORK/BLUEPRINT_ARCHITECTURE_MAPPING.md`（业务视角 ↔ Layer）。  
5. `docs/03_TRADING_TACTICS/API_Contract.md`（接口契约）。  
6. **实施蓝图全集列表**：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md`（**机器生成**，运行 `python scripts/generate_01_blueprints_index.py` 更新）。  
7. **能力 ↔ 蓝图对照**（若存在）：`docs/09_AUDIT/STATE/LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md`（以 `ARCHITECTURE.md` 引用为准；**若不存在则跳过，禁止编造**）。

### 18.2 「每一层级的子模块」怎么找（给未来 AI 的操作顺序）

1. 从 `ARCHITECTURE.md` 定位 **Layer 编号**与相关链接。  
2. 用 `MODULE_RESPONSIBILITY_BOUNDARIES.md` 查 **该层职责与模块名**。  
3. 在 `01_BLUEPRINTS/INDEX.md` **搜索**关键词或模块名，打开对应 `*_BLUEPRINT.md`。  
4. 若一篇蓝图 **front matter** 或正文有 `related_documents` / 「相关蓝图」小节，**优先**沿链跳转。  
5. 若同一主题出现多路径，**先查** `CANONICAL_POINTERS.md` 再读正文。

### 18.3 蓝图 ↔ 蓝图互链（建议增量、非一次全连）

- **不要求** N×N 全连接；**要求**「同一数据/执行链路上的邻接蓝图」在正文或 `related_documents` 中 **可点击**互指（与 §11.5、架构审计 Q3 一致）。  
- **新增**互链时每批改后跑 **L1**。  
- **overlap** 文稿按 `docs/06_ARCHIVE/OVERLAP_CANONICAL_POINTER_TEMPLATE.md` 标明 canonical，避免读者读到旧稿误以为现行。

### 18.4 8 小时内与本节相关的可交付增量

- [ ] `CANONICAL_POINTERS.md` 中 **P0 重复簇**至少 **N→0 个 TBD**（N 由台账规定，做不到则写明 Owner 指派与截止日）。  
- [ ] `01_BLUEPRINTS/INDEX.md` 与磁盘一致（脚本重生成并提交）。  
- [ ] 在 **P0 蓝图**篇内补齐 **指向契约**与 **1～3 条相关蓝图**链接（有则补，无则登记 G5）。

---

## 19. 变更记录（本交接文档）

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-04-08 | 初版：孤儿接力 |
| v1.0.1 | 2026-04-08 | 扩展路径；避免 L1 误判占位链接 |
| v1.1.0 | 2026-04-08 | 增加一并检查项、过时审计处理原则、清洁阶段剩余清单、施工门禁衔接 |
| v1.2.0 | 2026-04-08 | §11.5：模块与蓝图互链的「应检查」与「不要求全网双向 INDEX」口径（对齐架构审计 Q3 / G4 / MAPPING §4） |
| v1.3.0 | 2026-04-08 | §13 OpenClaw 成因说明；§14 施工文档前专业机构清洁名目全文；变更记录顺延为 §15 |
| v1.4.0 | 2026-04-08 | §13 改为行业通用术语（remediation / closure / gate）；§13.4 蓝图阶段「干净」边界与临时稿处理；§11.4、§14.7～14.8 用语对齐 |
| v1.5.0 | 2026-04-08 | §13.4 重写为「目标 + 边界 + 分层」全文入档；新增 §13.5 达成目标的步骤表 S1～S7 与验收直觉 |
| v1.6.0 | 2026-04-08 | 新增 §13.6：第 2 阶段前硬门槛（§0.1/§0.1a 等）与蓝图阶段最终交付物化自检表 |
| v2.0.0 | 2026-04-08 | 整册定稿：§0 目录；§15 Git；§16 防幻觉；§17 Trae×GLM-5.1 八小时方案；§18 重复与分层导航；变更记录改为 §19 |
