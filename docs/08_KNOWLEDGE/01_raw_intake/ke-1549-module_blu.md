---
module_id: KE-1459
status: active
title: 13.1 完整文件清单
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.1 完整文件清单

13.1 完整文件清单

```
src/zephyr/llm-security/
├── __init__.py                          ✅ 已实现 — 模块入口+架构注释
├── protocol.py                          ░░ 待创建 — LLMSecurityProtocol 抽象基类
│
├── input_sanitizer.py                   ✅ 已实现 — L1原始实现（直接注入检测）
├── process_sandbox.py                   ✅ 已实现 — L2a子进程沙箱（独立模块）
├── behavior_audit_logger.py             ✅ 已实现 — L6审计日志引擎
│
├── layers/
│   ├── l0_supply_chain.py               ░░ 待创建 — L0供应链安全
│   ├── l1_input.py                      ░░ 待创建 — L1完整输入防护（整合input_sanitizer）
│   ├── l2_prompt_protection.py          ░░ 待创建 — L2 Prompt保护+防泄露
│   ├── l3_output.py                     ░░ 待创建 — L3输出安全（含沙箱扩展）
│   ├── l4_agent.py                      ░░ 待创建 — L4 Agent安全+HITL
│   ├── l5_resource_protection.py        ░░ 待创建 — L5资源保护+成本熔断
│   ├── l6_observability.py              ░░ 待创建 — L6可观测性（整合audit_logger）
│   └── l7_validation.py                ░░ 待创建 — L7持续验证+Red Team
│
├── patterns/
│   ├── secrets.py                       ░░ 待创建 — PII/Secret模式库（25+条规则）
│   └── injection_patterns.py            ░░ 待创建 — 注入Payload特征库
│
├── payloads/
│   └── red-team-payloads.yaml           ░░ 待创建 — Red Team攻击载荷库（200+条）
│
└── sandbox/
    ├── code_exec_sandbox.py             ░░ 待创建 — 代码执行沙箱（Docker/WASI）
    └── __init__.py                      ░░ 待创建
```
