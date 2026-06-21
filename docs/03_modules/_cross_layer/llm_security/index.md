---
blueprint_id: DOM-GOV-001
created: '2026-05-03'
doc_type: index
module_id: MOD-INF-049
status: Active
title: llm-security — MOD-INF-014 目录索引
updated: '2026-05-05'
version: 0.3.0
---


# LLM Security Gateway (MOD-INF-014)

> 八层纵深防御 · fail-closed 原则 · 对标 OWASP Top 10 for LLM 2025
> 蓝图版本：v0.3.0 | 整体完整度：~18%

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [blueprint.md](blueprint.md) | Markdown | 主蓝图文档 — L0-L7 八层防御完整设计 |
| [index.md](index.md) | Markdown | 本索引文件 |

## 源码落位

| 文件 | 状态 | 说明 |
|------|:--:|------|
| `src/zephyr/security/llm_defense/llm-security/__init__.py` | ✅ | 模块入口 · 架构注释 |
| `src/zephyr/security/llm_defense/llm-security/input_sanitizer.py` | ✅ | L1子层1A · 直接注入检测 |
| `src/zephyr/security/llm_defense/llm-security/process_sandbox.py` | ✅ | L2a · 独立进程沙箱 |
| `src/zephyr/security/llm_defense/llm-security/behavior_audit_logger.py` | ✅ | L6 · 审计日志引擎 |
| `src/zephyr/security/llm_defense/llm-security/layers/l0_supply_chain.py` | ░░ | L0 · 供应链安全 |
| `src/zephyr/security/llm_defense/llm-security/layers/l1_input.py` | ░░ | L1 · 完整输入防护 |
| `src/zephyr/security/llm_defense/llm-security/layers/l2_prompt_protection.py` | ░░ | L2 · Prompt保护+防泄露 |
| `src/zephyr/security/llm_defense/llm-security/layers/l3_output.py` | ░░ | L3 · 输出安全 |
| `src/zephyr/security/llm_defense/llm-security/layers/l4_agent.py` | ░░ | L4 · Agent安全+HITL |
| `src/zephyr/security/llm_defense/llm-security/layers/l5_resource_protection.py` | ░░ | L5 · 资源保护+熔断 |
| `src/zephyr/security/llm_defense/llm-security/layers/l6_observability.py` | ░░ | L6 · 可观测性 |
| `src/zephyr/security/llm_defense/llm-security/self_protection/l7_validation.py` | ░░ | L7 · 持续验证+Red Team |
| `src/zephyr/security/llm_defense/llm-security/patterns/secrets.py` | ░░ | PII/Secret模式库 |
| `src/zephyr/security/llm_defense/llm-security/patterns/injection_patterns.py` | ░░ | 注入Payload特征库 |
| `src/zephyr/llm-security/payloads/red-team-payloads.yaml` | ░░ | Red Team攻击载荷库 |
| `src/zephyr/security/llm_defense/llm-security/sandbox/code_exec_sandbox.py` | ░░ | 代码执行沙箱 |

## 相关文档

| 文件 | 说明 |
|------|------|
| [KBG-0020](../../02_enterprise_architecture/adr/adr-0020-llm-security-gateway.md) | LSG 架构决策记录 |
| [KBG-0022](../../02_enterprise_architecture/adr/adr-0022-directory-dual-governance.md) | 目录双轨治理决策 |
| [b_llm_security.yaml](../../../architecture-model/layers/b_llm_security.yaml) | 分层模型定义 |
| [LSG Interface](../../_b_track_interfaces/llm-security-gateway-interface.md) | LSG 接口合同 |

## 导航

- [上级目录](../index.md)
- [项目根](../../../index.md)