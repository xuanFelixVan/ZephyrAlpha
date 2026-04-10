---
module_id: DOC_REMEDIATION_TASK_DIRECTIVE_20260408
---

# ZephyrAlpha 文档整改 — 详细任务指令（可复制给执行者 / AI）

> **仓库根**: `D:\ZephyrAlpha`（执行时 `cd` 到该目录）  
> **角色分工**: 执行者（你或 AI）改文件与跑脚本；**你**负责 Git 分支、合并、对 dry-run 点头。  
> **权威规则**: 任何与下述文件冲突的操作 **一律停止并先改裁决书**，不得在正文中自创规则。  
> **日期**: 2026-04-08

---

## 一、必须遵守的权威输入（执行前通读）

按顺序打开并作为**硬约束**：

1. `docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md` — **全部 ADR（双 YAML、audit_state、module_id、pre-commit、重复正文）**  
2. `docs/09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md` — **阶段顺序、Exit Criteria（EC-1～EC-7）**  
3. `docs/09_AUDIT/REPORTS/OPENCLAW_REMEDIATION_BACKLOG.md` — **P0/P1 任务行**  
4. `docs/09_AUDIT/REPORTS/OPENCLAW_AUDIT_SUMMARY_20260408.md` — **基线数字与 P0 清单**  
5. （可选）`docs/09_AUDIT/REPORTS/OPENCLAW_L3_CONFLICTS.md`、`docs/09_AUDIT/STATE/` 下 `module_id_duplicates_detail*.md` — **去重依据**

---

## 二、全局禁止事项

- 不要跳过 **P0-B 双 YAML** 的 **50 文件 dry-run** 未经人工（或你本人）确认就全库写回。  
- 不要在一次巨大 commit 里混合：**双 YAML 合并** + **大规模目录搬迁** + **audit_state 合并**；按阶段拆分。  
- 不要长期无记录使用 `git commit --no-verify`；若必须，按 **ADR-OC-004** 写入 `docs/09_AUDIT/STATE/PRECOMMIT_FAILURE_LOG_20260408.md`。  
- 不要删除「看起来像重复」的正文文档而不检查：内链、Git 历史、**ADR-OC-005**。

---

## 三、开始前（一次性）

1. `cd D:\ZephyrAlpha`  
2. `git checkout -b docs/remediation-openclaw-20260408`（分支名可自定，须独立分支）  
3. 保存当前基线 L1（复制输出即可）：  
   ```text
   python scripts/sentinel_l1_governance_scan.py
   ```  
   将生成的 `docs/09_AUDIT/STATE/` 下最新 `SENTINEL_L1_SCAN_*.md` 与 `.json` 复制一份，命名为带 `BASELINE_PRE_REMEDIATION` 后缀的文件，便于对比 EC-6。  
4. （可选）复制 `docs/09_AUDIT/STATE/OPENCLAW_INVENTORY_AUDIT_LEDGER.csv` 为带 `BASELINE` 后缀的备份。

---

## 四、阶段 P0-A（顺序第 1，完成 EC-1 + EC-2）

### 4.1 根目录 `temp_*.md`

1. 在仓库根列出所有 `temp_*.md`（与 `OPENCLAW_AUDIT_SUMMARY` 中 P0 列表对照）。  
2. 对每个文件：  
   - 尝试识别 **mojibake**（UTF-8/GBK 误读）；能可靠转码则转码为 **UTF-8** 后阅读。  
   - 若正文与某正式 `docs/` 下文档**完全重复或已被替代**：删除根目录文件 **或** 移入 `docs/06_ARCHIVE/temp_pending/` 并在该目录 README 中记一行来源。  
   - 若有**独有信息**：修复编码后移入合适 `docs/` 路径或 `temp_pending`，**不要**长期留在仓库根。  
3. **完成**：仓库根无「不可读」的 `temp_*.md`；满足 **EC-1**。

### 4.2 蓝图双重路径链接

