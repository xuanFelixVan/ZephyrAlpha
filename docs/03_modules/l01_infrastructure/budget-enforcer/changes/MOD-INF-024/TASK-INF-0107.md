---
task_id: "TASK-INF-0107"
module_id: "MOD-INF-024"
title: "Semantic Cache — Prompt/Tool/Embedding 三层语义缓存（§2.6 + D-024-07）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.6"
estimated_tokens: 3500
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\semantic_cache.py"
acceptance_criteria:
  - "AC-01: 三层缓存架构完整：layer_1_prompt_cache (exact_hash, TTL 3600s), layer_2_tool_cache (param_hash, TTL 300s), layer_3_embedding_cache (content_hash, TTL 86400s)"
  - "AC-02: 后端使用 ChromaDB——复用已有向量库，零新增依赖"
  - "AC-03: prompt_cache hit 后零新增 token 消耗——直接返回缓存的 completion"
  - "AC-04: layer_1 hit_ratio_target >= 0.40"
  - "AC-05: layer_2 hit_ratio_target >= 0.30"
  - "AC-06: AES-256 at rest 加密——敏感数据（含 API response）在缓存中加密存储"
  - "AC-07: 可观测 metrics：cache_hit_rate, cache_saved_tokens, cache_saved_cost——每次 hit 写入 audit trail"
  - "AC-08: Cache 键过期机制——TTL 到期后自动标记 stale，下次查询时惰性删除"
  - "AC-09: 缓存预热——Session 启动时预加载常用 prompt cache"
  - "AC-10: 提供 invalidate(pattern) 接口——支持按 pattern 批量失效缓存"
  - "AC-11: 缓存大小上限——默认最大占用 512MB 磁盘；超过上限 LRU 逐出"
rollback_instructions: "删除 semantic_cache.py，移除调用点 import。系统退化为零缓存模式——每次 API 调用全新请求，token 消耗增加 30-50%（缓存降本效果估算的逆运算）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L423-L454 (§2.6 Semantic Cache)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [semantic-cache, chromadb, prompt-cache, tool-cache, embedding-cache, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0107: Semantic Cache — 三层语义缓存

## 1. 任务目标

实现三层语义缓存——Prompt Cache（精确哈希）、Tool Cache（参数哈希）、Embedding Cache（内容哈希）。缓存是成本最低的性能优化——hit 后零新增 token 消耗。对标 Anthropic cache-aware token management 实践。

## 2. 背景

蓝图 §2.6（决策 D-024-07）：Agent 成本控制实战表明缓存降本 30-50%。使用 ChromaDB 复用已有向量库，避免新增依赖。三层各独立 TTL 和加密策略。

## 3. 实施步骤

### Step 1: 类型定义
```python
from enum import Enum

class CacheLayer(Enum):
    PROMPT = "prompt"     # hash(system_prompt + context_hash)
    TOOL = "tool"         # hash(tool_name + params)
    EMBEDDING = "embedding"  # hash(chunk_content)

@dataclass
class CacheEntry:
    layer: CacheLayer
    key_hash: str
    value: bytes             # AES-256 encrypted
    ttl: float
    created_at: float
    hit_count: int
    tokens_saved: int
```

### Step 2: SemanticCache 核心
```python
class SemanticCache:
    def __init__(self, backend: ChromaDB, config: CacheConfig):
        self.backend = backend
        self.config = config
        self._encryptor = AES256Encryptor()

    def get(self, layer: CacheLayer, key: str) -> bytes | None:
        key_hash = self._hash(layer, key)
        entry = self.backend.get(key_hash)
        if entry and not self._is_expired(entry):
            entry.hit_count += 1
            self._record_hit(layer, entry.tokens_saved)
            return self._encryptor.decrypt(entry.value)
        return None

    def set(self, layer: CacheLayer, key: str, value: bytes,
            tokens_saved: int):
        key_hash = self._hash(layer, key)
        encrypted = self._encryptor.encrypt(value)
        entry = CacheEntry(layer, key_hash, encrypted,
                          self._ttl_for(layer), time.monotonic(),
                          0, tokens_saved)
        self.backend.upsert(key_hash, entry)

    def _hash(self, layer: CacheLayer, key: str) -> str:
        return hashlib.sha256(f"{layer.value}:{key}".encode()).hexdigest()
```

### Step 4: Init Methods
- ChromaDB Collection 初始化：`semantic_cache_{layer.value}`
- 索引维度 = 768（与 embedding 模型一致）
- LRU eviction policy 基于 ChromaDB metadata.created_at

### Step 5: Observability
- `get_stats()` → CacheStats(hit_rate, tokens_saved, cost_saved, layer_breakdown)
- `_record_hit()` → 写入 metrics + audit trail

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/semantic_cache.py` | 新建 |
