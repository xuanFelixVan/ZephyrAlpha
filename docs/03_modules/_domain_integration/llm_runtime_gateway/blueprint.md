---
blueprint_id: MOD-INF-051
module_name: llm_runtime_gateway
domain: D_INTEGRATION
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-31
owner: ZephyrAlpha-Owner
---

# MOD-INF-051 llm_runtime_gateway 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：10号文 §4 Phase 0.2/0.3（登记对账）+ Phase 1.1（统一入口骨架）+ 18号清单 §5 E1 裁定（MVP 范围封顶）+ #ARCH-162；44号 §9.14（M3-⑨ 首个消费场景，波5 接线）。
> 代码：`src/zephyr/integration/llm_runtime_gateway.py`

## 0. 定位

L2/L3 统一 LLM 推理门面 MVP：单一 infer 签名 + DeepSeek→Qwen→Ollama 三通道降级链 + 每次调用登记落库（governance.db `llm_call_log`）+ LSG 注入点 + 日终对账。治理 LLM 调用入口分散（DeepSeekChat/OllamaChat 直实例化）无统一登记对账的缺口。纯网关——infer 不承载业务语义，task_type 仅登记/对账维度，不参与路由决策。

## 1. 接口

```python
class LLMRuntimeGateway(clients=None, db_path=None, lsg_enabled=None, chain=None)
    .infer(task_type, prompt, model=None, max_tokens=4096, temperature=0.2,
           channel=None, **kw) -> InferResult   # 统一推理入口
def reconcile_daily_calls(day, *, db_path=None, expected_cost_yuan=None) -> dict
def ensure_llm_call_log_table(db_path=None) -> Path   # 幂等建表+ts 索引
def compute_cost_yuan(provider, model, tokens_in, tokens_out, ts) -> float
def is_valley_period(ts) -> bool   # Asia/Shanghai 18:00(含)-次日9:00(不含)
class QwenChat   # 备用通道轻量客户端（OpenAI 兼容端点，读 QWEN_API_KEY/BASE_URL/MODEL）
```

`clients` 支持测试注入假通道；缺省懒构造真实客户端并缓存复用。channel 显式指定时只打该通道（不静默降级），未知 channel → ValueError。

## 2. 输出契约

- `InferResult`（dataclass，全基元字段 JSON 可序列化）：text/model_version/provider/tokens_in/tokens_out/cost_yuan/latency_ms/status（ok/error/blocked）/error。
- 落库 `llm_call_log`（DDL 常量 `LLM_CALL_LOG_DDL` 即本模块 schema 唯一真源，禁止测试侧复刻副本）：ts（ISO8601 Asia/Shanghai）/task_type/model/provider/tokens/cost_yuan/latency_ms/status/error（截断 300 字）/created_at（UTC）。append-only 仅 INSERT，SQL 参数化常量（NO-BARE-SQL）。
- 对账返回 dict：total_calls/by_status/by_provider/total_tokens/total_cost_yuan/recomputed_cost_yuan/cost_delta_yuan/over_expected（expected_cost_yuan 缺省 None 不判定——预算硬门属 GP1）。

## 3. 不变量

- 调用必登记：每次 infer 含失败/被拦均落 llm_call_log；降级链留痕（每一通道尝试各落一行）
- LSG 不过不调用：入口 enforce_input 判决 BLOCK/DENY 或 LSG 异常 → status=blocked 落库，不发起任何通道调用；客户端自闸门判决不降级（同一 prompt 换通道重发无意义）
- 单通道失败（异常/超时/非 200/SecretsError）不抛 → 降级下一通道并留痕；全失败返回 status=error
- 计价：deepseek 系按内置价表谷峰分时（model_pricing.yaml 运行时镜像；谷>峰方向与公开折扣相反，已登记待 Owner 校准，单测锁定工单口径）；qwen 0.0 待校准；ollama 本地零费用；tokens 为 len/4 估算值，真 usage 待波5 从 API 响应回填
- db_path 默认 None 走 DB_PATH SSoT（测试注入临时库，prediction_log_writer 同款隔离先例）

## 4. 降级行为

- ERROR_CONTRACT：未知 channel → ValueError（fail-closed 输入校验）；通道异常不抛 → 降级；LSGBlockedError 捕获 → status=blocked 返回；登记落库 sqlite3.Error 透传（审计 fail-closed，同 prediction_log_writer 先例）
- QwenChat `__repr__` 显式排除 _api_key（防泄露纪律）；secret 经 get_required_secret 解析（缺失即 SecretsError → 按通道失败降级）

## 5. 边界（不做）

- 不做预算硬门/路由级联（GP1 范围）；只做登记与对账
- 不承载业务语义路由；task_type 为纯标签
- QwenChat 随 MVP 单文件收敛（仓内无既有 QwenChat 实证），GP1 转正时可迁 local_model/ 另行登记

## 6. 测试

tests/model/test_llm_runtime_gateway.py（34 用例）；对账报告 docs/_archive/2026-08-22-llm-registry-reconciliation.md（四源对账 + Q8 裁定 + 谷峰价 F3 待校准项）。
