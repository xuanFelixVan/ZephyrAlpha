---
module_id: MOD-MKT-003
title: "行情数据连接器蓝图 — 连接生命周期+实时订阅框架"
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

# MOD-MKT-003 Connectors — 行情数据连接器 蓝图

> **module_id**: MOD-MKT-003 | **域**: D_MKT_DATA | **层**: L01 基础平台
> **优先级**: P1 | **成熟度**: production | **对标能力**: 行情连接器
> **SSoT**: depgraph MOD-MKT-003 | **设计真源**: 23_d_mkt_data.md

## 1. 定位

行情数据连接器——MarketDataVendor 抽象基类的连接管理层扩展。在 vendor_base
定义的数据获取接口之上, 增加连接生命周期管理(connect/disconnect/reconnect)
和实时行情订阅(subscribe/unsubscribe/on_tick)能力, 供具体厂商连接器
(tushare/akshare/CTP 等)继承实现。

ConnectorManager 统一管理多个连接器的生命周期(批量连接/断开/健康检查)。

属 A 类基础设施(连接框架), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"管理数据源连接 + 推送实时行情"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 连接配置(endpoint/credentials) | ConnectorConfig |
| 输入 | 订阅请求(symbol + callback) | subscribe() |
| 输出 | 连接状态(ConnectionState) | — |
| 输出 | 实时行情回调(TickData) | on_tick callback |
| 输出 | 日K数据(NormalizedMarketData) | 继承自 vendor_base |

## 3. 核心规则

### 3.1 连接状态机 (ConnectionState)

```
DISCONNECTED --connect()--> CONNECTING --on_connected--> CONNECTED
CONNECTED --disconnect()--> DISCONNECTING --on_disconnected--> DISCONNECTED
CONNECTED --on_error--> RECONNECTING --on_connected--> CONNECTED
RECONNECTING --reconnect_failed--> ERROR
```

非法状态转换抛出 ConnectorError。

### 3.2 实时订阅

```
subscribe(symbol, callback)  # 注册回调
unsubscribe(symbol)           # 注销回调
on_tick(tick)                 # 连接器内部收到行情时调用, 分发给注册的回调
```

- 同一 symbol 可注册多个 callback, 收到 tick 时全部调用
- callback 异常不影响其他 callback 和连接(捕获+日志)

### 3.3 连接生命周期

```
connect()     # 子类实现 _do_connect(), 基类管理状态转换
disconnect()  # 子类实现 _do_disconnect(), 基类管理状态转换
reconnect()   # disconnect() + connect()
```

## 4. 关键不变量 (INVARIANTS)

- ConnectionState/ConnectorConfig/TickData 为 frozen dataclass 或 Enum
- MarketDataConnector 为 ABC 不可直接实例化(继承自 MarketDataVendor ABC)
- 状态转换加 Lock 保护, 线程安全
- 订阅回调注册表加 Lock 保护, 线程安全
- callback 异常被捕获记录, 不传播(不影响其他回调/连接)
- CONNECTED 状态才能 subscribe/fetch; 否则 raise ConnectorError

## 5. 错误契约

- `ConnectorError` (ZA-MKT-0003): 连接操作异常(非法状态转换/未连接/连接失败)

## 6. 数据模型

```python
class ConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    RECONNECTING = "reconnecting"
    ERROR = "error"

@dataclass(frozen=True)
class ConnectorConfig:
    endpoint: str
    vendor_id: str
    timeout_ms: int = 5000
    reconnect_max_retries: int = 3
    params: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TickData:
    symbol: str
    price: Decimal
    volume: Decimal
    timestamp: datetime
    bid: Decimal | None = None
    ask: Decimal | None = None
```

## 7. API

```python
class MarketDataConnector(MarketDataVendor):
    def __init__(self, config: ConnectorConfig) -> None: ...
    @property
    def connection_state(self) -> ConnectionState: ...
    def connect(self) -> None: ...        # 管理 _do_connect()
    def disconnect(self) -> None: ...     # 管理 _do_disconnect()
    def reconnect(self) -> None: ...
    def subscribe(self, symbol: str, callback: TickCallback) -> None: ...
    def unsubscribe(self, symbol: str, callback: TickCallback | None = None) -> int: ...
    def on_tick(self, tick: TickData) -> None: ...
    # 子类实现:
    def _do_connect(self) -> None: ...
    def _do_disconnect(self) -> None: ...

class ConnectorManager:
    def __init__(self) -> None: ...
    def register(self, connector: MarketDataConnector) -> None: ...
    def connect_all(self) -> dict[str, bool]: ...
    def disconnect_all(self) -> dict[str, bool]: ...
    def health_check_all(self) -> dict[str, bool]: ...
    def get(self, connector_id: str) -> MarketDataConnector | None: ...
    @property
    def count(self) -> int: ...
```

## 8. 依赖

- `zephyr.market_data.vendor_base` (MarketDataVendor, VendorStatus) — import
- `zephyr.shared.contracts.market_data` (NormalizedMarketData)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D_MKT_DATA autoload, D_EX_SOR (运行时行情)
- 设计真源: 23_d_mkt_data.md

## 9. 测试

- `tests/market_data/connectors/test_connector_base.py`
- `tests/market_data/connectors/test_connector_manager.py`
- 覆盖: 状态机转换(合法/非法)、订阅/退订/回调分发、callback异常隔离、
  连接生命周期、ConnectorManager 批量操作、线程安全

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-003` 的 6 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-003` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-003 | MOD-MKT-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 6 文件 | N/A | — |

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
| `src/zephyr/market_data/connectors/__init__.py` | ✅ 已实现 | |
| `src/zephyr/market_data/connectors/base.py` | ✅ 已实现 | |
| `src/zephyr/market_data/connectors/manager.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/connectors/__init__.py` | ⚠️ 骨架 | |
| `tests/market_data/connectors/test_connector_base.py` | ✅ 已实现 | |
| `tests/market_data/connectors/test_connector_manager.py` | ✅ 已实现 | |

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


