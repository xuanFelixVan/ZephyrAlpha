---
module_id: TRAE_BLUEPRINT_TASK_LEDGER_20260408
version: 1.1.0
status: Active
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 仓库 Owner
standard_type: 审计台账
applicable_scope: Trae（GLM）与 Cursor 分工、蓝图阶段批次与交接
parent_document: ./CONSTRUCTION_GATE_CRITERIA_20260408.md
responsibility:
  - 记录 Trae 每批任务、状态与交付摘要
  - 供 Cursor 新会话恢复上下文，避免遗忘布置内容
related_documents:
  - ./CONSTRUCTION_GATE_CRITERIA_20260408.md
  - ../STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md
---

# Trae × Cursor 蓝图阶段任务台账

> **用途**：Owner 在 **Trae** 与 **Cursor** 两边并行推进蓝图终稿时，**以本文件为唯一进度真源**；新开的 Cursor 对话只要读本文件 + `CONSTRUCTION_GATE`，即可接续安排 Trae、核对交付。  
> **谁维护**：**Cursor** 在每批派发/验收后更新「批次进度表」与「Cursor 占用清单」；**Owner** 可把 Trae 返回的摘要粘贴进 §6。

---

## 1. 分工总览（长期有效）

| 执行方 | 目录包（任务包） | 负责 | 不负责 |
|--------|------------------|------|--------|
| **Trae** | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` 按批次 | 该目录内所列文件的蓝图终稿化（§2） | `docs/01_FRAMEWORK/`；`scripts/`；门禁/标准真源；台账本文 |
| **Cursor** | `docs/01_FRAMEWORK/` 根目录下 `*BLUEPRINT*.md` 按字母序分批（每批 ≤8，见 §3 Cursor） | 框架层蓝图终稿化（同五条）；台账；L1；分支合并建议 | `01_BLUEPRINTS/` 内 Trae 批次正文（除非 Owner 指派） |

**两边共同遵守**：`CONSTRUCTION_GATE_CRITERIA_20260408.md` §0.1、`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`、`docs/03_TRADING_TACTICS/API_Contract.md`。

---

## 2. 可复制给 Trae 的完整任务说明（已填好占位）

**以下整块可复制到 Trae 对话开头（每新开一批时，把 §3 中「本批文件列表」同步贴到文首或文末）。**

```text
【项目】ZephyrAlpha 文档仓库 — 蓝图阶段（第 1 阶段）Trae 执行包

【仓库根】D:\ZephyrAlpha（所有路径相对仓库根）

【你的角色】Trae + GLM-5.1：蓝图正文终稿化；不改 Python；不改编排好的门禁/标准真源文件。

【必须先读】
1. docs/09_AUDIT/STATE/CONSTRUCTION_GATE_CRITERIA_20260408.md — §0.1 蓝图终稿五条、§0.2 全库蓝图范围。
2. docs/09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md
3. docs/03_TRADING_TACTICS/API_Contract.md
4. docs/01_FRAMEWORK/TECH_DECISION_RECORDS.md

【本批允许修改的文件】
仅允许修改下方「批次进度表」中 **Trae 当前批次** 列出的路径；未列出的文件一律不要打开、不要保存。

【禁止修改】
- scripts/ 下任何文件
- docs/09_AUDIT/STATE/CONSTRUCTION_GATE_CRITERIA_20260408.md
- docs/09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md（除非 Owner 书面授权改 §6）
- docs/09_AUDIT/STATE/TRAE_BLUEPRINT_TASK_LEDGER_20260408.md（由 Cursor 维护）
- docs/01_FRAMEWORK/ 下任何文件（Cursor 目录包，除非 Owner 书面授权）
- 「Cursor 占用清单」§5 中列出的路径

【每篇须满足（CONSTRUCTION_GATE §0.1）】
1. 职责边界：负责什么 / 不负责什么。
2. 接口：可点击链到 API_Contract 或已存在子契约。
3. 验收：至少一句可检查标准。
4. YAML：status 不得为 Draft；建议 Active；version ≥ 1.0.0。
5. 无悬空 Draft/待补/TBD；若有，归入「已知限制」+ 补全计划或注明需 Owner 豁免。

【语言】正文中文；标识符、文件名、API 名保持英文。

【本批结束前】在仓库根执行：python scripts/sentinel_l1_governance_scan.py
若你改动的文件导致无效内链，修到 0 再交付。

