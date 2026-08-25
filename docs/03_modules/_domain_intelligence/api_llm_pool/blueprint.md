---
blueprint_id: MOD-INT-API-LLM-POOL
module_name: api_llm_pool
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
path: src/zephyr/intelligence/api_llm_pool.py
granularity: file
---

# MOD-INT-API-LLM-POOL api_llm_pool 蓝图（API LLM 池）

> **module_id**: MOD-INT-API-LLM-POOL | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B11-02629（AUD-DRAFT-001-DIGEST P1 波 W-P1-11，§8.1）
> 代码：`src/zephyr/intelligence/api_llm_pool.py`

## 0. 定位

API LLM 池（DeepSeek/GLM/Claude/OpenAI 多 provider）：provider 池注册
（模型/价格/限额/超时）+ token 计费台账（按 Agent/任务归集，经
`usage_sink` 委托 cost_tracker 落账）+ 池健康度（成功率/延迟）驱动调度 +
成本超限自动产**降级本地池建议**（`degrade_to_local` 信号，执行委托本地
LLM 池 B11-02628 / llm_gateway 降级链，本模块不执行切换）。

与既有族分工（查重裁定）：
- MOD-INF-009 llm_gateway：真实 API 调用面与 provider 降级链（生产），本池不
  复制调用逻辑，只做池化治理（注册/计费/健康/调度建议）。
- MOD-INF-009 model_router：任务→模型静态路由与降级链声明；本池管运行期
  provider 健康与成本归集，互补不重复。
- 本地 LLM 池（B11-02628，W-P1-10 另波施工）：本地推理池；本池只产降级
  信号，不 import 不复制。
- 密钥走 secrets 管理不落盘（本模块零密钥字段，密钥仍在 llm_gateway 层）。

## 1. 判定核心（纯内存，无 IO）

- `register_provider(spec)`：`ApiProviderSpec`（frozen：provider/model/
  input_price_per_m/output_price_per_m/rate_limit_rpm/timeout_s）非法
  （空名/负价/非正限额/非正超时）→ `InvalidProviderSpecError`（Fail-Closed）；
  重复注册同名 provider → `ProviderAlreadyRegisteredError`。
- `record_usage(provider, agent_id, task_id, input_tokens, output_tokens)`
  → `UsageRecord`（cost_usd = input/1M×in_price + output/1M×out_price），
  台账内嵌（tuple 追加不可变语义）+ 经 `usage_sink` 外发；未注册 provider
  → `ProviderNotRegisteredError`；token 数为负 → `InvalidUsageError`。
- `record_call_result(provider, success, latency_ms)`：健康度累计
  （成功/失败计数、EMA 延迟、连续失败数）。
- `select_provider(preferred_chain)`：只在 healthy（连续失败 < 阈值）中按
  preferred_chain 顺序取首个；全不健康 → `ProviderSelection(selected=None,
  degrade_to_local=True)`；成本累计 ≥ cost_limit_usd（配置可空=不限）→
  任何选择均带 `degrade_to_local=True`（预算超限自动降级建议）。
- `total_cost(agent_id=None, task_id=None)`：台账按 Agent/任务维度归集。

## 2. 接口

```python
@dataclass(frozen=True) ApiProviderSpec: provider/model/input_price_per_m/output_price_per_m/rate_limit_rpm/timeout_s
@dataclass(frozen=True) ProviderHealth: success_count/failure_count/ema_latency_ms/consecutive_failures/is_healthy
@dataclass(frozen=True) UsageRecord: provider/model/agent_id/task_id/input_tokens/output_tokens/cost_usd
@dataclass(frozen=True) ProviderSelection: selected/degrade_to_local/reasons
@dataclass(frozen=True) ApiLlmPoolConfig: unhealthy_threshold=3/cost_limit_usd=None
class ApiLlmPool(config=None, usage_sink=None):
    register_provider/record_usage/record_call_result/select_provider/health/total_cost/ledger
class InvalidProviderSpecError/ProviderAlreadyRegisteredError/ProviderNotRegisteredError/InvalidUsageError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；usage_sink 异常不阻断台账（记录仍内嵌返回）。
- 成本计算确定性：同输入必同 cost_usd；台账只增不改。
- 健康度调度：连续失败 ≥ unhealthy_threshold → unhealthy，不入选择集。
- 零密钥：本模块无任何密钥/凭证字段（密钥在 llm_gateway 经 secrets 管理）。

## 4. 依赖

- MOD-INF-009 llm_gateway（设计边：真实调用面与降级链执行体）
- MOD-INF-009 pipeline cost_tracker（设计边：计费台账落账委托）
- MOD-INF-009 model_router（设计边：任务→模型路由语义对齐）

## 5. MVP 边界

- 运行时接线（usage_sink 接 cost_tracker 真实落账、provider 注册表从配置
  装配、degrade_to_local 接本地池切换执行）留运行时装配批；本模块交付
  池注册 + 计费台账 + 健康度调度判定核心 + 降级信号契约。
