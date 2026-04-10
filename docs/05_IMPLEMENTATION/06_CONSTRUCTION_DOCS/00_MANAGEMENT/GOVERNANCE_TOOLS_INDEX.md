---
module_id: GOVERNANCE_TOOLS_INDEX_001
version: 1.2.1
status: Active
created_date: 2026-04-10
last_updated: '2026-04-11'
owner: 文档负责人（可指定）
responsibility:
  - 治理类脚本与门禁工具的统一索引（办公室入口）
standard_type: 导航索引
applicable_scope: 仓库根执行的文档治理、链接校验、目录聚合、重复扫描、架构目录
---

# 治理工具总索引（办公室 · 快速查询）

> **物理位置**：治理脚本集中在 [`scripts/governance/`](../../../../scripts/governance/)（机构常见的 **tooling 子树**）。仓库根 [`scripts/*.py`](../../../../scripts/) 下同名文件为 **薄兼容入口**（`runpy` 转发），历史文档中的 `python scripts/<name>.py` 仍可执行。  
> **本文件**：逻辑归口——从这里查「干什么、怎么跑、产出在哪」。  
> **与任务清单的关系**：执行口径与波次见 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)；扫描**能做什么、不能做什么**见该文 **§1.1**。  
> **删稿裁决**（机器不代劳）：见 [文件删除与保留裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)。  
> **文档地图 + 放置**：搬迁或新建 `docs/` 路径前，先 [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md)（**§1 第 5 条**摘要）+ [办公室放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)（**§1.5** 详述；互指 [`ARCHITECTURE.md`](../../../01_FRAMEWORK/ARCHITECTURE.md)、REPO_WIDE **§2.3.1**）；**勿**另立平行标准；再跑本表脚本验收。

---

## 1. 工具一览表

| 工具（脚本） | 一句话 | 命令（仓库根，推荐） | 主要产出 |
|--------------|--------|----------------------|----------|
| `sentinel_l1_governance_scan.py` | Markdown **内链** + 首道 front matter **`module_id` 重复** | `python scripts/governance/sentinel_l1_governance_scan.py` | `docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_*.md`（及 json，以脚本为准） |
| `backfill_missing_module_id.py` | 为首道 FM **补 `module_id`**（粘连 `---`、未闭合 FM、纯报表无头等） | `python scripts/governance/backfill_missing_module_id.py --apply` | 就地改写目标 `.md`；跑后须复跑 **L1** |
| `export_repo_directory_rollup.py` | **Git 已跟踪**路径按目录深度 **2～6** 聚合计数；可选未跟踪 | `python scripts/governance/export_repo_directory_rollup.py`（可加 `--include-untracked`） | `docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*.{md,json}` |
| `generate_architecture_service_catalog.py` | **架构/服务目录 + C4 摘要**（`src/`、routes、`pyproject`） | `python scripts/governance/generate_architecture_service_catalog.py` | `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*.{md,json}` |
| `scan_duplicate_file_content.py` | **内容 SHA256 重复**（**必须**传 `--ext`，默认 `md`）；可选 `--include-untracked` | `python scripts/governance/scan_duplicate_file_content.py --ext md` | `docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*.{md,json}` |
| `scan_basename_collisions.py` | **同名不同路径（C2）**：按 basename 分组（默认 `docs/` + `--ext md`）；可选 `--all-repo` | `python scripts/governance/scan_basename_collisions.py` | `docs/09_AUDIT/STATE/BASENAME_COLLISIONS_*.{md,json}` |
| `scan_blueprint_d_overlap_candidates.py` | **蓝图 D 类重叠候选**：启发式相似度 + **建议 canonical / 合并大纲**（非最终裁决） | `python scripts/governance/scan_blueprint_d_overlap_candidates.py` | `docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_*.{md,json}` |
| `triage_blueprint_d_overlap_pairs.py` | **D 类 A 档分流** + 生成二审 **JSONL**（含摘录）；见 [二审提示词模板](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md) | `python scripts/governance/triage_blueprint_d_overlap_pairs.py --date YYYYMMDD` | `BLUEPRINT_D_OVERLAP_TRIAGE_*`、`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_*.jsonl` |
| `scan_index_health.py` | **索引健全性**：`docs/` 下 md **零入链**候选（全库 md 相对链统计） | `python scripts/governance/scan_index_health.py` | `docs/09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_*.{md,json}` |
| `sample_docs_nav_coverage.py` | **P3 抽样**：合并若干 INDEX/SITEMAP 为导航 blob，检路径子串宽松命中（**不**替代 `scan_index_health`） | `python scripts/governance/sample_docs_nav_coverage.py`（可选 `--sample`、`--seed`、`--date`） | 默认终端摘要；样例见 `docs/09_AUDIT/STATE/DOCS_NAV_COVERAGE_SAMPLE_*.md` |
| `verify_01_blueprints_index_links.py` | 校验 `01_BLUEPRINTS/INDEX.md` 内链 | `python scripts/governance/verify_01_blueprints_index_links.py` | 终端输出 |
| `verify_scattered_blueprints_manifest_links.py` | 校验分散蓝图清单内链 | `python scripts/governance/verify_scattered_blueprints_manifest_links.py` | 终端输出 |
| `verify_manifest_paths_strict.py` | 校验总清单正文路径 | `python scripts/governance/verify_manifest_paths_strict.py` | 终端输出 |
| `generate_01_blueprints_index.py` | **重生成**图纸柜 `INDEX.md` | `python scripts/governance/generate_01_blueprints_index.py` | `01_BLUEPRINTS/INDEX.md` |
| `generate_scattered_blueprints_manifest_task1.py` | 生成分散蓝图路径清单（任务用） | `python scripts/governance/generate_scattered_blueprints_manifest_task1.py` | `docs/09_AUDIT/STATE/` 下 json（以脚本为准） |

