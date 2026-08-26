---
module_id: MOD-MKT-006
title: "原始数据缓存蓝图 — 行情原始数据 LRU+TTL 缓存"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L01_foundation
layer_name: foundation
functional_domain: mkt_data
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-MKT-006 Raw Data Cache — 原始数据缓存 蓝图

> **module_id**: MOD-MKT-006 | **域**: D_MKT_DATA | **层**: L01 基础平台
> **优先级**: P1 | **成熟度**: production | **对标能力**: 原始数据缓存
> **SSoT**: depgraph MOD-MKT-006 | **设计真源**: 23_d_mkt_data.md

## 1. 定位

原始数据缓存——行情数据标准化前的原始数据缓存层。从数据源拉取的原始行情
(FetchResult rows / vendor 原始响应)在标准化为 NormalizedMarketData 之前,
先写入缓存, 支持重放/回放/故障恢复/审计核对。

属 A 类基础设施(内存缓存, LRU+TTL 淘汰), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"把原始数据暂存起来以备重放"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | raw_payload (原始数据, bytes/str/结构化) | 来自 D_DATA provider_base FetchResult |
| 输入 | symbol + date (缓存键) | — |
| 输入 | source_vendor (数据来源) | vendor_id |
| 输出 | CacheEntry (缓存条目, 含哈希指纹) | — |
| 输出 | 命中/未命中 + 范围查询结果 | — |

## 3. 核心规则

### 3.1 缓存键 (CacheKey)

```
key = (symbol, date_str)  # 如 ("600000.SH", "2026-08-01")
```

同一 symbol + date + source 视为同一缓存项(覆盖更新)。

### 3.2 淘汰策略 (EvictionPolicy)

- **LRU**: 容量达 max_size 时淘汰最久未访问的条目
- **TTL**: 条目超过 ttl_seconds 自动过期(惰性淘汰 + 主动 evict)
- 默认策略: LRU + TTL 双重淘汰

### 3.3 内容哈希 (content_hash)

```
content_hash = SHA-256(raw_payload)[:16]  # 16字符短哈希
```

用于校验缓存数据完整性, 检测数据被外部篡改。

### 3.4 范围查询

```
query(symbol, start_date, end_date) -> list[CacheEntry]
```

返回 [start_date, end_date] 区间内该 symbol 的所有有效缓存条目(跳过过期)。

## 4. 关键不变量 (INVARIANTS)

- CacheEntry / CacheConfig / CacheKey / CacheStats 为 frozen dataclass (不可变)
- raw_payload 写入后不可修改 (entry 不可变, 更新=覆盖写入新 entry)
- 所有读写操作加 threading.Lock 保护, 线程安全
- content_hash 在写入时计算, 读取时不重算 (信任写入时的哈希)
- 容量超限时按 LRU 淘汰, 不抛异常
- TTL 过期的条目在读取时返回 None (视为未命中)

## 5. 错误契约

- `CacheError` (ZA-MKT-0006): 缓存操作异常(写入空 symbol / 非法日期)

## 6. 数据模型

```python
class EvictionPolicy(str, Enum):
    LRU = "lru"
    TTL = "ttl"
    LRU_TTL = "lru_ttl"  # 默认: 双重淘汰

@dataclass(frozen=True)
class CacheKey:
    symbol: str
    date: str  # YYYY-MM-DD

@dataclass(frozen=True)
class CacheEntry:
    key: CacheKey
    source_vendor: str
    raw_payload: bytes
    content_hash: str
    fetched_at: datetime
    payload_size: int
    expires_at: datetime | None  # None=不过期

@dataclass(frozen=True)
class CacheConfig:
    max_size: int = 10000           # 最大条目数
    ttl_seconds: int | None = 86400 # TTL(秒), None=不过期
    policy: EvictionPolicy = EvictionPolicy.LRU_TTL

@dataclass(frozen=True)
class CacheStats:
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    eviction_count: int
    @property
    def hit_rate(self) -> float: ...
```

## 7. API

```python
class RawDataCache:
    def __init__(self, config: CacheConfig | None = None) -> None: ...

    def put(
        self, symbol: str, date: str, raw_payload: bytes,
        source_vendor: str, ttl_seconds: int | None = None,
    ) -> CacheEntry: ...

    def get(self, symbol: str, date: str) -> CacheEntry | None: ...

    def query(self, symbol: str, start_date: str, end_date: str) -> list[CacheEntry]: ...

    def exists(self, symbol: str, date: str) -> bool: ...

    def evict_expired(self) -> int: ...

    def clear(self) -> int: ...

    @property
    def stats(self) -> CacheStats: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 数据来源: D_DATA provider_base (FetchResult rows) — data 依赖
- 消费者: D_MKT_DATA normalized_market_data_producer (重放/恢复)
- 设计真源: 23_d_mkt_data.md

## 9. 测试

- `tests/market_data/raw_data_cache/test_raw_data_cache.py`
- 覆盖: put/get 基本读写、LRU 淘汰、TTL 过期、范围查询、
  哈希校验、线程安全、统计信息、边界值(空 symbol 拒绝/容量超限淘汰)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-006` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-006` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-006 | MOD-MKT-006 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/market_data/raw_data_cache/__init__.py` | ✅ 已实现 | |
| `src/zephyr/market_data/raw_data_cache/cache.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/raw_data_cache/__init__.py` | ⚠️ 骨架 | |
| `tests/market_data/raw_data_cache/test_raw_data_cache.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


