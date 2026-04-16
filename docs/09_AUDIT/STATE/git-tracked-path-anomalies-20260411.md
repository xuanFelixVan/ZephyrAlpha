---
module_id: GIT_TRACKED_PATH_ANOMALIES_20260411
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: STATE
---







# Git 路径：引号 / 八进制输出 vs 索引真源（澄清说明）

> **用途**：为 全仓库文件治理任务清单 **§1**、**P2** 提供可复跑说明；**纠正**「看见 `git ls-files` 带引号 = 索引里路径坏了」的误判。

## 结论（先看这段）

1. **`review_materials_package` 下含中文文件名的路径**：在 Git **索引与工作区**中一般为 **正常 UTF-8**；**并非**必须 `git mv` 才能「修复索引」。
2. PowerShell / 终端在**默认** `core.quotePath` 下，`git ls-files` 对非 ASCII 可能输出 **双引号 + `\nnn` 八进制转义**——这是 **CLI 显示层**行为，不是第二套路径。
3. **整仓统计、rollup、重复扫描**等自动化应使用 **`git -c core.quotePath=false ls-files`**（Python 侧加 `encoding="utf-8"`），或使用 **`git ls-files -z` + UTF-8 解码**（本仓库 `scan_index_health.py` 已用 `-z`）。**2026-04-11** 起 `export_repo_directory_rollup.py`、`scan_*`、`sample_docs_nav_coverage.py`、`generate_architecture_service_catalog.py` 等已统一 `quotePath=false`。
4. 若历史平面清单（如 `REPO_GIT_TRACKED_FILES_20260410.txt`）前几行出现引号形式，属**导出命令未关 quotePath**；请改用 `REPO_GIT_TRACKED_FILES_20260411.txt` 或按 REPO_WIDE §1 推荐 one-liner 重导。

## 复现「带引号」输出（仓库根 · PowerShell）

```powershell
git ls-files | Select-String -Pattern '^"'
```

对 `review_materials_package` 中含非 ASCII 的路径，默认配置下常可得到 **8** 行（与「扩展名看似 `md"`」的误读为**同一批**，非 16 条）。

## 人类可读 UTF-8 输出（对照）

```powershell
git -c core.quotePath=false ls-files review_materials_package/
```

## 附录：默认 `git ls-files` 下的转义显示示例（8 条）

下列为 **显示层**逐字拷贝，**不要**当作 Markdown 内链或脚本路径字面量使用：

```text
"review_materials_package/data_consistency/Saga\346\250\241\345\274\217\345\256\236\347\216\260\346\265\201\347\250\213\345\233\276.md"
"review_materials_package/data_consistency/\345\244\232\345\274\225\346\223\216\346\225\260\346\215\256\344\270\200\350\207\264\346\200\247\350\256\276\350\256\241\346\226\271\346\241\210.md"
"review_materials_package/data_consistency/\350\241\245\345\201\277\344\272\213\345\212\241\350\256\276\350\256\241\346\226\207\346\241\243.md"
"review_materials_package/trading_costs/\344\272\244\346\230\223\346\210\220\346\234\254\346\265\213\350\257\225\347\224\250\344\276\213\350\256\276\350\256\241.md"
"review_materials_package/web_interface/API\346\216\245\345\217\243\350\247\204\350\214\203\346\226\207\346\241\243.md"
"review_materials_package/web_interface/\345\211\215\347\253\257\347\273\204\344\273\266\347\273\223\346\236\204\345\233\276.md"
"review_materials_package/\346\212\200\346\234\257\346\226\271\346\241\210\350\256\276\350\256\241\346\261\207\346\200\273\346\212\245\345\221\212.md"
"review_materials_package/\346\212\200\346\234\257\346\226\271\346\241\210\350\257\204\345\256\241\344\274\232\350\256\256\350\256\256\347\250\213.md"
```

```
```---
```

**维护**：若 Git 默认配置变更或新增非 ASCII 路径，可复跑上文命令核对；**无需**为此单独开「路径规范化」PR，除非确有**错误字面路径**被提交（与本附录所示**显示转义**不同）。
