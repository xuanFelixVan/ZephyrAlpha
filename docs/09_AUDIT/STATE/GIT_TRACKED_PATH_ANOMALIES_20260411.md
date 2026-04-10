---
module_id: GIT_TRACKED_PATH_ANOMALIES_20260411
standard_type: audit_state
applicable_scope: Git 索引异常路径清点（P2 前置证据）
generated_date: '20260411'
---

# Git 已跟踪路径异常清单（引号 / 八进制转义）

> **用途**：为 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§1**、**P2** 提供**可复跑、可 diff** 的逐路径真源；**不**在本文件中执行 `git mv`（须单独 PR + 备份 + L1）。  
> **口径说明**：下列 **8** 条在 `git ls-files` 输出中以 **前导双引号 `"`** 包裹，且路径中含 **`\nnn` 八进制转义**（Git 对非 ASCII 的引用形式）。统计上常被误计为「`"` 前缀桶」与「扩展名看似 `md"`」**两类异常**，实为**同一批 8 条**，非 16 条。

## 复跑（仓库根 · PowerShell）

```powershell
git ls-files | Select-String -Pattern '^"'
```

（与 `Select-String -Pattern 'md"$'` 对上述 8 条输出一致。）

## 异常路径（逐字拷贝自 `git ls-files`，共 8 条）

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

## 同目录「正常 UTF-8 路径」对照（无引号 · 示例）

便于确认 **并非** 整树异常，而是上述 8 条与下列 **5** 条等并存：

```text
review_materials_package/a_stock_rules/T.08.AR001.a_stock_rule_engine_design.md
review_materials_package/a_stock_rules/a_stock_rules_config.yaml
review_materials_package/trading_costs/T.05.TE001.trading_cost_model_algorithm_document.md
review_materials_package/trading_costs/trading_cost_config_template.yaml
review_materials_package/web_interface/T.06.UI001.web_management_interface_architecture_design.md
```

## P2 规范化建议（摘要）

1. 新开分支；必要时先 `git archive` 或整仓备份。  
2. 使用 `git mv`（或两步 mv）将每条**异常字面**迁到目标 UTF-8 相对路径；避免在 shell 中手工拼接引号导致二次转义。  
3. 全仓检索 Markdown / 脚本中是否硬编码了带引号或八进制的旧路径。  
4. 复跑 `python scripts/governance/sentinel_l1_governance_scan.py`（判定无效 **0**）、`export_repo_directory_rollup.py`，并更新 [`REPO_GIT_TRACKED_FILES_*.txt`](./REPO_GIT_TRACKED_FILES_20260410.txt) 若仍作为基线。  

---

**生成**：2026-04-11；与当时 `git ls-files` 一致。
