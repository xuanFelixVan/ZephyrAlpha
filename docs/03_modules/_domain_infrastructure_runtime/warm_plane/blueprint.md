---
blueprint_id: MOD-INF-071
module_name: warm_plane_budget
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
path: src/zephyr/infrastructure/warm_plane_budget.py
granularity: file
---

# MOD-INF-071 warm_plane_budget 蓝图（Warm 平面 10ms~1s 预算与 11 态路由 SSOT）

> **module_id**: MOD-INF-071 | **域**: D_INFRA_RUNTIME | **优先级**: P1
> **来源**: B14-04547（AUD-DRAFT-001-DIGEST P1 波 W-P1-17，CAND-H1FS-007，A9 运维架构 §2.3）
> 代码：`src/zephyr/infrastructure/warm_plane_budget.py`

## 0. 定位

Warm 平面（10ms~1s）时延预算与 11 种市场状态路由表**唯一真源**——与 Hot 档
MOD-INF-065 同族衔接的 Warm 档补件。TSV 现状注记：平面标记契约
（runtime_plane_tag）有，Warm 1s 预算分解与市场状态路由表未落地；本模块收口
A9 §2.3 为可校验真源。

查重分工（W-P1-17 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| hot_plane_budget | MOD-INF-065 | Hot <10ms 预算 2/3/5ms+资源独占 | 本模块=Warm 10ms~1s 档，复用其阶段预算+Fail-Closed 模式 |
| runtime_plane_tag | MOD-INF-002 | Hot/Warm/Cold 平面枚举契约（10ms~1s 定义） | 本模块落地 Warm 档预算与路由，枚举不重定义 |
| warm_hot_gate | MOD-INF-002 | Warm→Hot 阻断门（验证通过才进 Hot） | 门禁判定不管预算/路由表 |
| signal_engine_process_spec | MOD-INF-070 | P2 进程规格（核4-7/16GB/hb 5s/30s） | Warm 平面进程归属与产出通道声明对齐其规格 |

不做什么：不执行核绑定/资源隔离（Owner 窗口）、不重定义平面枚举
（MOD-INF-002 契约）、不管 Cold 平面（>1s 档，A9 §2.4 另件）。

## 1. 预算真源（A9 §2.3.1）

- 增量因子计算 200ms（累计 200ms，NumPy/Pandas 向量化 + GPU 批量加速）。
- 信号生成+聚合 300ms（累计 500ms，多策略并行 + 进程内线程池）。
- 策略路由+仓位裁决 500ms（累计 1000ms，市场状态驱动路由 + Redis 缓存市场状态）。
- 端到端 1s（P95）；**超 1s 信号视为过期信号 → P3 使用缓存信号替代**
  （04-D-SIGNAL §8.1 硬约束），判定动作=stale_signal_use_cache（纯数据判定，
  执行归 P3/P4）。

## 2. 路由真源（A9 §2.3.2，11 态 7 行）

| 市场状态 | 路由策略 | 信号权重 | 仓位上限 |
|---|---|---|---|
| ①②趋势向上 | 动量策略优先 | 动量0.6/价值0.2/防御0.2 | 80% |
| ③高波动 | 做T策略激活 | 动量0.3/做T0.4/防御0.3 | 60% |
| ④⑤震荡 | 均值回归优先 | 均值0.5/价值0.3/防御0.2 | 50% |
| ⑥压缩突破 | 突破策略待命 | 动量0.4/均值0.3/突破0.3 | 40%→70% |
| ⑦⑧⑨趋势向下 | 防御策略主导 | 防御0.6/价值0.3/动量0.1 | 30%→10% |
| ⑩事件驱动 | 事件策略激活 | 事件0.5/动量0.3/防御0.2 | 按事件调整（None） |
| ⑪板块轮动 | 轮动策略激活 | 轮动0.5/动量0.3/价值0.2 | 70% |

- 每行信号权重 Σ=1.0（Fail-Closed 校验）；11 个状态码（①~⑪）全覆盖且唯一映射。
- 产出单向通道（§2.4.2 规则2）：Warm→Hot 仅经 Redis `signal:*` Pub/Sub +
  `market:state` 传递，P3 订阅；Cold→Hot 禁止直连（本模块只声明 Warm 侧出口）。

## 3. 判定规则（确定性，纯函数）

1. Fail-Closed：未知阶段/负时延/缺阶段 → WarmPlaneBudgetError；未知市场状态码/
   权重Σ≠1/仓位上限越界 → WarmPlaneRoutingError。
2. `check_budget(measured)`：任一阶段超限或总和 >1000ms → within_budget=False，
   动作=stale_signal_use_cache。
3. `get_routing(state_code)`：①~⑪ → 路由行（策略/权重/仓位上限区间）。
4. `render_warm_plane_declaration()` 配置就绪件 dict（**仅声明不执行**）。

## 4. 依赖前置

- MOD-INF-065 hot_plane_budget（Hot 档衔接同族模式）。
- MOD-INF-063 redis_state_layer_ssot（signal:*/market:state 命名空间真源）。
- MOD-INF-070 signal_engine_process_spec（P2 进程归属与产出通道对齐）。
- 契约对齐：runtime_plane_tag（MOD-INF-002，WARM 平面枚举/10ms~1s 档定义）。

## 5. 验收标准

- 单测全绿（预算分解真源值/11 态路由表与权重Σ=1/未知态 Fail-Closed/超限过期
  信号判定/就绪件仅声明）；相关域集成零回归。
