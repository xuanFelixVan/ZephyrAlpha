---
blueprint_id: MOD-INF-073
module_name: external_system_connector
domain: D_INTEGRATION
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_INTEGRATION
path: src/zephyr/integration/external_system_connector.py
granularity: file
---

# MOD-INF-073 external_system_connector 蓝图（D-INT-10 统一外部系统连接器契约）

> **module_id**: MOD-INF-073 | **域**: D_INTEGRATION | **优先级**: P1
> **来源**: B1-00326（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-BACL-003，跨域元文档 §功能域模块·D-INTEGRATION）
> 代码：`src/zephyr/integration/external_system_connector.py`

## 0. 定位

券商（miniQMT 通道）与数据源的**统一外部连接器契约层**：能力声明
（行情/交易/另类）+ 健康检查 + 配额管理 + source_circuit_breaker 挂接
+ 统一登记注册表。

查重分工（W-P1-25 铁律③探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| vendor_registry | MOD-MKT-001 | **行情域** vendor 注册表（vendor_id/capabilities/fetch_daily_kline/health_check） | 仅行情数据源；本件=跨域统一契约（行情+交易+另类），不替代行情域内注册 |
| failover_coordinator | MOD-INF-042 | 三源优先级+质量分**选源切换**协调（行情源故障转移） | 运行时选源决策；本件=连接器**登记与契约**（谁接入/什么能力/配额多少），选源仍归 failover |
| source_circuit_breaker | MOD-L00-004 | 单数据源熔断器（失败计数/半开探测） | 本件**挂接复用**（每连接器一熔断器实例，DI 工厂注入），不重建熔断逻辑 |
| broker_api_connector | EXT-001（ex_sor/api） | 券商 API **执行通道**（下单/撤单/查询） | 执行面；本件=契约登记面（声明该通道能力/配额/健康），不直接下单 |
| settlement 系 adapter | D_TRADING | 券商结算适配 | 分置在案（TSV 原文），本件只做统一登记不搬移 |

TSV 裁定原文："行情vendor注册与券商结算adapter分置，缺统一外部连接器
契约（能力声明/健康检查/配额）"——施工形态=纯内存契约+注册表，真实
miniQMT/数据源绑定归运行时装配批（health_probe/quota 全 DI）。

## 1. 规则（确定性，纯内存）

- **能力声明** ConnectorCapability：kind（market_data|trading|alt_data）
  + operations（frozenset[str]，如 fetch_daily_kline/place_order/
  fetch_news）+ vendor 标识。
- **健康检查**：`health_check(connector_id)`——经注入 `health_probe`
  回调执行（默认未配置→UNKNOWN）；结果 HealthStatus
  （HEALTHY/DEGRADED/UNHEALTHY/UNKNOWN）+ 最近检查时间（注入时钟）。
- **配额管理** QuotaPolicy：rate_per_sec（每秒调用上限）+ daily_cap
  （日累计上限，None=不限）；`acquire(connector_id, n=1)` 令牌桶语义
  纯内存计数（注入时钟分桶），超限 → Fail-Closed 抛 QuotaExceeded。
- **熔断挂接**：每连接器登记时经 `breaker_factory` 注入创建/复用
  source_circuit_breaker 实例；`report_result(connector_id, ok)` 透传
  熔断器；熔断 OPEN → `is_callable=False`。
- **统一登记** ConnectorRegistry：connector_id 唯一（重复注册抛
  ConnectorAlreadyRegisteredError）；按 kind/capability 查询；
  `callable_connectors(kind)`=健康非 UNHEALTHY 且熔断非 OPEN 且配额
  未触顶的可用列表（确定性排序 connector_id）。
- Fail-Closed：空 connector_id/未知连接器操作/非法配额参数 →
  ExternalConnectorError。

## 2. 接口

```python
class ConnectorKind(str, Enum): MARKET_DATA/TRADING/ALT_DATA
class HealthStatus(str, Enum): HEALTHY/DEGRADED/UNHEALTHY/UNKNOWN
@dataclass(frozen=True) class ConnectorCapability: kind/operations/vendor
@dataclass(frozen=True) class QuotaPolicy: rate_per_sec/daily_cap
@dataclass(frozen=True) class ConnectorProfile: connector_id/capability/quota/health/registered_at

class ExternalSystemConnectorRegistry:
    __init__(*, clock=None, health_probe=None, breaker_factory=None)
    register(connector_id, capability, quota=None) -> ConnectorProfile
    unregister(connector_id) -> None
    health_check(connector_id) -> HealthStatus
    acquire(connector_id, n=1) -> None
    report_result(connector_id, ok: bool) -> None
    is_callable(connector_id) -> bool
    callable_connectors(kind=None) -> list[ConnectorProfile]
ExternalConnectorError / ConnectorAlreadyRegisteredError / ConnectorNotFoundError / QuotaExceeded
# 占位错误码 ZA-INT-UNREGISTERED-EXT-CONNECTOR（纪律⑦）
```

## 3. 依赖

- 设计边：`source_circuit_breaker`（node 10624653，熔断挂接复用）、
  `vendor_registry`（node 10626429，行情域内注册分工）、
  `failover_coordinator`（node 10626306，登记 vs 选源分工）。
- 运行时装配（非本件）：miniQMT 通道/各数据源 connector 实例登记；
  health_probe 绑定真实 ping/快照接口；配额参数入 config。

## 4. 测试

`tests/integration/test_external_system_connector.py`（[TTL] permanent）。
