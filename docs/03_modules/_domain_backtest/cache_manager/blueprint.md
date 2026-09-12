---
module_id: MOD-BT-020
title: "回测缓存管理器蓝图 — 结果缓存与复用"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-020 Cache Manager — 回测缓存管理器 蓝图

> **module_id**: MOD-BT-020 | **域**: D_BACKTEST | **层**: L_BACKTEST 回测引擎层
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-020 | **设计真源**: D:\临时工作区\依赖图\32-D-BACKTEST-回测引擎域.md §1 BT-20

## 1. 定位

回测缓存管理器——对回测结果进行内存缓存与复用, 避免相同参数重复回测。
基于策略ID+参数哈希+日期范围计算缓存键, LRU淘汰策略管理缓存容量,
支持按键/按策略/全量失效, 提供命中率统计。

属 A 类基础设施(纯内存管理+哈希计算, 逻辑明确), 容量为 C 类可调参数。
纯工具模块, 不依赖外部数据库, 缓存生命周期由调用方管理。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | BacktestResult (回测结果) + 缓存参数 (strategy_id, params, date_range) | 来自 BT-02/09 回测引擎 |
| 输出 | CacheResult (命中→缓存结果 / 未命中→None) + CacheStats (命中率统计) | 供 BT-21 param_analyzer / BT-24 result_comparator 消费 |

## 3. 核心机制

### 3.1 缓存键计算

```
cache_key = CacheKey(
    strategy_id: str,
    params_hash: str,       # SHA-256(json(params))[:16]
    start_date: str,
    end_date: str,
    benchmark_symbol: str | None,
)
```

- 相同 strategy_id + 相同参数 + 相同日期范围 → 相同 cache_key → 命中缓存
- 参数序列化使用 `json.dumps(params, sort_keys=True, default=str)` 保证顺序无关

### 3.2 LRU 淘汰

- 使用 `OrderedDict` 实现 LRU: get 时 move_to_end, put 时弹出最旧条目
- 达到 `max_entries` 时淘汰最久未访问的条目
- 淘汰计数记入 `CacheStats.evictions`

### 3.3 失效策略

| 操作 | 范围 | 返回 |
|------|------|------|
| `invalidate(key)` | 单个缓存键 | bool (是否存在并删除) |
| `invalidate_strategy(strategy_id)` | 该策略所有缓存 | int (删除条数) |
| `clear()` | 全部缓存 | int (删除条数) |

### 3.4 统计

```
CacheStats:
    hits: int           # 命中次数
    misses: int         # 未命中次数
    evictions: int      # LRU 淘汰次数
    total_entries: int  # 当前缓存条目数
    hit_rate: float     # 命中率 = hits / (hits + misses)
```

## 4. 关键不变量 (INVARIANTS)

- CacheKey / CacheConfig / CacheStats / CacheEntry 为 frozen dataclass (不可变)
- 缓存值不修改 (存入即冻结快照, 调用方不应修改返回的对象)
- 空 params → params_hash = SHA-256("null")[:16] (合法, 不报错)
- max_entries <= 0 时 raise CacheError
- get 未命中返回 None (不报错)
- 线程安全: 使用 threading.Lock 保护内部 OrderedDict

## 5. 错误契约

- `CacheError` (ZA-BT-0020): 配置非法(max_entries<=0) / 缓存键计算失败

## 6. 数据模型

```python
@dataclass(frozen=True)
class CacheConfig:
    max_entries: int = 256
    max_size_bytes: int = 0  # 0=不限大小

@dataclass(frozen=True)
class CacheKey:
    strategy_id: str
    params_hash: str
    start_date: str
    end_date: str
    benchmark_symbol: str | None = None

@dataclass(frozen=True)
class CacheEntry:
    key: CacheKey
    value: Any
    created_at: str
    hit_count: int = 0

@dataclass(frozen=True)
class CacheStats:
    hits: int
    misses: int
    evictions: int
    total_entries: int
```

## 7. API

```python
class BacktestCacheManager:
    def __init__(self, config: CacheConfig | None = None) -> None: ...
    def compute_key(
        self, strategy_id: str, params: dict,
        start_date: str, end_date: str,
        benchmark_symbol: str | None = None,
    ) -> CacheKey: ...
    def get(self, key: CacheKey) -> Any | None: ...
    def put(self, key: CacheKey, value: Any) -> bool: ...
    def invalidate(self, key: CacheKey) -> bool: ...
    def invalidate_strategy(self, strategy_id: str) -> int: ...
    def clear(self) -> int: ...
    def stats(self) -> CacheStats: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 标准库: `hashlib`, `json`, `threading`, `collections.OrderedDict`
- 消费者: MOD-BT-021 (param_analyzer), MOD-BT-024 (result_comparator)

## 9. 测试

- `tests/backtest/test_cache_manager.py`
- 覆盖: 基本put/get、缓存命中/未命中、LRU淘汰、按键失效、按策略失效、全量清空、
  统计正确性、缓存键计算(相同参数→相同键/不同参数→不同键)、
  线程安全、空params、配置校验、frozen不可变

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-BT-020`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-BT-020` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-BT-020` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-BT-020 | MOD-BT-020 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/backtest/test_cache_manager.py` | ✅ 已实现 | |

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


