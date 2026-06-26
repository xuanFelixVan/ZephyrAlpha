---
module_id: KE-1845---api-provider----------d-001
status: active
title: 2.27 模型API多Provider容灾与降级链（决策 D-022-19）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.27 模型API多Provider容灾与降级链（决策 D-022-19）

2.27 模型API多Provider容灾与降级链（决策 D-022-19）

> **决策 D-022-19**：升级协议必须内置多Provider API容灾。当DeepSeek/GLM/Claude任一API不可用时，升级协议自身不能失效——它需要知道如何切换模型来完成升级判定。
> **对标**：API易多云架构(Cloudflare故障中保持99.9%) + LLM Gateway(Cascading Failover: OpenAI→Anthropic→Gemini→国产) + Requesty 99.99999% uptime。

```yaml
multi_provider_resilience:

  provider_failover_chain:
    tier1_primary:
      provider: "DeepSeek"
      role: "主力推理+升级判定"
      health_check: "每30s ping /status"
      failure_threshold: "连续3次超时/5xx→触发降级"

    tier2_fallback:
      provider: "GLM (Zhipu)"
      role: "备用推理+升级判定(国内线路)"
      activation: "Tier1故障后<2s自动切换"

    tier3_fallback:
      provider: "Claude Opus (Anthropic)"
      role: "高能力备用(升级Triage+复杂判定)"
      activation: "Tier1+2均故障后"

    tier4_last_resort:
      provider: "本地备用(ollama/qwen-local)"
      role: "仅升级判定(基础能力,无代码生成)"
      constraint: "仅用于P0升级场景,非P0降级为自处理"

    tier5_emergency_stop:
      trigger: "所有Provider不可用"
      action: "系统进入ALL_STOP模式——暂停所有AI操作+持久化所有待处理升级+每30s重试Tier1"

  escalation_during_api_outage:
    partial_outage: "1个Provider故障→标准升级流程(用备用Provider判定)"
    multi_outage: "≥2个Provider故障→自动升级P1+通知Owner"
    total_outage: "全Provider故障→ALL_STOP+本地日志持久化+P0通知"

  geographic_redundancy:
    principle: "API请求跨区域路由——避免单区域Cloudflare/CDN故障"
    routing: "亚太→国内(DeepSeek/GLM), 欧美→Azure/Anthropic"
```

---
