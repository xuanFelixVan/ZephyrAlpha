---
module_id: KE-documentat-3_2_owasp_llm_top_10____2023_2-002
title: 3.2 OWASP LLM Top 10 映射（2023/2024）
category: documentation
---

# 3.2 OWASP LLM Top 10 映射（2023/2024）

3.2 OWASP LLM Top 10 映射（2023/2024）

AI 协作域带来 10 类 LLM 特有威胁，本系统覆盖情况：

| OWASP ID | 威胁 | 本系统暴露面 | experimental 防御 | 参考 |
|----------|------|-------------|-------------|------|
| LLM01 | **Prompt Injection** | Cursor / Trae 对话 + 注入外部文档 | LSG L1 输入分类器 + L2 System Prompt 隔离 | LSG §4 |
| LLM02 | **Insecure Output Handling** | AI 输出直接写文件 | LSG L3 输出 Schema + Pydantic extra='forbid' | LSG §4 |
| LLM03 | **Training Data Poisoning** | ❌ 不训练模型（只用推理）| N/A | — |
| LLM04 | **Model DoS** | LLM API 被重复调用 | Orchestrator 任务限速 + 配额 | Orc §6 |
| LLM05 | **Supply Chain** | 第三方 MCP Tool 不可信 | Agent Sandbox 白名单（§5）| ADR-0018 |
| LLM06 | **Sensitive Info Disclosure** | AI 输出包含 API Key | LSG L3 输出 Secret Pattern 扫描 | LSG §4 |
| LLM07 | **Insecure Plugin Design** | MCP tools 接口越权 | LSG L4 Pattern 巡检 + Sandbox | LSG §4 |
| LLM08 | **Excessive Agency** | Agent 拥有过多权限 | 白名单命令集 + 资源配额 | ADR-0018 |
| LLM09 | **Overreliance** | AI 幻觉未检测 | Orchestrator 幻觉检测 + Context Engine validate | Orc §5 |
| LLM10 | **Model Theft** | ❌ 本地 BGE-M3 / Qwen2.5-3B 是开源公开模型 | N/A | — |

**关键洞察**：本系统 AI 攻击面集中在 **LLM01 / LLM02 / LLM06 / LLM08 / LLM09**（5 条 P0），其他 5 条不适用或 P2 级。
