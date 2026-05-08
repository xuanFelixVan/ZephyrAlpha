"""LLM Security Gateway (LSG)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一
MOD-INF-014 · v1.0.0 · blueprint 对标 OWASP Top 10 for LLM 2025

职责
----
LLM 交互的九层纵深防御（Defense-in-Depth）：
  L0  供应链安全 —— 模型验证 / 依赖扫描 / MCP验证 / Prompt模板审计
  L1  输入防护层 —— 直接注入 + 间接注入(RAG/文件/URL) + 越狱专项检测 + 编码逃逸防御
  L2  Prompt保护层 —— 四段式Prompt模板 / 防泄露检测 / 话题边界控制
  L3  输出安全层 —— Schema验证 / 代码执行沙箱 / PII脱敏 / 幻觉检测 / AI代码信任边界
  L4  Agent安全层 —— 权限最小化 / HITL审批 / 工具参数注入防护 / 金融合规
  L5  资源保护层 —— Token预算 / 速率限制 / 成本熔断 / 并发限制 / 性能SLO
  L6  可观测性层 —— 安全日志 / 异常告警 / 仪表板 / 定期审计报告 / 侧信道防御
  L7  持续验证层 —— 自动Red Team / 安全回归测试 / 威胁情报更新 / 防御度量
  L8  多Agent安全层 —— 跨Agent权限继承 / 权限泄漏防护 / Agent信任链验证

原则：fail-closed —— LSG 不可用 → 所有 LLM 流量 reject 而非 bypass
      L6(L7) fail-open 降级例外

统一入口
--------
LSGSecurityGateway — 九层防御链式编排，提供 scan_input / scan_output /
scan_agent_action / full_scan 四种扫描模式.

已实现模块:
  ✅ gateway.py — LSGSecurityGateway 统一编排入口（L0-L8 链式串联）
  ✅ protocol.py — SecurityDecision / SecurityContext / SecurityResult / LLMSecurityProtocol
  ✅ input_sanitizer.py — L1子层1A 直接注入检测
  ✅ process_sandbox.py — L2a 独立进程沙箱（被L3/L4消费）
  ✅ behavior_audit_logger.py — L6 审计日志引擎
  ✅ layers/l0_supply_chain.py — L0 供应链安全（模型验证/依赖扫描/MCP验证/Slopsquatting）
  ✅ layers/l1_input.py — L1 输入防护（直接+间接+越狱+ToolResultTransform+编码逃逸）
  ✅ layers/l2_prompt_protection.py — L2 Prompt保护（防泄露/话题控制）
  ✅ layers/l2a_process_sandbox.py — L2a 进程沙箱
  ✅ layers/l3_output.py — L3 输出安全（脱敏/沙箱/幻觉/代码信任边界/公域发言）
  ✅ layers/l4_agent.py — L4 Agent安全（权限/HITL/金融合规/长时域/冒充防御）
  ✅ layers/l5_resource_protection.py — L5 资源保护（Token/速率/熔断/递归/性能/模型提取/缓存）
  ✅ layers/l6_observability.py — L6 可观测性（事件/异常/告警/报告/Promptware/侧信道）
  ✅ layers/l8_multi_agent.py — L8 多Agent安全（信任评分/身份验证/跨Agent权限）
  ✅ self_protection/l7_validation.py — L7 持续验证（完整性/DeepSeek风险/供应商隔离/回归）
  ✅ patterns/injection_patterns.py — 注入检测正则模式库
  ✅ patterns/secrets.py — 密钥/PII扫描模式库

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
蓝图 SSoT：docs/03_modules/_cross_layer/llm-security/blueprint.md
"""

__all__ = [
    'behavior_audit_logger',
    'gateway',
    'input_sanitizer',
    'process_sandbox',
    'protocol',
    'layers',
    'self_protection',
    'patterns',
    'payloads',
    'dashboard',
    'sandbox',
]
