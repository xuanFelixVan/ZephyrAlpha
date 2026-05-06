"""LLM Security Gateway (LSG)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一
MOD-INF-014 · v0.3.0 · blueprint 对标 OWASP Top 10 for LLM 2025

职责
----
LLM 交互的八层纵深防御（Defense-in-Depth）：
  L0  供应链安全 —— 模型验证 / 依赖扫描 / 来源追溯
  L1  输入防护层 —— 直接注入 + 间接注入(RAG/文件/URL) + 越狱专项检测
  L2  Prompt保护层 —— System Prompt隔离 / 防泄露检测 / 话题控制
  L3  输出安全层 —— Schema验证 / 代码执行沙箱 / PII脱敏 / 幻觉检测
  L4  Agent安全层 —— 权限最小化 / Human-in-Loop / 操作审计 / 工具防护
  L5  资源保护层 —— 速率限制 / Token预算 / 成本熔断 / 并发限制
  L6  可观测性层 —— 安全日志 / 异常告警 / 仪表板 / 定期审计报告
  L7  持续验证层 —— 自动Red Team / 安全回归测试 / 威胁情报更新 / 防御度量

原则：fail-closed —— LSG 不可用 → 所有 LLM 流量 reject 而非 bypass
      L6(L7) fail-open 降级例外

已实现模块（~18% 完整度）:
  ✅ input_sanitizer.py — L1子层1A 直接注入检测
  ✅ process_sandbox.py — L2a 独立进程沙箱（被L3/L4消费）
  ✅ behavior_audit_logger.py — L6 审计日志引擎

待施工模块（Phase 0→P0优先）:
  ░░ layers/l1_input.py — L1完整输入防护（1B间接+1C越狱）
  ░░ layers/l5_resource_protection.py — L5资源保护+成本熔断
  ░░ layers/l3_output.py — L3输出安全（脱敏/沙箱/幻觉）
  ░░ layers/l2_prompt_protection.py / l0_supply_chain.py / l4_agent.py / l6_observability.py / l7_validation.py

对标:
  OWASP Top 10 for LLM Applications 2025 · MITRE ATLAS v5.1
  NIST AI RMF 1.0 (GenAI Profile) · NVIDIA AI Safety Recipe
  Anthropic Safeguards Framework · Microsoft SAIF · SafeVibecoding

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：见 ADR-0022 目录双轨治理 + ADR-0020 LSG
架构真源：docs/02_enterprise_architecture/target-architecture/
         vibe-coding-infrastructure-architecture.md §3.1
蓝图 SSoT：docs/03_modules/l01_infrastructure/llm-security/blueprint.md

Phase 路线
----------
defer → Phase 0 (L1B+L5+L3C, ~3天) → Phase 1 (L2+L3B+L6扩展, ~2.5天)
→ Phase 2 (L0+L4+L7, ~4天) → Phase 3 (L3D+仪表板+报告, ~2.5天)
"""
