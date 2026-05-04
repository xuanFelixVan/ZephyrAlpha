"""LLM Security Gateway (LSG)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一

职责
----
LLM 交互的四层安全防御：
  L1 输入分类（Prompt Injection 检测）
  L2 System Prompt 隔离（User/System 边界）
  L3 输出 Schema 验证（Pydantic + Secret Scanner）
  L4 Pattern 巡检（历史攻击模式 EMA）

原则：fail-closed —— LSG 不可用 → 所有 LLM 流量 reject 而非 bypass

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：见 ADR-0022 目录双轨治理 + ADR-0020 LSG
架构真源：docs/02_enterprise_architecture/target-architecture/
         vibe-coding-infrastructure-architecture.md §3.1

Phase 路线
----------
Phase 0  : defer
Phase 1  : LocalLLMSecurityGateway（Pydantic + OWASP LLM Top 10 规则集）
Phase 2  : 红队语料库 ≥150 条 + 绕过率 ≤5%
Phase 3+ : 服务化（若需要）
"""
