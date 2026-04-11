---
module_id: GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF_001
version: 1.0.14
status: Active
created_date: 2026-04-10
last_updated: '2026-04-16'
owner: 仓库 Owner / 文档负责人
responsibility:
  - 供「新开 AI 对话」启动整仓文件治理时一次性粘贴的指令真源；与 REPO_WIDE、工具总表、放置规程对齐
standard_type: 操作规程
applicable_scope: 本 Git 仓库；路径级尽治与 Markdown 主导门禁；非外规法律 hold 体系
---

# 全局文件治理 — 会话交接（新对话粘贴用）

> **用途**：你在**新对话**里要做「从全局扫描开始、深度清洁每一处」时，把下文 **「二、工作交接指令（请全文执行）」** 整段复制给 AI；并说明工作区根目录为 **ZephyrAlpha** 仓库。本文即一种 **「接力说明」**（给下一任的短交代）；术语亦见 [项目办公室 AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md) **§0**。  
> **真源优先级**：执行细节以 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 为准（**§2.3.1** Layer 与路径防混；**§2.3.2**「位置是否正确」↔ 放置规程 **§1.6**）；命令表以 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) 为准；放置以 [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)（**§1 第 5～6 条**）+ [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)（**§1.5**、**§1.6**）为准；系统 **Layer 0～11** 以 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md) 为准，**勿**从 `10_*` 目录名推断；**勿**新建平行「Layer 放置标准」。

---

## 一、与专业机构文件治理对照：本仓库已有什么、还缺什么

### 1.1 已对齐的常见机构做法

