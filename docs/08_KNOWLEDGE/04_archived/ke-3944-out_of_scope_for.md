---
module_id: KE-3792------out-of-scope-for-v0--000
title: 10.2 明确不做（Out of Scope for v0.1.0）
category: module_blueprint
ttl: permanent
---

# 10.2 明确不做（Out of Scope for v0.1.0）

10.2 明确不做（Out of Scope for v0.1.0）

| 不做 | 原因 |
|------|------|
| ❌ 内容级审计（代码质量/安全漏洞） | 已由 MOD-INF-014 (LLM Security) + MOD-INF-017 (Code Dedup) + Snyk/VAS 覆盖 |
| ❌ 外部 API/服务资产发现 | 项目当前无外部服务依赖——当有 MCP Server 对外暴露时再扩展 |
| ❌ 资产财务估值（成本/折旧） | 个人项目不涉及财务核算 |
| ❌ Web UI 仪表盘 | Phase 2 考虑——当前 YAML/JSON 输出已满足 AI 消费需求 |
| ❌ 实时文件监控（inotify/watchdog） | Windows 兼容性差——定时扫描足以覆盖需求 |

---