【交付格式】
1. 修改文件路径列表
2. 每文件 3 行：改了什么；status/version；接口链接位置
3. Git：建议分支 docs/blueprint-trae-batch-序号；commit 示例 docs(blueprint): 批次X 终稿化（Trae）
```

---

## 3. 批次进度表

### 3.1 Trae（`01_BLUEPRINTS`）

**策略**：先清空 YAML 为 `status: Draft` 的四篇（批次 T1）；其后按 `01_BLUEPRINTS/INDEX.md` 顺序每批 ≤8 篇。

| 批次 | 文件（仓库相对路径） | 执行方 | 状态 | 交付日期 | L1 无效链 | 备注 |
|------|----------------------|--------|------|----------|-----------|------|
| T1 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BENCHMARK_MANAGEMENT_BLUEPRINT.md` | Trae | 待开始 | | | Draft→终稿 |
| T1 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ESG_INVESTMENT_SYSTEM_BLUEPRINT.md` | Trae | 待开始 | | | Draft→终稿 |
| T1 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/IPS_MANAGEMENT_SYSTEM_BLUEPRINT.md` | Trae | 待开始 | | | Draft→终稿 |
| T1 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MACRO_FACTOR_SYSTEM_BLUEPRINT.md` | Trae | 待开始 | | | Draft→终稿 |
| T2+ | （派发前按 INDEX 填入下一组 ≤8 篇） | Trae | 未派发 | | | |

### 3.2 Cursor（`docs/01_FRAMEWORK/` 根目录 `*BLUEPRINT*.md`，字母序）

**策略**：每批最多 **8** 个文件；子目录（如 `LAYER4_ML/`）单独开批次号 **C-L4-***，避免与根目录混批。

| 批次 | 文件（仓库相对路径） | 执行方 | 状态 | 交付日期 | L1 无效链 | 备注 |
|------|----------------------|--------|------|----------|-----------|------|
| C1 | `docs/01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | YAML 修复 + §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/ACTIVE_LEARNING_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/ADVERSARIAL_ROBUSTNESS_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/AI_AGENT_FRAMEWORK_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/AI_CAPABILITY_GAP_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/AI_CONVERSATIONAL_INTERFACE_ENHANCEMENT_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C1 | `docs/01_FRAMEWORK/AI_DECISION_AUDIT_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_EVOLUTION_LOOP_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_GOVERNANCE_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_MEMORY_ADDITIONAL_BLUEPRINTS.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_MEMORY_FINAL_SUPPLEMENT_BLUEPRINTS.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_MEMORY_MODULES_BLUEPRINT_COLLECTION.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_REPORT_GENERATION_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C2 | `docs/01_FRAMEWORK/AI_STRATEGY_AUTOMATION_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/AI_TRUST_CALIBRATION_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALERT_MANAGEMENT_INTERFACE_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALGORITHM_DEPLOYMENT_CONTROL_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALGORITHM_INVENTORY_MANAGEMENT_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALGORITHM_PERFORMANCE_BENCHMARK_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALGORITHMIC_TRADING_COMPLIANCE_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALGORITHMIC_TRADING_TEST_FRAMEWORK_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C3 | `docs/01_FRAMEWORK/ALPHA_FACTOR_LAYER_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C4 | `docs/01_FRAMEWORK/API_MANAGEMENT_INTERFACE_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C4 | `docs/01_FRAMEWORK/ARBITRAGE_DETECTION_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C4 | `docs/01_FRAMEWORK/AUDIT_LOG_VIEWER_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |
| C4 | `docs/01_FRAMEWORK/AUDIT_TRAIL_SYSTEM_BLUEPRINT.md` | Cursor | 已完成 | 2026-04-08 | 0 | §0.1 合规段 |

**Git 建议**：Cursor 使用分支 `docs/blueprint-cursor`；Trae 使用 `docs/blueprint-trae-batch-N`。

---

## 4. 批次规则摘要

- **Trae** 与 **Cursor** **并行**：不得同时修改对方目录包内的文件。  
- **每批最多 8 个文件**（单会话可控）。  
- **Trae T1** 固定为 `01_BLUEPRINTS` 四篇 Draft。  
- **Trae T2+**：`python scripts/generate_01_blueprints_index.py` 刷新索引后按 `INDEX.md` 顺序取下一组。  
- **Cursor C***：`docs/01_FRAMEWORK/` **根目录** `*BLUEPRINT*.md` 按文件名排序分批；子目录另开 **C-L4-***。

---

## 5. Cursor 占用清单（避免与 Trae 撞文件）

> Trae **禁止**改下列路径（除非 Owner 书面收回 Cursor 批次）。

- `docs/01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ACTIVE_LEARNING_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ADVERSARIAL_ROBUSTNESS_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_AGENT_FRAMEWORK_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_CAPABILITY_GAP_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_CONVERSATIONAL_INTERFACE_ENHANCEMENT_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_DECISION_AUDIT_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_EVOLUTION_LOOP_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_GOVERNANCE_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_MEMORY_ADDITIONAL_BLUEPRINTS.md`
- `docs/01_FRAMEWORK/AI_MEMORY_FINAL_SUPPLEMENT_BLUEPRINTS.md`
- `docs/01_FRAMEWORK/AI_MEMORY_MODULES_BLUEPRINT_COLLECTION.md`
- `docs/01_FRAMEWORK/AI_REPORT_GENERATION_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_STRATEGY_AUTOMATION_BLUEPRINT.md`
- `docs/01_FRAMEWORK/AI_TRUST_CALIBRATION_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALERT_MANAGEMENT_INTERFACE_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALGORITHM_DEPLOYMENT_CONTROL_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALGORITHM_INVENTORY_MANAGEMENT_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALGORITHM_PERFORMANCE_BENCHMARK_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALGORITHMIC_TRADING_COMPLIANCE_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALGORITHMIC_TRADING_TEST_FRAMEWORK_BLUEPRINT.md`
- `docs/01_FRAMEWORK/ALPHA_FACTOR_LAYER_BLUEPRINT.md`

---

## 6. Trae 交付粘贴区（Owner 可把 Trae 回复摘要贴在此节下方）

### 模板

```
日期：
批次号：
Trae 修改文件列表：
L1 结果（无效链）：
待 Cursor 跟进：
```

### 历史记录

（每次粘贴后 Cursor 将要点同步到 §3「状态/备注」行）

---

## 7. 变更记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-08 | 初版：分工、已填充 Trae 说明、批次 1 四文件、批次规则、交接区 |
| 1.1.0 | 2026-04-08 | 并行分工；Trae/Cursor 分表；Cursor C1 八文件；占用清单 |