| 机构常见能力 | 本仓库对应 |
|--------------|------------|
| 文档地图 + 放置规则 | [DOCUMENT_REPOSITORY_LAYOUT_STANDARD](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)、[DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)、图纸柜 [01_BLUEPRINTS_REPOSITORY_RULES](./01_BLUEPRINTS_REPOSITORY_RULES.md) |
| 基线清单与目录热力 | `git ls-files`、平面清单、`export_repo_directory_rollup.py` → `REPO_DIRECTORY_ROLLUP_*` |
| 链接健康门禁 | `sentinel_l1_governance_scan.py`（Invalid links → 0 为团队习惯；见 [`SENTINEL_L1_SCAN_20260408.md`](../../../09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md) **判定无效 0**） |
| 首道 `module_id`（台账口径） | 同一份 L1 报告：**首道无 `module_id` → 0**、**跨文件重复 → 0**；散稿批量补全见 `backfill_missing_module_id.py`（[治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)） |
| 蓝图/总清单机器校验 | `verify_01_*`、`verify_scattered_*`、`verify_manifest_paths_strict.py` |
| 同内容重复（文本类） | `scan_duplicate_file_content.py` + REPO_WIDE **§3**（C1/C2/D）；蓝图 D **低置信**合稿台账 [D 类合稿待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md) |
| 同名不同路径（basename · **非导航**） | `scan_basename_collisions.py` → [`BASENAME_COLLISIONS_*`](../../../09_AUDIT/STATE/BASENAME_COLLISIONS_20260411.md)；**非导航类当前为 0**（2026-04-11，见 REPO_WIDE **§3.6 C2**）；`INDEX`/`README` 等导航名多份并存见报表「导航名」分表，默认不强制改名 |
| 蓝图 D 类重叠（启发式候选） | `scan_blueprint_d_overlap_candidates.py` → 最新 [`BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md)（**非最终裁决**）；可选 `triage_blueprint_d_overlap_pairs.py` → [`TRIAGE_20260412`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_20260412.md) + [`SECOND_PASS_QUEUE_20260412.jsonl`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl) + [二审模板](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md)；低置信合稿登记 [D 类合稿待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md) |
| 索引健全性信号（v1） | `scan_index_health.py` → 零入链候选（非「必须在某 INDEX」裁决） |
| **「位置是否正确」分桶（与入链分立）** | [放置规程 §1.6](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) + [REPO_WIDE §2.3.2](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) + [LAYOUT §1 第 6 条](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)；搬迁 PR 至少对照 **A（物理树）+ E（L1/可选零入链）** |
| 删稿裁决（人） | [FILE_DELETION_OR_RETENTION_PLAYBOOK](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md) |
| 深度队列与退出标准 | REPO_WIDE **§7.2～§7.3** |
| 架构/服务目录生成 | `generate_architecture_service_catalog.py` |

### 1.2 相对「大型机构受控文档体系」仍可能缺失（诚实清单）

以下**未**在本仓库单独立全套流程；若外规要求，需 Owner **另档**或接 CI/外系统：

- **记录保留期 / 法律 hold / 密级标签**（与 Git 历史、删除权交叉）。  
- **CI 强制**：每次 PR 自动跑齐 L1 + verify + rollup（当前多为**约定**与本地/批次跑）。  
- **二进制与 LFS**：体积阈值、误提交大块文件的**自动拒收**（仅有架构目录里的缺口提示类信息）。  
- **域内 INDEX 必列规则**的**自动化**（规则未冻结前不做硬门禁，见 [放置规程 §5.3](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)）。  
- **全格式语义审阅**（PDF/Office/图片 OCR 等）——本清单**明确不做**（REPO_WIDE **§1.1**）。  
- **逻辑模块全景 `MODULE_PANORAMA_*`**：仍为 **P4 可选**（REPO_WIDE **§2.4**）。

### 1.3 办公室与任务清单联动自检（维护者用）

- [ ] [办公室 README](./README.md) 流程 1～7 与 [蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md)、REPO_WIDE **无冲突表述**（并列、W 轨 ≠ 尽治）。  
- [ ] [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) 与 `scripts/governance/` 实际脚本一致。  
- [ ] REPO_WIDE **§8** 自查项仍可达（含 AI 交接 **①‴**、**§3.2**、放置规程 **§1.5**、**§1.6**、索引健全性）。  

---

## 二、工作交接指令（请全文执行）

**上下文**

- 工作区根目录：**ZephyrAlpha**（本仓库）。  
- 目标：从**全局扫描与基线刷新**开始，按**可打勾的目录前缀队列**做**深度清洁**（摆放、重复、导航、内链），直到 REPO_WIDE **§7** 退出标准或已登记**书面例外**。  
- **硬约束**：  
  1. **不**在未读 [删稿裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md) 的情况下批量删除。  
  2. 合并重复须遵守 REPO_WIDE **§3**（尤其 C1 流程与归档区策略 **§3.1**）。  
  3. 每批实质性改路径后：`sentinel_l1_governance_scan.py` → **Invalid links = 0**（除非 Owner 书面例外）。  
  4. 搬迁/新建路径须符合 [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)；拿不准时先读 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)。  
  5. **「每一个文件」**：以**路径与链接可治理**为目标；**不承诺**对每份文件做业务语义审阅（见 REPO_WIDE **§1.1**）。

**阶段 A — 先读后扫（约 15～30 分钟）**

1. 阅读 REPO_WIDE **§0、§1、§1.1**（扫描能做什么、不能做什么）。  
2. 阅读 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md) 全文。  
3. 阅读 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§1.6**（「位置是否正确」分桶表）+ **§3～§5**（扫描→归位→索引→零入链）。  
4. 若本轮含 **蓝图 D 类（主题可能重叠）**：阅读 [D 类蓝图重叠 Playbook](./D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md)（机器建议 ≠ 最终裁决；**§5 双轨**；**§3.5** 分流/二审）。若执行 **低置信**合稿（新路径 + 旧稿 stub）：每例在 [D 类合稿待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md) **追加一行**（路径列用 Markdown 相对链，便于一点就跳）。

**阶段 B — 全局基线刷新（仓库根执行；`YYYYMMDD` 换成当天）**

按顺序运行并 **commit** 更新后的 STATE（或按 Owner 要求仅保留本地）：

```text
python scripts/governance/export_repo_directory_rollup.py --date YYYYMMDD
python scripts/governance/export_repo_directory_rollup.py --date YYYYMMDD --include-untracked
python scripts/governance/scan_duplicate_file_content.py --ext md --date YYYYMMDD
python scripts/governance/scan_duplicate_file_content.py --ext md --date YYYYMMDD --include-untracked
python scripts/governance/scan_basename_collisions.py --date YYYYMMDD
python scripts/governance/scan_blueprint_d_overlap_candidates.py --date YYYYMMDD
python scripts/governance/triage_blueprint_d_overlap_pairs.py --date YYYYMMDD
python scripts/governance/scan_index_health.py --date YYYYMMDD
python scripts/governance/generate_architecture_service_catalog.py
python scripts/governance/sentinel_l1_governance_scan.py
```

若 L1 报告 **首道无 `module_id` > 0**：先 `python scripts/governance/backfill_missing_module_id.py` 预览，再 `python scripts/governance/backfill_missing_module_id.py --apply`，**然后**再跑一次 `sentinel_l1_governance_scan.py`（见 [治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)）。

另用仓库内已载明的 PowerShell/Python 片段**可选**刷新 `REPO_GIT_TRACKED_FILES_*.txt`（REPO_WIDE **§1**）。

**阶段 C — 建立深度清洁队列**

1. 打开 `docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_YYYYMMDD.md` 的 **深度 5、6**（及 3、4）表，结合 `.json` 全量前缀。  
2. 按 REPO_WIDE **§7.1** 拆分超大前缀（如 `docs/09_AUDIT/STATE`）为子队列。  
3. 为每一前缀建立「本批 PR 描述」模板：目标、是否动 archive、是否只做导航不写语义。

**阶段 D — 逐前缀执行（每批建议可控规模，如 20～80 个文件或单个子树）**

对当前前缀队列中的每一批：

1. **摆放**：对照 LAYOUT + [放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§4** 决定是否搬迁；动 `01_BLUEPRINTS` 时叠加图纸柜规则。  
2. **重复**：若存在 C1，按 REPO_WIDE **§3.2**（canonical → 替换链接 → 删或 stub）。  
3. **导航**：父级或本级 **INDEX / README / 上级入口**（§7.2）。  
4. **内链**：`sentinel_l1_governance_scan.py`；触及蓝图则跑相关 `verify_*` 与 `generate_01_blueprints_index.py`（若适用）。  
5. **索引信号**：视需要复跑 `scan_index_health.py`（零入链**不**等于必须删）。  
6. **收口**：`git commit`；下一批前可再跑 `export_repo_directory_rollup.py --date YYYYMMDD` 看前缀是否「变薄」。

**阶段 E — 里程碑**

- 对照 REPO_WIDE **§7.3** 总勾选与 **§8** 办公室自查。  
- 与 [蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **扩展轨 W0～W4** **并列核对**（W 轨勾完 ≠ 尽治完毕）。

**停止并询问 Owner 的条件**

- 需 **canonical / 归档策略 / 外规** 裁决；或 sentinel 长期无法归零且涉及历史快照/审计正文是否可改。

---

## 三、版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.14 | 2026-04-16 | 文首标明「接力说明」并互指 AI 交接 **§0**；真源段增 **§1.6 / §2.3.2**、LAYOUT **§1 第 6 条**；§1.1 增「位置是否正确」分桶行；阶段 A 增读 **§1.6**；§1.3 自检增 **§1.6** |
| 1.0.13 | 2026-04-11 | 阶段 C 恢复三步（撤除第 4 步「多会话 / 排队执行」表述）；与撤回根 `AGENTS.md`、`.cursor/rules` 接力附件对齐 |
| 1.0.12 | 2026-04-12 | 阶段 C 曾增第 4 步（接力/运行队列废止后的 PR 批次说明；见 1.0.13 收敛） |
| 1.0.11 | 2026-04-11 | 阶段 C 曾互指运行队列（已废止，见 1.0.12） |
| 1.0.10 | 2026-04-10 | 阶段 B 增 `triage_blueprint_d_overlap_pairs.py`；§1.1 D 类行与阶段 A 互指 TRIAGE / SECOND_PASS_QUEUE / [二审模板](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md) |
| 1.0.9 | 2026-04-10 | §1.1 增首道 `module_id` 行（L1 报告无 id/重复双 0 + `backfill_missing_module_id.py`）；阶段 B 增 backfill→复跑 L1 说明 |
| 1.0.8 | 2026-04-12 | §1.1 增 D 类候选报表入口（`BLUEPRINT_D_OVERLAP_CANDIDATES_20260412`）与待审登记表互指 |
| 1.0.7 | 2026-04-11 | §1.1 链接健康行互指 L1 快照（判定无效 0） |
| 1.0.6 | 2026-04-11 | §1.1 表增 C2 basename（非导航已收口）；互指 `BASENAME_COLLISIONS_20260411` 与 REPO_WIDE §3.6 |
| 1.0.5 | 2026-04-10 | 真源段互指 LAYOUT **§1 第 5 条**；禁平行 Layer 放置真源 |
| 1.0.4 | 2026-04-10 | 真源段与 §1.3 自检互指 [放置规程 §1.5](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)、`ARCHITECTURE.md`、REPO_WIDE **§2.3.1**、AI 交接 **§3.2**（Layer 与路径防混） |
| 1.0.3 | 2026-04-10 | 机构对照表与阶段 A 互指 [D 类合稿待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md)（低置信 + 可点击链） |
| 1.0.2 | 2026-04-11 | 阶段 B 增 `scan_blueprint_d_overlap_candidates.py`（D 类蓝图重叠候选） |
| 1.0.1 | 2026-04-11 | 阶段 B 增 `scan_basename_collisions.py`（C2 basename 报表） |
| 1.0.0 | 2026-04-10 | 首版：机构对照缺口、办公室自检、可复制会话指令 |
