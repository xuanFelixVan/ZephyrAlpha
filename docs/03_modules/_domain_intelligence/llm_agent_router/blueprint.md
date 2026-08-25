---
blueprint_id: MOD-INT-AGENT-ROUTER
module_name: llm_agent_router
domain: D_INTELLIGENCE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_INTELLIGENCE
path: src/zephyr/intelligence/llm_agent_router.py
granularity: file
---

# MOD-INT-AGENT-ROUTER llm_agent_router 蓝图（LLM Agent 路由）

> **module_id**: MOD-INT-AGENT-ROUTER | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B11-02458（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§0边界声明/§8）
> 代码：`src/zephyr/intelligence/llm_agent_router.py`

## 0. 定位

LLM Agent 级路由门面（业界对标 LiteLLM Router/FrugalGPT 成本感知路由）：
任务分类（规则优先）→ 模型选择（成本-性能权衡，**委托**既有级联决策引擎）
→ 成本控制（日预算门 + 超限自动降级本地信号）三级流水线；分时策略（盘中
本地优先/盘后 API 深度）；路由决策+成本落审计；延迟预算 Stage1<50ms/
Stage2<10ms/Stage3<5ms 校验留痕。

与既有族分工（查重裁定，2026-08-25 场内复核）：
- MOD-MODEL_ROUTER_ORCH cascade_orchestrator（2026-08-24 建，晚于
  2026-08-23 深挖审计）：L1 能力门→L2 任务适配→L3 成本/层级路由级联决策
  引擎，已覆盖 TSV 所载"时段限制+三阶段级联"缺口——本模块**不重建级联**，
  模型选择段经注入 decision_engine callable 委托其 route()，只做 Agent 级
  增量：日预算门/审计落账/延迟预算校验。
- MOD-INF-024 governance model_router：tier×perf-aware API 侧终裁（级联
  L3 的消费对象）。
- MOD-INF-009 llm_gateway：真实调用面与 provider 降级链；pipeline
  model_router：API 模型静态选择+fallback+成本估算。
- MOD-INT-API-LLM-POOL api_llm_pool：API 池化治理（provider 注册/计费台账/
  健康调度/degrade_to_local 信号）——本模块日预算门与其池级成本上限分工：
  本模块管**路由决策时点**的日预算判定与降级信号，池内累计台账仍归池。
- 本模块判定核心纯内存：任务分类规则/日预算判定/延迟预算校验/审计记录
  组装；决策引擎与审计外发全经注入，零密钥零直连。

## 1. 判定核心（纯内存，无 IO）

- `classify(task)`：任务分类规则优先——声明式规则表（kind/local_pref/
  api_allowed），未登记任务按默认 local 规格并留痕（与级联 task_routes
  先例同款兜底）。
- `route(request)` 三级流水线：
  - Stage1 任务分类（规则优先，预算 <50ms）；
  - Stage2 模型选择：经注入 `decision_engine`（默认委托 cascade
    orchestrator route() 语义）产候选决策（预算 <10ms）；
  - Stage3 成本控制（预算 <5ms）：当日累计成本 + 本单预估成本 >
    daily_budget_usd → 产 `degraded_to_local=True` 决策（本地兜底模型），
    不执行切换；预算未超 → 透传 Stage2 决策。
- 分时策略：`period`（intraday 盘中本地优先 / postmarket 盘后 API 深度）
  声明式配置；盘中非 API 白名单 kind 强制本地候选。
- 延迟预算：三段实际耗时 vs 预算比对，超限落 `latency_violations` 留痕
  （不阻断路由返回）。
- 审计：每次路由产 `RouteAuditRecord`（任务/分类/决策/预估成本/日累计/
  降级标记/时段/延迟留痕），经注入 `audit_sink` 外发；sink 异常不阻断
  （sink_errors 留痕）。

## 2. 接口

```python
@dataclass(frozen=True) TaskClassification: task_type/kind/local_pref/reason
@dataclass(frozen=True) RouteRequest: task_type/candidates/period/complexity/estimated_cost_usd
@dataclass(frozen=True) AgentRouteDecision: task_type/selected_model/provider/source/degraded_to_local/reasons/latency_violations
@dataclass(frozen=True) RouteAuditRecord: request_fingerprint/classification/decision/daily_cost_before/daily_cost_after/period
@dataclass(frozen=True) AgentRouterConfig: daily_budget_usd/period_rules/latency_budgets_ms=(50,10,5)
class LlmAgentRouter(config, decision_engine=None, cost_ledger=None, audit_sink=None, clock=None):
    classify/route/daily_cost/reset_daily
class InvalidRouterConfigError/RouteDecisionError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；decision_engine/cost_ledger/audit_sink/clock 全注入。
- 配置非法 Fail-Closed：负日预算/未知时段规则/非正延迟预算 →
  `InvalidRouterConfigError`；空候选 → `RouteDecisionError`。
- 成本判定确定性：同输入必同降级结论；日台账只增不改装配期经 clock 注入
  判定日界。
- 降级=信号语义：`degraded_to_local=True` 仅产建议，切换执行委托本地池
  （B11-02628）与 llm_gateway 降级链。
- 零密钥字段；仅信号输入无下单语义。

## 4. 依赖

- MOD-MODEL_ROUTER_ORCH cascade_orchestrator（设计边：级联决策引擎委托）
- MOD-INT-API-LLM-POOL api_llm_pool（设计边：池级成本台账/降级信号语义对齐）
- MOD-INF-009 llm_gateway（设计边：真实调用面与降级链执行体）

## 5. MVP 边界

- 运行时接线（decision_engine 接 cascade_orchestrator 实例、cost_ledger
  接 cost_tracker/api_llm_pool 台账、audit_sink 接审计链、period 接交易
  时段真源）留运行时装配批；本模块交付任务分类 + 日预算门 + 延迟预算校验
  + 路由审计判定核心。
