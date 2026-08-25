---
blueprint_id: MOD-INT-LOCAL-LLM-POOL
module_name: local_llm_pool
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
path: src/zephyr/intelligence/local_llm_pool.py
granularity: file
---

# MOD-INT-LOCAL-LLM-POOL local_llm_pool 蓝图（本地 LLM 池）

> **module_id**: MOD-INT-LOCAL-LLM-POOL | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B11-02628（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§8.1）
> 代码：`src/zephyr/intelligence/local_llm_pool.py`

## 0. 定位

本地 LLM 池（Ollama/vLLM 本地 7B + AWQ 4bit 量化）：主力 Qwen2.5-7B +
备选 DeepSeek-7B 多模型常驻注册表；AWQ 4bit 模型加载/卸载管理；显存预算
门（盘中不超过 6GB 含 KV cache，超限拒载并产降级 API 池信号）；与
gpu_monitor 联动（显存快照经注入采集）；延迟/成功率入模型画像（经注入
profile_sink 外发）。

与既有族分工（查重裁定，canonical 分工在案）：
- MOD-INT-API-LLM-POOL api_llm_pool（P1 R1 已建）：**API 侧**池化治理
  （provider 注册/计费台账/健康调度/degrade_to_local 信号）——本池是其
  降级信号的**本地侧对应物**，两池对称不重复：API 池管云端 provider，本
  池管本地推理模型；本池超限产 `degrade_to_api` 信号（切换执行委托
  api_llm_pool/llm_gateway，本模块不执行）。
- MOD-INF-042 ollama_chat：单模型 Ollama HTTP 客户端（真实调用面）——
  本池不复制调用逻辑，模型加载/卸载/调用经注入 executor 委托。
- MOD-INF-042 local_model_scheduler：24/7 任务队列调度循环（Embedding/
  Ollama 分派），与本池池化治理互补。
- MOD-RESOURCE_OPTIMIZATION_ENGINE gpu_monitor：nvidia-smi GPU 状态采集
  ——本池显存快照经注入 `gpu_stats_provider` 消费其产出语义，不直接调
  nvidia-smi。
- MOD-INF-034 model_profiling/profiler：模型 benchmark 画像——本池延迟/
  成功率经 `profile_sink` 外发入画像，不重建画像逻辑。
- 密钥零字段；本地池无密钥语义（纯 localhost 推理治理）。

## 1. 判定核心（纯内存，无 IO）

- `LocalModelSpec`（frozen）：name/quant（awq-4bit 等）/vram_gb（含 KV
  cache 预算）/role（primary/backup）——空名/负显存/未知角色 →
  `InvalidLocalModelSpecError`（Fail-Closed）；重复注册同名 →
  `LocalModelAlreadyRegisteredError`。
- `request_load(model, period)`：显存预算门——当前已载显存合计 +
  待载 spec.vram_gb > budget_gb（盘中 6GB 声明式可配）→ 拒载产
  `LoadDecision(loaded=False, degrade_to_api=True, reasons)`；预算内 →
  `loaded=True` 并经注入 `executor` 委托加载；未注册模型操作 →
  `LocalModelNotRegisteredError`。
- `request_unload(model)`：卸载委托 + 已载台账移除；未加载 → Fail-Closed。
- `record_call_result(model, success, latency_ms)`：健康度累计（成功/失败
  计数、EMA 延迟、连续失败数）+ 经 `profile_sink` 外发入模型画像（sink
  异常不阻断）。
- `select_model(preferred_role=None)`：只在已载且 healthy（连续失败 <
  阈值）中按注册序/角色优先取首个；全不可用 →
  `LocalModelSelection(selected=None, degrade_to_api=True)`。
- 盘中显存保护：`period=intraday` 时 budget_gb 取盘中档（默认 6GB），
  盘后档可放宽（声明式 `PoolBudgets`）；gpu_stats_provider 注入时以其
  memory_used_gb 为当前占用真源，未注入时以内嵌已载台账合计。

## 2. 接口

```python
@dataclass(frozen=True) LocalModelSpec: name/quant/vram_gb/role
@dataclass(frozen=True) PoolBudgets: intraday_gb=6.0/postmarket_gb=8.0
@dataclass(frozen=True) LocalModelHealth: success_count/failure_count/ema_latency_ms/consecutive_failures/is_healthy
@dataclass(frozen=True) LoadDecision: model/loaded/degrade_to_api/reasons
@dataclass(frozen=True) LocalModelSelection: selected/degrade_to_api/reasons
@dataclass(frozen=True) LocalLlmPoolConfig: unhealthy_threshold=3/budgets=PoolBudgets()
class LocalLlmPool(config=None, executor=None, gpu_stats_provider=None, profile_sink=None):
    register_model/request_load/request_unload/record_call_result/select_model/health/loaded_models
class InvalidLocalModelSpecError/LocalModelAlreadyRegisteredError/LocalModelNotRegisteredError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；executor/gpu_stats_provider/profile_sink 全注入；
  零密钥字段。
- 显存预算门 Fail-Closed：超预算拒载并产 degrade_to_api 信号（信号语义，
  不执行切换）。
- 健康度调度：连续失败 ≥ unhealthy_threshold → unhealthy，不入选择集。
- 已载台账只增不改（卸载经显式 request_unload 留痕）；同输入必同判定
  （确定性）。

## 4. 依赖

- MOD-INF-042 ollama_chat（设计边：本地模型真实调用面执行体）
- MOD-RESOURCE_OPTIMIZATION_ENGINE gpu_monitor（设计边：显存快照采集面）
- MOD-INT-API-LLM-POOL api_llm_pool（设计边：降级 API 池信号对称面）
- MOD-INF-034 model_profiling/profiler（设计边：延迟/成功率画像外发面）

## 5. MVP 边界

- 运行时接线（executor 接 ollama_chat/vLLM 加载卸载、gpu_stats_provider
  接 gpu_monitor.collect_gpu_stats、profile_sink 接模型画像、degrade_to_api
  接 api_llm_pool 切换）留运行时装配批；本模块交付本地模型注册表 + 显存
  预算门 + 加载/卸载管理 + 健康度调度判定核心。
