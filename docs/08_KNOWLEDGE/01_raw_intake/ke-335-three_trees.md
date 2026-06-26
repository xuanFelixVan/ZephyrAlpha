---
module_id: KE-335
status: active
title: 4. Three trees / 三棵树的架构对应关系
category: documentation
ttl: permanent
---

# 4. Three trees / 三棵树的架构对应关系

4. Three trees / 三棵树的架构对应关系

The ZephyrAlpha 2.0 repository has three main trees, each corresponding to a primary architecture view:

ZephyrAlpha 2.0 仓库有三棵主树，每棵对应一个主要架构视图：

| Tree / 树 | Primary view / 核心视图归属 | Key diagrams / 主要图 | Owner document / 归属文档 |
|----------|--------------------------|---------------------|--------------------------|
| `docs/` | Information Architecture | `docs/` 抽屉拓扑图 + 文档生命周期图 + 跨抽屉引用图 | `information_architecture.md` |
| `src/` | Application Architecture | C4-L1 系统上下文 + C4-L2 容器图 + 14 层代码分层图 + 跨层数据流图(CTR-001~006) | `application_architecture.md` |
| `scripts/` | Application Architecture (sub-view) | 治理代码拓扑图 + pre-commit/CI 钩子流程图 | `application_architecture.md §4` |

---
