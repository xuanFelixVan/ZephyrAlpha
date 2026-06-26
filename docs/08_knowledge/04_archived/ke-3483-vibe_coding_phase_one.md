---
module_id: KE-3348
title: 5A.1 6 大核心服务一句话定位
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5A.1 6 大核心服务一句话定位

5A.1 6 大核心服务一句话定位

| 缩写 | 服务全称 | 一句话定位 | 接口规范 |
|------|---------|-----------|---------|
| **LSG** | LLM Security Gateway | LLM 交互的"安全闸"，四层防御，fail-closed | `08_.../llm-security-gateway-interface.md` |
| **CE** | Context Engine | AI 编码的"中枢神经"，上下文 build/compress/validate/inject | `08_.../context-engine-interface.md` |
| **Orc** | Agent Orchestrator | Vibe Coding 2.0 的"任务引擎"，任务生命周期 + Agent 沙箱 | `08_.../agent-orchestrator-interface.md` |
| **VMS** | Vector Memory Service | 知识与决策的"向量记忆库"，ChromaDB 5 个 Collection | `08_.../vector-memory-service-interface.md` |
| **FLE** | Feedback Loop Engine | 系统自调节的"闭环大脑"，指标→异常→动作 | `08_.../feedback-loop-engine-interface.md` |
