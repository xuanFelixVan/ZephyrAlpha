---
blueprint_id: MOD-SECLLM-002
module_name: spectral_guard
domain: D_SECURITY_LLM
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_SECURITY_LLM
path: src/zephyr/security/llm_defense/spectral_guard.py
granularity: file
---

# MOD-SECLLM-002 spectral_guard 蓝图（Spectral注意力谱幻觉检测器）

> **module_id**: MOD-SECLLM-002 | **域**: D_SECURITY_LLM | **优先级**: P2
> **来源**: B10-01868（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SECLLM-001，A1 §29.24-7）
> 代码：`src/zephyr/security/llm_defense/spectral_guard.py`

## 0. 定位

Spectral Guardrails：注意力矩阵视作动态图→Laplacian谱能量特征（度矩阵-邻接，谱能量集中度/熵，纯numpy实现）+幻觉评分（能量分散度→评分）+分模型阈值校准（Qwen/DeepSeek双阈值表注入）+recall优先判定语义。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/security/llm_defense/test_spectral_guard.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
