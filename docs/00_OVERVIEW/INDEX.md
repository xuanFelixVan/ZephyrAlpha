---
module_id: 00_OVERVIEW_INDEX
version: 1.0.1
status: Active
created_date: 2026-04-07
last_updated: '2026-04-11'
owner: 首席文档架构师
responsibility:
  - 00_OVERVIEW目录索引
---

﻿---
module_id: 00_OVERVIEW_INDEX_00_OVERVIEW
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: ﻠ۵ﮒﺕﮔﮔ۰۲ﮔﭘﮔﮒﺕ?standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻝﺑ۱ﮒﺙ
responsibility:
  - 目录导航与文档索引管理与优化维护
applicable_scope: ﻝﺏﭨﻝﭨﮔﭨﻟ۶
compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: ../INDEX.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?---

## 上级与接力

- [docs 根索引](../INDEX.md)
- [全仓库文件治理任务清单 §7](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准)
- [治理工具总索引](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)
- [09_AUDIT STATE 索引](../09_AUDIT/STATE/INDEX.md)

### 门面入链（P5 §7）

- [总览 README](./README.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（本批）**：[../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260514.md](../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260514.md)（`scan_index_health.py --prefix docs/00_OVERVIEW --date 20260514`；首轮 **`README.md`** 零入链，已由上链补入后复跑 **zero_inbound=0**）
- **rollup（深度 3）**：[../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md](../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md)（JSON 键 `docs/00_OVERVIEW` **3** 条路径）

---

# ﻝﺏﭨﻝﭨﮔﭨﻟ۶ﻝ؟ﮒﺛﻝﺑ۱ﮒﺙ
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﻝ؟ﮒﺛﻟﻟﺑ۲**: ﮔﻛﺝﻝﺏﭨﻝﭨﮒ۷ﮒﺎﻟ۶ﮒﺝﻙﮔﺍﮔ؟ﮔﭖﮒﻙﮒﺟ،ﻠﮒ۴ﻠ۷ﮔﮒﺙ?
## ﻭ ﻝ؟ﮒﺛﻝﭨﮔ

| ﮔﻛﭨﭘ/ﻝ؟ﮒﺛ | ﻟﻟﺑ۲ | ﻝﭘﮔ?|
|----------|------|------|

| DATA_FLOW.md | ﻝﺏﭨﻝﭨﮔﺍﮔ؟ﮔﭖﮒﮒ?| Active |

## ﻭ ﮒﺟ،ﻠﮒﺁﺙﻟ?
### ﮔﺕﮒﺟﮔﮔ۰۲
- **ﻝﺏﭨﻝﭨﮔﭘﮔ**: [../01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md)
- **ﮒﮒﮒﭦ?*: `../02_FACTOR_LIBRARY/INDEX.md`
- **ﻛﭦ۳ﮔﻝﻝ۴**: [../03_TRADING_TACTICS/INDEX.md](../03_TRADING_TACTICS/INDEX.md)
- **ﮔ۶ﻟ۰ﮒﺎ?*: [../04_EXECUTION/INDEX.md](../04_EXECUTION/INDEX.md)
- **ﮒ؟ﮔﺛﮔﮒ**: [../05_IMPLEMENTATION/INDEX.md](../05_IMPLEMENTATION/INDEX.md)

### ﮒ۳ﻠ۷ﻟﭖﮔﭦ
- **ﮒﺗﺏﮒﺍﮔﮔ۰۲**: [../00_RESOURCES/04_PLATFORM_DOCS/](../00_RESOURCES/04_PLATFORM_DOCS/)

## ﻭ ﻝ؟ﮒﺛﮒ؟ﻛﺛ

```
docs/
ﻗﻗﻗ 00_OVERVIEW/          ﻗ?ﮒﺛﮒﻝ؟ﮒﺛﺅﺙﻝﺏﭨﻝﭨﮔﭨﻟ۶ﺅﺙ?ﻗ?  ﻗﻗﻗ README.md         # ﻝﺏﭨﻝﭨﮒ۴ﮒ۲
ﻗ?  ﻗﻗﻗ DATA_FLOW.md      # ﮔﺍﮔ؟ﮔﭖﮒ
ﻗﻗﻗ 01_FRAMEWORK/         # ﮔﺕﮒﺟﮔ۰ﮔﭘ
ﻗﻗﻗ 02_FACTOR_LIBRARY/    # ﮒﮒﮒﭦ?ﻗﻗﻗ 03_TRADING_TACTICS/   # ﻛﭦ۳ﮔﻝﻝ۴
ﻗﻗﻗ 04_EXECUTION/         # ﮔ۶ﻟ۰ﮒﺎ?ﻗﻗﻗ 05_IMPLEMENTATION/    # ﮒ؟ﮔﺛﮔﮒ
ﻗﻗﻗ 06_ARCHIVE/           # ﮒﺛﮔ۰۲
ﻗﻗﻗ 07_RESEARCH/          # ﻝﻝ۸ﭘﮔﺁﮔ
ﻗﻗﻗ 09_AUDIT/             # ﮒ؟۰ﻟ؟۰
ﻗﻗﻗ 10_AI_WORKFLOW/       # AIﮒﺓ۴ﻛﺛﮔﭖ?```
---

*ﮔﮒﮔﺑﮔ? 2026-04-03*
