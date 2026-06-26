---
module_id: KE-2776
status: active
title: LLM Security Gateway Interface / LLM 安全网关接口规范
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# LLM Security Gateway Interface / LLM 安全网关接口规范

LLM Security Gateway Interface / LLM 安全网关接口规范

> **定位**：LLM 安全网关（LSG）——**接口与真源以 YAML frontmatter `truth_source` 为准**（`MOD-LLM_SECURITY` 蓝图 + `b_llm_security.yaml` + OWASP LLM Top 10 作外部威胁分类参考）。部署在 MCP Server 前端，对 **所有进出 LLM 的数据** 做 L1–L4 纵深防护并坚持 **fail-closed**。与 Agent Sandbox（KBG-0018）形成双层安全防线。
>
> **与其他 4 份规范的根本差异——fail-closed 原则**：
>
> | 服务 | 挂了如何活 |
> |------|----------|
> | VMS 挂 | 返回空 + degraded=True，上游降级到 grep |
> | Context Engine 挂 | 降级到规则压缩或 prompts 单通道 |
> | Orchestrator 挂 | 降级到日志缓冲，不丢任务 |
> | Feedback Loop 挂 | 上游本地缓冲 metrics，不阻塞 |
> | **LSG 挂** | **拒绝所有流量（fail-closed）**，宁可全停，不放水。安全是红线。 |

---