1. 目录：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`  
2. 按 `OPENCLAW_REMEDIATION_BACKLOG.md` **P0-5**：修正 Markdown 内链中 **多拼的 `docs/` 前缀**（双重路径），使链接在 L1 规则下可达。  
3. **完成**：该目录相关无效链为 0 或 Backlog 约定状态；满足 **EC-2**。

### 4.3 `[模块ID]` 占位符

1. 按 Backlog **P0-3** 与 OpenClaw 明细，将仍含字面量 `[模块ID]` 的 YAML/正文替换为**真实** `module_id`（与 canonical 文档一致）。  
2. **完成**：清单清零（以 L1 或手工 grep 为准）。

### 4.4 P0-A 质量门（本阶段结束必做）

1. `python scripts/sentinel_l1_governance_scan.py`  
2. 将输出复制/保存为：`docs/09_AUDIT/STATE/SENTINEL_L1_AFTER_P0A_20260408.md`（及对应 json 若有）  
3. 随机打开 **3～5** 个被改文件，确认 front matter 与正文未错位。  
4. `git add` / `git commit -m "docs(remediation): P0-A temp/blueprint links/module placeholder"`  
5. （推荐）`git tag remediation-p0a-complete`

---

## 五、阶段 P0-B（顺序第 2，完成 EC-3）

### 5.1 规则源

- **必须**严格实现 `GOVERNANCE_DECISIONS_LOCKED_20260408.md` 中的 **ADR-OC-001**（第二 YAML 块为主、第一块仅补缺键、正文不动等）。

### 5.2 Dry-run（未经确认禁止全库写回）

1. 从全库中选出 **50** 个已确认含「双 YAML 头」的 `.md` 文件（可与 OpenClaw 台账或自写检测脚本一致）。  
2. 对这批文件**仅生成** unified diff，输出到目录：  
   `docs/09_AUDIT/STATE/double_yaml_dryrun_<YYYYMMDD>/`（每批自建；**勿**与归档样本混放）  
   （每文件一个 `.diff` 或单一汇总 diff，由执行者选定，但必须可人工审阅。）  
   **历史样本（50 个 .diff）**见 [`docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample/`](../../06_ARCHIVE/20260408_double_yaml_dryrun_sample/README.md)。  
3. **你（人类）**审阅 diff：确认无「正文被吃进 YAML」、无「丢失 module_id」。  
4. 通过后，再按目录分批，每批 **100～200** 个文件应用相同算法写回仓库。

### 5.3 豁免

- 若个别文件经人工确认**必须**保留双头，写入 `docs/09_AUDIT/STATE/DOUBLE_YAML_EXCEPTIONS.md`（路径 + 理由）。无此文件则 **EC-3** 要求零双头。

### 5.4 P0-B 质量门

- 同 §4.4，报告命名为 `SENTINEL_L1_AFTER_P0B_20260408.md`，commit 信息标明 `P0-B double-yaml`，tag `remediation-p0b-complete`（推荐）。

---

## 六、阶段 P1-A（顺序第 3，完成 EC-4）

1. 使用 `OPENCLAW_L3_CONFLICTS.md` 与 `docs/09_AUDIT/STATE/` 下 **module_id_duplicates_detail**（或 L1 报告中的重复段）作为清单。  
2. 对每一组重复：选 **一篇 canonical**，其余按 **ADR-OC-003** 改 `module_id`（`_ARCHIVED` 或 `_YYYYMMDD` 后缀二选一，**同一批统一**），并加互链或篇首说明。  
3. 若存在 `docs/09_AUDIT/STATE/MODULE_ID_REGISTRY.md`（或项目规定的注册表），**每批同步更新**。  
4. 处理 **缺 module_id** 的文档（Backlog P1-7）：补最小 YAML 或标注非标准类型（与 Backlog 一致）。  
5. 质量门：L1 报告存为 `SENTINEL_L1_AFTER_P1A_20260408.md`，commit `P1-A module_id dedup`，tag `remediation-p1a-complete`（推荐）。

---

## 七、阶段 P1-B（顺序第 4，完成 EC-5）

1. **唯一权威目录**：`docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state`（**ADR-OC-002**）。  
2. 将 `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/` 下文件**迁入**权威目录：  
   - 文件名冲突时：比对日期与内容，保留较新或较完整者，另一份改名归档或合并说明。  
3. 全库搜索指向 `07_OPERATIONS/audit_state` 的链接，改为 `04_OPERATIONS/audit_state` 或相对路径等价形式。  
4. 在 `07_OPERATIONS/audit_state` 保留 **INDEX.md 或 README.md**，内容仅说明已迁移至 `../04_OPERATIONS/audit_state`（措辞与裁决书一致）。  
5. 质量门：`SENTINEL_L1_AFTER_P1B_20260408.md`，commit `P1-B audit_state consolidate`，tag `remediation-p1b-complete`（推荐）。

---

## 八、阶段 P1-C（顺序第 5）

1. 打开 `OPENCLAW_REMEDIATION_BACKLOG.md`，对仍属 **P1** 且未在前序阶段完成的行（如 INDEX 裸链、README 错误链、LAYER8 目标等）**逐项处理**。  
2. 每完成一类问题：小 commit + L1 留存（文件名带 `P1C_` 与步骤简述）。  
3. **不阻塞闭环**：若个别 P1 需外部信息，记入 `docs/09_AUDIT/STATE/P1C_DEFERRED_20260408.md` 并说明原因，**不得**静默跳过 EC 中与 P0 相关的项。

---

## 九、最终收口（闭环）

1. 在仓库根执行：  
   ```text
   python scripts/sentinel_l1_governance_scan.py
   ```  
2. 将最终报告保存为：  
   `docs/09_AUDIT/STATE/SENTINEL_L1_POST_REMEDIATION_20260408.md`（及 json）  
3. 核对 **EC-1～EC-7**（定义见 `OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md` §0）：  
   - 无效内链、双 YAML、重复 module_id **不劣于**基线，且 **P0 类为 0**。  
4. 新建：  
   `docs/09_AUDIT/REPORTS/REMEDIATION_EXECUTION_CLOSURE_20260408.md`  
   内容为 **EC-1～EC-7 逐条勾选表** + 关键 commit / tag 列表 + 最终 L1 文件路径。  
5. `git tag remediation-cycle-20260408-closed`（或等价）  
6. 合并分支到主分支（由你执行 PR 或直接 merge，按你习惯）。

---

## 十、交给 AI 时的一句话版（可贴在对话开头）

```text
你在仓库 D:\ZephyrAlpha 执行文档整改。硬约束：严格遵循
docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md 全部 ADR；
阶段顺序与验收见 docs/09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md；
逐步执行 docs/09_AUDIT/PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md。
当前只做阶段 [P0-A / P0-B / …]，本阶段结束前必须跑 python scripts/sentinel_l1_governance_scan.py 并把报告存到 docs/09_AUDIT/STATE/ 且命名含阶段代号。
禁止跳过 P0-B 的 50 文件 dry-run。Git 由人类合并，你只需给出建议的 commit message 与变更摘要。
```

---

## 十一、索引

| 文档 | 路径 |
|------|------|
| 本指令 | `docs/09_AUDIT/PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md` |
| 裁决书 | `docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md` |
| 执行手册 | `docs/09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md` |
