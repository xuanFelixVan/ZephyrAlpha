---
module_id: KE-2310
title: 5.3 VMS 代码文件（已实现）
category: module_blueprint
---

# 5.3 VMS 代码文件（已实现）

5.3 VMS 代码文件（已实现）

| 文件路径 | 对应蓝图 | 状态 |
|---------|------|:---:|
| `src/zephyr/vector-memory/in_process_vector_memory.py` | §2 8 Collection 核心入口 | ✅ 已实现 |
| `src/zephyr/vector-memory/embedding_router.py` | §3.1 双维度路由 | ✅ 已实现 |
| `src/zephyr/vector-memory/chunk_strategy_router.py` | §2.1 分块策略路由 | ✅ 已实现 |
| `src/zephyr/vector-memory/hybrid_retriever.py` | §3.2 混合检索 | ✅ 已实现 |
| `src/zephyr/vector-memory/provenance_enforcer.py` | §1 可审计设计哲学 | ✅ 已实现 |
| `src/zephyr/vector-memory/index_health_monitor.py` | §1 可自愈设计哲学 | ✅ 已实现 |
| `src/zephyr/vector-memory/cache_layer.py` | §3 技术选型 | ✅ 已实现 |
| `src/zephyr/vector-memory/bridge_layer.py` | §5.2 迁移桥接 | ✅ 已实现 |
| `src/zephyr/vector-memory/vector_bridge.py` | §7 CE集成 + KB同步写入 | ✅ 已实现 |
| `src/zephyr/vector-memory/retrieval_feedback.py` | §8 FLE检索质量反馈 | ✅ 已实现 |
| `src/zephyr/vector-memory/cross_collection_retriever.py` | §12.3 Phase 3 跨Collection联合检索 | ✅ 已实现 |
| `src/zephyr/vector-memory/collection_manager.py` | §2 Collection 管理 | ✅ 已实现 |
| `src/zephyr/vector-memory/vms_schemas.py` | §4 数据模型 | ✅ 已实现 |
| `tests/unit/vector-memory/test_vector_memory.py` | 单元测试 | ✅ 已实现 |

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---
