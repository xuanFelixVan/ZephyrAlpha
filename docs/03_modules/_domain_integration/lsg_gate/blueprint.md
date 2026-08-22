---
blueprint_id: MOD-INF-052
module_name: lsg_gate
domain: D_INTEGRATION
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-INF-052 lsg_gate 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：09号文 §4.2 P0-1（L2/L3 主链路 LSG 贯通）+ 18号清单 §4.1 + #ARCH-159；10号文 Q4（三通道同一闸门）。
> 代码：`src/zephyr/integration/local_model/lsg_gate.py`

## 0. 定位

local_model 包 LSG 统一注入闸门：L2/L3 运行时 LLM 客户端（OllamaChat / DeepSeekChat / LocalModelScheduler / EmbeddingRouter）构造点的统一安全闸门——所有本地模型调用在发起 API 请求前必经 LSGSecurityGateway 判决，判决记录落 L6 审计，三通道同一闸门无旁路（治理 L2/L3 客户端构造点零 LSG 引用的旁路缺口）。

## 1. 接口

- `resolve_lsg_enabled(override: bool | None) -> bool`：开关三级解析——构造参数 > 环境变量 `ZEPHYR_LSG_LOCAL_MODEL_ENABLED`（"0"/"false"/"off"/"no" 关闭）> 默认开。关闭仅供测试/应急，不改默认安全姿态。
- `get_gateway() -> LSGSecurityGateway | None`：网关懒加载进程内单例（线程安全双重检查）；构造失败返回 None 由调用方 fail-closed（下次调用重试）。
- `enforce_input(text, *, source, enabled=True) -> None`：调用前输入闸门，L0→L1→L2→L5 链式判决。
- `enforce_output(text, *, source, enabled=True) -> None`：响应返回前输出闸门，L3→L6 链式判决。
- `LSGBlockedError(RuntimeError)`：判决 BLOCK/DENY 或 LSG 不可用时抛；继承 RuntimeError 保持 OllamaChat/DeepSeekChat 既有错误契约零破坏。

## 2. 输出契约

- 放行：函数正常返回（None），调用方继续发起 API 调用。
- 拦截：抛 `LSGBlockedError`，本次 LLM API 调用不得发起；BLOCK/DENY 不重试直接上抛。
- 每次判决（含 ALLOW）落 L6 审计，事件 `lsg_local_model_gate`——只记元数据（direction/source/decision/blocked_by/elapsed_ms），**不记 prompt/响应原文**（防敏感内容入审计）；block/deny/error 记 HIGH，余 DEBUG。

## 3. 不变量

- fail-closed：LSG 不可用/判决 BLOCK/DENY/扫描异常 → 抛 LSGBlockedError 且不发起 LLM API 调用（蓝图 D-INF014-01：宁可停服不可裸奔）
- 开关默认开；空文本或 enabled=False 直接放行（测试/应急通道）
- L6 为 fail-open 层：审计记录失败绝不阻断主流程
- 性能：L1/L2 本地正则/模式匹配、L5 计数器检查，扫描微秒~毫秒级；网关单例复用不拖慢调用

## 4. 降级行为

- 网关构造失败 → get_gateway 返回 None → enforce_* fail-closed 抛错（下次调用重试构造）
- 扫描异常 → 记 L6（decision=error）后抛 LSGBlockedError
- L6 审计写失败 → 仅 debug 日志，不阻断

## 5. 边界（不做）

- 不改动 LSG 网关本体与各层逻辑（本件只是注入闸门）
- ~~L0 启动时验证（verify_model/scan_dependencies）无启动链路消费方，挂 _LocalModelBootstrap 为 P1 候选（#ARCH-159 登记缺口）~~ **已落地（2026-08-22，#255③）**：_LocalModelBootstrap.l0_supply_chain_verify 在 start_local_models 模型加载前调用，真源=config/model_digests.yaml（空表跳过），结果缓存 core._l0_verify_results，失败 fail-visible 不阻断 boot

## 6. 测试

tests/model/test_local_model_lsg_gate.py（26 用例）+ tests/llm_security/test_fail_closed.py 演练项（L1/L3/L4/L5 各挂一次全被拒 + Owner override 通道实证）；旁路扫描报告 docs/_working/reports/2026-08-22-lsg-bypass-scan.md + lsg-failclosed-drill.md。
