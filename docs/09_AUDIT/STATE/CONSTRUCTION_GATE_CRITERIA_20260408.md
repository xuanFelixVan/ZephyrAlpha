---
module_id: CONSTRUCTION_GATE_CRITERIA_20260408
version: 1.2.0
status: Active
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 仓库 Owner
standard_type: 审计台账
applicable_scope: 文档治理完成前禁止「按图施工」的验收门禁
compliance_level: 与裁决书、执行手册一致
parent_document: ../PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md
responsibility:
  - 汇总「先治理、后施工」的可验收条件
  - 与 OpenClaw EC、全系统审计批次、架构/模块方案对齐
  - Owner 确认的文档三阶段（蓝图 → 施工文档 → 代码施工）口径
---

# 施工门禁：先压文档与元数据风险，再进入实现

> **Owner 决策（2026-04-08）**：在本文 **§3 总清单** 全部勾选为完成（或经书面豁免并记入 §4）之前，**不启动第 3 阶段**（业务代码实现与大规模按图编码）。  
> **允许并行**：脚本化治理、L1 扫描、纯归档搬运、单文件小修，以及 **第 2 阶段**（施工流程/计划/方案类文档）的编写——但须在 **§0** 蓝图终稿达标之后启动。  
> **与 §0 的关系**：§0 定义「何时可写施工文档、何时可写代码」；§3 定义「写代码前还须满足的治理与审计总清单」。

---

## 0. 文档三阶段模型（Owner 已确认）

用盖楼打比方，把整个交付拆成 **三个阶段**；**施工**在本文里特指 **第 3 阶段（写代码、联调、跑通）**，避免与「施工文档」混淆。

| 阶段 | 名称 | 做什么 | 结束时应达到的感觉 |
|------|------|--------|-------------------|
| **第 1 阶段** | **蓝图** | 系统分层、模块职责、能力 ↔ 文档挂载、接口边界可查（`ARCHITECTURE`、`MODULE_RESPONSIBILITY_BOUNDARIES`、各域 `*_BLUEPRINT.md` 等） | 「盖哪栋楼、每层干什么、找哪份文档」已说清，**无大块空白** |
| **第 2 阶段** | **施工文档**（施工图纸 / 施工流程 / 施工计划 / 施工方案） | 按模块或里程碑拆解：**先后顺序、每步交付物、验收、风险、与 API/数据级的细化说明**；**默认目录**见 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) **§4**，索引入口 [`03_CONSTRUCTION_PLANS/INDEX.md`](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/03_CONSTRUCTION_PLANS/INDEX.md) | 「工人进场前，工序单和细化说明有了」 |
| **第 3 阶段** | **施工（实现）** | 按第 2 阶段文档 **编写与修改业务代码**、测试、部署或自用跑通 | 「真的在盖」 |

### 0.1 「蓝图终稿」标准（进入第 2 阶段的条件）

Owner 要求：**全库蓝图终稿后**，才进入第 2 阶段（编写施工流程/计划/方案等）。**「终稿」**指在 **§0.2 划定范围内** 的每一篇蓝图同时满足：

1. **职责**：负责什么 / 不负责什么 已写清。  
2. **接口**：与邻层、邻模块的约定可指到 **`API_Contract.md`**（或等价契约文档）。  
3. **验收**：至少有一句 **可检查** 的完成标准（何人何时如何判定本篇落地完成）。  
4. **状态**：front matter 中 **`status` 不得为 `Draft`**（建议 **`Active`** 或 Owner 规定的终态词）；**`version ≥ 1.0.0`**（全库统一版本规则）。  
5. **闭合**：篇首或显著位置 **不得** 再保留未解释的「Draft / 待补 / TBD 占位」；若确有已知限制，须归入 **「已知限制」** 并附 **补全计划或 §4 豁免**。

**进入第 2 阶段的放行**：上述条件在 §0.2 范围内 **全部满足** 后，可开始编写 **第 2 阶段** 成套施工文档（流程、计划、方案）。

### 0.1a 蓝图阶段：文档放置与目录标准（Owner 关切）

**方向是对的**：专业机构也会先定 **「文档地图 + 放置规则」**，再大规模写作；个人项目同样受益，否则文件会散到 AI 也难找。

