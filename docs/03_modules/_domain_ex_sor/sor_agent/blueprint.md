---
blueprint_id: MOD-XS-015
module_name: sor_agent
domain: D_EX_SOR
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
domain_id: D_EX_SOR
path: src/zephyr/ex_sor/core/sor_agent.py
granularity: file
---

# MOD-XS-015 sor_agent 蓝图（路由Agent（SOR））

> **module_id**: MOD-XS-015 | **域**: D_EX_SOR | **优先级**: P1
> **来源**: B11-02491（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-SOR-001，A7-Agent架构 §1.4）
> 代码：`src/zephyr/ex_sor/core/sor_agent.py`

## 0. 定位

SOR Agent 实体（A7 §1.4 族卡模式，与 MOD-AU-011 T0TraderAgent 同族）：
**Level 0 纯规则**（禁 LLM 调用写入门控）承载两技能——**智能路由**
（通道选择 / 盘口流动性评估）+ **拆单策略**（复用 order_splitter：
冰山 / TWAP / 量比拆单）；滑点实际 vs 预估回写反馈循环；**所有决策可回放**。

查重分工（W-P1-24 铁律⑤探查——**Agent 化是独立缺口**）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| optimal_order_router | MOD-XS-001 | 延迟/成交率/费用三维加权选券商（路由算法件） | 本件=Agent **实体**（族卡+技能编排+回放+反馈循环），路由评分算法自含轻量版（流动性维度并入），运行时亦可委托 MOD-XS-001（装配批） |
| order_splitter | MOD-EX-014 | TWAP/VWAP 拆单纯函数（门禁降级版） | 本件拆单技能经 splitter_fn 委托其 split_order，不重建拆单算法 |
| algo_execution_selector | MOD-XS-011 | 执行算法选择（TWAP/VWAP/POV 选取） | 算法选取件，非 Agent 实体 |
| slippage_analyzer | MOD-EX_SOR_EXT-001 | 滑点计算/归因/预测 | 本件滑点回写消费其口径，反馈记录经 feedback_sink 供其校准 |
| llm_agent_router | MOD-INT-AGENT-ROUTER | **LLM 任务→模型**路由（R1 已建） | **零交集**：彼=LLM 模型选择，此=订单通道路由（铁律⑤钉死） |
| smart_order_router | — | **不存在**（grep 全仓无此件） | SOR 族即 MOD-XS-001 等，Agent 化无既有实体 |

TSV 裁定原文："ex_sor 域与 order_splitter/t0_cost_model 已就位但 db 标记
design/planned，无 SOR Agent 实体（Level 0）承载智能路由与拆单两技能，滑点
控制闭环未 Agent 化"——施工形态=1 个新模块（Agent 实体）。

## 1. 规则（确定性，Level 0 纯规则）

- **族卡** AGENT_CARD：role="sor"，autonomyLevel="L0_rule_only"；
  capabilities=smart_routing（通道选择/流动性评估）+ order_splitting
  （拆单委托）；autonomyBoundaries.immutable 含「禁 LLM 调用」「SOR 不做
  风控判断（D-EX-SOR §6.1，归 EX-CORE Pre-Trade）」「本 Agent 无下单语义
  （执行委托券商通道装配批）」。
- **智能路由**：候选通道（broker_id + latency_ms + fill_rate + cost_bps +
  liquidity_score）四维加权评分（weights 配置注入，和=1.0 Fail-Closed）
  选最优；流动性评估=liquidity_score 低于 min_liquidity 的通道先行剔除
  （Fail-Closed 无候选 → SorAgentError）。
- **拆单技能**：splitter_fn 依赖注入（默认惰性委托
  zephyr.ex_core.order_splitter.split_order； iceberg/TWAP/量比口径由
  请求参数携带）；拆单失败透传 SorAgentError。
- **滑点回写反馈循环**：`record_fill_feedback(replay_id, actual_slippage_bps)`
  → 与决策时预估 expected_slippage_bps 配对，偏差入内部校准统计
  （per-broker bias 均值）+ feedback_sink 回调（装配批接
  slippage_analyzer/反馈回路）；未知 replay_id Fail-Closed。
- **决策可回放**：每次 decide 产 SorDecision（replay_id 单调递增）并落
  内部 replay_log（只读元组导出 replay_log()）；replay_sink 可选注入。
- **禁 LLM 门控**：构造期断言全部注入回调的 `__module__` 不含
  "llm"/"intelligence" 段（纯规则红线写入门控，非文档口号）。
- Fail-Closed：weights 和≠1.0 / 候选空 / 价格数量非正 / replay_id 未知 /
  LLM 回调注入 → SorAgentError。

## 2. 接口

```python
AGENT_CARD: dict（族卡，见 §1）
@dataclass(frozen=True) class BrokerCandidate: broker_id/latency_ms/fill_rate/cost_bps/liquidity_score
@dataclass(frozen=True) class SorRouteWeights: w_latency/w_fill_rate/w_cost/w_liquidity
@dataclass(frozen=True) class SorRequest: symbol/side/quantity/price/split_algo/volume_profile/expected_slippage_bps
@dataclass(frozen=True) class SorDecision: replay_id/broker_id/score/split_plan/estimated_cost_bps/rationale/decided_at
@dataclass(frozen=True) class SlippageFeedback: replay_id/broker_id/expected_bps/actual_bps/bias_bps

class SorAgent:  # splitter_fn/feedback_sink/replay_sink 注入
    decide(request, candidates, now_utc) -> SorDecision
    record_fill_feedback(replay_id, actual_slippage_bps) -> SlippageFeedback
    replay_log() -> tuple[SorDecision, ...]
    broker_bias(broker_id) -> float  # 滑点偏差校准统计（均值，无样本=0.0）
class SorAgentError(Exception): 占位 ZA-XS-UNREGISTERED-SOR-AGENT
```

## 3. 错误契约

- `SorAgentError`（未登记错误码-申请中，占位
  ZA-XS-UNREGISTERED-SOR-AGENT，建议顺延 ZA-XS-0015 见 W-P1-24 fragment）

## 4. 测试

- `tests/ex_sor/test_sor_agent.py`
- 覆盖：四维加权选优、低流动性剔除、无候选 Fail-Closed、拆单委托、
  滑点回写配对与 bias 统计、回放日志单调、禁 LLM 门控、weights 校验

## 5. 依赖

- 标准库 + `zephyr.ex_core.order_splitter`（惰性，splitter_fn 可注入替代）
- 下游（运行时装配，不 import）：MOD-XS-001 路由算法委托 / EX-CORE
  Pre-Trade 风控链 / 券商通道执行（broker_api_connector）/ D_FEEDBACK_LOOP
  滑点反馈回路
