---
module_id: MODULE_DESIGNS_INDEX_001
version: 1.0.1
status: Active
created_date: 2026-04-08
last_updated: '2026-04-11'
owner: 文档治理系统
standard_type: 索引文档
applicable_scope: docs/module_designs（模块设计草图入口）
compliance_level: 专业标准
---

## 上级与接力

- [docs 根索引](../INDEX.md)
- [全仓库文件治理任务清单 §7](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准)
- [治理工具总索引](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)
- [09_AUDIT STATE 索引](../09_AUDIT/STATE/INDEX.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：[../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260516.md](../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260516.md)（`scan_index_health.py --prefix docs/module_designs --date 20260516`；**zero_inbound=0**；候选 md **2**；首轮即零入链，本页增 P5 互指与台账登记）
- **rollup（深度 3）**：[../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md](../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md)（JSON 真源同 stem；键 `docs/module_designs` **2** 条路径）

---

# module_designs 索引

> **定位**：承接“模块设计草图/笔记/临时设计稿”的可达入口，避免形成“事实孤儿”。  
> **原则**：仅做索引挂载，不改正文；后续可按 Layer/主题继续拆分子索引。

## 🧭 入口列表

### Layer 0

- [L0_QMT](./layer_0/L0_QMT.md)
