---
module_id: D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK_001
version: 1.2.0
status: Active
created_date: 2026-04-11
last_updated: '2026-04-10'
owner: 仓库 Owner / 文档负责人
responsibility:
  - 定义蓝图 D 类（主题/职责重叠、表述不同）的发现、机器建议与人工收口流程
standard_type: 操作规程
applicable_scope: `docs/` 下 `*BLUEPRINT*.md` 及同类施工蓝图；与 C1/C2 互补
---

# D 类蓝图重叠 — Playbook（机器建议 + 人工裁决）

> **定位**：当两篇及以上蓝图 **不是** 字节相同（C1）、也 **不是** 仅 basename 撞名（C2），但 **主题或职责边界可能重叠** 时，按本文档执行。  
> **机器角色**：[`scan_blueprint_d_overlap_candidates.py`](../../../../scripts/governance/scan_blueprint_d_overlap_candidates.py) 产出 **候选对 + 指标 + 建议 canonical + 建议合并大纲**（**非最终裁决**）。  
> **人工角色**：确认是否真重叠、是否合并、canonical、stub/archive 与全仓改链。

---

## 1. 与 C1 / C2 / D 的边界

| 类型 | 典型信号 | 主工具 |
|------|----------|--------|
| **C1** | SHA256 相同 | `scan_duplicate_file_content.py` |
| **C2** | 同名不同路径 | `scan_basename_collisions.py` |
| **D** | 标题/responsibility/章节 **像** 同一主题，正文不同 | **本文 +** `scan_blueprint_d_overlap_candidates.py` |

---

## 2. 机器建议的含义（必读）

- 脚本使用 **启发式**（标题、YAML `responsibility`、`module_id`、正文抽样、H2 集合、token Jaccard），**不是** embedding / LLM 语义判重。  
- **假阳性**：不同模块共用大量通用词时，可能出现「像重复」；**假阴性**：表述差异极大但职责重叠时，可能未进候选表。  
- **建议 canonical** 规则偏向：路径含 **`01_BLUEPRINTS`**、正文体量更大、`last_updated` 更新等——**你必须**结合业务确认。  
- **建议合并大纲** 来自两稿 H2 的 **并集草案**，合并时须 **去重叙事、补边界、写清「不负责什么」**。

---

## 3. 推荐工作流（可与 §7 目录批次穿插）

1. **生成报表**（仓库根）：  
   `python scripts/governance/scan_blueprint_d_overlap_candidates.py --date YYYYMMDD`  
   → `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_YYYYMMDD.{md,json}`
2. **人工初筛**：对每一候选对打开 A/B，判定：  
   - **同一 bounded context** → 倾向 **合并**（颗粒度加细：总览 + 分节 deep dive）；  
   - **不同层/不同职责**（如数据源 vs ML 侧质量）→ **不合并正文**，改为 **互链 + 职责表**。  