更完整的脚本说明（含非治理类）见 [`scripts/README.md`](../../../../scripts/README.md)。

---

## 2. 推荐复跑顺序（大改文档/路径之后）

0. （若涉及**归位/新建目录**）对照 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)（**§1.5**）与 LAYOUT 标准，确认目标路径合法或已登记例外；**勿**用路径前缀代替 Layer 编号。  
1. `verify_*`（蓝图与总清单）  
2. `sentinel_l1_governance_scan.py`  
2′. （仅当 L1 报告 **首道无 `module_id` > 0**）`backfill_missing_module_id.py` → `--apply` → 再跑步骤 2  
3. `export_repo_directory_rollup.py`  
4. `generate_architecture_service_catalog.py`  
5. `scan_duplicate_file_content.py --ext md`（按需加 `yaml` 等；需要看工作区未跟踪重复时加 `--include-untracked`）  
6. `scan_basename_collisions.py`（C2 同名不同路径报表；与 C1 独立）  
7. `scan_blueprint_d_overlap_candidates.py`（D 类蓝图重叠候选 + 机器建议；见 [D 类 Playbook](./D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md) **§5**；**低置信**合稿须登记 [D 类合稿待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md)）  
7′. `triage_blueprint_d_overlap_pairs.py`（可选：A 档分流 + `SECOND_PASS_QUEUE_*.jsonl`；二审见 [D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md)）  
8. `scan_index_health.py`（大改导航或想查 **零入链** 候选时；见 [放置规程 §5.2](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)）  
8′. （可选）`sample_docs_nav_coverage.py` — 主导航正文覆盖率抽样；产出样例见 [REPO_WIDE §6](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 推荐阅读表  

合并重复内容前请再读 [任务清单 §3](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)（C1 / C2 / **D**）与 [删稿裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md)。

---

## 3. 常见问题（通俗）

### 为什么要「扫到」很多脚本？是不是都不能删？

**不是。**  
- **扫描 / 清单**的作用，是让你**看见**仓库里有什么（包括历史脚本、一次性修复脚本）。  
- **删不删**要按 [文件删除与保留裁决 Playbook](./FILE_DELETION_OR_RETENTION_PLAYBOOK.md) 判断：引用关系、CI、是否重复实现等。**本索引不替你决定删除**。

### 为什么治理脚本放在 `scripts/governance/`？

与常见 **platform / tooling** 目录习惯一致：门禁、rollup、校验与生成物脚本**成组存放**，根目录 `scripts/<name>.py` 仅保留兼容转发，减少历史文档与肌肉记忆失效成本。

---

## 4. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.2.1 | 2026-04-11 | 工具表与 §2 增 `sample_docs_nav_coverage.py`（P3 主导航抽样；互指 REPO_WIDE §6 样例） |
| 1.2.0 | 2026-04-10 | 增 `triage_blueprint_d_overlap_pairs.py`；§2 增 7′；二审模板 [D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md](./D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md) |
| 1.1.9 | 2026-04-10 | §2 复跑顺序增 2′（L1 无 `module_id` 时 `backfill_missing_module_id.py` → 再跑 L1） |
| 1.1.8 | 2026-04-10 | 工具表增 `backfill_missing_module_id.py` |
| 1.1.7 | 2026-04-10 | 文首互指 LAYOUT **§1 第 5 条**；禁平行 Layer 放置真源 |
| 1.1.6 | 2026-04-10 | 文首与 §2 第 0 步互指 [放置规程 §1.5](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)、`ARCHITECTURE.md`、REPO_WIDE **§2.3.1**（Layer 与路径防混） |
| 1.1.5 | 2026-04-10 | D 类步骤互指 [待审登记](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md)（低置信合稿 + Markdown 相对链） |
| 1.1.4 | 2026-04-11 | 增 `scan_blueprint_d_overlap_candidates.py`（D 类蓝图重叠）；§2 第 8 步 `scan_index_health` |
| 1.1.3 | 2026-04-11 | 增 `scan_basename_collisions.py`（C2 basename 报表）；§2 复跑顺序第 6～7 步 |
| 1.1.2 | 2026-04-10 | 增 `scan_index_health.py`（索引健全性 / 零入链）；§2 复跑顺序增第 6 步 |
| 1.1.1 | 2026-04-10 | 文首与 §2 互指 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) + LAYOUT 标准 |
| 1.1.0 | 2026-04-10 | 物理迁入 `scripts/governance/`；兼容桩；`scan`/`rollup` 支持 `--include-untracked`；互指删稿 Playbook |
| 1.0.0 | 2026-04-10 | 首版：治理工具总表 + FAQ + 复跑顺序 |
