---
blueprint_id: MOD-INF-070
module_name: signal_engine_process_spec
domain: D_INFRA_RUNTIME
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_INFRA_RUNTIME
path: src/zephyr/infrastructure/signal_engine_process_spec.py
granularity: file
---

# MOD-INF-070 signal_engine_process_spec 蓝图（P2 信号引擎进程规格 SSOT）

> **module_id**: MOD-INF-070 | **域**: D_INFRA_RUNTIME | **优先级**: P1
> **来源**: B14-04523（AUD-DRAFT-001-DIGEST P1 波 W-P1-17，CAND-H1FS-006，A9 运维架构 §1.1.1/§1.1.3）
> 代码：`src/zephyr/infrastructure/signal_engine_process_spec.py`

## 0. 定位

P2 signal_engine 独立进程规格**唯一真源**（SSOT）——与 P3 规格 MOD-INF-064
同族的 P2 补件。TSV 现状注记：盘中主循环（intraday_main）有但独立信号进程
未拆；本模块只收口 P2 进程规格**声明**（亲和/预算/心跳/降级语义/产出通道），
进程拆分与系统级设置（SetProcessAffinityMask 等）属 Owner 窗口，AI 不执行。

查重分工（W-P1-17 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| trading_core_process_spec | MOD-INF-064 | P3 进程规格 SSOT（四职责/核8-11/8GB/HC-01） | 本模块=P2 同族规格，复用其 frozen dataclass+Fail-Closed 模式 |
| process_supervisor | MOD-INF-066 | P1~P5 启停编排/崩溃策略/注册表 | P2 注册行已在其内，本模块为 P2 规格深件（职责四元组/产出通道/降级语义），双向对齐校验不重复声明 |
| hot_plane_budget | MOD-INF-065 | Hot <10ms 预算（2/3/5ms） | 本模块声明 Warm 档进程归属，预算面归 MOD-INF-071 |
| redis_state_layer_ssot | MOD-INF-063 | hb/signal/market_state 命名空间与 TTL 规则 | 心跳 TTL 计算复用其 dynamic_ttl，不重造 |

不做什么：不 spawn 进程（通道归 MOD-INF-016 ProcessLifecycleGateway）、不执行
核亲和/内存硬限（Owner 窗口）、不重建 P1~P5 编排（MOD-INF-066 职责）、不重造
心跳 TTL 规则（复用 MOD-INF-063 dynamic_ttl）。

## 1. 规格真源（A9 §1.1.1 进程矩阵 P2 行 + §1.1.3 健康检查 P2 行）

- process_id=P2 / process_name=signal_engine / priority=20（数值越小优先级越高）。
- 四职责：因子计算 / 信号生成 / 策略路由 / 市场状态判定。
- CPU 亲和核 4-7；内存预算 16GB 峰值上限。
- 心跳 `hb:signal_engine` 间隔 5s / 超时 30s（TTL=超时+30s 缓冲，规则复用
  MOD-INF-063 dynamic_ttl）；探针=信号产出计数器。
- 崩溃策略 core_degrade：**交易时段告警+P3 使用缓存信号降级**；非交易时段
  自动重启（3 次上限终止重启循环，上限真源归 MOD-INF-066）。
- 产出通道（§1.2.1/§2.4.2 规则2）：`signal:*` Pub/Sub（TTL 60s，Sorted Set
  信号队列）+ `market:state:current`（String）单向传 Hot，P3 订阅消费。

## 2. 判定规则（确定性，纯声明）

1. Fail-Closed：职责空/心跳间隔≥超时/核号重复或越界/内存非正/重启档非法/
   信号 TTL 非正 → SignalEngineSpecError。
2. `heartbeat_key()` = `hb:signal_engine`；`heartbeat_ttl_seconds()` 复用
   MOD-INF-063 dynamic_ttl（不重造规则）。
3. `check_supervisor_alignment()`：与 MOD-INF-066 FIVE_PROCESS_REGISTRY P2 行
   双向对账（优先级/核/内存/心跳/职责），漂移即 Fail-Closed（防两真源）。
4. `render_process_spec_declaration()` 产出配置就绪件 dict（**仅声明不执行**）。

## 3. 接口

```python
@dataclass(frozen=True)
class SignalEngineProcessSpec: ...   # 字段=§1 真源
SIGNAL_ENGINE_SPEC: Final[SignalEngineProcessSpec]
class SignalEngineSpecError(RuntimeError): ...
heartbeat_key() -> str
heartbeat_ttl_seconds() -> int
check_supervisor_alignment() -> SignalEngineProcessSpec
render_process_spec_declaration(spec=...) -> dict
```

## 4. 依赖前置

- MOD-INF-063 redis_state_layer_ssot（hb/signal/market_state 命名空间 + dynamic_ttl）。
- MOD-INF-064 trading_core_process_spec（P3 同族规格模式 + P3 缓存信号降级语义对端）。
- MOD-INF-066 process_supervisor（P2 注册行对账，不重复声明）。

## 5. 验收标准

- 单测全绿（规格真源值/畸形 Fail-Closed/心跳键与 TTL/supervisor 对账/就绪件
  仅声明）；相关域集成零回归。
