---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.integration（24 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.integration（24 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：wired=19，wired_by_header=4，wired_dynamic=1；初判汇总：mount=24

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/integration/ai_service_route_matrix.py` | AiServiceRouteMatrix — AI 服务分级路由表（MOD-INT-AIROUTE）。 | 2026-09-06（28天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/api_gateway.py` | ApiGateway — 单进程轻量 API 网关（MOD-INT-APIGW）。 | 2026-09-06（28天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/llm_bridge.py` | [BLUEPRINT] MOD-INF-028 — LLM 桥接 Stage 6 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/local_model/cache_layer.py` | CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU | 2026-09-16（18天） | in=6/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/local_model/ollama_embedding.py` | OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入 | 2026-09-05（29天） | in=3/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/mcp/error_codes.py` | MCP 错误码集中注册（MOD-INF-013 §3.4）。 | 2026-08-19（46天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/mcp/handoff_auto_loader.py` | Handoff 自动加载器——从 handoff 包恢复 AI session 上下文（MOD-INF-013 §5.3）。 | 2026-07-23（73天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/mcp/prompt_provider.py` | MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — 关闭 B3）。 | 2026-07-23（73天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/mcp/rate_limiter.py` | MCP Gateway 同步速率限制器（MOD-INF-013 §12 Step 3）。 | 2026-08-21（44天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/mcp/resource_provider.py` | MCP Resource 提供者（MOD-INF-013 Phase 6 — 关闭 B2/B41）。 | 2026-07-23（73天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/mcp_server.py` | AssetInventory MCP Server 兼容 shim — MOD-INF-026 蓝图 §21 | 2026-09-06（28天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/shared/events/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/shared/events/dlq_bridge.py` | CT-DLQ-001: DeadLetterQueue -> System Event Bus integration bridge. | 2026-09-05（29天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/shared/events/event_bus_upgrade.py` | EventBus Upgrade（事件版本化迁移）— backward-compat re-export shim。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/shared/events/event_schemas.py` | event_schemas.py —— Observer 事件体 Pydantic V2 Schema（盲点 B6/B10 修复） | 2026-08-19（46天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/shared/events/upgrade_strategy.py` | EventBus 升级策略引擎 — backward-compat re-export shim。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/bm25_index.py` | BM25Index — MOD-INF-011 稀疏检索组件 | 2026-08-21（44天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/cache_layer.py` | （无文档头，按文件名语义：cache_layer） | 2026-08-17（48天） | in=0/out=0·wired_dynamic | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/chunk_strategy_router.py` | ChunkStrategyRouter — MOD-INF-011 分块策略调度 | 2026-07-23（73天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/collection_schemas.py` | （无文档头，按文件名语义：collection_schemas） | 2026-09-05（29天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/in_memory_memory_backend.py` | DegradedVMSBackend — MOD-INF-011 降级兜底 | 2026-07-23（73天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/interface.py` | VMS — Vector Memory Service 接口基类 | 2026-07-23（73天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/ollama_embedding.py` | （无文档头，按文件名语义：ollama_embedding） | 2026-08-17（48天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/integration/vector_memory/vms_errors.py` | （无文档头，按文件名语义：vms_errors） | 2026-07-23（73天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
