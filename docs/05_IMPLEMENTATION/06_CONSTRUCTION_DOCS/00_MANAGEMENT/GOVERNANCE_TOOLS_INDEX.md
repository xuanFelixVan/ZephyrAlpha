---
module_id: GOVERNANCE_TOOLS_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 治理类脚本与门禁工具的统一索引（办公室入口）
standard_type: 导航索引
applicable_scope: 仓库根执行的文档治理、链接校验、目录聚合、重复扫描、架构目录
---

# 治理工具总索引（办公室 · 快速查询）

> **物理位置**：脚本仍在仓库根目录 [`scripts/`](../../../../scripts/) 下（与 Python 路径、既有 CI、习惯用法兼容），**不集中搬迁**，避免大面积改引用。  
> **本文件**：机构里常见的 **「工具目录 / Service catalog」** 的**逻辑归口**——从这里一键跳到「干什么、怎么跑、产出在哪」。  
> **与任务清单的关系**：执行口径与波次见 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)；扫描**能做什么、不能做什么**见该文 **§1.1**。

---

## 1. 工具一览表

| 工具（脚本） | 一句话 | 命令（仓库根） | 主要产出 |
|--------------|--------|----------------|----------|
| `sentinel_l1_governance_scan.py` | Markdown **内链** + 首道 front matter **`module_id` 重复** | `python scripts/sentinel_l1_governance_scan.py` | `docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_*.md`（及 json，以脚本为准） |
| `export_repo_directory_rollup.py` | **Git 已跟踪**路径按目录深度 **2～6** 聚合计数 | `python scripts/export_repo_directory_rollup.py` | `docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_*.{md,json}` |
| `generate_architecture_service_catalog.py` | **架构/服务目录 + C4 摘要**（`src/`、routes、`pyproject`） | `python scripts/generate_architecture_service_catalog.py` | `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*.{md,json}` |
| `scan_duplicate_file_content.py` | **内容 SHA256 重复**（**必须**传 `--ext`，默认 `md`） | `python scripts/scan_duplicate_file_content.py --ext md` | `docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_*.{md,json}` |
| `verify_01_blueprints_index_links.py` | 校验 `01_BLUEPRINTS/INDEX.md` 内链 | `python scripts/verify_01_blueprints_index_links.py` | 终端输出 |
| `verify_scattered_blueprints_manifest_links.py` | 校验分散蓝图清单内链 | `python scripts/verify_scattered_blueprints_manifest_links.py` | 终端输出 |
| `verify_manifest_paths_strict.py` | 校验总清单正文路径 | `python scripts/verify_manifest_paths_strict.py` | 终端输出 |
| `generate_01_blueprints_index.py` | **重生成**图纸柜 `INDEX.md` | `python scripts/generate_01_blueprints_index.py` | `01_BLUEPRINTS/INDEX.md` |
| `generate_scattered_blueprints_manifest_task1.py` | 生成分散蓝图路径清单（任务用） | `python scripts/generate_scattered_blueprints_manifest_task1.py` | `docs/09_AUDIT/STATE/` 下 json（以脚本为准） |

更完整的脚本说明（含非治理类）见 [`scripts/README.md`](../../../../scripts/README.md)。

---

## 2. 推荐复跑顺序（大改文档/路径之后）

1. `verify_*`（蓝图与总清单）  
2. `sentinel_l1_governance_scan.py`  
3. `export_repo_directory_rollup.py`  
4. `generate_architecture_service_catalog.py`  
5. `scan_duplicate_file_content.py --ext md`（按需加 `yaml` 等）  

合并重复内容前请再读 [任务清单 §3](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)（C1 流程）。

---

## 3. 常见问题（通俗）

### 为什么要「扫到」很多脚本？是不是都不能删？

**不是。**  
- **扫描 / 清单**的作用，是让你**看见**仓库里有什么（包括历史脚本、一次性修复脚本）。  
- **删不删**要单独判断：有没有被文档引用、有没有被 CI 调用、是否重复实现。**本索引不替你决定删除**，只提供工具定位；删改仍建议小步 PR + 评审。

### 能不能把所有治理脚本「搬到同一个文件夹」？

**可以物理搬迁，但不建议在本仓库贸然做**：会改大量文档里的命令、CI、个人习惯路径。  
**机构常见做法**正是：**物理仍在 `scripts/`，逻辑用本索引 + 任务清单归口**（你现在的结构）。

---

## 4. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-10 | 首版：治理工具总表 + FAQ + 复跑顺序 |
