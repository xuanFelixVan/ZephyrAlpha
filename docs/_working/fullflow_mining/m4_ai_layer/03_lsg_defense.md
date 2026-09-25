---
ttl: task_bound
title: M4 分册03 — LSG 网关与 LLM 裸调双捕防线
lane: m4_ai_layer
session: st-commitspeed-tbl-20260924
date: 2026-09-25
status: mined
---

# 03 — LSG Defense（zephyr.security.llm_defense）

## 一、环节定义与边界

LLM 安全网关（LSG）=`zephyr.security.llm_defense.llm_security.gateway` 的 `LSGSecurityGateway`（480 行，MOD-LLM_SECURITY，MATURITY=production，ai_autonomy=human_gated）。宪法 §9.2 红线执行体：**所有 LLM API 调用必经 LSG，裸调被 GATE-20+运行时拦截器双捕**。上游=全部业务 LLM 调用方（ai_layer.cleaning.washer 等）；下游=openai/anthropic/litellm/langchain 四库（patch 面）。

## 二、六向台账

| 向 | 实测证据 |
|---|---|
| 上游输入 | 业务调用方 scan_input/full_scan/scan_agent_action；包内件 22+（input_sanitizer/adversarial_robustness/alignment_scorer/behavior_audit_logger/sensitivity_classifier/solo_dev_safety_net/poisoning_monitor/lsg_pattern_tracker+red_team_corpus.yaml+dashboard/） |
| 下游消费 | runtime_interceptor 消费 gateway 的 ALLOW 裁定（grant_allowance 颁令牌）；ai_layer/cleaning/washer.py（全 ai_layer 唯一 GATE-20 字样命中件=合规调用示范点） |
| 自动化触发 | **解释器级自动**：sitecustomize.py（仓库根，实存）Python 启动即 bootstrap install()；GATE-20=pre-commit 事件触发（.pre-commit-config.yaml:681 entry 在案，脚本头 M11 豁免注记） |
| 真源与注册表 | RULE-LSG-001（拦截器头 INVARIANTS）；MODIFY-GUARD=sitecustomize 引导链；层件=layers/l0_supply_chain…l8_multi_agent+self_protection/l7_validation |
| 门禁与质量尺 | tests/llm_security/test_runtime_interceptor.py；kill-switch=ZEPHYR_RUNTIME_GATE=0（sitecustomize 与 install() 双重尊重） |
| 当前运行状态 | **绿（带一处诚实降级）**。实测：`LSGSecurityGateway()` 导入实例化 OK，layers=10；启动输出"AgentSecurityLayer: 未传 hmac_key 且 ZEPHYR_LSG_L4_HMAC_SECRET 未设置，明确降级" |

## 三、双捕机制实测拆解（runtime_interceptor.py 头注 1:18-50）

1. **第一捕 GATE-20（静态）**：`scripts/governance/d7_code/detect_direct_llm_calls.py`，pre-commit AST 门禁（.pre-commit-config.yaml:681）。已知上限：运行时 exec 外部内容 AST 不可见。
2. **第二捕 运行时拦截器**：sitecustomize 启动 install() → sys.meta_path finder 拦 openai/anthropic/litellm/langchain 导入 → monkey-patch 核心方法（chat.completions.create/messages.create/litellm.completion 等）→ 调用时验"LSG 放行令牌"（TTL 30s），缺失抛 `BareLLMCallError` 硬阻断。
3. **令牌混合存储**：contextvar（异步链）+threading.local（同步链，覆盖 asyncio.run 子 context 不回传问题）。
4. **逃生门**：`allow_llm_call()`/`allow_llm_call_async()` 上下文管理器（py:208-213，供测试/显式受控调用）；拦截器 ALLOWED Patch 点白名单含 "allow_llm_call"/"allow_llm_call_async"（py:74-75）。

## 四、层清单（10 层实测实例化）

L0 供应链 / L1 输入 / L2 提示保护 / L2a 进程沙箱 / L3 输出 / L4 智能体 / L5 资源保护 / L6 可观测（另 l6_feishu_alert/l6_observability）/ L7 自保护校验（self_protection/l7_validation）/ L8 多智能体（+l8_compliance）。gateway.py:39-52 逐层 import 实证。

## 五、堵点与病灶

1. **L4 HMAC 密钥未配置**：实测启动即降级 AgentSecurityLayer——修法=经 secrets.py 配 ZEPHYR_LSG_L4_HMAC_SECRET（RULE-SECRETS 通道，禁裸 getenv）｜工作量=配置级｜本车道可提出不可自改（secrets 属 Owner）
2. **cleaning 段 LLM 流量为零**：washer 经 LSG 的合规通道建成未通水（ai_cleaning_spec=0 行）——非 LSG 病灶，是上游进化循环未点火（见分册01 §四）
3. **拦截器覆盖面=四库**：openai/anthropic/litellm/langchain 之外的 SDK（google-genai/mistral 等）不在 patch 白名单——当前仓内无此类调用（GATE-20 静态侧兜底），扩库时须同步扩白名单

## 六、自审闸三态

**挖干可施工**：双捕链每环 file:line+实测实例化证据；测试面在案；零 LLM API 实际调用（本册全部证据为导入/实例化/静态读取，无一次真实外呼）。

## 七、复核命令

```bash
python -c "from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway; print(len(LSGSecurityGateway()._layers))"
head -50 src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py
sed -n '681p' .pre-commit-config.yaml
grep -n "install\|ZEPHYR_RUNTIME_GATE" sitecustomize.py | head -5
```
