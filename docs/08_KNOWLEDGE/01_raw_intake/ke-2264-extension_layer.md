---
module_id: KE-2170
title: 3e. 指标命名空间与冲突预防 🆕
category: module_blueprint
ttl: permanent
---

# 3e. 指标命名空间与冲突预防 🆕

3e. 指标命名空间与冲突预防 🆕

> **B78 修复**——v0.9.0 新增。多个模块被 AI 独立生成代码后，可能出现同一指标名被不同模块以不同语义使用。例如 MOD-CONTEXT_ENGINE 和 MOD-DATABASE 都注册了 `llm_calls_total`，但一个统计 API 调用、一个统计 LLM 内部调用——这会导致 FLE 告警误判和 Dashboard 数据混乱。这是 100% AI 施工的特有风险（人类开发会自然通过代码 review 发现）。
