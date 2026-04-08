---
module_id: CONSTRUCTION_GATE_CRITERIA_20260408
version: 1.0.0
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
---

# 施工门禁：先压文档与元数据风险，再进入实现

> **Owner 决策（2026-04-08）**：在本文 **§3 总清单** 全部勾选为完成（或经书面豁免并记入 §4）之前，**不启动**业务侧的垂直切片实现与大规模「按图施工」扩写。  
> **允许并行**：脚本化治理、L1 扫描、纯归档搬运、单文件小修，只要不冒充「已放行施工」。

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

## 3. 施工前总清单（建议按块顺序执行）

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

## 5. 放行声明模板（全部勾选后粘贴到 commit 或 REPORT）

```text
CONSTRUCTION GATE 20260408：§3 A～F 已满足（豁免见 CONSTRUCTION_GATE_CRITERIA_20260408 §4）。
L1 报告：docs/09_AUDIT/STATE/SENTINEL_L1_PRE_CONSTRUCTION_YYYYMMDD.md
可启动垂直切片实现 / 按图施工。
```

---

## 6. 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-08 | 初始：Owner「先治理后施工」决策与总清单 |
