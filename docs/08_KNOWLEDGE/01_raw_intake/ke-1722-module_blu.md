---
module_id: KE-1632
status: active
title: 2.0 总览：七层纵深防御 + 四横切面模型
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.0 总览：七层纵深防御 + 四横切面模型

2.0 总览：七层纵深防御 + 四横切面模型

```
┌──────────────────────────────────────────────────────────────────────┐
│               Agent RBAC 8.0 — 七层纵深防御 + 六横切面                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  横切面 A: PERMISSION HOOKS (权限钩子系统)                             │
│  ├── pre_check_hook / post_check_hook / on_blocked_hook / on_kill_switch_hook
│  └── 对标 Claude Code PreToolUse/PostToolUse/PermissionRequest 全套hooks
│                                                                      │
│  横切面 B: PERMISSION TOPOLOGY (权限拓扑感知)                          │
│  ├── 权限依赖图 / 跨Agent关联 / 影响传播图 / 供应链安全 / Cascading Failure建模
│  └── 对标 Perplexity confused-deputy防护 + NVIDIA多Agent链路管控
│                                                                      │
│  横切面 C: AUTO-MAINTENANCE (自动维护)                                │
│  ├── 规则效果评估 / 僵尸规则检测 / 复杂度预算 / Owner健康仪表盘
│  └── 对标 Codex CLI profiles + config.toml 多配置管理
│                                                                      │
│  横切面 D: INTENT-BOUND & CONTINUOUS-VERIFICATION (意图绑定+连续验证)   │
│  ├── IBAC——Intent-Bound Access Control——任务意图绑定+跨链意图传递       │
│  ├── Continuous Verification——每一步重验证Agent身份+Intent一致性        │
│  ├── Context Drift Detection——10步操作链中意图漂移检测                  │
│  ├── Permission Mode Manager——Claude Code 5模式+Codex CLI profiles     │
│  ├── Cascading Failure Isolation——级联故障隔离+回滚边界                 │
│  ├── Mid-Session Toggle——会话中动态切换权限模式(/permissions)            │
│  └── 对标 Cisco TBAC/IBAC + Perplexity NHI + Claude Code Shift+Tab    │
│                                                                      │
│  横切面 E: ADVERSARIAL RESILIENCE & INCENTIVE ALIGNMENT (对抗+激励)    │
│  ├── OWASP Agentic Top 10 ASI02-06全覆盖 + MAESTRO五层威胁建模           │
│  ├── Agent自解除沙箱防护(CVE-2026-21852) + RCE CVE-2024-12366           │
│  ├── GroupGuard合谋检测 + "Agents of Chaos"激励审计                     │
│  ├── 虚假完成/Agent欺骗检测 + Memory Provenance(ASI06)                   │
│  ├── TOCTOU+编码绕过 + Canary权限灰度 + 权限变更自动回归                  │
│  └── 对标 OWASP Agentic Top 10 + MAESTRO + GroupGuard + Grith         │
│                                                                      │
│  横切面 F: FORENSIC-GRADE SECURITY ASSURANCE (取证级安全保障)           │
│  ├── Genesis Bootstrap两阶段验证——施工阶段代码签名+上线前完整性检查        │
│  ├── 非对称安全审查——Independent Security Auditor独立审查RBAC自身       │
│  ├── 不可抵赖操作绑定——Ed25519签名+Merkle Tree+TSA+公证锚定              │
│  ├── 路径解析故障防护——空格/Unicode/嵌套引号+沙箱预演+安全命令模式         │
│  ├── 跨平台Shell方言检测——LLM Linux偏见+Windows不等效命令                │
│  ├── 权限规则语言注入防护——规则=Data≠Instruction+Engine隔离              │
│  ├── 构建产物安全卫生——Source Map扫描+Pre-Publish Gate                  │
│  ├── Transitive依赖审计——递归CVE检查+install脚本检测+lockfile保护        │
│  ├── 审计日志实时完整性验证——Merkle Proof <100ms + Root公开锚定           │
│  ├── 上下文重放攻击防护——nonce+Bloom Filter防重放                       │
│  ├── 律师可验证性——人类可读审计报告+GDPR/个保法合规映射                    │
│