3. **定稿动作**（合并路径）：对齐目录 → 吸收独有段落 → 更新 canonical → 另一路径 **stub** 或 **迁 archive** → [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3.2** 改链 → `sentinel_l1` / 相关 `verify_*`。  
4. **台账**：重大裁决可记入 [CANONICAL_POINTERS.md](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md) 或本目录登记表。

### 3.5 A 档分流与二审（更强模型）

为减少「逐对打开」成本，可在人工初筛前增加 **路径规则分流** 与可选 **二审（GLM / Claude Opus 等）**：

1. **A 档分流**（仓库根）：`python scripts/governance/triage_blueprint_d_overlap_pairs.py --date YYYYMMDD`（或 `--input docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_YYYYMMDD.json`）  
   - `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_YYYYMMDD.{md,json}`：全量 `triage_tier`、优先级统计与逐对摘录。  
   - `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_YYYYMMDD.jsonl`：**每行一个 JSON**，含机器指标 + `excerpt_a` / `excerpt_b`（非全文），供二审模型消费。  
   - 可选：`--queue-mode high_medium` — 不将 `second_pass_priority=LOW` 写入 JSONL（多为「图纸柜 vs 归档」组合，可按默认策略优先 stub/链收口）。  
2. **二审**：将 [二审提示词模板](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md) 全文与 **JSONL 片段**（可按 `second_pass_priority` 或 `pair_id` 截取）发给更强模型；**输出必须符合模板内 JSON Schema**；**仍须 Owner 抽样或签核**后再改仓库。  
3. **模板与规则迭代**：二审可在输出根对象中附带 `prompt_template_patch_proposal`（见模板 §六）；Owner 择优合并回模板或调整 `triage_blueprint_d_overlap_pairs.py`。

与 **§5 双轨**：二审结论若属 **低置信** 合稿路径，仍走 **5.2** 与 [待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md)。

---

## 4. 参数与调优

- **默认**：`--min-score`≈0.195、`--min-token-intersection`≈36，并按 score 截断 **`--max-output-pairs`（默认 400）**——报表只保留「最像重叠」的对，避免一次输出数万对。  
- 候选仍过多：提高 `--min-score` 或 `--min-token-intersection`，或降低 `--max-output-pairs`。  
- 候选过少：略降 `--min-score`；或缩小 `--prefix` 分批跑（如先 `docs/01_FRAMEWORK/`）。  
- 默认 **排除** `docs/09_AUDIT/STATE/overnight_runs/`；需纳入时加 `--keep-state-overnight`。

---

## 5. 双轨策略：高置信 vs 低置信（可同时采用）

> **原则**：**高置信**走「收口快、可不保留旧稿正文」；**低置信**走「合稿新路径 + 旧稿不删 + 登记待审」，降低误合并成本。

### 5.1 高置信（可不保留旧稿）

**含义**：机器/规则判定 **极可能** 为同一职责、合并误伤概率低时，允许 **不再保留旧路径上的长文**（删除原文件，或把内容完全并入唯一 canonical 后删除重复路径）。

**建议门槛（须书面冻结后执行；以下为示例，可按仓库调参）**：

- 已由 **C1**（`scan_duplicate_file_content`）证实 **全文 hash 相同** → **走 C1 流程**，不属 D；或  
- **同时满足**例如：`BLUEPRINT_D_OVERLAP` 的 **score** 高于团队设定上限、**heading_jaccard** 高于阈值、**两条路径均在** `docs/.../01_BLUEPRINTS/`、且 **无**明显 Layer/读者冲突（需脚本或清单排除跨层对）。

**仍建议**：

- **Git 历史**即「一键回滚」真源；PR 说明写清 **合并自哪些路径**。  
- 若希望 **零登记** 也可；若希望审计友好，可在 commit 或 `docs/09_AUDIT/STATE/` 写一行 **高置信合并日志**（可选，**不**使用下文「待审登记表」）。

### 5.2 低置信（合稿新路径 + 不立刻删旧稿）

**含义**：候选对 **不够确定** 或 **跨目录/跨层** 时：

1. **新稿**：写入 **新路径**，文件名建议 `*_CONSOLIDATED_YYYYMMDD.md`（或与 canonical 同目录、名称可检索）。  
2. **旧稿**：**不删路径**（推荐 **原地 stub**：短说明 + 指向合稿 + 可选「全文已迁 archive」链接），避免外链、书签、历史清单断掉。  
3. **可选**：将 **旧全文** 复制到 `docs/06_ARCHIVE/` 下固定子树（如 `docs/06_ARCHIVE/d_class_consolidation_pending/YYYYMMDD_批次/`），原路径仅保留 stub —— **旧稿是否「不在原地」**：  
   - **stub 仍在原 URL** → 协作上仍算「原地有文件」，只是内容变短；  
   - **长文**在 archive，便于你 **统一打开 archive 目录** 做后审，而不必全树搜索。

**必须**：每做一例，在 [D 类合稿待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md) **追加一行**，便于你 **统一审核**。

### 5.3 与「只动高置信子集」的关系

- **高置信子集** + **低置信子集** **可以同时作为方案**：同一轮 D 治理里，对报表自上而下 **先切高置信** 收口，再对余下 **走 5.2**。  
- **不要**对低置信执行 5.1 的「删旧稿」，除非事后登记为 accepted 且已确认无引用风险。

---

## 6. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.2.0 | 2026-04-10 | 增 **§3.5**：`triage_blueprint_d_overlap_pairs.py` + [二审提示词模板](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md)（JSON Schema + 模板自优化 proposal） |
| 1.1.0 | 2026-04-11 | §5 双轨：高置信可不保留旧稿 vs 低置信合稿新路径 + [待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md) |
| 1.0.0 | 2026-04-11 | 首版：D 类流水线与机器建议口径 |