**建议把握两点**（避免「把未来每一种文件名都预写死」这种做不到的事）：

1. **定「哪类进哪棵树」**：一级目录职责、实施子目录、`src` 与 `docs` 分工 —— 以 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) 为 **现行真源**；命名与路径格式另见 [`PATH_STANDARD.md`](../../05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md)、[`FILE_NAMING_STANDARD.md`](../STANDARDS/FILE_NAMING_STANDARD.md)。  
2. **新类型走变更**：以后出现新文档类型，**先**在 `LAYOUT` 标准 §6 或 `TECH_DECISION_RECORDS` **加一条**，再建新文件夹 —— 这样算「提前定规矩」，而不是开工后乱长。

**蓝图阶段完成项（与放置相关）**：

- [ ] **`DOCUMENT_REPOSITORY_LAYOUT_STANDARD`** 已阅读并确认无与 Owner 意图冲突（冲突则改标准或登记豁免）。  
- [ ] **`03_CONSTRUCTION_PLANS/`** 已存在且含 **`INDEX.md`**（可与蓝图终稿并行创建，见该目录当前文件）。  
- [ ] 蓝图终稿范围内各篇 **路径与链接** 符合 LAYOUT 表（或已在篇内说明例外理由）。

### 0.2 「全库蓝图」范围（须书面划定，可扩展）

**默认包含**（若 Owner 未另写范围，则 AI 以此为准）：

- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` 下除 **`INDEX.md`** 外的全部 `*.md`；  
- **`docs/01_FRAMEWORK/`** 下文件名含 **`BLUEPRINT`** 的 `*.md`。

**可选扩展**（若纳入，须在下方表格或 §4 逐条列出）：

- 例如 `docs/11_STRATEGIC_DECISION/` 下指定文件、`docs/module_designs/` 等。

| 路径或通配 | 是否纳入「全库蓝图」 |
|------------|----------------------|
| `01_BLUEPRINTS/*.md`（除 INDEX） | 是（默认） |
| `01_FRAMEWORK/*BLUEPRINT*.md` | 是（默认） |
| （Owner 增补） | |

### 0.3 第 2 阶段结束标准（进入第 3 阶段的条件）

在 **第 1 阶段已放行** 的前提下，**第 2 阶段**至少交付（可合并为多篇文档，但须有一篇 **索引入口**）：

1. **施工流程**：从需求/蓝图到编码、测试、合并的主路径与回滚/暂停条件。  
2. **施工计划**：里程碑、先后依赖、建议人力或 AI 轮次（个人项目可写「由 Owner + AI 执行」）。  
3. **施工方案**：与本轮实现范围对应的 **技术选型锁定、目录约定、配置与密钥管理原则、验收与联调顺序**。  
4. **与契约对齐**：第 3 阶段将改动的接口，已在 **`API_Contract.md`** 与 **`TECH_DECISION_RECORDS.md`** 中可追溯。

**进入第 3 阶段（写代码）**：除满足 **§0.3** 外，还须满足本文 **§3 A～F**（或 §4 豁免）及 **§2** 复跑 L1 / 双 YAML 结果。

---

## 1. 用语与仓库真源对照

| 你的说法 | 仓库内对应真源 / 动作 |
|----------|------------------------|
| **元数据风险** | OpenClaw 执行手册 **EC-1～EC-6**；`sentinel_l1_governance_scan.py`；双 YAML（`merge_double_yaml_frontmatter.py`）；首道 FM `module_id`（`dedupe_module_id_frontmatter.py`） |
| **架构 / 模块审核** | [`ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md`](../PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md) + [`ARCH_MODULE_GAP_REGISTER_20260408.md`](./ARCH_MODULE_GAP_REGISTER_20260408.md)；**扩展**：方案第二节未勾选的 **`01_BLUEPRINTS` 全量对账**、`docs/module_designs/` 与切片绑定后的一轮对照 |
| **审计（全库）** | [`FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md`](../PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md) 阶段 **A～H**（及方案所载阶段 I 若适用）+ 建议进度文件 [`§四` 进度 JSON 约定](../PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md) |
| **技术审批** | [`TECH_DECISION_RECORDS.md`](../../01_FRAMEWORK/TECH_DECISION_RECORDS.md)；施工前对 **`API_Contract`** 及跨模块接口的变更做 **TDR/ADR 登记**（最小：一条记录链到契约路径） |
| **架构瘦身** | 裁决书 **ADR-OC-005**（重复/多版本正文：canonical + 归档 + 内链）；`06_ARCHIVE` 根散落归类、**`09_AUDIT/REPORTS/` 版本链收敛**（与 Backlog P1-9 一致） |
| **文件治理** | OpenClaw **P1-C 余项**（见 [`P1C_DEFERRED_20260408.md`](./P1C_DEFERRED_20260408.md)）、`review_materials_package` 路径与豁免（P1-8）、双目录 INDEX 类问题 |

---

## 2. 基线：OpenClaw 正式闭环（若已满足则只存档、不重复劳动）

执行收口报告：[`REMEDIATION_EXECUTION_CLOSURE_20260408.md`](../REPORTS/REMEDIATION_EXECUTION_CLOSURE_20260408.md) 声称 **EC-1～EC-7** 已满足。  
**放行施工前**请在当前分支 **复跑** 并保存一次：

```text
python scripts/sentinel_l1_governance_scan.py
python scripts/merge_double_yaml_frontmatter.py --list
```

将最新 L1 输出覆盖或并存为 `docs/09_AUDIT/STATE/SENTINEL_L1_PRE_CONSTRUCTION_YYYYMMDD.md`（及 `.json`）；若 **`判定无效 ≠ 0`** 或 **双 YAML 列表非 0**，**不得**勾选 §3-A。

---

## 3. 第 3 阶段（代码施工）前总清单（建议按块顺序执行）

### A. 机械与链接门禁（P0）

- [ ] **A1** 当前仓库 L1：**Markdown 内链判定无效 = 0**（报告已存档）。  
- [ ] **A2** 双 YAML：**`merge_double_yaml_frontmatter.py --list` → 0**，或仅剩 [`DOUBLE_YAML_EXCEPTIONS.md`](./DOUBLE_YAML_EXCEPTIONS.md) 登记豁免。  
- [ ] **A3** 首道 FM **重复 `module_id` 组 = 0**（与 L1 / `dedupe_module_id_frontmatter.py` 口径一致）。  
- [ ] **A4** `audit_state` 仅 **`04_OPERATIONS/audit_state`** 为权威工作区；`07_.../audit_state` 仅为跳转说明（ADR-OC-002）。

### B. 架构 / 模块（语义 + 挂载）

- [ ] **B1** [`ARCH_MODULE_GAP_REGISTER_20260408.md`](./ARCH_MODULE_GAP_REGISTER_20260408.md) 内登记项均为 **已修正** 或已 **defer** 并注明理由。  
- [ ] **B2** **Layer 11**：[`LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md`](./LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md) 与 `ARCHITECTURE.md` Layer 11 表一致且无 TBD（当前 v1.2 为基线，若改架构需同步改表）。  
- [ ] **B3** **`01_BLUEPRINTS` 全量对账**：`generate_01_blueprints_index.py` 产物与目录一致，且与 `BLUEPRINT_ARCHITECTURE_MAPPING.md` **无未解释的孤儿挂载**（脚本或抽检报告路径写入 `audit_state` 或 `STATE`）。  
- [ ] **B4** **`docs/module_designs/`**：已与选定垂直切片绑定并完成 **阶段 1 对照审**（仅目录勾选后执行；未绑定则本项记「N/A」须 Owner 签字于 §4）。

### C. 全系统文档审计（分批深度）

按 [`FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md`](../PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md) **阶段 A～H** 执行；每批至少保留：**进度记录 + 本批结论摘要**（可放在 `audit_state` 或 `09_AUDIT/STATE`）。

- [ ] **C1** 阶段 **A**（入口与架构真源 A1–A4）  
- [ ] **C2** 阶段 **B**（实施与施工 B1–B6）  
- [ ] **C3** 阶段 **C**（审计体系 C1–C4）  
- [ ] **C4** 阶段 **D**（因子库与数据）  
- [ ] **C5** 阶段 **E**（执行、战术、战略、研究）  
- [ ] **C6** 阶段 **F**（人机、AI 工作流、合规）  
- [ ] **C7** 阶段 **G**（归档与历史）  
- [ ] **C8** 阶段 **H**（其余 docs 与仓库外 md）  
- [ ] **C9**（可选）阶段 **I**（Git 误删与备份价值审计，依赖方案前置 tag）

### D. 架构瘦身与文件治理（与 ADR-OC-005 / Backlog 对齐）

- [ ] **D1** `docs/06_ARCHIVE/` **根散落**约 236 篇：已 **分主题子目录** 或已登记分期计划与完成日期（P1-5）。  
- [ ] **D2** `docs/09_ARCHIVE/duplicates` 与 `06_ARCHIVE`：**交叉引用或合并策略**已写清并落实索引（P1-6）。  
- [ ] **D3** `docs/09_AUDIT/REPORTS/`：**版本链收敛**（保留现行入口 + 归档旧版，P1-9）。  
- [ ] **D4** **P1-7**：缺失 `module_id` 的文档已 **逐批补全** 或已登记「非标准文档」豁免集合。  
- [ ] **D5** **P1-8**：`review_materials_package` 内链与 **不参与内链检查** 的说明已落地。  
- [ ] **D6** **P1-3 残余**：全库检索旧 Layer8 / 旧文件名链接，历史报告内 **按需修正或标注「历史引用」**。

### E. 技术审批（施工前最小集）

- [ ] **E1** 拟施工涉及的 **公共接口 / 数据契约** 已在 [`API_Contract.md`](../../03_TRADING_TACTICS/API_Contract.md) 或子契约中有条目，且 [`TECH_DECISION_RECORDS.md`](../../01_FRAMEWORK/TECH_DECISION_RECORDS.md) 中有对应 **TDR/ADR** 或明确「沿用既有决策」的引用。  
- [ ] **E2** **pre-commit**：按 ADR-OC-004，已安排 **修钩子或收窄规则** 的跟踪项（不要求整改期内一次解决，但施工前须有结论或豁免）。

### F. P2 与「全部完成」的边界

- [ ] **F1** **P2（Backlog）**：已 **执行完毕** 或 Owner 在 §4 声明 **「P2 不阻塞施工」** 并注明复审频率（如每季度）。

---

## 4. 豁免与签字

仅当某项对当前阶段 **客观不可做** 时，允许豁免：**一项一段**，写明理由、替代措施、复审日期；由 Owner 在 Git 或本文件变更记录中留痕。

| 项编号 | 豁免理由 | 替代措施 | 复审日期 | Owner |
|--------|----------|----------|----------|-------|
| （示例）B4 未绑定 module_designs | 切片未定 | 仅框架目录只读清单 | YYYY-MM-DD | |

---

## 5. 放行声明模板（粘贴到 commit 或 REPORT）

**进入第 2 阶段（可开始编写施工流程/计划/方案）**

```text
CONSTRUCTION GATE 20260408 — 第 1 阶段（蓝图）终稿：§0.1 + §0.2 范围内已全部满足。
可启动第 2 阶段：施工流程 / 施工计划 / 施工方案文档。
```

**进入第 3 阶段（可开始业务代码实现）**

```text
CONSTRUCTION GATE 20260408 — 第 2 阶段（施工文档）已交付 §0.3；§3 A～F 已满足（豁免见 §4）。
L1 报告：docs/09_AUDIT/STATE/SENTINEL_L1_PRE_CONSTRUCTION_YYYYMMDD.md
可启动第 3 阶段：垂直切片实现 / 按图编码。
```

---

## 6. 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-08 | 初始：Owner「先治理后施工」决策与总清单 |
| 1.1.0 | 2026-04-08 | 新增 §0：蓝图 → 施工文档 → 代码施工三阶段；蓝图终稿与全库范围；两档放行声明 |
| 1.2.0 | 2026-04-08 | §0.1a 蓝图阶段目录标准；链到 `DOCUMENT_REPOSITORY_LAYOUT_STANDARD`；第 2 阶段默认 `03_CONSTRUCTION_PLANS/` |
