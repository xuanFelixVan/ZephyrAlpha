---
blueprint_id: MOD-INF-018
created: '2026-05-05'
doc_type: index
module_id: MOD-INF-068
status: Active
title: Agent RBAC — 七层纵深防御 + 六横切面 权限系统
updated: '2026-06-22'
version: 0.14.0
ttl: permanent
---


# Agent RBAC — 七层纵深防御 + 六横切面

> MOD-INF-018 | blueprint v0.14.0 | status: Active

## 核心文件

| 文件 | 说明 |
|------|------|
| [blueprint.md](blueprint.md) | **Agent 身份与权限系统蓝图 v0.14.0** — 七层纵深防御 + 六横切面 Runtime RBAC |
| adversarial_test_report.yaml | **红白对抗测试报告 2026-05-08** — 8 攻击向量 + 5 根因分析 + 追问到底 |

## 蓝图概览

| 属性 | 值 |
|------|-----|
| 架构模式 | 七层纵深防御 + 六横切面（Defense-in-Depth + Cross-Cutting） |
| 横切面 A | **Permission Hooks** — pre/post/on_blocked/on_kill_switch 四类钩子（9个预置钩子） |
| 横切面 B | **Permission Topology** — 权限依赖图/跨Agent关联/影响传播图/供应链安全/Cascading Failure建模 |
| 横切面 C | **Auto-Maintenance** — 规则效果评估/僵尸规则检测/复杂度预算/Owner健康仪表盘/多Profile管理 |
| 横切面 D | **Intent-Bound & Continuous-Verification（IBAC）** — 任务意图绑定/跨链意图传递/每步重验证/Context Drift检测/Cascading Failure隔离/权限模式管理器(5模式+Profiles+Mid-Session Toggle) |
| 横切面 E | **Adversarial Resilience & Incentive Alignment** — OWASP Agentic Top 10 ASI02-ASI06全覆盖/MAESTRO五层威胁建模/GroupGuard多Agent合谋博弈检测/Agent自解除沙箱防护(CVE-2026-21852)/虚假完成与欺骗检测/记忆来源追踪隔离(ASI06)/TOCTOU+编码绕过防护/Canary权限灰度/激励审计(Incentive Score)/Agent撒谎检测 |
| 横切面 F | **Forensic-Grade Security Assurance（取证级安全保障）** — Genesis Bootstrap两阶段验证/非对称安全审查(Independent Security Auditor)/不可抵赖操作绑定(Ed25519+Merkle Tree+TSA)/路径解析系统故障防护(9类危险信号+沙箱预演)/跨平台Shell方言检测(Linux偏见)/权限规则语言注入防护(Data≠Instruction)/构建产物安全卫生(Source Map扫描+Pre-Publish Gate)/Transitive依赖安全审计/审计日志实时完整性验证(<100ms Merkle Proof)/Agent上下文重放攻击防护(nonce+Bloom Filter)/律师可验证性(GDPR/个保法合规)/Rollback攻击载体隔离(快照签名+rollback_storm熔断) — **外部取证专家终极审视成果** |
| L0 | Immutable Core — 硬编码不可变保护路径(22+条)+OS级ACL双重兜底 + 冷启动锁 + Kill Switch(8种触发器+熔断源隔离+rollback_storm) + TOCTOU防护 + 自解除沙箱+虚假完成+记忆投毒 always_blocked + Python猴子补丁检测 + 路径解析安全 + Bootstrap哈希签名 |
| L1 | RBAC — 三层权限 + Agent创建权与遗传衰减 + SessionToken签名 + 横向越权防护 + 委托链追踪 + Agent Ed25519密钥对 |
| L2 | ABAC — 五维度感知(意图+时间+Maturity+资源+TLB) + Context Drift实时检测 + Inference合成泄漏检测 + 中文语义判定 |
| L3 | Input Guard — 参数schema + 危险模式 + package_install白名单 + network_target白名单 + env保护 + MCP Server身份校验 + TRAE专属Tool + 编码绕过预解码 + FileLock + SQL Template + 跨平台Shell方言检测 |
| L4 | Sequence Guard — 会话内序列 + 跨Session关联 + Agent间Covert Channel + 多Agent涌现行为检测 + GroupGuard合谋检测 + Micro-Verified先干后验 + 工具组合等效性分析 + 不可抵赖操作签名绑定 |
| L5 | Output Guard — PII/中文PII脱敏 + 凭证检测 + 大小截断 + Synthesis Leakage检测 + 跨步一致性 + 虚假完成(声称v.s.实际) + Prompt Injection文件写入审核 + 构建产物敏感信息扫描 |
| L6 | Observability — OTEL指标(含防篡改) + 告警信噪比 + 规则效果评估 + 行为异常 + 连续验证指标 + 自解释输出 + 激励审计(Incentive Score) + 降级静默告警 + 审计日志Merkle完整性验证 + Merkle Root公开发布 |
| L7 | Testing & Dry-Run — 影响分析 + Dry-Run + 对抗性测试 + 环境隔离 + 跨模型一致性 + Chaos + Edge Case(160项) + Multi-Agent Scenario + Genetic Permission Fuzzer + Canary灰度 + 权限变更自动回归 + 分类器对抗评估 + Forensic Evidence Kit演练 |
| 执行模式 | Micro-Verified先干后验 + 自动回滚 + 紧急覆盖令牌（JIT/<5分钟/一次性/CLI） + 操作nonce防重放 |
| 配置派生 | GOV-AI-001 自动派生 rbac_roles.yaml |
| 权限模式 | 5种模式(对标 Claude Code)——default/acceptEdits/plan/auto/emergency + Shift+Tab + Profiles |
| Mid-Session | /mode /permissions /profile /audit 四个运行时命令 |
| 多 IDE | 支持 TRAE / Cursor / RooCode 统一身份 |
| 决策数 | **45 项**（D-018-01 ~ D-018-45） |
| 盲点覆盖 | **160项** 全覆盖（P0: 24项 + P1: 93项 + P2: 43项） |
| 行业对标 | Grantex State of Agent Security 2026(30框架零Agent身份审计) / Google Antigravity P0路径解析事故 / VibeGuard盲点分类 / SecureVibes非对称审计算法 / Sherlock自我审计14漏洞清单 / SUSVIBES 10.5%安全率基准 / CSA ATF / D2四层 / NIST / Claude Code 5模式+hooks+CVE-2026-21852 / Cursor globs+alwaysApply / Windsurf Cascade / Google SAIF / OWASP LLM Top 10 / OWASP Agentic Top 10 ASI02-ASI06 / Perplexity NHI+confused-deputy / Cisco TBAC/IBAC / NVIDIA多Agent+AI Red Team / Codex CLI profiles+sandbox / GroupGuard(清华/港大) / "Agents of Chaos"(Harvard/MIT/Stanford) / Grith 7-Agent审计 / CyberArk MCP / TRAE Sandbox / MAESTRO五层威胁建模 / Oxford多Agent挑战 / OPA Rego / K8s RBAC / STRIDE Repudiation / Talan 500+扫描实践 / GDPR/个保法 |

## 导航

- [上级目录](../index.md)
- [项目根](../../index.md)
