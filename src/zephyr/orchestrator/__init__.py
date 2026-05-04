"""Agent Orchestrator (Orc)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一

职责
----
任务生命周期管理 + Agent 调度 + 沙箱执行 + 幻觉检测

状态机
------
DRAFT → QUEUED → ASSIGNED → RUNNING → REVIEWING → COMPLETED
分支 : BLOCKED / FAILED / CANCELLED / HALLUCINATING

基础设施
--------
任务队列 : SQLite + asyncio.Queue（Phase 1-2）
          NATS JetStream（Phase 3+ 升级）
沙箱     : Windows ACL + 只读挂载（Phase 1）
          Docker Desktop（Phase 3+ 升级）

P0 降级红线
-----------
DEGRADE-003: 沙箱创建失败 → 任务 FAIL，拒绝无沙箱运行（安全优于可用性）

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理 + ADR-0017 Orc + ADR-0018 Sandbox
架构真源：docs/02_enterprise_architecture/target-architecture/
         vibe-coding-infrastructure-architecture.md §3.4

依赖
----
- CE（context_engine/）：上下文构建
- VMS（vector_memory/）：任务输出写入
- LSG（llm_security/）：工具调用验证
"""
