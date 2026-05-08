---
module_id: KE-module_blu-8_10__________mod-inf-014_llm_-000
title: 8.10 跨模块集成补充——MOD-INF-014 LLM Security
category: module_blueprint
---

# 8.10 跨模块集成补充——MOD-INF-014 LLM Security

8.10 跨模块集成补充——MOD-INF-014 LLM Security

```yaml
skill_to_security_integration:
  description: "Skill 执行时必须通过 LLM Security 模块的运行时防护（MOD-INF-014）"
  integration_points:
    pre_load: "Skill 内容扫描——检测已知攻击模式（越权指令/工具诱导/数据外泄引导）"
    during_execution: "Skill 提示下的 Agent 工具调用 → 实时拦截异常调用"
    post_execution: "产出物扫描——检测产出的代码/文档是否包含注入 payload"
```

---
