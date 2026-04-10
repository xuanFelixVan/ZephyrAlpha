---
module_id: D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK_001
version: 1.0.0
status: Active
created_date: 2026-04-11
last_updated: '2026-04-11'
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

---

## 4. 参数与调优

- **默认**：`--min-score`≈0.195、`--min-token-intersection`≈36，并按 score 截断 **`--max-output-pairs`（默认 400）**——报表只保留「最像重叠」的对，避免一次输出数万对。  
- 候选仍过多：提高 `--min-score` 或 `--min-token-intersection`，或降低 `--max-output-pairs`。  
- 候选过少：略降 `--min-score`；或缩小 `--prefix` 分批跑（如先 `docs/01_FRAMEWORK/`）。  
- 默认 **排除** `docs/09_AUDIT/STATE/overnight_runs/`；需纳入时加 `--keep-state-overnight`。

---

## 5. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-11 | 首版：D 类流水线与机器建议口径 |
