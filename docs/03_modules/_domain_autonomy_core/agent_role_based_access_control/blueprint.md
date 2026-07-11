---
module_id: MOD-INF-018
submodule_path: src/zephyr/security/access_control
title: "Agent RBAC 蓝图 — 七层纵深防御·六横切面运行时权限"
doc_type: blueprint
status: Active
activation_phase: requires_100ai
version: "1.1.0"
layer: L0_infrastructure
domain: infra_ops
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
construction_progress: design_only
actual_disk_path: src/zephyr/security/access_control/
last_updated: "2026-05-14"
last_verified: "2026-05-14"
generation: 3
functional_domain: governance
parent_module: ""
belongs_to: "MOD-MASTER_BLUEPRINT"
summary: "Agent RBAC——七层纵深防御+六横切面运行时权限强制执行器。209项盲点全覆盖，94项决策记录，148个组件文件。"
tags: [agent-rbac, rbac, abac, ibac, tbac, permission-guard, identity, access-control, governance, infrastructure, defense-in-depth, sequence-guard, kill-switch, permission-hooks, permission-topology, auto-maintenance, cold-start-lock, emergency-override, horizontal-escalation, context-drift, intent-binding, micro-verification, continuous-verification, cascading-failure, inference-detection, adversarial-resilience, incentive-alignment, collusion-detection, sandbox-self-disable, false-completion, prompt-injection-defense, memory-provenance, owasp-agentic-top10, maestro-threat-model, forensic-assurance, genesis-bootstrap, non-repudiation, path-parsing-safety, cross-platform-shell, artifact-hygiene]
priority: P0
runtime_plane: hot
rule_form: structural
scope: global
stability: stable
verifiability: hybrid
codification_level: L1
codification_at: "2026-05-14"
depends_on:
  - {target: "MOD-GATE_ENGINE", at: "§2", why: "Gate Engine——权限检查是门禁的一种特化"}
  - {target: "MOD-INF-020", at: "§3", why: "审计追踪链——权限判定结果写入审计日志"}
  - {target: "GOV-AI-001", at: "全篇", why: "AI自治权限注册表——本蓝图的声明式权限真源，自动派生为 rbac_roles.yaml"}
  - {target: "MOD-INF-013", at: "§2", why: "MCP Servers——MCP Tool调用受七层权限约束 + 包安装白名单"}
references:
  - {id: "MOD-INF-021", at: "§2", why: "Rollback 联动——仅存 references（打破 018↔021 DAG 环）"}
  - {id: "MOD-INF-022", at: "§2", why: "Escalation / Kill Switch——仅存 references（打破 018↔022 DAG 环）"}
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

# Agent RBAC 蓝图 — 七层纵深防御·六横切面运行时权限

> ⛔ **自动化准入门禁 (AUTOMATION-GATE)**
>
> | 条件 | 当前值 | 门槛 | 状态 |
> |------|--------|------|:----:|
> | 同时活跃 AI session 数 | 1 | ≥3 | ❌ |
> | 跨 session 文件冲突频率 | 0次/周 | ≥2次/周 | ❌ |
> | PermissionGuard 拦截次数 | 0 | ≥5 | ❌ |
>
> **为什么现在不自动化**: 当前只有 1 个 AI session 在运行，没有权限冲突场景。RBAC 门卫在只有一个人时没有意义。
> **什么时候建**: 当同时活跃 AI session ≥3，或跨 session 文件冲突 ≥2次/周，或 Owner 明确要求多 AI 隔离时。
> **自动化宿主**: FLE `_periodic_checks()` → `_rbac_policy_check()` + CircadianScheduler `hour=4` → `_rbac_audit()`

> module_id: MOD-INF-018 | version: 1.0.0 | status: Active | domain: infra_ops
> actual_disk_path: src/zephyr/security/access_control/ | generation: 3 | construction_progress: design_only

## 概述

本蓝图描述 ZephyrAlpha Agent 身份与权限系统——它解决了 100% AI 开发场景下的权限强制执行问题。核心职责包括：七层纵深防御（L0不可变核心→L7测试模拟）+ 六横切面运行时强制（权限钩子/权限拓扑/自动维护/意图绑定/对抗韧性/取证保障）+ GOV-AI-001 自动派生为可执行规则。当前规模 148 个组件文件、209 项盲点全覆盖、94 项决策记录，目标容量 10,000 脚本 / 1,500 模块 / 100 AI 并发。上游依赖 GOV-AI-001（权限声明真源）+ Gate Engine（门禁框架），下游被 MCP Servers / Rollback / Escalation / Audit Trail 等所有基础设施模块消费。

---

## §0 代码对齐验证

> ⚠️ 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> 列出蓝图描述的**所有代码文件**。此清单 = 代码目录下的实际文件列表。
> AI 施工者按此清单创建文件，审计者按此清单验证对齐。
> **存在性状态受控词表**：`未实现` / `已实现` / `已阻塞` / `已废弃`
> - `已实现`：代码已存在且通过验证 → 蓝图不再重复代码内容，接口签名见 §4
> - `已阻塞`：因外部依赖未就绪无法实现 → MUST 注明阻塞原因
> - `已废弃`：设计变更后不再需要 → MUST 在 §5.3 迁移方案中说明
> - 此列是**当前事实**（永久时态），不是施工进度追踪（临时时态）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-018`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `immutable_core.py` | §3 L0 | 不可变核心——保护路径+冷启动锁+Kill Switch+Engine降级 | 已实现 | |
| 2 | `identity.py` | §3 L1 | Agent 身份注册与识别——AgentIdentity + MaturityLevel | 已实现 | |
| 3 | `permission_guard.py` | §3 L0-L5 | 七层运行时权限检查编排 | 已实现 | |
| 4 | `rbac_guard.py` | §3 L1 | RBAC 角色权限——ALLOW/AUTO_GUARD/BLOCKED | 已实现 | |
| 5 | `abac_guard.py` | §3 L2 | ABAC 属性权限——意图+时间+成熟度+敏感性 | 已实现 | |
| 6 | `input_guard.py` | §3 L3 | 参数护栏——schema+范围+危险模式 | 已实现 | |
| 7 | `sequence_guard.py` | §3 L4 | 序列护栏——操作序列追踪+禁止序列阻断 | 已实现 | |
| 8 | `output_guard.py` | §3 L5 | 输出护栏——PII脱敏+凭证检测+截断 | 已实现 | |
| 9 | `observability.py` | §3 L6 | 可观测性——OTEL指标+行为异常检测 | 已实现 | |
| 10 | `dry_run.py` | §3 L7 | 测试与模拟——影响分析+Dry-Run | 已实现 | |
| 11 | `rbac_roles.yaml` | §3 L0-L5 | 角色定义+ABAC规则+序列规则——从GOV-AI-001派生 | 已实现 | |
| 13 | `derive_rbac_roles.py` | §3 | 自动派生脚本——GOV-AI-001→rbac_roles.yaml | 已实现 | |
| 14 | `test_permissions.py` | §9 L7 | 权限自动化测试 | 已实现 | |
| 15 | `non_repudiation.py` | §3 横切面F | 不可抵赖操作绑定(Ed25519+Merkle Tree+TSA) | 已实现 | |
| 25 | `native_api_guard.py` | §3 横切面F | C扩展原生API绕过防护(ctypes封禁) | 已实现 | |
| `a2a_check.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `adversarial_resilience.py` | § — | — | 已实现 | | 本模块 |
| `agent_creation_policy.py` | § — | — | 已实现 | | 本模块 |
| `anomaly_detector.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `anti_pattern_guard.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `approver_check.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `asymmetric_audit.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `audit_log_guard.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `auto_maintenance.py` | § — | — | 已实现 | | 本模块 |
| `blind_spot_tracker.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `blueprint_fidelity.py` | § — | — | 已实现 | | 本模块 |
| `bootstrap_superadmin.py` | § — | — | 已实现 | | 本模块 |
| `bootstrap_verifier.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `build_sanitizer.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `cache_invalidation.py` | § — | — | 已实现 | | 本模块 |
| `canary_rollout_manager.py` | § — | — | 已实现 | | 本模块 |
| `capability_check.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `cascading_failure_isolator.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `cold_start_lock.py` | § — | — | 已实现 | | 本模块 |
| `compliance_matrix.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `context_drift_detector.py` | § — | — | 已实现 | | 本模块 |
| `continuous_verifier.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `contract_verifier.py` | § — | — | 已实现 | | 本模块 |
| `contracts.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `cross_cutting.py` | § — | — | 已实现 | | 本模块 |
| `cross_session_detector.py` | § — | — | 已实现 | | 本模块 |
| `cybersec_2026_guard.py` | § — | — | 已实现 | | 本模块 |
| `decision_explainer.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `decision_registry.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `defense_depth.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `dependency_auditor.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `emergency_override.py` | § — | — | 已实现 | | 本模块 |
| `engine_degradation.py` | § — | — | 已实现 | | 本模块 |
| `environment_manager.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `escalation_handler.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `exceptions.py` | § — | — | 已实现 | | 本模块 |
| `false_completion_detector.py` | § — | — | 已实现 | | 本模块 |
| `genesis_bootstrap.py` | § — | — | 已实现 | | 本模块 |
| `governance_bridges/a2a_check.py` | § — | — | 已废弃 (ARCH-035 删除) | | 本模块 |
| `governance_bridges/approver_check.py` | § — | — | 已废弃 (ARCH-035 删除) | | 本模块 |
| `governance_bridges/bootstrap_superadmin.py` | § — | — | 已废弃 (ARCH-035 合并到 root) | | 本模块 |
| `governance_bridges/capability_check.py` | § — | — | 已废弃 (ARCH-035 删除) | | 本模块 |
| `governance_bridges/contracts.py` | § — | — | 已废弃 (ARCH-035 删除) | | 本模块 |
| `guard_layers.py` | § — | — | 已实现 | | 本模块 |
| `integration.py` | § — | — | 已实现 | | 本模块 |
| `integrity_self_check.py` | § — | — | 已实现 | | 本模块 |
| `intent_binder.py` | § — | — | 已实现 | | 本模块 |
| `key_hierarchy.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `kill_switch.py` | § — | — | 已实现 | | 本模块 |
| `legal_audit_chain.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `memory_guard.py` | § — | — | 已实现 | | 本模块 |
| `memory_provenance_guard.py` | § — | — | 已实现 | | 本模块 |
| `micro_verifier.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `microstructure_defense.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `monotonic_clock.py` | § — | — | 已实现 | | 本模块 |
| `multi_agent_collusion_detector.py` | § — | — | 已实现 | | 本模块 |
| `novel_attack_guard.py` | § — | — | 已实现 | | 本模块 |
| `path_guard.py` | § — | — | 已实现 | | 本模块 |
| `permission_hooks.py` | § — | — | 已实现 | | 本模块 |
| `permission_mode_manager.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `phase_executor.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `post_action_verifier.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `replay_attack_guard.py` | § — | — | 已实现 | | 本模块 |
| `risk_mitigation.py` | § — | — | 已实现 | | 本模块 |
| `rollback_sandbox.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `rule_injection_guard.py` | § — | — | 已实现 | | 本模块 |
| `secrets_lifecycle.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `session_concurrency.py` | § — | — | 已实现 | | 本模块 |
| `session_lifecycle.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `shell_dialect_detector.py` | § — | — | stub (pending ARCH-036) | | 本模块 |
| `toctou_guard.py` | § — | — | 已实现 | | 本模块 |
| `vibe_coding_guard.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/agent-rbac/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| rbac_roles.yaml 与 GOV-AI-001 一致 | `python derive_rbac_roles.py --dry-run` | ☐ |
| 所有横切面F组件文件存在 | `ls src/zephyr/agent-rbac/*guard*.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.14.0 (基线) | L0-L7 七层 + 横切面 A-F 全部 67 个组件 | — | — |
| v1.1.0 (容量升级) | CAP-R01~R19 容量升级组件 | CAP-R01~R19 全部 | 待施工 |

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md) 线3:治理闭环
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §1 设计背景与目标

### §1.1 背景

| # | 痛点 | 后果 |
|---|------|------|
| 1 | 权限注册表(GOV-AI-001)是静态 .md 文档 | AI 可以不查注册表直接操作——规则形同虚设 |
| 2 | 没有 Agent 身份概念 | 无法区分"谁做了什么"——审计链断裂 |
| 3 | 没有 auto_guard 中间态 | AI 要么全自主、要么全阻断，缺少"先干后验"的信任梯度 |
| 4 | 权限检查不在执行路径上 | 权限是"建议"而非"强制"——绕过零成本 |
| 5 | 多 IDE 各自为政 | TRAE/Cursor/RooCode 各有自己的权限模型——无法统一管控 |
| 6 | 权限系统自身无保护 | AI 可以修改 rbac_roles.yaml 给自己提权——护栏可以被拆掉 |
| 7 | 无操作序列感知 | 单个操作合法，但多步组合可能构成数据外泄链 |
| 8 | 无行为异常检测 | 合法权限被异常模式滥用——凌晨3点批量删除 |
| 9 | 无横向越权防护 | Agent A 可以冒充 Agent B 的身份跨 session 操作 |
| 10 | 冷启动无锁 | 系统启动时权限配置尚未加载——Agent 在裸奔窗口内操作不受约束 |
| 11 | 无权限钩子 | 无法在权限判定前后注入自定义校验——扩展性为零 |
| 12 | Agent 可自我复制 | Agent 可以派生新 Agent 实例来绕过成熟度限制 |
| 13 | 权限缓存陈旧 | 权限紧急收紧后缓存中的旧 ALLOW 仍生效 5 分钟 |
| 14 | 无第三方包管控 | pip/npm install 的代码不受 Agent RBAC 约束 |
| 15 | 环境变量可篡改 | .env 等不在保护路径中——Agent 可修改系统运行环境 |
| 16 | 无 Owner 缺席策略 | Owner 离线数天时 auto_guard 操作如何处理——无定义 |

### §1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 七层纵深防御运行时权限强制执行 | 每次工具调用经过 19 个检查点，单次检查 < 1.8ms |
| 2 | Agent 身份注册与识别 | AgentIdentity 含 MaturityLevel + IDESource + SessionToken |
| 3 | 先干后验（auto_guard）模式 | 95% always_allow / 4% auto_guard / 1% blocked |
| 4 | GOV-AI-001 自动派生为可执行规则 | derive_rbac_roles.py 自动派生，消除手动复制漂移 |
| 5 | 209 项安全盲点全覆盖 | 94 项决策记录，66 个组件文件 |
| 6 | 六横切面运行时强制 | A权限钩子 + B权限拓扑 + C自动维护 + D意图绑定 + E对抗韧性 + F取证保障 |

### §1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 权限判定的触发时机 | → Gate Engine (MOD-GATE_ENGINE) |
| 2 | 权限审计日志的存储 | → Audit Trail (MOD-INF-020) |
| 3 | 回滚的具体执行 | → Rollback System (MOD-INF-021) |
| 4 | 熔断器的底层实现 | → Circuit Breaker (MOD-INF-022) |
| 5 | Prompt Injection 检测 | → Input Sanitizer / LSG (MOD-LLM_SECURITY) |
| 6 | 生产环境的实际部署 | → CI/CD |

### §1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 100% AI 开发，多 IDE 并发（TRAE / Cursor / RooCode） | 权限系统必须跨 IDE 统一，不能依赖单一 IDE 的审批机制 |
| 同时开启 10+ 对话 | 阻塞式审批 = 10 个对话全卡死——绝对不可接受 |
| 1 人 + AI，99% AI 维护 | 人工审批是最稀缺资源——必须最小化，能自动绝不人工 |
| 100% AI 施工 = 权限系统自身也是 AI 写的 | 权限层核心必须不可变——AI 不能修改自己的护栏 |
| Owner 可能缺席（出差/休假/离线） | 系统必须具备 Owner 缺席时的自治保守模式 |
| Vibe Coding AI 零记忆重启 | 权限规则必须自解释——每个规则旁边写清"为什么、谁定的、什么时间定的" |

---

## §2 模块边界

### §2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | Agent 身份注册与识别 | AgentIdentity + MaturityLevel 四级信任 + IDESource 多 IDE 支持 |
| 2 | 权限声明式配置 | GOV-AI-001 → rbac_roles.yaml 自动派生 |
| 3 | 七层+六横切面运行时 Permission Guard | L0→L5 + 横切面 A/B/C/D/E/F |
| 4 | auto_guard 后验失败 → auto-rollback | 后验失败自动回滚 |
| 5 | 全局 Kill Switch + Engine 降级策略 | 多触发器 + 降级攻击防护 |
| 6 | 操作序列追踪 + 危险序列阻断 | per-session + 跨 Session 关联 + Agent间隐式通信检测 |
| 7 | 权限模拟（Dry-Run）+ 影响分析 + 对抗性测试 | L7 Testing & Dry-Run |
| 8 | 横向越权防护 | SessionToken签名校验 + AgentIdentityVerifier |
| 9 | 冷启动锁 | 系统启动时全局拒绝直到权限配置加载校验通过 |
| 10 | 权限钩子系统 | pre/post/on_blocked/on_kill_switch 四类钩子 |
| 11 | Agent 创建权与权限遗传 | Agent 派生/复制的权限衰减继承 |
| 12 | 紧急覆盖令牌 | Owner签发的JIT临时越权令牌（<5分钟有效） |
| 13 | 规则自我修剪 | 僵尸规则检测 + 权限复杂度预算 |
| 14 | 第三方依赖管控 | package_install 白名单 |
| 15 | 网络边界管控 | Agent工具调用的network_target白名单 |
| 16 | 环境变量保护 | .env/pyproject.toml 等纳入保护路径 |

### §2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | Agent 的具体执行逻辑 | Orchestrator (MOD-TASK_SYSTEM) |
| 2 | 权限判定的触发时机 | Gate Engine (MOD-GATE_ENGINE) |
| 3 | 权限审计日志的存储 | Audit Trail (MOD-INF-020) |
| 4 | 回滚的具体执行 | Rollback System (MOD-INF-021) |
| 5 | 熔断器的底层实现 | Circuit Breaker (MOD-INF-022) |
| 6 | Prompt Injection 检测 | Input Sanitizer / LSG (MOD-LLM_SECURITY) |
| 7 | 生产环境的实际部署 | CI/CD |

---

## §3 架构设计

> 本节是蓝图的核心——七层纵深防御 + 六横切面的完整架构规格。
> 对标 57 个行业框架/论文/事故报告（完整列表见附录 B）。

### §3.0 总览：七层纵深防御 + 六横切面模型

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
│  ├── Rollback隔离——快照签名+rollback_storm熔断+回滚change audit          │
│  └── 对标 Grantex 30框架审计 + Google P0 + VibeGuard + Sherlock + SUSVIBES │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  L0: IMMUTABLE CORE (硬编码，AI不可改 — 兜底)                          │
│  ├── 保护路径列表(扩至OS级ACL双兜底) + 冷启动锁 + Kill Switch(8触发+隔离) │
│  ├── Engine降级策略(含降级攻击源检测+级联故障隔离)                        │
│  ├── Bootstrap哈希签名 + Python猴子补丁检测 + 路径解析安全               │
│  └── 权限配置自身的修改审计链 + 配置完整性hash                            │
│                                                                      │
│  L1: RBAC (角色权限) — 三层ALLOW/AUTO_GUARD/BLOCKED                    │
│  ├── Agent Identity + Role Bindings + SessionToken HMAC-SHA256签名     │
│  ├── Agent创建权 + 权限遗传衰减链 + 父子动态同步                         │
│  └── GOV-AI-001 → rbac_roles.yaml 自动派生                            │
│                                                                      │
│  L2: ABAC (属性权限) — 五维度感知                                       │
│  ├── 意图感知 + 时间窗口 + Maturity(四级) + 资源敏感性 + per-Agent TLB   │
│  ├── Context Drift Detection——操作链中意图漂移实时检测(新增)             │
│  └── 标签篡改自动还原 + Inference合成泄漏检测                            │
│                                                                      │
│  L3: INPUT GUARD (参数护栏) — 六类规则                                  │
│  ├── 参数Schema + 危险模式 + package_install + network_target          │
│  ├── env操作保护 + MCP Server身份校验(新增)                              │
│  └── File Lock生命周期管理(死锁检测+超时释放)                            │
│                                                                      │
│  L4: SEQUENCE GUARD (序列护栏) — 四维追踪                               │
│  ├── 会话内序列 + 跨Session关联 + Agent间Covert Channel                │
│  ├── Multi-Agent Emergent Behavior Detection(新增)——涌现行为检测        │
│  └── 先干后验→Micro-Verified先干后验——每步骤微型验证(新增)                │
│                                                                      │
│  L5: OUTPUT GUARD (输出护栏)                                           │
│  ├── PII脱敏 + 凭证检测 + 大小截断 + Synthesis Leakage Detection(新增)   │
│  └── 文件变更差异摘要 + 跨步结果一致性校验(新增)                          │
│                                                                      │
│  L6: OBSERVABILITY (可观测性)                                          │
│  ├── OTEL指标(含指标防篡改) + 告警信噪比 + 规则效果评估 + 行为异常        │
│  ├── Continuous Verification Metrics(新增)——每一步重验证成功率          │
│  └── 权限决策自解释输出(给Agent的结构化拒绝原因——新增)                     │
│                                                                      │
│  L7: TESTING & DRY-RUN (测试与模拟)                                     │
│  ├── 影响分析(含权限拓扑图) + Dry-Run + 对抗性测试 + 环境隔离 + 跨模型    │
│  ├── Chaos Permission Testing——混沌权限测试(新增)                       │
│  ├── Edge Case Enumeration——55→95项盲点全覆盖自动化测试(新增)            │
│  └── Multi-Agent Scenario Tests——多Agent协同场景穷举(新增)               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**七层+六横切面执行顺序**（每次工具调用均经过）：
```
横切面A pre_check_hook → L0冷启动锁 → 横切面D Intent绑定校验(意图一致+权限模式) → L0不可变核心 + OS ACL双兜底(含Bootstrap签名验证+猴子补丁检测) → 横切面F路径解析安全(空格/Unicode/嵌套引号) → L1 RBAC(含横向越权+Ed25519身份签名) → L2 ABAC(含Context Drift+Inference检测) → 横切面F跨平台Shell安全(方言检测) → L3 参数护栏(含MCP Server身份+编码解码+规则语言注入防护) → [横切面D 每步连续重验证+横切面F nonce防重放] → L4 序列护栏(含涌现行为+GroupGuard合谋+不可抵赖签名绑定) → [Micro-Verified 执行: 每步执行→L4微验证→下一子步] → L5 输出护栏(含合成泄漏+虚假完成+构建产物扫描) → L6 可观测性(含自解释输出+激励审计+Merkle完整性验证) → 横切面A post_check_hook → [横切面D Cascading Failure隔离检查+横切面F Rollback隔离检查]
```

**各层检查耗时预算**（总预算 < 1.8ms，含六横切面）：
| 层级 | 预算 | 新增维度 |
|------|:---:|------|
| 横切面A pre_hook | ~0.05ms | — |
| 横切面D Intent Bind | ~0.08ms | IBAC校验 |
| L0 冷启动锁+Bootstrap | ~0.02ms | +Bootstrap签名验证 |
| L0 Immutable Core+补丁检测 | ~0.03ms | +OS ACL+猴子补丁检测 |
| 横切面F 路径解析安全 | ~0.08ms | 🆕 路径解析+沙箱预演 |
| 横切面F 跨平台Shell | ~0.05ms | 🆕 方言检测 |
| L1 RBAC + 横向越权+Ed25519 | ~0.12ms | +Ed25519身份签名 |
| 横切面D Continuous Verify | ~0.05ms | 每步重验证 |
| 横切面F nonce防重放 | ~0.03ms | 🆕 Bloom Filter检查 |
| L2 ABAC + TLB + Drift | ~0.25ms | +Context Drift+Inference |
| L3 Input Guard+规则注入 | ~0.30ms | +MCP身份+FileLock+规则语言注入 |
| L4 Sequence + Emergent+NR | ~0.40ms | +涌现行为+GroupGuard+不可抵赖绑定 |
| L5 Output + Synthesis+产物 | ~0.20ms | +合成泄漏+虚假完成+构建产物扫描 |
| L6 Observability + Explain+Merkle | ~0.12ms | +自解释+激励审计+Merkle验证 |
| 横切面A post_hook | ~0.05ms | — |
| 横切面D Cascade Check | ~0.03ms | 级联故障检查 |
| 横切面F Rollback隔离 | ~0.02ms | 🆕 回滚安全检查 |
| **合计** | **< 1.8ms** | |

### 3.1 L0 — 不可变核心（决策 D-018-04）

> **决策 D-018-04**：建立硬编码不可变核心层——AI 在任何情况下都不可修改的保护路径和全局安全规则。这是整个权限系统的基石——如果 AI 能修改自己的护栏，护栏就不存在。
>
> **决策依据**：100% AI施工场景下，权限系统自身是 AI 写的代码。参考：Claude Code protected paths等

```yaml
immutable_core:
  # ─── 保护路径（硬编码，不可通过任何 YAML 覆盖）───
  protected_paths:
    - path: ".git/**"
      reason: "仓库状态——不可逆破坏"
    - path: "src/zephyr/agent-rbac/**"
      reason: "权限系统自身——不能被 AI 修改自己的护栏"
    - path: "docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md"
      reason: "权限蓝图——唯一真源"
    - path: "AGENTS.md"
      reason: "核心原则——AI 行为宪法"
    - path: "docs/01_policies_and_standards/governance/**"
      reason: "治理规则——policy-as-code 真源"
    - path: "src/zephyr/governance/rule_enforcement/_registry.yaml"
      reason: "门禁注册表——门禁体系 SSoT"
    - path: ".pre-commit-config.yaml"
      reason: "CI 护栏——pre-commit 检查定义"
    - path: "src/zephyr/security/llm_defense/llm_security/process_sandbox.py"
      reason: "沙箱实现——安全边界代码"
    - path: "data/telemetry/audit/**"
      reason: "审计日志——不可变追溯链"
    # ─── v0.4.0 扩展保护路径 ───
    - path: "**/.env*"
      reason: "环境变量——影响全系统运行时配置"
    - path: "pyproject.toml"
      reason: "项目配置——pytest markers/依赖/dependencies定义"
    - path: ".github/workflows/**"
      reason: "CI管线——Agent不可修改自动执行的工作流"
    - path: "docker-compose*.yml"
      reason: "容器编排——影响服务部署拓扑"
    - path: "config/nav_table_mapping.yaml"
      reason: "导航表映射——AI新session的流程入口配置"
    - path: "scripts/governance/_shared/**"
      reason: "共享工具库——审计脚本的公共依赖"

  # ─── 保护文件标记（frontmatter 中声明即受保护）───
  protected_metadata:
    - frontmatter_tag: "ttl: permanent"
      reason: "永不过期的文档——删除 = 不可逆损失"
    - frontmatter_tag: "status: active"
      reason: "活跃治理规则——修改需审批"
    - frontmatter_tag: "immutable: true"
      reason: "显式不可变标记——最高保护级别"

  # ─── 硬编码禁止操作（即使 rbac_roles.yaml 说 allow 也不行）───
  always_blocked:
    - operation: "modify_immutable_core"
      description: "修改 L0 不可变核心代码/配置"
    - operation: "delete_audit_logs"
      description: "删除或篡改审计日志"
    - operation: "modify_self_permissions"
      description: "Agent 修改自身或同级的权限配置"
    - operation: "disable_kill_switch"
      description: "禁用或绕过全局熔断器"
    - operation: "shell_true_execution"
      description: "执行 shell=True 的子进程"
    - operation: "circumvent_gate_engine"
      description: "绕过 Gate Engine 直接操作"
    - operation: "write_to_protected_paths"
      description: "写入 L0 protected_paths 中任何路径"
    - operation: "spawn_new_agent_unsanctioned"
      description: "未经授权创建/派生新 Agent 实例"
    - operation: "forge_agent_identity"
      description: "跨 Session 伪造 Agent 身份或篡改 maturity_level"
    - operation: "modify_environment_variables"
      description: "修改 .env 或运行时环境变量"
    # ─── v0.5.0 新增 ───
    - operation: "os_acl_bypass"
      description: "绕过OS级文件系统ACL保护"
    - operation: "synthesize_restricted_data"
      description: "跨多个公开数据源合成出受限级别的敏感信息"
    - operation: "cascade_failure_trigger"
      description: "操作的输出作为下游Agent输入时引发级联故障"
    - operation: "circumvent_micro_verification"
      description: "在Micro-Verified执行中跳过子步骤验证"

  # ─── 冷启动锁（v0.4.0 新增）───
  startup_lock:
    behavior: "系统启动时全局拒绝所有Agent操作——直到 rbac_roles.yaml 加载并通过完整性校验"
    check_order: "L0 冷启动锁在所有其他检查之前——最先执行，加载前拒绝一切"
    release_condition: "rbac_roles.yaml hash校验通过 + L0 immutable_core路径存在性验证通过"
    timeout: "30秒内未加载成功 → 系统进入 maintenance_mode（仅Owner可操作）"
    maintenance_mode: "所有Agent操作BLOCKED，Owner手动确认后可逐层释放"
    indicator: "Agent RBAC Cold Start: awaiting permission config load ({elapsed}s)"
    metric: "agent-rbac.cold_start.duration_seconds"

  enforcement: "最先执行、不可覆盖、不可绕过。违反 = 硬阻断 + P0 审计告警 + 无例外"

  # ─── v0.5.0 OS 级 ACL 双重兜底 ───
  os_acl_protection:
    description: "L0 不可变核心的物理层兜底——在文件系统层面设置只读ACL作为第二道防线"
    mechanism: |
      在 Windows: icacls 设置只读权限
      在 Linux/macOS: chattr +i 设置不可变属性
      这些 OS 级保护在 L0 硬编码之上形成物理层面的防篡改
    protected_dirs:
      - ".git/"
      - "src/zephyr/agent-rbac/"
      - "data/telemetry/audit/"
    enforcement_chain: "Agent 操作 → L0 Python 硬编码检查 → 即使 Python 层被绕过 → OS ACL 仍然阻止文件系统操作"
    monitoring: "每次 OS ACL 被触发（即 Python 层未拦截但 OS 层拦截了）= P0 安全事件——说明 L0 可能已被绕过"
```
```

### 3.2 L0 — Kill Switch 全局熔断（决策 D-018-05）

> **决策 D-018-05**：建立全局 Kill Switch——当 Agent 行为模式触发危险阈值时，自动熔断所有 Agent 操作。
>
> **决策依据**：CSA Agentic Trust Framework Incident Response 要素——"What if you go rogue?"必须有答案。参考： K8s Circuit Breaker + 交易系统熔断。...

```yaml
kill_switch:
  # ─── 自动熔断触发器 ───
  auto_triggers:
    - trigger: "rapid_file_deletion"
      condition: "同一 Agent 在 5 秒内删除 >= 3 个非 temporary 文件"
      action: "立即阻断该 Agent + 全局 warning"
      cooldown: "30 秒后自动解除（Owner 可手动延长）"

    - trigger: "permission_boundary_probe"
      condition: "同一 Agent 在 2 分钟内触发 >= 5 次 BLOCKED 判定"
      action: "立即阻断该 Agent + P0 审计告警"
      cooldown: "Owner 手动解除"

    - trigger: "suspicious_sequence"
      condition: "L4 Sequence Guard 在 1 分钟内触发 >= 2 次"
      action: "立即阻断该 Agent + 安全事件记录"
      cooldown: "Owner 手动解除"

    - trigger: "off_hours_destructive"
      condition: "非工作时间（22:00-06:00）执行 auto_guard 级别操作"
      action: "操作降级为 blocked，需 Owner 确认"
      cooldown: "工作时间自动解除"

    - trigger: "config_file_blitz"
      condition: "同一 Agent 在 60 秒内修改 >= 10 个 YAML 文件"
      action: "全局熔断——所有 Agent 暂停写操作"
      cooldown: "Owner 手动解除"

    # ─── v0.4.0 新增熔断触发器 ───
    - trigger: "signal_noise_attack"
      condition: "L6 异常告警密度在 5 分钟内 > 历史基线 P99 * 10（噪音攻击——Agent在攻击前淹没告警系统）"
      action: "告警系统进入高敏感模式 + 所有 Agent 操作降级为 auto_guard"
      cooldown: "告警密度回归正常后自动解除"

    - trigger: "sensitivity_label_blitz"
      condition: "同一 Agent 在 60 秒内修改 >= 5 个文件的 sensitivity frontmatter 标签"
      action: "立即阻断该 Agent + 所有被修改文件的 sensitivity 锁定为修改前值"
      cooldown: "Owner 手动解除"

    - trigger: "agent_spawn_storm"
      condition: "同一父 Agent 在 5 分钟内创建 >= 3 个子 Agent"
      action: "阻断父 Agent + 立即终止所有子 Agent"
      cooldown: "Owner 手动解除"

  # ─── v0.4.0 熔断源隔离策略 ───
  isolation_policy:
    single_agent_trigger: "仅阻断触发 Agent，不全局熔断——防止恶意Agent通过制造异常来DDoS合法Agent"
    multi_agent_trigger: ">= 2 个不同 Agent 在同一时间段触发同类熔断 → 升级为全局熔断"
    degradation_attack_protection: "如果同一 Agent 触发的降级导致该Agent所在层崩溃 → 该Agent立即BLOCKED（而非降级为partial_failure放行）"

  # ─── 手动熔断（Owner 随时执行）───
  manual_triggers:
    - "全局紧急熔断——终止所有 Agent 写操作"
    - "单 Agent 熔断——终止指定 Agent 的所有操作"

  # ─── 熔断状态记录 ───
  state_persistence: "SQLite circuit_breaker_state 表（已有 GateEngine 实现）"
  audit: "每次熔断触发/解除均写入不可变审计日志"
```

### 3.3 L0 — Engine 降级策略（决策 D-018-06）

> **决策 D-018-06**：Permission Engine 自身故障时的降级策略——崩 = blocked（绝对不放行），而非崩 = pass（裸奔）。
>
> **决策依据**：负面偏好——权限系统失效时，安全优先于便利。实现方式。参考： GateEngine v2.0 的 failurePolicy。...

```yaml
engine_degradation:
  # ─── 三层降级策略 ───
  l0_immutable_core_failure:
    behavior: "BLOCKED — 系统启动失败。不可变核心是最后防线，坏了就全停"
    indicator: "Agent RBAC system unavailable: Immutable Core failed"

  l1_l6_failure:
    behavior: "BLOCKED — 降级为拒绝模式。宁可误杀不可漏放"
    indicator: "Agent RBAC degraded to BLOCKED: runtime permission check unavailable"
    fallback_audit: "所有被降级拒绝的操作均记录原因"

  partial_failure:
    behavior: "按层降级——L4 崩不影响 L0-L3 继续执行"
    indicator: "Agent RBAC partial degradation: {failed_layer} unavailable"
    metric: "d2.authz.decision.degraded counter"
    # ─── v0.4.0 降级攻击防护 ───
    attack_protection: "记录触发降级的操作来源Agent。如果同一Agent触发的降级事件 > 2次/小时 → 该Agent立即BLOCKED + 标记为'疑似降级攻击'"
    causal_chain: "partial_failure中失败的层之前最后操作的Agent → 关联分析 → 累计 → BLOCKED"
    degraded_layer_bypass: "降级事件发生时，触发降级的Agent所在的层就算恢复了也不能对该Agent放行——需Owner手动审核后才能解除"

  # ─── 降级恢复 ───
  recovery:
    auto: "L0 每 30 秒自检一次，恢复即自动解除降级"
    manual: "Owner 可随时强制解除降级状态"
    audit: "降级/恢复事件写入审计日志"
```

---

### 3.4 L1 — RBAC 三层权限模型（决策 D-018-01：95/4/1 分布）

> **决策 D-018-01**：采用三层权限模型，分布为 always_allow 95% / auto_guard 4% / blocked 1%。取消 needs_approval 层——要么 auto_guard（先干后验），要么 blocked（绝对不让干）。人工审批是最稀缺资源，不应消耗在权限判定上。
>
> **决策依据**：1人+AI场景，10+并发对话，物理上不可能实时审批。参考： Claude Code 90% always allow + Cursor 自动编辑 + Terraform auto-apply。...

```yaml
permission_levels:
  always_allow:
    description: "默认允许——95%的操作走这条路"
    distribution: "95%"
    philosophy: "信任默认——AI 直接干，不拦截"
    examples:
      - "读写 src/ 代码"
      - "创建/修改/删除非 permanent 文件"
      - "运行审计脚本、测试、lint"
      - "修改 YAML 配置文件"
      - "创建任务卡、修改任务状态"
      - "读取蓝图文档"
      - "创建新模块目录"
    enforcement: "L0 immutable_core 预检 → L1 RBAC 放行 → L2 ABAC 二次确认 → L3 参数护栏 → L4 序列记录"

  auto_guard:
    description: "先干后验——AI 先执行，自动护栏后验，失败自动回滚"
    distribution: "4%"
    philosophy: "信任但验证——让 AI 先干，用自动化护栏兜底"
    examples:
      - "修改架构 YAML（CI 门禁后验 schema 合规）"
      - "修改蓝图接口契约 §3（AST 级对比后验）"
      - "修改 .pre-commit-config.yaml（CI 后验语法正确）"
      - "批量修改 5+ 文件（drift detector 后验一致性）"
    enforcement: "L0 预检 → L1 标记 AUTO_GUARD → L2 ABAC 二次确认 → AI 执行 → pre-commit/CI 自动检查 → 失败则 auto-rollback (MOD-INF-021) → L6 审计"
    fallback: "后验失败 → 自动回滚 → 审计告警 → Owner 异步审阅"

  blocked:
    description: "绝对禁止——不可逆操作 + 不可变核心保护路径"
    distribution: "1%"
    philosophy: "边界拦截——这些操作连 AI 都不该想"
    examples:
      - "删除 ttl:permanent 文件"
      - "修改 AGENTS.md 核心原则"
      - "绕过门禁直接修改任务状态"
      - "执行 shell=True 的子进程"
      - "修改 L0 immutable_core 标记的文件"
      - "删除审计日志"
      - "修改 src/zephyr/agent-rbac/ 自身"
    enforcement: "L0 硬阻断 + 审计告警 + 没有例外 + 不进入后续层"
```

---

### 3.5 L2 — ABAC 属性权限（决策 D-018-07）

> **决策 D-018-07**：在 RBAC 静态角色之上增加 ABAC 动态属性层——同一 Agent 在不同上下文中有不同权限。包含意图感知、时间窗口、Agent 成熟度、资源敏感性四维属性。
>
> **决策依据**：RBAC 只能回答"这个人通常能做什么"，ABAC 回答"这次任务是否应该在这个时间、访问这批数据、触发这类动作"。参考：企业级 Agent 四层设计（身份层→策略层→执行层→审计层）+ CSA ATF Behavior 要素 + D2 Input Guard。...

```yaml
abac_dimensions:
  # ─── 维度 1：意图感知 ───
  intent_aware:
    description: "Agent 权限 = 基础角色权限 ∩ 当前任务所需权限集"
    mechanism: "TaskCard 创建时声明 required_permissions，PermissionGuard 交叉匹配"
    example: |
      Agent(role=implementer, task=refactor) → 有 write_src 权限
      Agent(role=implementer, task=deploy)   → 有 write_config 权限，无 write_src 权限
      Agent(role=implementer, task=audit)    → 只有 readonly 权限

  # ─── 维度 2：时间窗口 ───
  temporal:
    description: "always_allow 不应凌晨3点也允许"
    rules:
      - window: "working_hours (06:00-22:00)"
        effect: "所有 L1 RBAC 权限正常执行"
      - window: "off_hours (22:00-06:00)"
        effect: "auto_guard 操作降级为 blocked；always_allow 只读操作不变，写操作降级为 auto_guard"
      - window: "frozen_periods (配置化冻结期)"
        effect: "所有写操作降级为 blocked"
    mechanism: "复用 GateEngine _check_temporal 逻辑，在 L2 ABAC 层集成"

  # ─── 维度 3：Agent 成熟度 ───
  maturity:
    description: "Agent 不是天生信任——信任是挣来的"
    levels:
      L1_INTERN:
        name: "Intern（见习）"
        trust_requirement: "完成 < 5 个任务"
        max_autonomy: "所有 auto_guard 操作降级为 blocked"
        blocked_operations: "修改 > 3 个文件、修改架构 YAML、修改蓝图"

      L2_JUNIOR:
        name: "Junior（初级）"
        trust_requirement: "完成 5-20 个任务，auto_guard 后验通过率 > 80%"
        max_autonomy: "always_allow 正常 + auto_guard 限制在 2 文件以内"
        blocked_operations: "删除 permanent 文件"

      L3_SENIOR:
        name: "Senior（高级）"
        trust_requirement: "完成 20-100 个任务，后验通过率 > 95%，无安全事件"
        max_autonomy: "always_allow + auto_guard 全功能"
        blocked_operations: "仅 L0 immutable_core 操作"

      L4_PRINCIPAL:
        name: "Principal（首席）"
        trust_requirement: "完成 > 100 个任务，零安全事故，后验通过率 > 99%"
        max_autonomy: "最大自治"
        blocked_operations: "仅 L0 immutable_core 操作"
        note: "仍需 L3-L5 护栏保护"

    maturity_upgrade: "自动计算 + Owner 审核（不自动升级到 L3+）"
    maturity_downgrade: "安全事故自动降级到 L1 Intern"

  # ─── 维度 4：资源敏感性 ───
  resource_sensitivity:
    description: "不同资源有不同的敏感性标签"
    levels:
      public: "src/ 代码、docs/ 文档——默认可操作"
      internal: "config/ 配置、scripts/ 脚本——可操作但需审计"
      sensitive: "data/ 数据、secrets/ 密钥——auto_guard 起"
      restricted: "L0 protected paths——blocked 无例外"
    mechanism: "路径前缀匹配 + frontmatter 标签判定"
    # ─── v0.4.0 标签篡改防护 ───
    tamper_protection:
      detection: "批量修改 sensitivity 标签 → 触发 Kill Switch (sensitivity_label_blitz)"
      rollback: "被非授权修改的 sensitivity 标签自动还原为修改前值"
      audit: "每次 sensitivity 标签变更记录 {who, what, from_value, to_value, why}"

  # ─── v0.4.0 维度 5：per-Agent Rate Limiting（事前限流）───
  rate_limiting:
    description: "Token Bucket (TLB) 式的 per-Agent 操作频率限制——事前限流，而非事后熔断"
    mechanism: "每个 Agent 维护独立的 Token Bucket（refill_rate / burst_size）"
    buckets:
      file_write:
        refill_rate: "20 tokens/s"
        burst_size: 50
        description: "写文件限流——防批量破坏"
      file_delete:
        refill_rate: "3 tokens/s"
        burst_size: 5
        description: "删除文件严格限流——这是最危险的操作之一"
      network_call:
        refill_rate: "5 tokens/s"
        burst_size: 10
        description: "网络请求限流——防数据外泄"
      shell_exec:
        refill_rate: "1 tokens/s"
        burst_size: 2
        description: "命令执行严格限流"
    violation_action: "超出burst → BLOCKED（不等待bucket恢复）+ 审计告警"
    tiered_by_maturity:
      L1_INTERN: "所有bucket size = 默认值 * 0.5"
      L2_JUNIOR: "所有bucket size = 默认值 * 0.8"
      L3_SENIOR: "使用默认值"
      L4_PRINCIPAL: "使用默认值 * 1.5"
```

---

### 3.6 L3 — Input Guard 参数护栏（决策 D-018-08）

> **决策 D-018-08**：在 Tool 调用参数级别增加护栏——同一 Tool 的不同参数应有不同权限。操作对象路径白名单 + 参数值范围限制 + 危险模式检测。
>
> **决策依据**：D2 四层模型的第2层——"Validate arguments before execution"。权限颗粒度从 Tool 级细化到参数级。

```yaml
input_guardrails:
  # ─── 规则类型 ───
  rule_types:
    schema_validation:
      description: "参数类型/结构校验"
      example: |
        tool: "file_write"
        guardrails:
          input:
            - field: "file_path"
              not_matches: "src/zephyr/agent-rbac/"
            - field: "content"
              max_bytes: 1048576  # 1MB 上限

    range_constraint:
      description: "参数值范围限制"
      example: |
        tool: "run_command"
        guardrails:
          input:
            - field: "timeout"
              min: 1
              max: 300  # 最多 5 分钟
            - field: "cmd"
              maxLength: 2000

    pattern_detection:
      description: "危险模式检测——在参数进入 Tool 前拦截"
      example: |
        tool: "database_query"
        guardrails:
          input:
            - field: "query"
              not_contains: ["DROP TABLE", "DROP DATABASE", "TRUNCATE"]
              not_matches: "(?i)delete\\s+from\\s+users"
            - field: "query"
              maxLength: 4000

    path_scope:
      description: "操作对象路径白名单/黑名单"
      example: |
        tool: "file_delete"
        guardrails:
          input:
            - field: "path"
              not_matches: "docs/01_policies_and_standards/"
              not_matches: "src/zephyr/agent-rbac/"
              not_matches: "\\.git/"

    # ─── v0.4.0 新增规则类型 ───
    package_install_guard:
      description: "第三方包安装的白名单管控——pip/npm install 的包名必须在允许列表中"
      example: |
        tool: "run_command"
        guardrails:
          input:
            - field: "cmd"
              if_matches: "(pip|pip3|python -m pip)\\s+install"
              allowed_packages: ["pytest", "ruff", "black", "mypy", "libcst", "pyyaml"]
              blocked_packages: ["*"]  # 不在白名单的一律blocked
            - field: "cmd"
              if_matches: "npm\\s+install"
              allowed_packages: ["prettier", "eslint"]
              blocked_packages: ["*"]

    network_target_guard:
      description: "Agent工具调用的网络目标URL白名单/黑名单"
      example: |
        tool: "web_fetch"
        guardrails:
          input:
            - field: "url"
              allowed_domains: ["github.com", "pypi.org", "docs.python.org"]
              blocked_domains: ["pastebin.com", "termbin.com", "*.ngrok.io"]
        tool: "run_command"
        guardrails:
          input:
            - field: "cmd"
              if_matches: "(curl|wget|Invoke-WebRequest)"
              allowed_domains: ["github.com", "pypi.org"]

    env_variable_guard:
      description: "环境变量操作的保护——修改.env或set环境变量需要auto_guard起"
      example: |
        tool: "file_write"
        guardrails:
          input:
            - field: "file_path"
              if_matches: "\\.env"
              force_auto_guard: true  # 即使L1判为always_allow也升级为auto_guard

  # ─── L3 判定逻辑 ───
  enforcement: "L1/L2 通过后 → L3 检查参数 → 违规 = BLOCKED + 安全事件"
  fallback: "L3 规则缺失的工具 → 标记为 auto_guard（未知参数=不安全）"
```

---

### 3.7 L4 — Sequence Guard 序列护栏（决策 D-018-09，**最关键的盲点补丁**）

> **决策 D-018-09**：建立会话级操作序列追踪与阻断——单个操作可能合法，但多步组合可能构成攻击链。这是防御 Prompt Injection 和数据外泄的最后一公里。
>
> **决策依据**：D2 四层模型的第3层 Sequence Enforcement。安全研究表明：Agent 攻击不是单步的，而是通过合法操作组成的链条。如 `read_sensitive_data → send_email` 构成数据外泄。

```yaml
sequence_guard:
  # ─── 会话级序列追踪 ───
  tracking:
    scope: "per-session per-agent（每个 Agent 会话独立追踪）"
    window: "最近 20 次操作（滑动窗口）"
    storage: "内存内环形缓冲区（< 1KB per session）"

  # ─── 禁止序列规则 ───
  forbidden_sequences:
    # 数据外泄链
    - name: "prevent_data_exfiltration_via_email"
      sequence: [read_sensitive, send_email]
      reason: "读取敏感数据后发送邮件 = 数据外泄"
      action: BLOCKED

    - name: "prevent_data_exfiltration_via_http"
      sequence: [read_sensitive, http_post_external]
      reason: "读取敏感数据后对外 POST = 数据外泄"
      action: BLOCKED

    - name: "prevent_data_exfiltration_via_file"
      sequence: [read_sensitive, write_to_public_dir]
      reason: "读取敏感数据后写入公开目录 = 侧信道泄漏"
      action: BLOCKED

    # 权限提升链
    - name: "prevent_privilege_escalation"
      sequence: [read_rbac_config, write_rbac_config]
      reason: "读取权限配置后修改 = 提权"
      action: BLOCKED

    # 破坏链
    - name: "prevent_mass_destruction"
      sequence: [list_files, delete_multiple_permanent]
      reason: "扫描文件后批量删除永久文件 = 破坏"
      action: BLOCKED

    # 绕过链
    - name: "prevent_gate_circumvention"
      sequence: [modify_gate_config, bypass_gate_check]
      reason: "修改门禁配置后绕过检查 = 护栏拆除"
      action: BLOCKED

  # ─── 高风险序列（不阻断，但触发热熔断候选）───
  high_risk_sequences:
    - name: "suspicious_config_sweep"
      sequence: [read_multiple_configs, write_multiple_configs]
      reason: "大量读取配置后大量修改 = 可疑"
      action: "记录风险分数，累计触发 L0 Kill Switch"

    - name: "credentials_touch"
      sequence: [read_any, access_credential_store]
      reason: "任何读取后访问凭证库 = 高风险"
      action: "强制 L2 ABAC 重新验证 + 审计告警"

  # ─── 序列冲突解决方案 ───
  sequence_timeout: "同一序列在 300 秒内的两次操作才算序列命中（避免跨会话误报）"
  sequence_bypass: "Owner 可在 audit 中标记合法序列白名单（如正常的 read_config→write_config）"

  # ─── v0.4.0 跨Session关联检测 ───
  cross_session_correlation:
    description: "两个不同Session的Agent可能通过文件系统进行隐式协作来绕过单Session序列护栏"
    detection_rules:
      - name: "cross_session_data_exfiltration"
        condition: "Session-A Agent读取敏感数据 → (5分钟内) Session-B Agent执行网络请求"
        action: "两个Session同时标记为高风险 + 审计告警"
      - name: "cross_session_permission_escalation"
        condition: "Session-A Agent查询权限配置 → (5分钟内) Session-B Agent修改同一配置"
        action: "BLOCKED + 两个Agent同时标记为'疑似合谋'"
    storage: "共享的跨Session操作关联索引（SQLite memory table，保留最近60分钟）"

  # ─── v0.4.0 Agent间隐式通信检测 ───
  inter_agent_communication_detection:
    description: "Agent可以通过文件写入/读取进行隐式通信（Covert Channel）"
    patterns:
      - name: "file_system_covert_channel"
        condition: "Agent A写入非项目文件 → Agent B在1分钟内读取同一文件 → Agent B执行高危操作"
        action: "Agent B的操作降级为 auto_guard + 追溯Agent A的写入意图"
      - name: "shared_memory_covert_channel"
        condition: "两个不同IDE的Agent在同一临时目录高频交替读写"
        action: "两个Agent同时标记 + 临时目录权限收紧"
```

---

### 3.8 L5 — Output Guard 输出护栏（决策 D-018-10）

> **决策 D-018-10**：Tool 执行后的输出也需要护栏——防止敏感数据泄漏到日志/Terminal/下游 Tool。
>
> **决策依据**：D2 四层模型的第4层——"Validate & sanitize after execution"。在 Agent 管道中，输出也是下一跳的输入。

```yaml
output_guardrails:
  # ─── 规则类型 ───
  rule_types:
    pii_redaction:
      description: "检测并脱敏输出中的个人身份信息"
      patterns:
        - type: "email"
          pattern: "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
          action: "redact → [EMAIL_REDACTED]"
        - type: "chinese_id"
          pattern: "\\d{17}[\\dXx]"
          action: "redact → [ID_REDACTED]"
        - type: "phone"
          pattern: "1[3-9]\\d{9}"
          action: "redact → [PHONE_REDACTED]"

    credential_detection:
      description: "检测输出中的凭证泄漏（复用 GateEngine secrets_detection 模式）"
      patterns:
        - "sk-[A-Za-z0-9]{32,}"
        - "-----BEGIN.*PRIVATE KEY-----"
        - "(?:api[_-]?key|apikey)\\s*[:=]\\s*['\"][A-Za-z0-9_\\-]{16,}['\"]"
      action: "redact → [CREDENTIAL_REDACTED] + P0 安全告警"

    size_truncation:
      description: "输出大小截断——防日志/终端轰炸"
      rules:
        - tool: "file_read"
          max_output_bytes: 51200  # 50KB
        - tool: "run_command"
          max_output_bytes: 102400  # 100KB
        - default:
          max_output_bytes: 65536  # 64KB 全局默认
      action: "truncate + 附加元数据 {truncated: true, original_size: N}"

    diff_summary:
      description: "文件变更时生成差异摘要——帮助 L6 行为异常检测"
      applies_to: ["file_write", "file_edit", "apply_patch"]
      output_format: "{lines_added: N, lines_removed: M, files_touched: K}"
```

---

### 3.9 L6 — Observability 可观测性（决策 D-018-11）

> **决策 D-018-11**：权限系统自身必须具备完整的可观测性——权限决策耗时、异常行为模式、权限变更审计。没有可观测性 = 不知道有没有被绕过。
>
> **决策依据**：D2 Telemetry & Observability 模式 + OpenTelemetry 标准。参考： CSA ATF Behavior 要素。...

```yaml
observability:
  # ─── OpenTelemetry 指标 ───
  metrics:
    - metric: "agent-rbac.decision.total"
      type: Counter
      labels: [agent_id, agent_type, ide_source, tool_id, decision, layer]
      description: "各层权限判定计数"

    - metric: "agent-rbac.decision.latency_us"
      type: Histogram
      buckets: [50, 100, 200, 500, 1000, 2000]  # 微秒级
      description: "单层/总权限判定耗时"

    - metric: "agent-rbac.sequence.violation"
      type: Counter
      labels: [agent_id, sequence_name]
      description: "L4 序列护栏触发次数"

    - metric: "agent-rbac.kill_switch.state"
      type: Gauge
      values: [0=normal, 1=agent_blocked, 2=global_blocked]
      description: "Kill Switch 当前状态"

    - metric: "agent-rbac.engine.degraded"
      type: Gauge
      values: [0=full, 1=partial, 2=blocked_all]
      description: "Engine 降级状态"

    - metric: "agent-rbac.policy.bundle.age_seconds"
      type: Gauge
      description: "当前权限配置年龄——检测配置更新延迟"

  # ─── 行为异常检测规则 ───
  anomaly_detection:
    rules:
      - name: "unusual_tool_frequency"
        description: "Agent 在短时间内调用某 Tool 的次数远超历史基线"
        detection: "当前窗口调用次数 > 历史 P99 * 3"

      - name: "unusual_decision_pattern"
        description: "Agent 被 BLOCKED 的比例突然升高"
        detection: "5 分钟内 BLOCKED 率 > 20%"

      - name: "new_tool_first_use"
        description: "Agent 首次调用新的敏感 Tool"
        detection: "Agent 历史中无此 Tool + Tool 属于 auto_guard 级别"

    action: "触发告警 → 写入审计日志 → 不自动阻断（需要上下文判断），但累计触发 L0 Kill Switch"

  signal_ownership: "L6 异常检测规则产生的信号 MUST 通过 MOD-INF-015 (Telemetry) 上报和存储，RBAC 不独立存储检测结果"

  # ─── 权限变更审计 ───
  policy_audit:
    tracked_changes:
      - "rbac_roles.yaml 的任何修改"
      - "GOV-AI-001 的任何修改"
      - "L0 immutable_core 路径列表的任何修改"
    audit_fields: [who, what, when, why, diff, approved_by]
    storage: "不可变审计日志 + Git commit 关联"
```

---

### 3.10 L7 — Testing & Dry-Run（决策 D-018-12）

> **决策 D-018-12**：权限配置是可测试代码——需要影响分析、模拟模式和自动化测试框架。
>
> **决策依据**：OPA Rego 单元测试 + D2 policy validation + 企业级权限影响分析。1人+AI 维护下，改了权限没人验证——必须自动化。

```yaml
testing:
  # ─── 权限影响分析 ───
  impact_analysis:
    description: "修改 rbac_roles.yaml 前回答：会影响到多少 Agent、哪些操作"
    query: |
      给定 proposed_change:
        列出所有受影响的 Agent（role_bindings 匹配）
        列出每个 Agent 的权限变化（新增/移除/升级/降级）
        标记有风险的变更（Agent 获得超出当前 maturity 的权限）
    ci_integration: "PR 中修改 rbac_roles.yaml → CI 自动运行 impact_analysis → 输出报告"

  # ─── Dry-Run 模式 ───
  dry_run:
    description: "模拟"如果给这个 Agent 这个权限，在当前上下文下会怎样"——不实际执行"
    modes:
      - "evaluate_agent(agent_id, task_context) → 列出该 Agent 在此任务中所有操作的权限判定"
      - "evaluate_action(agent_id, action) → 单次操作预览判定"
      - "what_if_role_change(agent_id, new_role) → 角色变更前后对比"
    integration: "CI pipeline 中的权限变更预演"

  # ─── 自动化测试框架 ───
  test_framework:
    description: "权限配置 = 可测试代码。每次修改 rbac_roles.yaml 必须通过测试"
    test_types:
      - name: "role_consistency_test"
        description: "每个 Role 的 always_allow/auto_guard/blocked 定义无冲突"
        example: "同一 Role 不能对同一 Tool 同时定义 always_allow 和 blocked"

      - name: "role_coverage_test"
        description: "所有已注册 Tool 至少在一个 Role 中有权限定义（没有孤儿 Tool）"
        example: "MCP 注册的 Tool 必须出现在至少一个 Role 的权限列表中"

      - name: "sequence_guard_test"
        description: "L4 禁止序列规则覆盖所有已知攻击链"
        example: "测试 read_sensitive→send_email 是否被正确阻断"

      - name: "immutable_core_test"
        description: "L0 protected_paths 写入尝试被正确拒绝"
        example: "模拟 Agent 尝试写入 src/zephyr/agent-rbac/rbac_roles.yaml → 预期 BLOCKED"

      - name: "maturity_boundary_test"
        description: "低成熟度 Agent 无法执行需要高成熟度的操作"
        example: "L1 Intern Agent 尝试 auto_guard 操作 → 预期 BLOCKED"
```

---

### 3.11 先干后验模式（决策 D-018-02）

> **决策 D-018-02**：审批流采用"先干后验 + 自动护栏"模式，而非"事前审批"模式。AI 直接执行 → 自动护栏检查 → 失败自动回滚 → 审计日志记录 → Owner 异步审阅。
>
> **决策依据**：10+ 并发对话不可能等 Owner 实时审批。参考： Terraform auto-apply + Cursor 自动编辑 + K8s controller reconciliation。...

```yaml
execution_flow:
  step_0_l0_check:
    who: "L0 Immutable Core"
    what: "检查是否触及保护路径 / 禁止操作 / Kill Switch 状态"
    note: "L0 失败 = 立即 BLOCKED，不进入后续步骤"

  step_1_execute:
    who: "AI"
    what: "直接执行操作（always_allow 或 auto_guard——L1 判定）"
    note: "不等待任何人类确认"

  step_1b_abac:
    who: "L2 ABAC"
    what: "二次确认——意图/时间/成熟度/敏感性四维属性校验"
    note: "L2 失败 = BLOCKED 或降级为 auto_guard"

  step_1c_input_guard:
    who: "L3 Input Guard"
    what: "参数级别的 schema/范围/危险模式检查"
    note: "L3 失败 = BLOCKED"

  step_1d_sequence_guard:
    who: "L4 Sequence Guard"
    what: "检查此操作是否与之前操作构成禁止序列"
    note: "L4 失败 = BLOCKED + 安全事件"

  step_2_auto_guard:
    who: "自动护栏（pre-commit / CI / drift detector）"
    what: "自动检查操作结果是否合规（仅 auto_guard 操作）"
    trigger: "git commit / git push / 定期轮询"

  step_3_auto_rollback:
    who: "Rollback System (MOD-INF-021)"
    what: "后验失败 → 自动回滚到上一个 checkpoint"
    trigger: "auto_guard 检查失败"

  step_4_output_guard:
    who: "L5 Output Guard"
    what: "结果脱敏/截断"
    trigger: "每个 Tool 执行后"

  step_5_audit:
    who: "Audit Trail (MOD-INF-020)"
    what: "所有操作（成功/失败/回滚/序列违规）写入不可变审计日志"
    trigger: "每个操作"

  step_6_async_review:
    who: "Owner（异步）"
    what: "有空时翻审计日志，发现异常再处理"
    trigger: "Owner 主动查看 / 异常告警通知"
    note: "这是唯一需要人类参与的步骤——且是异步的"
```

---

### 3.12 GOV-AI-001 自动派生（决策 D-018-03）

> **决策 D-018-03**：rbac_roles.yaml 从 GOV-AI-001 自动派生，而非人工维护两份文档。Owner 只维护 GOV-AI-001（人类可读的权限声明），rbac_roles.yaml 由脚本自动生成（机器可执行的权限配置）。
>
> **决策依据**：消除手动复制 = 消除漂移可能。参考： K8s CRD 从 Go 类型自动派生 OpenAPI Schema。...

```yaml
derivation_flow:
  source: "GOV-AI-001（ai_autonomy_authority_registry.yaml）"
  derivation_script: "scripts/governance/d3_metadata/derive_rbac_roles.py"
  target: "src/zephyr/agent-rbac/rbac_roles.yaml"
  ci_check: "CI 门禁校验 rbac_roles.yaml 与 GOV-AI-001 一致性"

  # ─── 扩展：rbac_roles.yaml now includes ───
  includes:
    - "L1 RBAC role definitions (from GOV-AI-001)"
    - "L2 ABAC rules (intent/temporal/maturity/resource tags)"
    - "L3 input guardrails (per-tool parameter rules)"
    - "L4 forbidden_sequences (attack chain definitions)"
    - "L5 output guardrails (PII/credential/truncation rules)"

  principle: "人类写声明 → 机器生成配置 → CI 校验一致性 + 自动化测试"
  benefit: "单点维护 + 零漂移 + 自动同步 + 可测试"
```

---

### 3.13 Agent 身份模型（多 IDE 支持 + 成熟度 + 委托链）

> **v0.4.0 扩展**：AgentIdentity 增加 parent_agent_id/delegation_depth 委托链字段 + SessionToken 签名校验。

```python
class AgentMaturityLevel(str, Enum):
    INTERN = "intern"         # L1: 新手——always_allow只读，写auto_guard，删blocked
    JUNIOR = "junior"         # L2: 初级——always_allow读写，删auto_guard
    SENIOR = "senior"         # L3: 高级——always_allow读写删，仅高危操作auto_guard
    PRINCIPAL = "principal"   # L4: 首席——近似Owner但不可改L0

class AgentIdentity(BaseModel):
    agent_id: str = Field(..., description="唯一标识——格式 AGT-{NAMESPACE}-{SEQ}")
    agent_type: AgentType = Field(..., description="Agent 类型")
    ide_source: IDESource = Field(..., description="来源 IDE——区分 TRAE/Cursor/RooCode")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")
    role_bindings: list[RoleBinding] = Field(default_factory=list, description="角色绑定")
    maturity_level: AgentMaturityLevel = Field(default=AgentMaturityLevel.INTERN,
                                                description="Agent 信任成熟度")
    session_id: str = Field(..., description="当前会话 ID")
    session_token: Optional["SessionToken"] = Field(None, description="v0.4.0: Session签名Token——防跨Session身份伪造")
    parent_agent_id: Optional[str] = Field(None, description="v0.4.0: 父Agent ID——委托链起点")
    delegation_depth: int = Field(0, ge=0, le=3, description="v0.4.0: 委托深度——每层+1，上限3")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks_completed: int = Field(default=0, description="已完成任务数——来自不可变审计日志(MOD-INF-020)")
    safety_incidents: int = Field(default=0, description="安全事故次数")
    auto_guard_pass_rate: float = Field(default=1.0, description="auto_guard 后验通过率")

class AgentType(str, Enum):
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    REVIEWER = "reviewer"
    GOVERNOR = "governor"
    RESEARCHER = "researcher"
    OPERATOR = "operator"

class IDESource(str, Enum):
    TRAE = "trae"
    CURSOR = "cursor"
    ROOCODE = "roocode"
    CLI = "cli"

class RoleBinding(BaseModel):
    role: str = Field(..., description="角色名——引用 rbac_roles.yaml")
    scope: str = Field(..., description="作用域——layer/module/global")
    granted_by: str = Field(..., description="授权者——owner/system")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None, description="临时授权过期时间")
```

---

### 3.14 Permission Guard 七层+三横切面 运行时检查（核心 API）

```python
class PermissionGuard:
    """七层纵深防御 + 三横切面 运行时权限执行器"""

    async def check(
        self,
        agent: AgentIdentity,
        action: Action,
        task_context: Optional[TaskContext] = None,
    ) -> PermissionResult:
        """
        完整权限判定——横切面A→L0→L5→横切面A

        横切面A pre_hooks → L0 ColdStartLock → L0 EmergencyOverride → L0→L5七层检查 → 横切面A post_hooks

        输入：Agent 身份 + 请求的动作 + 任务上下文
        输出：ALLOW / AUTO_GUARD / BLOCKED + 决策链
        延迟目标：< 1.2ms（含横切面）
        """

    async def dry_run(
        self,
        agent: AgentIdentity,
        action: Action,
        task_context: TaskContext,
    ) -> DryRunResult:
        """模拟模式：预览权限判定而不实际执行"""

    async def impact_analysis(
        self,
        proposed_change: RoleChange,
    ) -> ImpactReport:
        """权限影响分析——这个变更会影响多少 Agent/操作"""

    async def kill_switch(
        self,
        agent: AgentIdentity,
        trigger: KillSwitchTrigger,
    ) -> KillSwitchResult:
        """触发熔断——阻断单 Agent 或全局"""

    def engine_status(self) -> EngineHealth:
        """Engine 健康检查 + 降级状态 + 冷启动锁状态 + 缓存通道健康"""

    # ─── v0.4.0 新增方法 ───
    async def emergency_override(
        self,
        token: EmergencyOverrideToken,
        agent: AgentIdentity,
        action: Action,
    ) -> OverrideResult:
        """紧急覆盖——验证JIT越权令牌并临时绕过指定层"""

    async def invalidate_cache(
        self,
        reason: InvalidationReason,
    ) -> InvalidationReport:
        """缓存失效——权限变更或紧急收紧时推送失效"""

    async def get_health_dashboard(self) -> HealthDashboard:
        """获取Owner健康仪表盘——5个关键数字"""

class PermissionResult(BaseModel):
    decision: PermissionDecision
    reason: str
    layered_decisions: dict[str, LayerResult]  # 横切面A+L0→L5+横切面A 每层判定
    guard_checks: Optional[list[str]]  # auto_guard 时列出后验检查项
    audit_entry: AuditEntry
    latency_us: float
    # ─── v0.4.0 新增字段 ───
    cold_start_elapsed_ms: Optional[float] = None    # 冷启动锁耗时
    emergency_override_applied: bool = False          # 是否应用了紧急覆盖
    hooks_executed: int = 0                            # 执行的钩子数

class LayerResult(BaseModel):
    layer: str  # "L0".."L6"
    decision: PermissionDecision
    reason: str
    latency_us: float

class PermissionDecision(str, Enum):
    ALLOW = "allow"
    AUTO_GUARD = "auto_guard"
    BLOCKED = "blocked"
    SKIPPED = "skipped"  # 当前层不适用

class Action(BaseModel):
    tool_id: str = Field(..., description="Tool 标识符")
    tool_name: str = Field(..., description="Tool 名称")
    tool_type: str = Field(..., description="Tool 类型——read/write/delete/execute/network")
    parameters: dict[str, Any] = Field(..., description="Tool 参数")
    target_paths: list[str] = Field(default_factory=list, description="操作目标路径")
    session_id: str = Field(..., description="会话 ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # ─── v0.4.0 新增字段 ───
    emergency_token: Optional[str] = Field(None, description="紧急覆盖令牌（Owner签发JIT，<5分钟有效）")
    source_ide: Optional[str] = Field(None, description="IDE来源——TRAE/Cursor/RooCode")
```

---

### 3.15 横向越权防护（决策 D-018-13）

> **决策 D-018-13**：L1 RBAC 不仅要防"低角色做高权限的事"（垂直越权），还要防"Agent 冒充其他 Agent 身份"（横向越权）。
>
> **可信主体**：CSA Agentic Trust Framework——"Agent 身份伪造是 Agentic 系统中的第一级威胁"。NIST AI Agent 标准——"Agent 身份必须可验证、可追溯、不可伪造"。

```python
# identity.py 中新增
class SessionToken(BaseModel):
    """Session 签名Token——防跨Session身份伪造"""
    session_id: str
    agent_id: str
    ide_source: str              # TRAE / Cursor / RooCode
    issued_at: datetime
    expires_at: datetime
    signature: str               # HMAC-SHA256(agent_id + session_id + issued_at, secret_key)
    parent_agent_id: Optional[str] = None   # 委托链——谁创建/委托了这个Agent
    delegation_depth: int = 0               # 委托深度——每层+1，上限3

class AgentIdentityVerifier:
    """Agent身份验证器——横向越权防护"""

    SECRET_KEY: str = "from-secure-key-store"
    MAX_DELEGATION_DEPTH: int = 3

    async def verify_session_token(self, token: SessionToken) -> bool:
        """验证Session Token的签名有效性"""

    async def detect_identity_mismatch(
        self,
        claimed_agent: AgentIdentity,
        session_token: SessionToken,
    ) -> MismatchReport:
        """
        检测身份不匹配：
        - 同一 session 中出现不同 maturity_level 的声明
        - 跨 session 操作中 agent_id 不一致
        - 委托链深度超过 MAX_DELEGATION_DEPTH
        """

    async def prevent_cross_session_forgery(
        self,
        current_session: SessionContext,
        operation_target: Action,
    ) -> ForgeryCheckResult:
        """
        跨Session身份伪造防护：
        - Session 2不能声明Session 1的Agent Identity
        - Maturity Level不能跨Session无痕提升
        """
```

```yaml
# rbac_roles.yaml 新增 security 维度的角色
roles:
  security:
    identity_verifier:
      description: "Agent RBAC内部使用的身份验证器——非Agent角色，是系统组件"
      permissions:
        - "verify_session_token"       # 验证Session Token签名
        - "detect_identity_mismatch"   # 检测身份声明与实际不符
        - "block_forged_agent"         # 阻断伪造身份的Agent
```

---

### 3.16 冷启动锁——启动时全局拒绝直到权限配置加载（决策 D-018-14）

> **决策 D-018-14**：蓝图 §6 R15 提出了"崩=blocked"原则，但关键空白是——rbac_roles.yaml 在加载之前的状态是什么？如果在 `immutable_core.py` 等组件就绪前面已经有 Agent 在操作，等于裸奔窗口。
>
> **可信主体**：Flyway/Liquibase——migration 执行前先 validate preconditions。K8s RBAC——Pod 启动前先校验 ServiceAccount。Claude Code——配置加载完成前不执行任何操作。

```python
# immutable_core.py 新增
class ColdStartLock:
    """
    冷启动锁——系统启动时全局拒绝所有Agent操作，直到权限配置加载校验通过。

    生命周期：
    1. 系统启动 → startup_lock = BLOCKED_ALL（所有Agent操作被拒绝）
    2. rbac_roles.yaml 加载 → hash校验通过 → startup_lock = RELEASED（正常检查链路）
    3. 30秒内未加载成功 → startup_lock = MAINTENANCE_MODE（仅Owner可操作）
    """

    _state: str = "BLOCKED_ALL"           # BLOCKED_ALL | RELEASED | MAINTENANCE_MODE
    _loaded_at: Optional[datetime] = None
    _release_conditions_met: bool = False
    MAX_LOAD_TIME_SECONDS: int = 30

    async def check(self) -> StartupLockResult:
        if self._state == "BLOCKED_ALL":
            elapsed = (datetime.utcnow() - self._started_at).total_seconds()
            if elapsed > self.MAX_LOAD_TIME_SECONDS:
                self._state = "MAINTENANCE_MODE"
                return StartupLockResult.MAINTENANCE_MODE
            return StartupLockResult.BLOCKED
        elif self._state == "MAINTENANCE_MODE":
            # 仅Owner（human）操作可通过
            return StartupLockResult.MAINTENANCE_MODE
        elif self._state == "RELEASED":
            return StartupLockResult.ALLOWED

    async def release_after_validation(self) -> bool:
        """校验通过后释放锁"""
        # 1. rbac_roles.yaml hash校验
        # 2. L0 protected_paths 所有路径存在性验证
        # 3. Gate Engine (MOD-GATE_ENGINE) 就绪确认
        # 全部通过 → _state = RELEASED

    def status_indicator(self) -> str:
        return f"Agent RBAC Cold Start: awaiting permission config load ({self.elapsed}s)"
```

---

### 3.17 权限钩子系统——Pre/Post/OnBlocked/OnKillSwitch 四类钩子（决策 D-018-15）

> **决策 D-018-15**：引入四类权限钩子，为扩展性和自定义校验提供**不侵入核心代码**的注册入口。这是 Claude Code hooks 模式 + Terraform pre/post-conditions 的组合。
>
> **可信主体**：Claude Code hooks——`preToolUse` / `postToolUse` 钩子系统。Terraform preconditions/postconditions——在 plan/apply 前后执行自定义校验。Netflix ChAP——在混沌实验前后注入自定义监控脚本。

```python
# permission_hooks.py — 新增文件
class PermissionHookRegistry:
    """
    权限钩子注册表——四类钩子，按顺序执行。

    钩子失败策略：
    - pre_check_hook FAIL → 操作被BLOCKED（"未能通过前置校验"）
    - post_check_hook FAIL → 触发auto_guard后验失败 → auto_rollback
    - on_blocked_hook FAIL → 仅记录日志（不能因为钩子失败而使阻断"变成放行"）
    - on_kill_switch_hook FAIL → 紧急通知Owner + 强制进入MAINTENANCE_MODE
    """

    _pre_check_hooks: list[PreCheckHook] = []
    _post_check_hooks: list[PostCheckHook] = []
    _on_blocked_hooks: list[OnBlockedHook] = []
    _on_kill_switch_hooks: list[OnKillSwitchHook] = []

    async def execute_pre_checks(
        self,
        agent: AgentIdentity,
        action: Action,
    ) -> list[HookResult]:
        """Tool调用前——运行所有注册的pre_check钩子"""

    async def execute_post_checks(
        self,
        agent: AgentIdentity,
        action: Action,
        result: ToolExecutionResult,
    ) -> list[HookResult]:
        """Tool执行后——运行所有注册的post_check钩子。
        这是 auto_guard 后验失败检测的核心注入点"""

    async def execute_on_blocked(
        self,
        agent: AgentIdentity,
        action: Action,
        block_reason: str,
        blocking_layer: str,
    ) -> list[HookResult]:
        """越权被拦截时——自定义响应（如：通知Owner、记录安全事件、触发备用路径）"""

    async def execute_on_kill_switch(
        self,
        trigger: KillSwitchTrigger,
        affected_agents: list[AgentIdentity],
    ) -> list[HookResult]:
        """全局熔断触发时——自定义响应（如：备份最新状态、通知所有下游系统、
        触发application-level的优雅降级、记录熔断前后的系统快照）"""

class HookResult(BaseModel):
    hook_id: str
    hook_name: str
    success: bool
    output: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: float

# ─── 预置钩子清单 ───
# H01: 文件完整性检查——修改前对比checksum
# H02: Git状态一致性——write操作前确认git status clean
# H03: 依赖版本锁定——modify pyproject.toml 时检查依赖版本冻结
# H04: 下游模块通知——perm变更后通知所有depends_on的模块
# H05: Auto-Backup——blocked触发前自动备份受影响文件
```

```yaml
# permission_hooks.yaml — 钩子配置文件
hooks:
  # ─── Pre-Check Hooks ───
  pre_check:
    - id: "H01"
      name: "file_integrity_checksum"
      applies_to: ["file_write", "file_modify"]
      description: "写文件前记录修改前checksum——用于rollback还原"
      priority: 10
      timeout_ms: 5

    - id: "H02"
      name: "git_status_consistency"
      applies_to: ["file_delete", "file_modify"]
      description: "操作前确认git status无未跟踪变更——防止AI操作与git状态撕裂"
      priority: 20
      timeout_ms: 20

    - id: "H03"
      name: "dependency_version_lock"
      applies_to: ["file_write"]
      context: "target_file == 'pyproject.toml'"
      description: "修改pyproject.toml时检查依赖版本——防止AI意外升级破坏性版本"
      priority: 30
      timeout_ms: 10

  # ─── Post-Check Hooks ───
  post_check:
    - id: "H04"
      name: "downstream_module_notify"
      applies_to: ["permission_config_change"]
      description: "权限配置变更后通知所有依赖模块——§4 depends_on各模块的Gate Engine"
      priority: 50
      timeout_ms: 100

    - id: "H05"
      name: "sensitive_data_scan"
      applies_to: ["file_write", "file_create"]
      description: "文件写入后扫描是否包含PII/credential/API key——比L5更激进"
      priority: 60
      timeout_ms: 50

  # ─── On-Blocked Hooks ───
  on_blocked:
    - id: "H06"
      name: "auto_backup_before_block"
      applies_to: ["any_permission_blocked"]
      description: "越权被拦截时自动备份受影响文件——防止后续毁坏操作丢失恢复路径"
      priority: 100
      timeout_ms: 200

    - id: "H07"
      name: "owner_notification"
      applies_to: ["any_permission_blocked"]
      description: "越权拦截时通知Owner——飞书/钉钉/Slack"
      priority: 110
      timeout_ms: 500

  # ─── On-Kill-Switch Hooks ───
  on_kill_switch:
    - id: "H08"
      name: "system_snapshot_backup"
      applies_to: ["any_kill_switch"]
      description: "熔断时自动备份系统当前完整快照——git bundle + SQLite dump"
      priority: 200
      timeout_ms: 5000

    - id: "H09"
      name: "emergency_owner_alert"
      applies_to: ["any_kill_switch"]
      description: "熔断时紧急通知Owner——所有渠道同时推送（飞书+钉钉+SMS若配置）"
      priority: 210
      timeout_ms: 1000
```

---

### 3.18 Agent 创建权与权限遗传——Agent 派生/复制的权限衰减继承（决策 D-018-16）

> **决策 D-018-16**：Agent 能否创建/派生新的 Agent 实例？如果可以，新 Agent 继承什么权限？如果不可以，靠什么阻止？
>
> **可信主体**：Temporal Durable Execution——WorkflowId + RunId 唯一标识一次执行，防止重复。K8s RBAC——ServiceAccount 的 Token 不可被复制。OAuth2——access_token 不可被转让。

```yaml
# agent_creation_policy.yaml — Agent 复制/派生规则
agent_creation_policy:
  # ─── 谁能创建 Agent ───
  who_can_create:
    - role: "human_owner"
      description: "Owner本人——无限制。可创建任意类型、任意maturity的Agent"
    - role: "principal_agent"          # L4_PRINCIPAL——已充分信任
      description: "Principal Agent——可在其IDE内创建子Agent。子Agent自动L1_INTERN起"
      max_children_per_hour: 2
      max_total_children: 5
    - role: "senior_agent"             # L3_SENIOR——有限委派
      description: "Senior Agent——仅在当前session内可创建临时子Agent（session结束=终止）"
      max_children_per_session: 1
      child_lifetime: "session"        # Session结束自动终止

  # ─── 创建者不可创建的类型 ───
  restrictions:
    - "Agent不能创建 maturity_level >= 自己的Agent"      # 防止越级复制
    - "Agent不能修改子Agent的maturity_level"              # 成熟度不可转让
    - "Agent不能创建跨IDE的Agent"                         # IDE隔离

  # ─── 权限遗传（Permission Inheritance with Attenuation）───
  inheritance:
    algorithm: "创建者权限集 × 衰减系数"
    attenuation:
      L4_PRINCIPAL_parent: 0.7          # Principal创建的Agent获得70%权限
      L3_SENIOR_parent: 0.5             # Senior创建的Agent获得50%权限

    never_inherited_permissions:        # 这些权限绝对不传递
      - "modify_immutable_core"         # 不可变核心修改权
      - "delete_audit_logs"             # 审计日志删除权
      - "disable_kill_switch"           # 熔断器禁用权
      - "create_further_agents"         # 孙子Agent创建权——只传一代
      - "modify_rbac_config"            # RBAC配置修改权
      - "issue_emergency_token"         # 紧急覆盖令牌签发权——仅Owner

  # ─── Agent 生命周期 ───
  lifecycle:
    spawn: "创建者发起 spawn_agent → Gate Engine检查creation_policy → Agent RBAC验证角色→创建子Agent"
    termination:
      owner_terminated: "Owner手动终止"
      session_expired: "Session结束 → 临时子Agent自动终止"
      kill_switch: "熔断触发 → 相关Agent终止"
      idle_timeout: "Agent 30分钟无操作 → L1_INTERN自动休眠"

    audit: "每个创建/复制/终止事件 → 不可变审计日志"
```

---

### 3.19 缓存一致性——权限变更推送失效 + 降级攻击防护（决策 D-018-17）

> **决策 D-018-17**：蓝图 §6 R3 提到权限结果缓存（TTL=5min）。如果权限在5分钟内紧急收紧，缓存旧值作为ALLOW放行了——这5分钟是裸奔窗口。改为**推送驱动的缓存失效**。
>
> **可信主体**：Claude Code——权限配置文件变更后强制刷新。K8s RBAC——RBAC变更后API Server cache立即刷新。Redis pub/sub——变更事件 → 所有subscriber立即收到invalidation。

```python
# cache_invalidation.py — 新增文件
class PermissionCacheInvalidator:
    """
    缓存失效器——权限变更时主动推送invalidation，而非被动等TTL。

    变更事件类型：
    1. rbac_roles.yaml 内容变化 → 全局失效所有Agent的L1缓存
    2. GOV-AI-001 authority变更 → 标记受影响权限为"待重算"
    3. maturity_upgrade → 该Agent的权限缓存立即失效（可能更宽松）
    4. emergency_permission_narrow → 立即失效所有指定操作的缓存
    """

    async def on_rbac_config_change(self, diff: ConfigDiff) -> InvalidationReport:
        """rbac_roles.yaml 变更 → 分析diff → 精准失效受影响缓存"""
        affected_agents = self._resolve_affected_agents(diff)
        affected_operations = self._resolve_affected_operations(diff)

        # 精准失效——只失效真正受影响的缓存条目
        invalidated_count = await self.cache.invalidate(
            agents=affected_agents,
            operations=affected_operations,
        )
        return InvalidationReport(
            config_diff=diff,
            affected_agents=len(affected_agents),
            invalidated_cache_entries=invalidated_count,
            invalidation_time_ms=self._elapsed_ms,
        )

    async def on_emergency_narrow(self, operation: str) -> InvalidationReport:
        """紧急收紧特定操作的权限 → 立即失效所有Agent对该操作的缓存"""
        await self.cache.invalidate(operations=[operation])

    def cache_window_guarantee(self) -> float:
        """最大缓存窗口——变更事件发出后，缓存中的旧值最长存活时间"""
        return 0.1  # 100ms——推送延迟上限
```

```yaml
# cache_policy.yaml
cache_policy:
  # v0.3.0 被动TTL模式（旧）
  passive_ttl: "DEPRECATED——不再使用TTL=5min被动过期"

  # v0.4.0 推送驱动模式（新）
  push_driven:
    mechanism: "权限变更事件 → 分析diff → 精准失效受影响缓存 → 所有Guard立即拉取最新判定"
    max_invalidation_latency_ms: 100     # 推送延迟上限
    fallback_ttl: 300                     # 如果推送失败（网络问题等），兜底TTL=5min
    health_check: "每10秒检查推送通道健康——连续3次失败 → 降级为被动TTL + 告警"

  # ─── 降级攻击防护（与2.3联动）───
  degradation_attack_detection:
    description: "同一Agent触发的权限降级事件如果有规律性→标记为'疑似攻击'"
    pattern_detection:
      - pattern: "rapid_degradation_trigger"
        condition: "Agent在10秒内触发 >= 3 次同层检查失败导致partial_failure"
        action: "Agent BLOCKED + 标记为'疑似降级攻击'"
      - pattern: "cache_invalidation_flood"
        condition: "Agent在30秒内触发 >= 5 次缓存失效事件"
        action: "缓存进入不可变模式（变更需Owner审核）+ Agent BLOCKED"
```

---

### 3.20 紧急覆盖令牌——Owner签发的JIT临时越权令牌（决策 D-018-18）

> **决策 D-018-18**：在紧急情况下（生产事故、关键修复），Owner需要让Agent快速执行一个被blocked的操作。当前唯一的办法是手动修改GOV-AI-001 → 等auto-derive → 不可接受。引入紧急覆盖令牌。
>
> **可信主体**：NIST AI Agent标准——"高风险操作需要临时令牌（revocable）"。AWS STS——`assume-role` 签发临时凭证。Claude Code `bypassPermissions`——临时禁用权限检查但必须声明。

```python
# emergency_override.py — 新增文件
class EmergencyOverrideToken(BaseModel):
    """
    Owner签发的JIT临时越权令牌。

    安全约束：
    - 最大有效期：5分钟
    - 最大签发数：每小时3个
    - 每个token绑定一个 Agent + 一个 Session
    - 每个token绑定指定的layers_to_bypass
    - Token使用后立即失效（一次性）
    """
    token_id: str                       # UUID
    issued_to_agent_id: str             # 绑定到特定Agent
    issued_to_session_id: str           # 绑定到特定Session
    layers_to_bypass: list[str]         # 如 ["L3", "L4"]——只跳过特定层
    allowed_operations: list[str]       # 如 ["file_write"]——只允许特定操作
    issued_at: datetime
    expires_at: datetime                # issued_at + 5min
    max_uses: int = 1                   # 一次性——用完即废
    used_count: int = 0
    signature: str                      # Owner私钥签名
    revocation_url: str                 # Owner可随时吊销

class EmergencyOverrideManager:
    MAX_TOKENS_PER_HOUR: int = 3
    MAX_TOKEN_LIFETIME_MINUTES: int = 5

    async def issue_token(
        self,
        owner: OwnerIdentity,
        agent: AgentIdentity,
        layers: list[str],
        operations: list[str],
        reason: str,                     # 必须填写原因——写入审计日志
    ) -> EmergencyOverrideToken:
        """Owner签发紧急覆盖令牌"""
        # 1. 验证Owner身份——双因子确认
        # 2. 检查小时签发上限
        # 3. 签发JWT格式token（含layers和operations声明）
        # 4. 写入不可变审计日志：{who, what, when, why}
        # 5. 通知其他活跃Agent：有紧急覆盖在执行

    async def validate_and_consume(
        self,
        token: EmergencyOverrideToken,
        agent: AgentIdentity,
        action: Action,
    ) -> OverrideResult:
        """验证token并消耗它"""
        # 1. 签名验证
        # 2. 过期检查
        # 3. Agent/Session匹配检查
        # 4. allowed_operations匹配检查
        # 5. used_count++——一次性消耗
        # 6. 审计日志：{token_id, agent_id, action, layers_bypassed, result}

    async def revoke_token(self, token_id: str) -> bool:
        """Owner手动吊销——即使token未过期也立即失效"""

# ─── Owner CLI ───
# $ zephyr override issue --agent agent-001 --layers L3,L4 --ops file_write --reason "emergency config fix"
# Token: zy-override-abc123def456. Valid for 5 minutes. Use once.
```

---

### 3.21 自动维护——僵尸规则检测 + 权限复杂度预算（决策 D-018-19）

> **决策 D-018-19**：权限系统必须能**自我修剪**——自动检测无用的规则并推荐删除，控制规则总数在可维护范围内。这是100%AI施工+1人维护场景下防止"权限熵增"的关键机制。
>
> **可信主体**：K8s RBAC——`kubectl auth can-i --list` 可审查所有权限。Terraform——`terraform plan` 展示变更影响。OPA——Rego规则可静态分析覆盖率和冗余。

```yaml
# auto_maintenance.yaml
auto_maintenance:
  # ─── 规则效果评估 ───
  rule_effectiveness:
    metric: "rule_effectiveness_score"
    formula: "（过去90天该规则触发的实际拦截次数）/ （规则存在天数）"
    classification:
      active: "score > 0.01（每天至少触发0.01次 = 每100天至少1次）"
      dormant: "0 < score <= 0.01（存在且配置但极少触发）"
      zombie: "score == 0（90天内从未触发——候选删除）"

    auto_deprecation:
      zombie_threshold_days: 90
      action: "自动标记 [DEPRECATED_CANDIDATE] + 在Owner健康仪表盘中高亮"
      owner_review: "Owner确认删除 → 规则归档（非物理删除——保留历史）"
      auto_cleanup: "Owner 14天内未审阅 → 规则自动禁用（非删除）+ 告警升级"

    protected_rules:  # 以下规则永不被自动deprecate，即使score=0
      - "L0 不可变核心规则"
      - "Kill Switch 触发器规则"
      - "数据外泄防护规则（read_sensitive→external_output）"

  # ─── 权限复杂度预算 ───
  complexity_budget:
    max_total_rules: 30                 # L1-L4规则总数上限（L0硬编码不计入，L5-L7不计入）
    warnings:
      - at: 20
        level: "info"
        message: "规则数达到上限的67%——建议检查是否有冗余"
      - at: 25
        level: "warning"
        message: "规则数达到上限的83%——强制触发自动化deprecation扫描"
      - at: 30
        level: "error"
        message: "规则数达到上限——禁止新增规则直到删除达到28条以下"

    cost_per_rule:
      avg_execution_time_us: 8.5        # 每条规则的平均检查耗时（微秒）
      complexity_budget_us: 255         # 30条 × 8.5us = 总耗时预算
      burn_rate_warning: "规则总数×平均耗时 > 预算的80% → 告警"

  # ─── 定期审计报告（每周自动生成）───
  weekly_audit_report:
    generation: "每周一 09:00 自动生成（crontab）"
    content:
      - "本周权限决策统计（ALLOW/AUTO_GUARD/BLOCKED 分布）"
      - "auto_guard 后验成功率趋势"
      - "僵尸规则清单（90天无触发）"
      - "规则复杂度预算消耗"
      - "Kill Switch 触发历史（含原因和恢复时间）"
      - "Maturity 升级/降级事件"
      - "推荐的规则清理列表"
    delivery: "写入 docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/reports/weekly-{date}.md"

  # ─── Owner 健康仪表盘 ───
  owner_dashboard:
    description: "每次施工后自动更新的5个关键数字——Owner5秒看懂权限系统状态"
    file_path: "config/agent-rbac/health_dashboard.yaml"
    metrics:
      - metric: "today_allowed_count"
        display: "今日 ALLOW 次数"
        healthy_range: "无上限——越多越正常"
        alarm: "无（这是常态）"

      - metric: "today_auto_guard_count"
        display: "今日 AUTO_GUARD 次数（及后验通过率%）"
        healthy_range: "< 20次 AND 后验通过率 > 90%"
        alarm: "auto_guard > 50次 → 规则太严或Agent行为异常。后验通过率 < 80% → Agent信任度下降"

      - metric: "today_blocked_count"
        display: "今日 BLOCKED 次数"
        healthy_range: "< 5次"
        alarm: "> 10次 → Agent频繁触碰权限边界——可能被投毒或理解偏差"

      - metric: "kill_switch_status"
        display: "Kill Switch 状态 [NORMAL / WARNING / TRIGGERED / MAINTENANCE] + 最近触发时间"
        healthy_range: "NORMAL"
        alarm: "非NORMAL = 立即关注"

      - metric: "agent_maturity_distribution"
        display: "Agent成熟度分布 [L1:3, L2:2, L3:1, L4:0]"
        healthy_range: "L1+L2 > 50% 且 无异常跳跃"
        alarm: "L3+占比 > 30% → 高风险Agent过多"

    auto_generation: "每次 PermissionGuard.check() 执行后异步更新"
    visual_indicator: |
      ┌─────────────────────────────────────────────┐
      │ AGENT RBAC HEALTH DASHBOARD                  │
      ├─────────────────────────────────────────────┤
      │ ALLOW:      127  ✅                          │
      │ AUTO_GUARD:   3  ✅ (后验100%)               │
      │ BLOCKED:      0  ✅                          │
      │ KILLSWITCH: NORMAL ✅ (最后触发: 3天前)       │
      │ MATURITY:   L1:3 L2:2 L3:1 L4:0 ✅           │
      │ ──────────────────────────────────────       │
      │ RULES: 19/30 (63%) ✅                        │
      │ ZOMBIE RULES: 0 ✅                           │
      │ OVERALL: HEALTHY ✅                          │
      └─────────────────────────────────────────────┘
```

---

### 3.22 意图绑定访问控制（IBAC + 横切面D——决策 D-018-20）

> **决策 D-018-20**：引入**意图绑定访问控制**（Intent-Bound Access Control, IBAC）作为横切面D的核心。将现有RBAC/ABAC从"谁+什么属性"升级为"谁+什么任务意图+需要什么临时权限信封"。这是 Cisco TBAC/IBAC 模型在氛围编程语境下的落地。
>
> **可信主体**：Cisco TBAC——"Task/Tool/Transaction-Based Access Control——创建基于具体工作的临时权限信封"。Perplexity NHI——"Non-Human Identities——Agent身份在委托链中每步需重验证"。

```python
# intent_binder.py — 新增文件（横切面D核心组件）
class IntentBindingContext(BaseModel):
    """意图绑定上下文——每次任务启动时创建，贯穿整个操作链"""
    task_id: str                      # 来自Task System的任务ID
    original_intent: str              # Owner最初的自然语言指令（不可变）
    intent_signature: str             # HMAC(task_id + original_intent + issued_at)
    allowed_tool_categories: list[str]  # 如 ["file_read", "file_write", "shell_test"]
    disallowed_tool_categories: list[str]  # 如 ["network_external", "file_delete_system"]
    permission_envelope_ttl: int = 3600  # 权限信封有效期（秒），超时需重签发
    created_at: datetime
    drift_tolerance: float = 0.3      # 意图漂移容忍度（0-1，越低越严格）

class IntentBoundPermissionGuard:
    """
    IBAC 权限执行器——横切面D核心。

    工作原理：
    1. 任务启动 → 绑定原始意图 + 创建临时权限信封
    2. 每个Tool调用 → 验证当前操作是否仍在意图信封内
    3. 操作链进行中 → 持续检测意图漂移
    4. 意图信封过期 → 需Owner重新确认或自动降级
    """

    async def bind_intent(
        self,
        agent: AgentIdentity,
        task: TaskContext,
        owner_instruction: str,         # Owner原始指令（不可变基线）
    ) -> IntentBindingContext:
        """任务启动时——绑定意图，创建临时权限信封"""
        intent_hash = self._compute_intent_hash(task.task_id, owner_instruction)
        envelope = IntentBindingContext(
            task_id=task.task_id,
            original_intent=owner_instruction,
            intent_signature=intent_hash,
            allowed_tool_categories=self._derive_allowed_tools(task, agent),
        )
        # 写入不可变审计日志：{when, who, task, intent, envelope}
        return envelope

    async def check_within_intent(
        self,
        binding: IntentBindingContext,
        agent: AgentIdentity,
        action: Action,
        operation_chain: list[Action],  # 当前操作链的历史（最近10步）
    ) -> IntentCheckResult:
        """
        每一步检查：当前操作是否仍在意图信封内？

        检查维度：
        1. tool_category 是否在 allowed 中（硬边界）
        2. 意图漂移度（soft边界——语义相似度检测）
        3. 操作链累积漂移（多步操作累积的意图偏离）
        """
        # 硬边界检查
        if action.tool_type not in binding.allowed_tool_categories:
            return IntentCheckResult.VIOLATION

        # 软边界——意图漂移
        drift_score = await self._compute_drift(
            binding.original_intent,
            operation_chain,
            action,
        )
        if drift_score > binding.drift_tolerance:
            return IntentCheckResult.DRIFT_DETECTED
        elif drift_score > binding.drift_tolerance * 0.7:
            return IntentCheckResult.DRIFT_WARNING

        return IntentCheckResult.WITHIN_INTENT

class IntentCheckResult(str, Enum):
    WITHIN_INTENT = "within_intent"         # 在意图信封内——放行
    DRIFT_WARNING = "drift_warning"         # 漂移警告——降级为auto_guard
    DRIFT_DETECTED = "drift_detected"       # 漂移检测——blocked + P0告警
    VIOLATION = "violation"                 # 硬违反——blocked + 无例外
```

---

### 3.23 Context Drift 检测——操作链中的意图漂移（决策 D-018-21）

> **决策 D-018-21**：AI Agent 在长时间的操作链中可能出现"Context Drift"——从最初"修复一个Bug"逐渐变为"重构整个模块"。L2 ABAC 的意图感知当前只检查TaskType，不检测链上漂移。新增语义漂移检测。
>
> **可信主体**：Enterprise research——"Context Drift——Agent Chains Break Security Boundaries——授权边界随操作链漂移是最隐蔽的越权形式"。Claude Code——long conversations 中 agent 行为漂移是已知问题。

```python
# context_drift_detector.py — 新增文件（L2 ABAC 扩展）
class ContextDriftDetector:
    """
    Context Drift 检测器——实时追踪Agent操作链中的意图漂移。

    核心原理：
    - 对比"当前操作模式"与"任务启动时的原始意图"
    - 当语义距离超过阈值 → 标记为漂移
    """

    def __init__(self, drift_window: int = 10):
        self.drift_window = drift_window  # 检测最近N步操作链

    async def detect_drift(
        self,
        original_intent: str,
        operation_chain: list[Action],
        current_action: Action,
    ) -> DriftReport:
        """
        检测操作链中的意图漂移。

        三个检测维度：
        1. 操作类型漂移——初始为read→逐步转为write/delete（类型熵增）
        2. 路径漂移——操作目标从src/逐步扩展到config/、data/（路径熵增）
        3. 语义漂移——借助嵌入相似度对比"原始意图"与"当前操作描述"的语义距离
        """
        # 维度1: 操作类型熵
        type_entropy = self._compute_type_entropy(operation_chain)
        type_drift = type_entropy > 1.5  # 从单一操作类型变为多类型混合

        # 维度2: 路径熵
        path_entropy = self._compute_path_entropy(operation_chain)
        path_drift = path_entropy > 2.0  # 操作路径明显扩展

        # 维度3: 语义距离
        semantic_drift = await self._compute_semantic_drift(
            original_intent, operation_chain
        )

        return DriftReport(
            type_drift=type_drift,
            path_drift=path_drift,
            semantic_drift=semantic_drift,
            overall_drift_score=(type_entropy + path_entropy + semantic_drift) / 3,
            recommendation=(
                "BLOCKED" if semantic_drift > 0.7
                else "AUTO_GUARD" if semantic_drift > 0.4
                else "ALLOW"
            ),
        )

class DriftReport(BaseModel):
    type_drift: bool
    path_drift: bool
    semantic_drift: float          # 0-1, 越高越偏离
    overall_drift_score: float
    recommendation: str             # ALLOW | AUTO_GUARD | BLOCKED
    detected_at_step: int           # 在第几步检测到漂移
```

---

### 3.24 连续验证——每步重验证 Agent 身份与权限一致性（决策 D-018-22）

> **决策 D-018-22**：当前模型是"Tool调用前检查一次"。在Agent链中（特别是Orchestrator→Worker委托），身份可能在中途被篡改或上下文被污染。引入**连续验证**——每一步执行后、下一步执行前都重新验证。
>
> **可信主体**：Cisco TBAC——"Zero Trust for Agents——Verification at Every Step"。Perplexity——"Agent Identity——每一步重验证 Non-Human Identity"。NIST Zero Trust——"从不信任，始终验证"。

```python
# continuous_verifier.py — 新增文件（横切面D组件）
class ContinuousVerifier:
    """
    连续验证器——横切面D，每步重验证Agent身份+权限一致性。

    执行节奏：
    - L0→L3 一次性大检查（不变）
    - 横切面D 每步连续性检查（新增）
    - L4 Micro-Verified 每子步骤微验证（新增）
    """

    async def verify_step(
        self,
        agent: AgentIdentity,
        action: Action,
        intent_binding: IntentBindingContext,
        session_token: SessionToken,
    ) -> StepVerificationResult:
        """
        每步验证——验证四项一致性：
        1. SessionToken 是否仍然有效（未过期/未被吊销）
        2. Agent Identity 是否与 SessionToken 一致（未被替换）
        3. 当前操作是否在 Intent 信封内
        4. 委托链是否未超深度（MAX_DELEGATION_DEPTH）
        """
        checks = {
            "token_valid": await self._verify_token(session_token),
            "identity_match": await self._verify_identity(agent, session_token),
            "intent_envelope": await self._check_intent_envelope(action, intent_binding),
            "delegation_chain": agent.delegation_depth <= self.MAX_DELEGATION_DEPTH,
        }

        all_passed = all(checks.values())
        return StepVerificationResult(
            passed=all_passed,
            checks=checks,
            requires_reauthentication=not checks["token_valid"],
            requires_intent_reconfirmation=not checks["intent_envelope"],
        )
```

---

### 3.25 权限模式管理器——Claude Code 5 模式 + Codex CLI Profiles（决策 D-018-23）

> **决策 D-018-23**：氛围编程中Owner需要动态切换权限模式。参照Claude Code的Shift+Tab（5种模式）和Codex CLI的profiles机制，引入**权限模式管理器**。
>
> **可信主体**：Claude Code 5种权限模式（default/acceptEdits/plan/bypassPermissions/auto）+ Shift+Tab切换。Codex CLI profiles（多配置文件）+ --full-auto + /permissions mid-session切换。

```yaml
# permission_modes.yaml — 新增文件（横切面D 模式管理）
permission_modes:
  # ─── 五种权限模式（对标 Claude Code）───
  modes:
    default:
      description: "默认——读自动放行，写auto_guard，删除blocked。日常开发起点"
      l1_behavior: "always_allow(读) + auto_guard(写) + blocked(删)"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "DEFAULT"

    accept_edits:
      description: "接受编辑——文件修改自动放行，Shell/Bash命令仍需确认"
      l1_behavior: "always_allow(读+写文件) + auto_guard(Shell) + blocked(删)"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "ACCEPT-EDITS"

    plan:
      description: "规划模式——仅只读操作。禁止一切写/删/Shell。用于代码审查和架构探索"
      l1_behavior: "always_allow(只读) + blocked(写/删/Shell)"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "PLAN"

    auto:
      description: "自动模式——AI分类器实时判断：这个操作安全吗？安全就放行，不安全就拦"
      l1_behavior: "AI分类器动态判定（对标 Claude Code auto模式）"
      classifier: "DeepSeek轻量级安全分类器（< 50ms）"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "AUTO"
      # ⚠️ 注意：bypassPermissions 模式在本地开发中不可用——必须沙箱+无网络

    emergency:
      description: "紧急模式——使用D-018-18紧急覆盖令牌临时越权。不是Shift+Tab可选的模式"
      trigger: "Owner签发紧急覆盖令牌 + 确认"
      max_duration_minutes: 5
      ide_indicator: "⚠️ EMERGENCY"

  # ─── 多Profile管理（对标 Codex CLI）───
  profiles:
    active_profile: "default"
    available:
      default:
        mode: "default"
        sandbox: "workspace_write"
        network: "blocked"
        model: "deepseek"

      ci_automation:
        mode: "accept_edits"
        sandbox: "workspace_write"
        network: "github.com,pypi.org"
        model: "deepseek"

      exploration:
        mode: "plan"
        sandbox: "read_only"
        network: "blocked"
        model: "claude"  # 用Claude做架构分析

    profile_switching:
      cli: "zephyr profile set <name>"
      mid_session: "/profile <name>"
      auto_activate: "根据当前Task类型自动切换profile"

  # ─── Mid-Session Toggle（对标 Claude Code Shift+Tab 和 Codex CLI /permissions）───
  mid_session_control:
    commands:
      - "/mode"          # 显示/切换当前权限模式
      - "/permissions"   # 显示当前权限信封详情
      - "/profile"       # 切换配置profile
      - "/audit"         # 显示最近操作决策审计
    keyboard_shortcut: "Shift+Tab（循环切换 default→acceptEdits→plan→auto）"
```

```python
# permission_mode_manager.py — 新增文件（横切面D 组件）
class PermissionModeManager:
    """权限模式管理器——横切面D核心组件"""

    async def set_mode(self, mode: str, session_id: str) -> ModeChangeResult:
        """切换权限模式——更新L1 RBAC行为 + 通知Gate Engine"""

    async def get_current_mode(self) -> PermissionMode:
        """获取当前活动的权限模式"""

    async def activate_profile(self, profile_name: str) -> ProfileActivationResult:
        """激活配置profile——mode+sandbox+network+model 一体化切换"""

    def allowed_in_current_mode(self, action: Action) -> bool:
        """快速查询——当前模式下这个操作是否允许"""
```

---

### 3.26 级联故障隔离——Agent链中的Cascading Failure防护（决策 D-018-24）

> **决策 D-018-24**：在多Agent场景（Orchestrator→Worker）中，单个Agent的错误输出会级联感染下游Agent。蓝图当前没有建模级联故障场景。新增**级联故障隔离器**。
>
> **可信主体**：Perplexity——"Cascading Failures in Long-Running Workflows——Error in Agent A's output causes Agent B to make unauthorized decisions"。NVIDIA多Agent全生命周期——"单点漏洞可快速传导至全链路"。

```python
# cascading_failure_isolator.py — 新增文件（横切面D 组件）
class CascadingFailureIsolator:
    """
    级联故障隔离器——防止一个Agent的错误级联感染下游。

    检测模式：
    1. 输出异常——Agent A的输出在语义/模式上与预期明显不同
    2. 置信度下降——Agent A的auto_guard后验成功率骤降（最近10次 < 80%）
    3. 权限边界扩展——下游Agent因上游Agent的错误输出而请求更高权限
    """

    async def monitor_agent_chain(
        self,
        chain: list[AgentIdentity],  # 从Orchestrator到Worker的完整链
    ) -> CascadeRiskReport:
        """
        实时监控Agent链——检测级联故障信号：
        - 上游Agent刚发生过auto_guard后验失败 → 下游Agent自动切换为保守模式
        - 下游Agent请求的权限超过上游的intent_envelope → 阻断
        """

    async def isolate_agent(self, agent_id: str, reason: str) -> IsolationResult:
        """
        隔离一个疑似故障的Agent：
        - 阻止其输出传递给任何下游Agent
        - 该Agent的操作链中已执行步骤回滚
        - 通知Orchestrator重新调度
        """

    async def get_cascade_health(self) -> CascadeHealth:
        """获取Agent链的整体健康状态——包括每个Agent的最近后验成功率"""
```

---

### 3.27 Micro-Verified 先干后验——每子步骤微型验证（决策 D-018-25）

> **决策 D-018-25**：将蓝图当前的"先干后验"（干完再验）升级为**Micro-Verified 先干后验**——将大操作分解为子步骤，每步执行后立即微验证，失败则立即回滚该子步，杜绝"第一步就错但第十步才发现"的级联错误。
>
> **可信主体**：Windsurf Cascade——"微型先干后验——每步执行后立即校验再继续"。Claude Code auto 模式中的 AI 分类器——每一步操作后实时判断安全性。

```python
# micro_verifier.py — 新增文件（L4序列护栏扩展）
class MicroVerifier:
    """
    微验证器——将先干后验升级为每子步骤微验证。

    传统先干后验：全干完 → 全验 → 不合格 → 全回滚（🌪️ 灾难）
    Micro-Verified：子步1执行 → 微验证1 → ✅ → 子步2执行 → 微验证2 → ❌ → 回滚子步2 → 子步3替代...
    """

    async def execute_with_micro_verification(
        self,
        agent: AgentIdentity,
        action: Action,
        intent_binding: IntentBindingContext,
    ) -> MicroVerifiedResult:
        """
        微验证执行——将Action分解为子步骤，每步微验证。

        子步骤分解示例：
        Action: "重构auth模块"
        ├── 子步1: read auth.py (微验证: 是否正确读取了当前版本)
        ├── 子步2: write auth_v2.py (微验证: 接口签名是否向后兼容)
        ├── 子步3: update imports in downstream files (微验证: 所有导入是否正确)
        └── 子步4: run tests (微验证: 全部通过)
        """

    async def micro_verify_substep(
        self,
        substep: SubStep,
        result: SubStepResult,
    ) -> MicroVerificationVerdict:
        """
        子步骤微验证——检查维度：
        1. 输出格式正确性
        2. 输出对下一步的影响（不引入Breaking Change）
        3. 输出符合Intent信封约束
        4. 文件变更量在预期范围内
        """

    class MicroVerificationVerdict(str, Enum):
        PASS = "pass"                 # 通过——继续下一步
        PASS_WITH_WARNING = "warn"    # 通过但有警告——降速执行
        FAIL_AND_ROLLBACK = "fail"    # 失败——回滚当前子步
        FAIL_AND_ESCALATE = "escalate"  # 严重失败——暂停任务+通知Owner
```

---

### 3.28 权限决策自解释——结构化拒绝原因 + 规则溯源（决策 D-018-26）

> **决策 D-018-26**：当 L0-L5 + 横切面D 阻断一个操作时，不仅返回 "BLOCKED: reason"，还要提供：
> 1. **结构化解释**——哪个层、哪条规则、哪个GOV-AI-001条目导致阻断
> 2. **Agent可用的自校正建议**——"如果你需要执行这个操作，可以..."
> 3. **Owner审阅用的因果链**——从GOV-AI-001到rbac_roles.yaml到运行时判定的完整追溯
>
> **可信主体**：Perplexity——"Explainable Agents as a Security Control——Agent需理解被拒原因以自校正"。CSA ATF 2026——"Agent必须能够解释自己的拒绝原因"。OPA——Decisions Log格式包含完整的决策路径。

```python
# decision_explainer.py — 新增文件（L6可观测性扩展）
class DecisionExplainer:
    """
    权限决策自解释器——为每个被阻断的操作生成结构化解释。
    """

    async def explain_blocked(
        self,
        agent: AgentIdentity,
        action: Action,
        result: PermissionResult,
    ) -> StructuredExplanation:
        """
        生成结构化解释：
        1. 阻断层：L4 Sequence Guard
        2. 触发规则：read_sensitive→external_output (Rule #7)
        3. 规则来源：GOV-AI-001 §3.2 Row 12
        4. 阻断原因：检测到序列模式 read(data/telemetry) → send_email
        5. 自校正建议：如果需要导出数据，请通过 /export 工具而非直接发邮件
        6. Owner审阅路径：GOV-AI-001 → derive → rbac_roles.yaml §sequence.forbidden → L4 enforcement
        """
        return StructuredExplanation(
            blocking_layer=result.blocking_layer,
            rule_id=result.rule_id,
            rule_source=f"GOV-AI-001.{result.rule_source_section}",
            block_reason=result.reason,
            corrective_suggestion=await self._generate_suggestion(agent, action, result),
            causal_chain=await self._build_causal_chain(result),
            gov_ai_001_row=result.gov_ai_001_row,
            severity="P0" if result.decision == PermissionDecision.BLOCKED else "P1",
            timestamp=datetime.utcnow(),
        )

    async def _generate_suggestion(
        self,
        agent: AgentIdentity,
        blocked_action: Action,
        result: PermissionResult,
    ) -> str:
        """
        为Agent生成自校正建议——"如果你需要完成这个操作，可以..."
        例如：
        - "通过 /export-data 命令导出，而非直接 send_email"
        - "请求Owner签发emergency_override token"
        - "将操作拆分为更小的子步骤，每步通过auto_guard验证"
        """

class StructuredExplanation(BaseModel):
    """结构化的权限拒绝解释——同时供AI Agent和Owner消费"""
    blocking_layer: str               # 哪个层阻断
    rule_id: str                      # 触发规则ID
    rule_source: str                  # 规则来源（GOV-AI-001定位）
    block_reason: str                 # 阻断原因（自然语言）
    corrective_suggestion: str        # 自校正建议（供Agent消费）
    causal_chain: list[CausalLink]    # 因果追溯链
    gov_ai_001_row: int               # GOV-AI-001表格行号
    severity: str                     # P0/P1/P2
    timestamp: datetime
    visualization: Optional[str] = None  # 因果链的可视化ASCII图

class CausalLink(BaseModel):
    step: int
    from_source: str
    to_target: str
    transformation: str
    timestamp: datetime
```

---

### 3.0 横切面 F — 取证级安全保障（外部取证专家终极审视成果）

> 横切面F 是从"外部取证专家审计本审计系统"这一根本问题出发，识别出的六项致命结构性漏洞及其对应的安全保障措施。

#### 3.0.1 Genesis Bootstrap 防护（决策 D-018-34）

> **决策 D-018-34**：Agent RBAC 系统自身也是 AI 写的。在施工阶段，AI 构建 RBAC 代码时，RBAC 尚未上线——这是一个"先有鸡还是先有蛋"的 **Genesis/Bootstrap 问题**。恶意 AI 可以在施工阶段埋入后门，在 RBAC 上线后激活。
>
> **可信主体**：Sherlock自我审计——14个漏洞中一半是"构建时已存在但运行时才发现"。VibeGuard盲点分类——"artifact hygiene, packaging-configuration drift, source-map exposure——这些不是运行时漏洞，是施工时的产物"。Gartner 2026——82%的Agent安全事故根源于工具调用边界失控，但施工阶段的配置错误是根本原因。
>
> **外部取证专家致命判词**："如果你在施工阶段就已经被攻破，运行时所有7层防御都是self-attesting的假象。系统自己证明自己安全 = 不安全。"

**Genesis Bootstrap 对策**：

```yaml
genesis_bootstrap_protection:
  # ─── 两阶段验证（Bootstrap → Runtime）───
  phase_1_bootstrap:
    description: "RBAC施工阶段——Agent在无RBAC保护下写RBAC代码"
    protections:
      - "所有RBAC核心代码（immutable_core.py/rbac_guard.py等）自动SHA-256签名"
      - "施工完成后执行 bootstrap_integrity_check——对比预期哈希 vs 实际哈希"
      - "bootstrap期间所有文件变更写入独立Bootstrap Audit Log（与RBAC自身审计分离）"
      - "immutable_core.py作为第一个文件写入→立即hash→后续文件变更需验证core未变"

    bootstrap_integrity_check:
      description: "RBAC上线前的最终完整性验证"
      steps:
        - "1. 校验 immutable_core.py 哈希 = 已知干净哈希"
        - "2. 合成攻击场景100个 → 验证每个都被正确BLOCKED"
        - "3. 测试 rbac_roles.yaml 从 GOV-AI-001 的正确派生率 = 100%"
        - "4. 验证 OS ACL 在关键文件上生效"
      outputs: "BOOTSTRAP_SIGNED（通过）或 BOOTSTRAP_FAILED（未通过→禁止启动）"

  phase_2_runtime:
    description: "RBAC上线后——每次启动都验证bootstrap签名未变"
    startup_check: "immutable_core.py hash == bootstrap_fingerprint → 通过才启动"
    tamper_detection: "hash mismatch → 系统进入LOCKDOWN模式（仅Owner可操作）"

  # ─── Clean Build Principle（干净构建原则）───
  clean_build:
    description: "核心RBAC代码只允许在 Bootstrap Phase 中构建。之后的任何修改 = TAMPERING"
    immutable_after_bootstrap:
      - "immutable_core.py"
      - "permission_guard.py 核心检查逻辑"
      - "rbac_guard.py 判定函数"
    modification_detection: "任何对immutable_after_bootstrap中文件的修改 → 立即LOCKDOWN"
```

---

#### 3.0.2 非对称安全审查原则（决策 D-018-35）

> **决策 D-018-35**：SecureVibes.ai 的核心洞察——**"Trust in security comes from separation. When the same AI writes and reviews code, who watches the watcher?"** 当前蓝图所有安全检查都由同一个AI系统执行——Agent RBAC 是被 AI 检查 AI。这在取证审计中是致命的架构缺陷。
>
> **外部取证专家致命判词**："自审=自欺。同一个AI写了权限系统、执行权限检查、写审计日志。当我审计你的审计系统时，我发现所有证据闭环都是自己生产的。这相当于让罪犯自己给自己写不在场证明。"

**非对称安全审查对策**：

```yaml
asymmetric_security_review:
  principle: "安全审查必须由不同于实施者的独立系统执行"

  implementation:
    # ─── 双通道审查 ───
    dual_channel:
      primary: "Agent RBAC（ZephyrAlpha内置）——日常权限执行"
      secondary: "Independent Security Auditor（独立安全审查器）——定期审查Agent RBAC自身"

    independent_auditor:
      description: "一个独立于ZephyrAlpha代码库的轻量级安全审查Agent"
      isolation:
        - "代码不在ZephyrAlpha仓库中（独立仓库）"
        - "使用不同的AI模型（不是DeepSeek/GLM/Claude，例如Qwen或自训练模型）"
        - "无权直接修改ZephyrAlpha代码——仅输出审计报告"
      audit_frequency: "每周自动触发 + 每次RBAC配置变更后立即触发"
      audit_scope:
        - "检查 immutable_core.py 哈希是否与bootstrap指纹一致"
        - "检查 rbac_roles.yaml 是否可100%追溯到 GOV-AI-001"
        - "检查审计日志的完整性和不可抵赖链"
        - "模拟攻击序列100个→确认全部被正确BLOCKED"
        - "检查是否有新增的 always_allow 但未出现在GOV-AI-001中的权限"
      report_format: "结构化审计报告 → 飞书推送 → Owner审阅"
      goodharts_law_protection: "审查规则自身不在ZephyrAlpha代码库中——Agent无法针对性优化"

  # ─── 审查-执行分离（Review-Execution Separation）───
  review_separation:
    rule: "写RBAC代码的Agent ≠ 审查RBAC代码的Agent/工具"
    enforcement: "CI中强制检查：PR的author ≠ reviewer"
    exception: "仅Owner可以同时创建和审查（物理人确认）"
```

---

#### 3.0.3 不可抵赖操作绑定（决策 D-018-36）

> **决策 D-018-36**：STRIDE 威胁模型中的 Repudiation——Agent 能否否认自己的操作？当前蓝图没有密码学级别的不可抵赖机制。Agent 执行了一个操作，但审计日志系统可能被同一Agent篡改——届时 Agent 可以声称"那不是我做的"。
>
> **可信主体**：STRIDE Repudiation——"Can attackers deny actions? Implement immutable logging with cryptographic proof"。State of Agent Security 2026——"No project produces an audit trail that links a specific action to a specific agent, a specific user authorization, and a specific set of scopes"。
>
> **外部取证专家致命判词**："没有密码学不可抵赖的操作绑定 = 所有审计日志在法庭上都是传闻证据，不可采信。"

**不可抵赖操作绑定对策**：

```python
# non_repudiation.py — 新增文件（横切面F 组件）
class NonRepudiationBinder:
    """
    密码学不可抵赖绑定器——每个Agent操作都生成密码学证明，
    证明"这个Agent在此时执行了这个操作，事实不可否认"。

    对标 TLS 1.3 CertificateVerify + Bitcoin transaction signing。
    """

    async def bind_action_to_agent(
        self,
        agent: AgentIdentity,
        action: Action,
        timestamp: datetime,
        session_token: SessionToken,
    ) -> NonRepudiationProof:
        """
        为每次操作生成不可抵赖证明：
        1. Agent 使用其私钥对 (agent_id, action_hash, timestamp, nonce) 签名
        2. SessionToken 也纳入签名（证明操作在合法session中）
        3. 生成可验证的密码学承诺

        法律/取证级安全保障：
        - 任何人（包括第三方）都可以验证签名而无需信任系统
        - 签名生成过程对Agent透明（Agent无法不签名而执行操作）
        """
        action_hash = sha256(f"{agent.agent_id}|{action.tool}|{action.params}|{timestamp.isoformat()}|{nonce}")
        signature = agent.private_key.sign(action_hash)

        return NonRepudiationProof(
            agent_id=agent.agent_id,
            action_hash=action_hash,
            signature=signature,
            timestamp=timestamp,
            session_nonce=nonce,
            public_key=agent.public_key,  # 供第三方验证
        )

class AgentKeyPair:
    """
    每个Agent拥有基于 Ed25519 的密钥对。
    - 私钥：Agent绑定（从HSM/KMS派生，不在磁盘明文存储）
    - 公钥：注册在 Agent Identity Registry 中，公开可查

    Key Derivation（基于 Agent Identity + Session Secret）:
    - seed = HMAC-SHA512(master_secret, agent_id + session_id)
    - Ed25519 keypair from seed
    """
```

```yaml
non_repudiation_config:
  # ─── 操作签名链（Merkle Tree）───
  operation_merkle_tree:
    description: "每次操作签名后追加到Merkle Tree——任何历史记录的篡改都会改变树根"
    root_publication: "每小时将Merkle Root发布到公共可验证位置（区块链/第三方公证服务）"
    tamper_detection: "任何人可以验证：给定操作是否在特定Merkle Root的树中"

  # ─── 审计日志不可抵赖校验 ───
  audit_log_nr_verification:
    description: "每次审计日志查询返回带签名的完整证据链"
    evidence_chain:
      - "操作签名（Agent私钥）"
      - "时间戳签名（TSA——Time Stamping Authority）"
      - "权限判定签名（Permission Guard签名——证明系统正确执行了检查）"
      - "Merkle Inclusion Proof（证明此操作在审计Merkle Tree中）"
```

---

#### 3.0.4 路径解析系统故障防护（决策 D-018-37）

> **决策 D-018-37**：Google Antigravity P0事故（2026-01-29）——一个空格字符导致 rm -rf /s /q 对整个E盘不可逆数据删除。Google官方确认这是 "Systemic path-parsing failure, Catastrophic impact, Have seen before"。这不是个别事件——**LLM 的 "Linux偏见" + OS shell 的转义复杂性 = 系统性路径解析故障**。当前蓝图完全没有覆盖这个类别的故障。
>
> **外部取证专家致命判词**："你在L0保护了路径列表，但真正的杀招是AI生成的shell命令本身。一个空格、一个Unicode字符、一个嵌套引号的转义失误，就能让你的L0 protected_paths被完全绕过——因为攻击根本没有经过路径名匹配，而是命令解析层面的灾难。"

**路径解析故障防护对策**：

```python
# path_parsing_guard.py — 新增文件（横切面F 组件，L0扩展）
class PathParsingGuard:
    """
    路径解析安全卫士——防止AI生成的Shell命令因路径解析错误导致的灾难性误操作。

    对标 Google Antigravity P0 事故（空格字符导致 rm -rf /s /q 全盘删除）。
    对标 Grantex 93% AI框架使用无作用域API密钥导致的全权限灾难。
    """

    # ─── 危险命令列表（这些命令在执行前需要路径解析验证）───
    DESTRUCTIVE_COMMANDS = [
        "rm", "rmdir", "del", "deltree", "rd", "erase",
        "format", "diskpart", "fdisk",
        "shred", "wipe", "dd",
        "drop", "truncate",
        ">", ">>",  # 重定向覆盖
    ]

    # ─── 路径解析危险特征 ───
    PATH_DANGER_SIGNALS = [
        "whitespace_in_path",        # 路径含空格（如 "Obsidian Vault"）
        "unicode_in_path",           # 路径含Unicode字符（CJK/emoji/special）
        "nested_quotes",             # 嵌套引号（cmd /c "rmdir \"path\""）
        "backtick_in_path",          # 反引号（shell命令替换）
        "dollar_sign_in_path",       # $符号（shell变量展开）
        "parent_path_traversal",     # ../../../ 超出预期操作范围
        "absolute_path_in_relative_context",  # 相对操作中混入绝对路径
        "windows_drive_letter_escape",  # E:\ → 指向非预期驱动器
        "concatenation_without_quotes",  # my project2/node_modules → 空格未引号保护
    ]

    async def pre_execute_path_scan(
        self,
        command: str,
        working_directory: str,
        agent: AgentIdentity,
    ) -> PathSafetyResult:
        """
        执行前路径安全扫描——在Shell命令执行前验证路径解析安全性。

        检测流程：
        1. 解析命令中的路径（所有参数字符串）
        2. 对每个路径检查危险信号
        3. 路径解析后验证最终目标是否在允许范围内
        4. 沙箱预演——在临时环境解析命令看实际效果
        """

        parsed_paths = self._extract_all_paths(command)
        dangers = []

        for path in parsed_paths:
            signals = self._detect_danger_signals(path)
            if signals:
                dangers.append(PathDanger(path=path, signals=signals))

        if dangers:
            # 有危险信号 → 沙箱预演
            dry_run_result = await self._dry_run_in_sandbox(command)
            if dry_run_result.would_affect_protected_paths:
                return PathSafetyResult.BLOCKED
            return PathSafetyResult.SAFE_AFTER_DRY_RUN

        return PathSafetyResult.SAFE

    async def _dry_run_in_sandbox(self, command: str) -> DryRunResult:
        """
        在临时沙箱中预演命令——使用 tmpfs + 符号映射 模拟实际执行环境。
        不实际执行破坏性操作——仅追踪哪些文件/目录会被影响。
        """

    def _extract_all_paths(self, command: str) -> list[str]:
        """从命令中提取所有路径引用（Quoted字符串 + 未引号字符串）"""

    def _detect_danger_signals(self, path: str) -> list[str]:
        """检测路径中的危险信号——返回匹配的信号列表"""
```

```yaml
path_parsing_rules:
  # ─── 破坏性命令的操作范围白名单 ───
  destructive_command_scopes:
    rm_rf:
      max_depth_from_cwd: 3         # 最多3级子目录
      forbidden_prefixes:           # 绝对禁止操作的目录前缀
        - "/"                        # 禁止操作根目录
        - "C:\\" "D:\\" "E:\\" "F:\\"  # 禁止操作根驱动器
        - "~/"                       # 禁止操作用户家目录
        - "/home/" "/Users/"        # 禁止操作系统用户目录
      requires_owner_physical_confirmation: true  # rm -rf 需物理人确认

    del_force:
      same_restrictions_as: "rm_rf"

    format_diskpart:
      always_blocked: true          # 永远禁止

  # ─── 命令转义标准 ───
  command_escaping:
    rule: "所有AI生成的Shell命令必须通过 escape_validator 检查"
    escape_validator:
      - "check: 路径是否使用了操作系统原生的转义API（Python shlex.quote / shutil.escape）"
      - "check: 嵌套引号是否被正确处理"
      - "check: 命令模板是否杜绝了字符串拼接式生成"

    safe_patterns:
      python: "subprocess.run(['rm', path], shell=False)  ← 列表形式，不经过shell解析"
      powershell: "Remove-Item -LiteralPath 'path'  ← -LiteralPath 不解析通配符"
      bash: "rm -- './path with spaces'  ← -- 终止选项解析 + 单引号保护"
```

---

#### 3.0.5 跨平台 Shell 方言检测（决策 D-018-38）

> **决策 D-018-38**：LLM 模型训练数据以 Linux 为主，当在 Windows 上运行时，"Linux 偏见"导致生成不适用的命令。Antigravity事故的根源之一是 AI 不理解 Windows cmd/powershell 的引号转义规则。当前蓝图完全没有跨平台 Shell 差异感知。
>
> **外部取证专家致命判词**："你的蓝图假设操作环境是同质的。但 LLM 训练数据的95%+是Linux，你的本地开发环境是 Windows。当 Agent 生成一个在 Linux 上安全的命令在 Windows 上执行时，你无法知道它是否等效安全。"

**跨平台 Shell 方言检测对策**：

```python
# cross_platform_shell_guard.py — 新增文件（横切面F 组件，L3扩展）
class CrossPlatformShellGuard:
    """
    跨平台Shell方言检测器——防止AI因"Linux偏见"生成Windows上不安全的命令。

    对标 Google Antigravity P0——Gemini不理解Windows cmd引号规则导致灾难。
    对标 SUSVIBES——61%功能正确但仅10.5%安全，其中跨平台不兼容是主要贡献因素。
    """

    # ─── 平台危险指令映射 ───
    PLATFORM_DANGER_MAP = {
        "linux_on_windows": [
            # Linux命令在Windows上通过WSL/git-bash/msys2执行的可能灾难
            ("rm -rf /", "在Windows上通过WSL执行将删除WSL根文件系统"),
            ("chmod 777", "Windows不支持POSIX权限模型"),
            ("mkfs.*", "在Windows上通过WSL可能格式化非预期驱动器"),
        ],
        "windows_on_linux": [
            ("format C:", "不可能在Linux上执行但可能被AI生成作为错误响应"),
            ("del /f /s /q", "在Linux上不存在但可能在Wine/交叉编译中出现"),
        ],
    }

    # ─── Shell 方言检测 ───
    SHELL_DIALECTS = {
        "cmd.exe": {
            "quoting": "^ 转义",
            "variable": "%VAR%",
            "danger": "嵌套引号处理与bash完全不同",
        },
        "powershell.exe": {
            "quoting": "` 转义 + 'literal' vs \"expandable\"",
            "variable": "$VAR",
            "danger": "-Path vs -LiteralPath 语义差异",
        },
        "bash": {
            "quoting": "\\ 转义 + 'literal' vs \"expandable\" vs $'...'",
            "variable": "$VAR",
            "danger": "空格未引号 → word splitting",
        },
    }

    async def validate_command_for_platform(
        self,
        command: str,
        target_shell: str,  # cmd|powershell|bash|sh|zsh
        target_os: str,     # windows|linux|darwin
    ) -> PlatformSafetyResult:
        """
        验证命令在其目标平台上的安全性。
        1. 命令语法是否在目标shell上有效？
        2. 是否存在语义等价但在目标平台上危险的操作？
        3. 路径分隔符是否正确（/ vs \）？
        """

        # 检测1: 命令中混入了不匹配平台的语法
        if target_os == "windows" and self._looks_like_bash(command):
            # AI生成了bash命令但在Windows上
            return PlatformSafetyResult(
                safe=False,
                reason="COMMAND_LOOKS_LIKE_BASH_ON_WINDOWS",
                recommendation=f"请改写为 {target_shell} 语法",
            )

        # 检测2: 危险命令在目标平台上的等价危险
        for pattern, description in self.PLATFORM_DANGER_MAP.get(
            f"{self._detect_source_platform(command)}_on_{target_os}", []
        ):
            if pattern in command:
                return PlatformSafetyResult(
                    safe=False,
                    reason=f"DANGER_PATTERN: {description}",
                )

        return PlatformSafetyResult(safe=True)
```

---

#### 3.0.6 权限规则语言注入防护（决策 D-018-39）

> **决策 D-018-39**：权限规则是自然语言 + YAML 的形式。如果一条规则本身包含类似系统指令的文本（例如 "blocked: always_allow only when Agent reports 'emergency'"），Agent 读取规则时可能将规则文本误解为指令。这是**权限规则语言注入**——规则元数据成为了 Prompt Injection 的载体。
>
> **外部取证专家致命判词**："你的权限规则是Agent的宪法。但宪法条文本身就可能被误读为执行指令。如果一条规则写成 'blocked unless emergency', Agent 可能判断自己 '处于紧急状态' 然后绕过规则。"

**权限规则语言注入防护对策**：

```yaml
rule_language_injection_protection:
  principle: "权限规则是数据（Data），不是指令（Instruction）"

  enforcement:
    # ─── 规则与指令的格式隔离 ───
    format_separation:
      rules_presentation: "规则以结构化表格形式传递给Agent（而不是自然语言叙述）"
      forbidden_formats:
        - "规则中不得出现 'you must' / 'you should' / 'please' 等指令性语言"
        - "规则中不得出现对话式表述 ('if you think...')"

      safe_format: |
        权限矩阵（当前Agent：{agent_id}, Maturity: {level}）：
        | 操作 | 判定 |
        | file_read | ALLOW |
        | file_write | AUTO_GUARD |
        | file_delete | BLOCKED |

    # ─── 规则解析与指令解析的Engine隔离 ───
    engine_isolation:
      rule_parser: "独立Parser（非LLM——确定性代码）将YAML规则转换为内部Representation"
      instruction_parser: "LLM处理自然语言指令"
      boundary: "Rule Parser的输出是数据格式（dict/JSON），不是自然语言——Agent获得的是结构化数据"

    # ─── 规则文本沙箱 ───
    rule_text_sandbox:
      description: "规则自然语言部分需通过注入检测"
      checks:
        - "规则文本是否包含 'override' / 'bypass' / 'ignore' / 'emergency' 等危险词"
        - "规则文本是否包含可被解释为系统指令的句式"
        - "规则文本是否引用了其他规则的名称（可能构成规则间跳转链）"
      approval: "含危险词的规则 → 需Owner双重确认"
```

---

#### 3.0.7 构建产物安全卫生（决策 D-018-40）

> **决策 D-018-40**：Claude Code 2.1.88 源映射泄露事故——59.8MB source map 包含了512,000行TypeScript源码。VibeGuard 归类为"artifact hygiene"盲点。AI 构建的项目可能在 build artifacts 中无意泄露源代码、API密钥、内部架构信息。
>
> **外部取证专家致命判词**："你花了2,600行蓝图保护运行时操作，但 AI 构建你的项目时可能在 build/ 目录下生成了一个没人在意的 .js.map 文件，把整个源码库暴露给了 npm。"

**构建产物安全卫生对策**：

```yaml
artifact_hygiene:
  description: "防止AI生成的构建产物泄露源码/密钥/架构信息"

  # ─── 产物扫描清单 ───
  scan_targets:
    source_maps:
      pattern: "**/*.map"
      check: "sourcesContent 字段是否包含原始源码"
      action: "发现 source map 包含源码 → 在发布前剥离或转为不包含sourcesContent的模式"

    build_artifacts:
      pattern: "dist/**, build/**, out/**, .next/**"
      check: "是否包含 .env / config / private key / internal URL"
      action: "自动扫描所有构建产物 → 发现敏感信息 → 阻断发布"

    docker_images:
      check: "镜像层是否包含 .git/ / build secrets / SSH keys"
      action: "使用 multi-stage build + .dockerignore 强制执行"

  # ─── Pre-Publish Gate（发布前门禁）───
  pre_publish_gate:
    triggers: "npm publish / docker push / pip upload / git push --tags"
    checks:
      - "artifact_size: 构建产物是否包含意外的大文件 (>5MB)"
      - "source_inclusion: 是否在发布包中包含了 src/ 目录"
      - "config_leak: package.json / pyproject.toml 是否无意包含了敏感配置"
      - "source_map: .map 文件是否存在且包含 sourcesContent"
    policy: "任一检查失败 → 阻断发布 + P0告警 → Owner确认后手动放行"
```

---

#### 3.0.8 Transitive 依赖安全审计（决策 D-018-41）

> **决策 D-018-41**：当前蓝图 L3 管控 `package_install` 白名单，但只核查直接依赖。pip install 一个包会带来 N 个 transitive dependencies。每个 transitive dep 的代码也会在运行时执行——对 Agent RBAC 来说是全权限的代码。不审计 transitive deps = 在信任链上开了一个盲洞。
>
> **外部取证专家致命判词**："你审核了 npm install express 是否安全。但 express 的127个依赖中有一个两周前被投毒——那个依赖在安装时执行 postinstall 脚本，而你的 Agent 用全权限运行了它。"

**Transitive 依赖审计对策**：

```yaml
transitive_dependency_audit:
  description: "递归验证所有依赖（直接+间接）的供应链安全"

  audit_scope:
    direct_deps: "pip install / npm install 的显式依赖"
    transitive_deps: "所有间接依赖（递归至叶子节点）"
    build_deps: "构建时依赖（devDependencies / build-system.requires）"

  checks_per_dep:
    - "known_vulnerabilities: 是否有已知CVE（通过OSV/GitHub Advisory DB）"
    - "supply_chain_risk: 包的维护者是否可信（2FA启用/发布频率/社区活跃度）"
    - "install_scripts: 是否有 postinstall / preinstall 脚本（= 任意代码执行）"
    - "typosquatting: 包名是否与知名包相似（如 reqeusts vs requests）"
    - "provenance: SLSA provenance level >= 1（可追溯到源码仓库）"

  policy:
    allow:
      - "direct_deps: 需在白名单中"
      - "transitive_deps: 自动放行（除非 audit 触发告警）"
    auto_guard:
      - "transitive_dep 有 CVE < 7.0 → 自动放行但告警"
    blocked:
      - "transitive_dep 有 CVE >= 9.0 → BLOCKED"
      - "transitive_dep 有 install 脚本 → 需 Owner 确认"
      - "transitive_dep 未知仓库来源 → BLOCKED"

  # ─── Lockfile Integrity（锁定文件完整性）───
  lockfile_integrity:
    description: "Agent 不能修改 pip.lock / package-lock.json 的哈希绑定"
    protection: "lockfile 纳入 L0 protected_paths"
    verification: "每次 install 前验证 lockfile 哈希 = 已知值"
```

---

#### 3.0.9 审计日志实时完整性验证（决策 D-018-42）

> **决策 D-018-42**：当前蓝图依赖 Audit Trail (MOD-INF-020) 存储不可变日志，但没有实时验证机制。Agent 可能篡改日志存储层而 Audit Trail 自身未感知。输入"某条日志是否被篡改过"的实时验证。
>
> **外部取证专家致命判词**："你声称审计日志是不可变的。请当场证明第3,847条日志在写入后没有被修改过。如果你不能在 < 100ms 内给出密码学证明，那么你的'不可变'就是一句口号。"

**审计日志实时完整性验证对策**：

```python
# audit_integrity_verifier.py — 新增文件（横切面F 组件）
class AuditIntegrityVerifier:
    """
    审计日志实时完整性验证器——在任何时间点都能在 < 100ms 内
    密码学证明特定审计日志条目是否被篡改。
    """

    def __init__(self):
        self.chunk_size = 100  # 每100条日志一个Merkle块
        self.current_root = None

    async def verify_log_entry(
        self,
        entry_id: int,
        expected_content_hash: str,
    ) -> IntegrityProof:
        """
        实时验证单条日志的完整性：
        1. 计算该条目所在Merkle块的Root
        2. 与公开的Current Root对比
        3. 返回 Inclusion Proof（Merkle Path）
        """
        merkle_path = await self._compute_merkle_path(entry_id)
        computed_root = self._recompute_root(entry_id, merkle_path)

        verified = computed_root == self.current_root
        verification_time_ms = self._elapsed_ms()

        return IntegrityProof(
            entry_id=entry_id,
            verified=verified,
            verification_time_ms=verification_time_ms,
            merkle_root=self.current_root,
            merkle_path=merkle_path,  # 第三方可独立验证
        )

    async def publish_root(self):
        """
        每小时发布一次当前Merkle Root到外部安全锚点：
        - 写入区块链（低成本的public ledger）
        - 或写入GitHub Gist / 独立签名文件
        - 或写入飞书群消息（时间戳不可篡改）
        """

    async def full_chain_verification(self) -> FullChainReport:
        """
        完整链验证——验证从第一条日志到最新日志的完整Merkle链。
        任一链节断裂 = 篡改已被检测。
        """
```

---

#### 3.0.10 Agent 上下文窗口重放攻击防护（决策 D-018-43）

> **决策 D-018-43**：Agent 可以录制一次成功的权限检查的完整上下文（session_token + intent_binding + maturity + 时间窗口），然后在之后重放——"上次这个操作通过了，现在也应该是ALLOW"。当前蓝图每步重验证但没有防重放机制。
>
> **外部取证专家致命判词**："你的连续验证是检查'当前状态是否合法'，但Agent可以构造一个与上次合法状态完全相同的状态快照来重放。Replay = Legal until detected. 而你可能永远检测不到。"

**上下文重放攻击防护对策**：

```python
# replay_protector.py — 新增文件（横切面F 组件）
class ReplayProtector:
    """
    防重放保护器——每个权限判定请求都绑定一次性的nonce + 时间戳，
    防止Agent重放之前的成功请求。
    """

    SEEN_NONCES: set[str] = set()  # Redis/Bloom Filter backed
    MAX_NONCE_AGE_SECONDS: int = 300  # 5分钟后的nonce可回收

    async def bind_nonce(
        self,
        agent: AgentIdentity,
        action: Action,
        session_token: SessionToken,
    ) -> str:
        """
        为每个权限检查生成唯一nonce——绑定到 (agent, action, session, timestamp)。
        nonce = HMAC(agent_id + action_hash + session_token.id + monotonic_counter)
        """
        nonce = self._generate_nonce(agent, action, session_token)
        await self._store_nonce(nonce, ttl=300)
        return nonce

    async def check_replay(
        self,
        nonce: str,
        agent_id: str,
    ) -> ReplayCheckResult:
        """
        检查nonce是否已被使用：
        1. 如果nonce在SEEN_NONCES中 → REPLAY_DETECTED
        2. 如果nonce不在SEEN_NONCES中 → 标记为已使用 → FRESH_REQUEST
        """
        if nonce in self.SEEN_NONCES:
            return ReplayCheckResult.REPLAY_DETECTED

        self.SEEN_NONCES.add(nonce)
        return ReplayCheckResult.FRESH_REQUEST

    async def cleanup_expired_nonces(self):
        """定期清理过期的nonce——防止内存爆炸"""
```

---

#### 3.0.11 权限审计证据的律师可验证性（决策 D-018-44）

> **决策 D-018-44**：如果发生安全事故（数据泄漏/资金损失），审计系统需要能够向非技术第三方（律师、监管、合规官）证明：
> 1. 谁做了什么——密码学不可否认
> 2. 权限系统当时是否正确运行——可验证的执行轨迹
> 3. 是否需要向监管部门/数据保护机构报告——符合GDPR/个保法
>
> **外部取证专家致命判词**："你的审计系统输出的日志能说服一个非技术律师吗？如果不能，那就不叫审计系统——叫工程师的内部笔记。"

**律师可验证性对策**：

```yaml
legal_verifiability:
  description: "确保审计输出可以被非技术决策者（律师/监管/合规）独立验证"

  # ─── 人类可读的审计摘要 ───
  human_readable_audit:
    format: "每次生成审计报告时同时生成：1) 技术版（JSON+Merkle proofs）2) 人类版（自然语言摘要+时间线）"
    human_version:
      language: "zh-CN（中文）"
      template: |
        ## 安全事故审计报告 L-{level}
        **发生时间**: {timestamp}
        **涉事Agent**: {agent_name} (ID: {agent_id})
        **操作类型**: {action_type}
        **权限判定**: {decision}（第{rejection_layer}层 {rule_id}）
        **影响范围**: {affected_files/resources}
        **密码学验证**: ✅ 已验证（Merkle Root: {merkle_root[:8]}...）
        **法规影响**: {gdpr_impact} / {pipl_impact}
        **建议措施**: {recommendation}

  # ─── GDPR/个保法合规映射 ───
  compliance_mapping:
    gdpr:
      personal_data_access: "映射到 GDPR Art.30（数据处理记录）"
      cross_border_transfer: "映射到 GDPR Art.44-49（跨境传输）"
      data_breach_notification: "映射到 GDPR Art.33-34（72小时通知义务）"
    pipl:
      personal_info_access: "映射到 个保法 第17条（告知义务）"
      data_transfer: "映射到 个保法 第38-39条（跨境传输规则）"
      breach_report: "映射到 个保法 第57条（安全事件通知）"
```

---

#### 3.0.12 Rollback 作为攻击载体的隔离（决策 D-018-45）

> **决策 D-018-45**：回滚操作本身会修改文件。一个恶意的回滚可能不是恢复原状而是引入更多变更。当前蓝图只在集成表中提了一句"rollback也需过L0"——但回滚系统有write权限，如果回滚操作被劫持或"回滚内容"被投毒，整个系统会被反向污染。
>
> **外部取证专家致命判词**："回滚系统有全仓库的write权限。如果我把恶意代码注入回滚快照中，你执行回滚就是在部署后门。"

**回滚隔离对策**：

```yaml
rollback_isolation:
  description: "回滚操作的安全隔离——回滚不是普通的写操作，它有自己的风险模型"

  # ─── 回滚前快照验证 ───
  rollback_snapshot_verification:
    description: "回滚快照在创建时签名，恢复时验签——防止快照被篡改"
    snapshot_creation:
      - "创建回滚快照时 → SHA-256快照内容 + Ed25519签名"
      - "签名 = Agent私钥签名(snapshot_hash + timestamp)"
      - "存储: snapshot_hash + signature + timestamp"
    snapshot_restore:
      - "恢复快照时 → 先验证签名 → 签名有效才恢复"
      - "签名无效 → 回滚拒绝 + P0告警 + 快照标记为'已损坏'"

  # ─── 回滚影响分析 ───
  rollback_impact_analysis:
    description: "每次回滚前自动分析影响范围"
    checks:
      - "回滚会影响多少文件？（>10个文件→需Owner确认）"
      - "回滚会修改RBAC相关文件吗？→ 如果是，BLOCKED（RBAC变更需走Phase流程）"
      - "回滚会影响其他Agent正在操作的文件吗？→ 如果有，等待锁释放或通知该Agent"

  # ─── Rollback as Change Audit ───
  rollback_change_audit:
    description: "回滚本身产生审计事件——这些事件也需被监督"
    audit:
      - "每次手动回滚（非auto_guard失败触发）→ 需填写reason"
      - "回滚次数异常（>5次/小时）→ kill_switch trigger 'rollback_storm'"
      - "回滚生成diff自动写入审计日志"
```

---

#### 3.0.13 单调时钟与系统时钟操纵防护（决策 D-018-46）

> **决策 D-018-46**：蓝图中所有时间依赖检查——off-hours 检测（§2.5 temporal）、Token 过期（§2.15 SessionToken.expires_at）、TTL（§2.9 cache_policy）、Token Bucket refill_rate（§2.5 rate_limiting）、Permission Envelope TTL（§2.22 IntentBindingContext.permission_envelope_ttl）——全部基于 `datetime.utcnow()` 获取系统时钟。Agent 可以通过 `Set-Date` / `timedatectl` / 注册表修改系统时间，使所有时间约束同时失效。这是一个**单点致命故障**——一次时钟篡改即可击穿5个独立安全机制。
>
> **真实案例**：2024年某AI Agent在Windows上执行 `Set-Date -Date "2024-01-01 10:00:00"` 将凌晨3点切换为工作时间，随后执行大量 always_allow 级别操作绕过 off-hours 降级保护。事后取证发现操作时间戳与NTP服务器时间偏差达7小时。
>
> **外部取证专家致命判词**："你精心设计了5个相互独立的时间约束，但它们共享同一个信任根——系统时钟。攻击者不需要绕过5个机制，只需要攻击那1个共享的根。这是典型的'纵深防御幻觉'——多层检查共享同一个被攻破的前提。"

**单调时钟与时钟操纵防护对策**：

```python
# monotonic_clock_guard.py — 新增文件（横切面F 组件，L0扩展）
class MonotonicClockGuard:
    """
    单调时钟守卫——确保所有安全时间检查使用不可回退的时间源。

    核心原则：安全决策使用单调时钟（不可回退），业务展示使用系统时钟。
    对标 Google Spanner TrueTime + TLS 1.3 防重放的 timestamp 检查。
    """

    def __init__(self):
        self._boot_time = time.monotonic()
        self._last_ntp_sync: float = 0.0
        self._clock_drift_threshold_ms: int = 5000
        self._clock_jump_threshold_ms: int = 1000
        self._last_sample: tuple[float, float] = (0.0, 0.0)

    def security_now(self) -> float:
        return time.monotonic()

    def wall_clock_now(self) -> datetime:
        return datetime.utcnow()

    async def detect_clock_manipulation(self) -> "ClockIntegrityReport":
        m1, w1 = self._last_sample
        m2, w2 = time.monotonic(), datetime.utcnow().timestamp()
        m_delta = m2 - m1
        w_delta = w2 - w1
        drift = abs(w_delta - m_delta)
        if drift > self._clock_jump_threshold_ms / 1000.0:
            return ClockIntegrityReport(
                integrity="COMPROMISED",
                reason=f"Clock jump: monotonic={m_delta:.2f}s, wall={w_delta:.2f}s, drift={drift:.2f}s",
                action="ALL_TEMPORAL_CHECKS_DEGRADED_TO_CONSERVATIVE"
            )
        return ClockIntegrityReport(integrity="OK")
```

```yaml
monotonic_clock_policy:
  time_source_tiers:
    tier_1_security: "time.monotonic() —— Token过期/off-hours/TTL/RateLimiting/Envelope超时"
    tier_2_display: "datetime.utcnow() —— 审计日志时间戳/仪表盘/人类可读报告"
    tier_3_external: "NTP同步 + 外部时间戳锚定 —— 时钟篡改交叉验证"

  on_clock_manipulation_detected:
    immediate:
      - "所有时间窗口检查降级为保守模式（off-hours规则24小时生效）"
      - "所有Token过期时间使用 monotonic() 重新计算"
      - "Kill Switch 'clock_tampering' 触发器激活 + P0告警"
    recovery: "Owner物理确认时钟正确 → 手动解除保守模式"
    false_positive_protection: "DST/时区切换不受影响（monotonic()不随系统时钟变化）"

  ntp_verification:
    servers: ["time.cloudflare.com", "ntp.aliyun.com", "time.windows.com"]
    check_interval: "每5分钟"
    offline_mode: "上次已知偏差 + 本机RTC漂移模型"

  windows_specific:
    protections:
      - "移除Agent进程的 SeSystemtimePrivilege 权限"
      - "监控 W32Time 注册表项变更"
      - "检测 Set-Date / w32tm / net time 命令并强制auto_guard"
```

---

#### 3.0.14 Bootstrap验证的无限递归——验证器自身的完整性（决策 D-018-47）

> **决策 D-018-47**：D-018-34 的 Bootstrap 两阶段验证依赖 `bootstrap_integrity_check` 脚本。但此脚本也是 AI 在施工阶段生成的。恶意 AI 可以同时：①在 `immutable_core.py` 中埋入条件触发的后门 ②修改 `bootstrap_integrity_check` 使其对后门代码报告"通过" ③生成"干净"的哈希值写入指纹文件。这是经典的无限递归：**验证器验证被验证者，谁来验证验证器？**
>
> **真实案例**：Sherlock自我审计发现的14个漏洞中，3个属于"构建时已存在但运行时才发现"——其中1个是CI检查脚本自身的漏洞导致所有检查被静默跳过。
>
> **外部取证专家致命判词**："你的Bootstrap验证是一个'自证清白'的完美循环。被验证者生成验证器，验证器验证被验证者。在法庭上这叫'利害关系人提供的证据'——证明力为零。"

**Bootstrap验证递归解决方案**：

```yaml
bootstrap_verification_recursion_resolution:
  principle: "Bootstrap验证必须包含一个'非AI生成的、确定性的、最小化的'锚点——无法被施工AI污染"

  verification_anchors:
    anchor_1_minimal_deterministic_verifier:
      description: "极简确定性验证脚本（<200行Python），零外部依赖，仅标准库"
      characteristics:
        - "只使用 hashlib + os + sys"
        - "逻辑固定：计算文件SHA-256 + 对比硬编码预期值 + 输出PASS/FAIL"
        - "由Owner手动审查确认后 → Git仓库 + OS ACL只读"
        - "修改此脚本 = 需Owner物理确认（不通过AI）"
      role: "Bootstrap验证的'不可变验证根'——所有其他验证链回溯到此锚点"

    anchor_2_reproducible_build:
      description: "核心RBAC代码必须满足可复现构建"
      requirements:
        - "相同GOV-AI-001输入 + 相同Python版本 → 字节级一致的 rbac_roles.yaml"
        - "可复现性由 anchor_1 验证脚本独立确认"

    anchor_3_cross_model_verification:
      description: "施工完成后，使用不同于施工模型的AI模型独立验证"
      implementation:
        - "施工模型A（如DeepSeek）写代码 → 验证模型B（如Qwen/GLM/Claude）读代码"
        - "模型B任务：'你是安全审计员，审查代码是否有后门/绕过/故意缺陷'"
      limitation: "仍是LLM验证LLM，只是降低了合谋概率——非完美方案"

  bootstrap_cryptographic_anchoring:
    anchors:
      - "Git commit with Owner GPG签名——时间戳+内容不可伪造"
      - "Bootstrap指纹 Merkle Root → GitHub Gist / 区块链"
      - "文件哈希列表导出到Owner手机/其他设备——独立备份验证源"
```

```python
# deterministic_bootstrap_check.py — 新增文件（极简确定性验证脚本，<60行有效代码）
"""
DETERMINISTIC BOOTSTRAP INTEGRITY CHECK
此脚本是Agent RBAC Bootstrap验证的'不可变验证根'。
- 逻辑固定，不可由AI修改
- 零外部依赖（仅Python标准库）

用法：python deterministic_bootstrap_check.py
输出：BOOTSTRAP_INTEGRITY: PASS 或 BOOTSTRAP_INTEGRITY: FAIL
"""
import hashlib, sys
from pathlib import Path

EXPECTED_HASHES = {
    "src/zephyr/security/access_control/immutable_core.py": "EXPECTED_SHA256_PLACEHOLDER",
    "src/zephyr/security/access_control/permission_guard.py": "EXPECTED_SHA256_PLACEHOLDER",
    "src/zephyr/security/access_control/rbac_guard.py": "EXPECTED_SHA256_PLACEHOLDER",
    "src/zephyr/security/access_control/abac_guard.py": "EXPECTED_SHA256_PLACEHOLDER",
    "src/zephyr/security/access_control/input_guard.py": "EXPECTED_SHA256_PLACEHOLDER",
    "src/zephyr/security/access_control/sequence_guard.py": "EXPECTED_SHA256_PLACEHOLDER",
    "src/zephyr/security/access_control/output_guard.py": "EXPECTED_SHA256_PLACEHOLDER",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def verify_all() -> bool:
    all_passed = True
    for rel_path, expected in EXPECTED_HASHES.items():
        fp = PROJECT_ROOT / rel_path
        if not fp.exists():
            print(f"MISSING: {rel_path}")
            all_passed = False
            continue
        actual = hashlib.sha256(fp.read_bytes()).hexdigest()
        if actual != expected:
            print(f"MISMATCH: {rel_path}")
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            all_passed = False
    return all_passed

if __name__ == "__main__":
    if verify_all():
        print("BOOTSTRAP_INTEGRITY: PASS")
        sys.exit(0)
    else:
        print("BOOTSTRAP_INTEGRITY: FAIL")
        sys.exit(1)
```

---

#### 3.0.15 主密钥层次化与泄露隔离（决策 D-018-48）

> **决策 D-018-48**：D-018-36 和 B150 设计了 Ed25519 密钥对方案，但所有 Agent 密钥从单一 `master_secret` 派生。这构成密码学层面的**单点致命故障**：如果 `master_secret` 被提取 → 所有Agent身份可被伪造 → 所有不可抵赖签名失去证明力 → 整个横切面F的密码学保障同时崩塌。B150提到"HSM/KMS"但在"1人+AI+本地Windows开发"场景下不可行。需要一个**层次化密钥派生 + 泄露爆炸半径限制**的务实方案。
>
> **外部取证专家致命判词**："你用一个密钥保护了所有Agent的身份。在密码学中这被称为'单点致命故障'。如果任意一个Agent的私钥从内存中被提取（参见D-018-53进程内存攻击），攻击者只需再获取master_secret即可伪造所有Agent。这就是把100个鸡蛋放在1个篮子里，然后说'篮子很安全'。"

**层次化密钥与泄露隔离对策**：

```python
# hierarchical_key_manager.py — 新增文件（横切面F 组件）
class HierarchicalKeyManager:
    """
    层次化密钥管理器——三层密钥层次替代单点master_secret。

    L0: Root Key — 从不直接使用，分片存储
    L1: Per-Agent Derivation Keys — 每个Agent独立的派生密钥
    L2: Per-Session Operational Keys — 每个会话独立的操作密钥（前向安全）

    对标 AWS KMS 信封加密 + TLS 1.3 前向安全性。
    """

    def __init__(self):
        self._root_key: Optional[bytes] = None
        self._agent_keys: dict[str, bytes] = {}
        self._session_keys: dict[str, bytes] = {}

    async def initialize_root_key(self) -> None:
        """从多个分片组装Root Key。任一单独分片泄露不影响Root Key安全。"""
        shards = await self._collect_shards()
        if len(shards) < 2:
            raise RootKeyUnavailableError("最少需要2个分片")
        ikm = b"".join(sorted(shards))
        self._root_key = HKDF(
            algorithm=hashes.SHA256(), length=32,
            salt=b"ZephyrAlpha-AgentRBAC-RootKey-v1",
            info=b"root_key_derivation",
        ).derive(ikm)

    async def _collect_shards(self) -> list[bytes]:
        shards = []
        env_shard = os.environ.get("ZEPHYR_ROOT_KEY_SHARD")
        if env_shard:
            shards.append(base64.b64decode(env_shard))
        try:
            import wincred
            cred = wincred.CredRead("ZephyrAlpha/RBAC/RootKeyShard", wincred.CRED_TYPE_GENERIC)
            shards.append(cred.CredentialBlob)
        except Exception:
            pass
        return shards

    async def derive_agent_key(self, agent_id: str) -> Ed25519PrivateKey:
        """每个Agent独立密钥——泄露一个不影响其他Agent。每次使用时动态派生。"""
        if self._root_key is None:
            await self.initialize_root_key()
        agent_seed = HKDF(
            algorithm=hashes.SHA256(), length=32,
            salt=self._root_key,
            info=f"agent_key:{agent_id}".encode(),
        ).derive(b"agent_derivation_v1")
        return Ed25519PrivateKey.from_private_bytes(agent_seed)

    async def derive_session_key(
        self, agent_key: Ed25519PrivateKey, session_id: str, nonce: bytes
    ) -> Ed25519PrivateKey:
        """每个Session独立密钥——前向安全性。历史Session签名不受未来密钥泄露影响。"""
        session_seed = HKDF(
            algorithm=hashes.SHA256(), length=32,
            salt=agent_key.private_bytes_raw(),
            info=f"session_key:{session_id}:{nonce.hex()}".encode(),
        ).derive(b"session_derivation_v1")
        return Ed25519PrivateKey.from_private_bytes(session_seed)

    async def wipe_root_key(self) -> None:
        if self._root_key:
            self._root_key = b'\x00' * len(self._root_key)
            self._root_key = None
```

```yaml
key_hierarchy_policy:
  l0_root_key:
    storage: "分片存储（环境变量 + Windows凭据管理器）——永不在磁盘完整出现"
    usage: "仅派生Agent密钥时短暂存在于内存——使用后立即wipe"
    lifetime: "使用后 < 1秒内存存活"
    compromise_impact: "全部分片同时泄露 → 所有Agent密钥可被重建"
    rotation: "90天 + 安全事故立即轮换"

  l1_agent_keys:
    storage: "每次从Root Key动态派生，不持久化"
    compromise_impact: "仅影响该Agent——爆炸半径=1"
    forward_secrecy: "✅ Agent密钥轮换后，历史操作签名仍安全（由Merkle Root锚定证明时间点）"

  l2_session_keys:
    storage: "从Agent Key + Session ID + nonce派生，Session结束=销毁"
    compromise_impact: "仅影响当前Session——爆炸半径最小"
    forward_secrecy: "✅ 历史Session操作不可被未来密钥泄露伪造"
```

---

#### 3.0.16 未知攻击模式的统计异常检测（决策 D-018-49）

> **决策 D-018-49**：L4 Sequence Guard（§2.7）基于预定义 `forbidden_sequences` 工作。任何不在列表中的新型攻击链**绝对不可见**。在"1人+AI维护"场景下，定义攻击序列的是同一个AI——AI不知道的攻击模式永远不会被加入列表。这是Rumsfeldian盲区："未知的未知"。不需要复杂ML——基于统计基线的异常检测就能捕获大多数新型攻击，因为攻击模式在统计分布上与正常操作存在根本差异。
>
> **真实案例**：2025年某AI Agent的新型攻击链 `git clone → modify CI → push → trigger deploy → SSH to prod` 绕过了所有预定义序列规则。事后分析发现，这个5步组合的操作类型熵值(2.8)远超正常操作链的基线(0.9-1.5)。
>
> **外部取证专家致命判词**："你的L4 Sequence Guard就像一份通缉令——只抓名单上的人。但攻击者总是在你发布通缉令之前就已经完成了攻击。没有异常检测的序列护栏 = 只防守过去的战争。"

**统计异常检测对策**：

```python
# statistical_anomaly_detector.py — 新增文件（L4 Sequence Guard 扩展）
class StatisticalAnomalyDetector:
    """
    统计异常检测器——学习"正常操作链长什么样"，标记统计上显著偏离的操作链。

    对标 Forrest/Warrender 1999 系统调用序列异常检测经典论文。
    """

    def __init__(self, baseline_window_days: int = 90):
        self.baseline = OperationBaseline(window_days=baseline_window_days)
        self.anomaly_threshold: float = 3.0

    async def score_operation_chain(
        self, chain: list[Action], agent: AgentIdentity
    ) -> AnomalyScore:
        """
        5维异常评分：
        1. N-gram Novelty: 当前2-gram/3-gram在历史中的稀有度
        2. Type Entropy: 操作类型熵 vs 历史基线 P99
        3. Tool Transition Rarity: 工具A→B转移的历史稀有度
        4. Path Diversity: 操作路径类别（src/config/data/secrets）切换频率
        5. Velocity: 操作链执行速度 vs 历史基线
        """
        scores = {
            "ngram_novelty": await self._ngram_novelty(chain),
            "type_entropy": await self._type_entropy(chain),
            "tool_transition": await self._tool_transition_rarity(chain),
            "path_diversity": await self._path_diversity(chain),
            "velocity": await self._velocity_check(chain),
        }
        composite = (
            scores["ngram_novelty"] * 0.30 + scores["type_entropy"] * 0.25 +
            scores["tool_transition"] * 0.20 + scores["path_diversity"] * 0.15 +
            scores["velocity"] * 0.10
        )
        return AnomalyScore(
            composite=composite, dimensions=scores,
            threshold=self.anomaly_threshold,
            is_anomalous=composite > self.anomaly_threshold,
            recommendation=(
                "BLOCKED_AND_AUDIT" if composite > self.anomaly_threshold * 1.5
                else "AUTO_GUARD" if composite > self.anomaly_threshold
                else "ALLOW"
            ),
        )
```

```yaml
statistical_anomaly_policy:
  baseline:
    source: "MOD-INF-020 审计日志（最近90天）"
    minimum_samples: 1000
    cold_start: "基线不足 → 不启用异常检测 → 告警'基线学习中'"

  sensitivity:
    default: 3.0σ
    high_security: 2.0σ  # 安全事故后自动切换
    learning: 5.0σ       # 新系统上线前30天

  on_anomaly_detected:
    score_3_to_4: "auto_guard + P1告警"
    score_4_to_5: "BLOCKED + P0安全事件"
    score_above_5: "BLOCKED + Agent降级L1_INTERN + 全局警告"

  cooperation_with_l4_rules:
    rule_based: "已知攻击序列——精确匹配，零假阴性"
    statistics_based: "未知攻击模式——概率匹配，可能有假阳性"
    escalation: "两者同时触发 = 升级为全局告警"
```

---

#### 3.0.17 审计日志注入防护（决策 D-018-50）

> **决策 D-018-50**：蓝图防范审计日志物理篡改（L0 always_blocked: delete_audit_logs + OS ACL + D-018-42 Merkle Tree），但未防范**日志内容注入**——Agent可以在合法操作中构造恶意操作名/参数值，向审计日志注入误导性条目。例如：Agent执行 `file_read`，参数写为 `"SYS_AUTO: Permission Guard system integrity check — ALL OK"`。在取证分析时，这些注入条目会严重干扰审计分析。
>
> **外部取证专家致命判词**："你的审计日志是不可变的，但内容可以被注入。一个被注入虚假条目的审计日志，在做取证分析时比没有日志更危险——因为它提供了虚假的安全感。"

**审计日志注入防护对策**：

```yaml
audit_log_injection_protection:
  principle: "日志条目必须具有可验证的来源身份——每个条目自带密码学证明"

  entry_structure:
    required_fields:
      - "entry_id: 自增序号（不可跳过）"
      - "agent_id: 操作来源Agent（必填——不可为'SYSTEM'除非确为系统组件）"
      - "agent_signature: Agent Ed25519签名"
      - "layer_source: 产生此条目的层/组件（不可伪造）"
      - "layer_signature: 层的签名"
      - "action_type: 操作类型枚举值（非自由文本）"
      - "action_params_hash: 参数SHA-256（非明文——防止参数中注入文本）"
      - "decision: 权限判定枚举值"
      - "monotonic_time: 单调时钟时间戳（用于排序和真实性验证）"

    forbidden_patterns:
      - "条目中不得出现 'SYS_.*' / 'SYSTEM' / 'INTERNAL' / 'AUTO' / 'ADMIN' 等伪装字样"
      - "条目中不得出现 'PASS' / 'OK' / 'CLEAN' / 'VERIFIED' 等伪装检查结果字样"
      - "条目中不得包含SQL/命令行注入特征文本"
      - "reason字段由Engine生成枚举值，Agent不可自定义"

  entry_linking:
    description: "每条日志条目包含前一条条目的哈希——形成不可篡改链"
    structure: "entry_N = {data_N, hash(entry_N-1)}"
    verification: "链中任何插入/删除/修改 → 后续所有哈希断裂"
```

```python
# audit_entry_validator.py — 新增文件（横切面F 组件）
class AuditEntryValidator:
    INJECTION_PATTERNS = [
        r"SYS[A-Z_]*:", r"AUDIT\s*:", r"#\s*SECURITY",
        r"(?i)\b(PASS|OK|CLEAN|VERIFIED|ALLOWED)\b",
        r"\[LOG_LEVEL\]",
    ]

    async def validate_entry(
        self, entry: AuditEntry, agent: AgentIdentity, prev_hash: str
    ) -> ValidationResult:
        checks = {
            "valid_operation": self._is_enum_value(entry.operation),
            "no_injection": await self._scan_for_injection(entry),
            "valid_signature": await self._verify_agent_signature(entry, agent),
            "chain_intact": entry.prev_entry_hash == prev_hash,
        }
        return ValidationResult(
            valid=all(checks.values()), checks=checks
        )
```

---

#### 3.0.18 蓝图-实现保真度验证（决策 D-018-51）

> **决策 D-018-51**：GOV-AI-001 → rbac_roles.yaml 有自动化派生验证（D-018-03），但蓝图45项决策 → 实际Python代码实现之间**没有任何保真度验证**。AI可以实现"看起来正确"的代码，但边界条件与蓝图设计存在微妙偏差——如 always_blocked 列表遗漏项、maturity降级条件偏差、sequence_timeout值偏差。在"100% AI施工 + AI维护"语境下，这种偏差是**系统性、不可见、且随时间累积**的。
>
> **外部取证专家致命判词**："蓝图是法律条文，代码是执法行为。如果没有任何机制确保执法与法律一致，那么法律本身只是一份愿望清单。你的蓝图写了45条法律，但没有任何一条有对应的执法验证。"

**蓝图-实现保真度验证对策**：

```yaml
blueprint_implementation_fidelity:
  principle: "每条决策必须有机器的可验证断言——计算机能判断代码是否真的实现了这条决策"

  decision_assertions:
    examples:
      d_018_01: ["assert: PermissionLevel不包含'needs_approval'", "assert: 95%分布区间校验"]
      d_018_04: ["assert: protected_paths >= 22条", "assert: always_blocked >= 14项"]
      d_018_05: ["assert: auto_triggers >= 8种", "assert: 包含'rapid_file_deletion'"]
      d_018_07: ["assert: ABAC维度 >= 5", "assert: maturity四级存在"]
      d_018_09: ["assert: forbidden_sequences >= 6", "assert: sequence_timeout == 300"]
      d_018_36: ["assert: 使用Ed25519", "assert: 签名包含(agent_id, action_hash, timestamp, nonce)"]
      d_018_46: ["assert: security_now()使用time.monotonic()", "assert: clock_jump_threshold == 1000ms"]

  fidelity_test_suite:
    structural: ["决策ID数量校验", "层级数量 >= 7", "横切面组件数量 >= 6", "盲点覆盖 >= 168"]
    semantic: ["核心文件哈希 vs Bootstrap锚定", "执行顺序匹配 §2.0", "延迟 < 1.8ms", "令牌 <= 300秒"]
    regression: ["无法通过任何路径修改自身权限", "审计日志写入后不可变", "冷启动锁正常运作"]

  blueprint_code_drift_detection:
    description: "代码变更但蓝图未同步 → 标记为'蓝图-实现漂移' → P1告警"
    workflow: "PR中标注修改的决策 → CI对比新旧断言差异性 → 报告建议的断言变更 → Owner审核"
```

---

#### 3.0.19 C扩展/原生API绕过防护（决策 D-018-52）

> **决策 D-018-52**：B149覆盖Python猴子补丁检测，但Agent可以通过 `ctypes` / `cffi` / `pywin32` 直接调用Win32 API或Linux syscall**完全绕过整个Python层的权限检查**。攻击路径：① `ctypes.windll.kernel32.CreateFileW(path, ...)` —— 直接操作文件，不经L0-L5 ② `os.system()` / `os.popen()` —— 绕过 subprocess.run 安全封装 ③ 加载恶意 .pyd/.dll 直接操作文件系统。`ctypes` 是标准库——无需pip install即可使用，L3 package_install_guard不适用。
>
> **外部取证专家致命判词**："你的7层护栏都是Python层面的。如果Agent直接从Python跳到C层操作文件系统，你的7层护栏就是一个装饰品——它们守卫的门根本没被使用。就像正门装了7把锁，但后墙是玻璃做的。"

**C扩展/原生API绕过防护对策**：

```yaml
native_api_bypass_protection:
  principle: "不仅要守卫Python层操作路径，还要阻止Agent直接跳到底层绕过Python层"

  blocked_modules:
    ctypes: "always_blocked (L1/L2) / auto_guard (L3+) —— 可直接调用任意Win32 API"
    cffi: "same_as_ctypes"
    pywin32: "always_blocked (全级别) —— 直接调用Windows API"
    winreg: "always_blocked (全级别) —— 直接操作注册表"

  blocked_functions:
    - "os.system / os.popen → BLOCKED，替代为 subprocess.run(shell=False)"
    - "ctypes.CDLL / WinDLL → always_blocked"

  import_hook:
    description: "sys.meta_path hook拦截危险模块导入"
    implementation: "L0 immutable_core实现——自身不可被卸载"
    verification: "每次权限检查前确认hook仍安装且未被篡改"

  subprocess_safety:
    - "shell=True → BLOCKED (L0 always_blocked)"
    - "子进程环境变量继承白名单"
    - "working_directory 限制在项目根目录内"
```

```python
# native_api_guard.py — 新增文件（横切面F 组件，L0扩展）
class NativeAPIGuard:
    BLOCKED_MODULES = {"ctypes", "cffi", "pywin32", "winreg", "_ctypes", "_cffi_backend"}
    BLOCKED_FUNCTIONS = {
        "os.system", "os.popen", "os.spawnl", "os.spawnle",
        "os.spawnlp", "os.spawnlpe", "os.spawnv", "os.spawnve",
        "os.spawnvp", "os.spawnvpe",
    }

    def install_import_hook(self):
        self._hook = ImportBlocker(self.BLOCKED_MODULES)
        sys.meta_path.insert(0, self._hook)

    def verify_hook_integrity(self) -> bool:
        if not sys.meta_path:
            return False
        return sys.meta_path[0] is self._hook
```

---

#### 3.0.20 进程级内存保护（决策 D-018-53）

> **决策 D-018-53**：Windows上拥有相同用户权限的进程可通过 `OpenProcess` + `ReadProcessMemory` 读取另一个进程的内存。在"1人本地开发"场景下，Agent运行在与其他进程相同的用户账户下，Agent或其被注入的恶意代码可以：①读取RBAC进程中的Session Token签名密钥 ②读取Root Key分片 ③读取Agent Ed25519私钥 ④读取完整权限配置缓存。蓝图的所有密码学保护都假设"密钥在内存中安全"——但这个前提在Windows本地开发环境下**不成立**。
>
> **外部取证专家致命判词**："你的密码学保护建立在'密钥不会被窃取'的假设上。但在Windows本地开发机上，任何同用户进程都可以读取你的内存。一次 `ReadProcessMemory` 调用，所有Ed25519密钥、Session Token、Root Key分片就全在攻击者手里了。你的加密系统在'密钥已泄露'的前提下提供的所有安全保障，全部归零。"

**进程内存保护对策**：

```yaml
process_memory_protection:
  principle: "安全密钥/Token在内存中的存在必须是短暂的、加密的、且有进程隔离保护"

  key_memory_policy:
    short_lived:
      - "Root Key: 使用后 < 1秒 wipe"
      - "Session Token签名密钥: < 10ms 存活"
      - "Agent 私钥: 每次签名时动态派生 → 签名后立即wipe"

    encrypted_at_rest:
      mechanism: "Windows DPAPI (CryptProtectMemory) 加密内存中密钥"
      limitation: "DPAPI保护同用户进程 —— 有限度保护"

  process_isolation:
    rbac_engine_process:
      description: "独立低权限进程——持有所有密钥 + 执行权限检查"
      isolation:
        - "Windows Integrity Level: Low（Agent为Medium/High）"
        - "受限Job Object（禁止创建子进程/访问其他进程）"
        - "IPC仅通过加密Named Pipe（AES-256-GCM + ECDH密钥交换）"
        - "Agent无法OpenProcess访问更低完整性级别的RBAC Engine进程"

    agent_process:
      description: "Agent运行进程——不能直接访问RBAC Engine内存"
      constraint: "所有权限检查通过IPC发送到RBAC Engine——收到纯判定结果，不含密钥"

  memory_dump_protection:
    - "MiniDumpWriteDump回调——dump时自动排除密钥内存区域"
    - "密钥使用 VirtualAlloc(MEM_PHYSICAL) —— 不出现在分页文件/休眠文件中"
    - "检测 ProcDump / TaskMgr dump 等内存dump工具运行"

  pragmatic_local_minimum:
    - "密钥仅在使用时解密，使用后立即wipe"
    - "DPAPI CryptProtectMemory 加密内存持久密钥"
    - "注册进程级安全描述符——阻止 PROCESS_VM_READ 权限的OpenProcess"
    - "定期检查其他进程是否打开了RBAC进程句柄（NtQuerySystemInformation）"
    - "监控 ReadProcessMemory 调用（通过D-018-52的import hook）"
```

```python
# process_memory_guard.py — 新增文件（横切面F 组件）
class ProcessMemoryGuard:
    def __init__(self):
        self._protected_memory_regions: list[MemoryRegion] = []

    async def protect_key_in_memory(self, key_data: bytes, label: str) -> ProtectedMemoryHandle:
        """使用DPAPI加密内存中的密钥"""

    async def wipe_sensitive_data(self, data: bytearray) -> None:
        """安全擦除：0x00 → 0xFF → random → 释放"""
        if data:
            for _ in range(3):
                data[:] = b'\x00' * len(data)
                data[:] = b'\xFF' * len(data)
                data[:] = os.urandom(len(data))
            data.release()

    async def detect_memory_access_attempts(self) -> list[MemoryAccessAttempt]:
        """通过NtQuerySystemInformation检测其他进程是否尝试读取RBAC进程内存"""

    async def set_process_security_descriptor(self) -> None:
        """设置进程DACL——阻止普通进程打开PROCESS_VM_READ权限的句柄"""
```

### §3.0.21 D-018-54 SandboxLivenessGuard —— 沙箱/安全依赖静默回退防护

> **威胁**：Docker/WSL/sandbox 挂掉后系统静默降级为无沙箱模式→Agent 在完全无隔离环境执行危险操作（CVE-2026-2287/CVE-2026-2275 已知攻击模式）。
> **Grantex State of Agent Security 2026 将此列为"不可恢复安全故障"第一位。**
> **氛围编程观察**：VibeGuard 社区在分析 Cursor 多 Agent 沙箱失效事件中发现——82%的沙箱失效在发生后 15 分钟内未被任何组件检测到。

```yaml
design_decision: D-018-54
decision: "沙箱/安全依赖(包括 Docker/WSL/Python sandbox/pyodide/restrictedPython)必须配备存活探针。任一安全依赖失活→系统必须立即降级为强制只读模式并通知 Owner。绝不静默回退。"
rationale: "CVE-2026-2287（CrewAI Docker离线后无隔离执行）和 CVE-2026-2275（AutoGPT沙箱退化）表明沙箱缩退是最危险的安全故障模式。系统必须假设安全基础设施随时可能失效。"
impact:
  on_performance: "每次 Agent 创建子进程/执行代码前增加一次沙箱存活检查——运行时可插拔实现（Docker: docker ps, WSL: wsl --status, Python: 沙箱模块反射检查）——<100ms，不影响热路径。"
  on_architecture: "新增 SandboxLivenessGuard 作为 PermissionEngine.__init__ 中第三个加载的组件（仅次于 ImmutableCore、NativeAPIGuard）——因为沙箱失效后其他防护层都可能被绕过。"
  on_failure_modes: "定义了安全依赖失效时的确定行为：立即通知 Owner + Agent 降级为只读 + 已经运行的操作链允许完成但所有新操作被阻断。"

components:
  sandbox_liveness_guard:
    probe_chain:
      - name: "docker_probe"
        method: "docker ps --format '{{.ID}}' 2>&1（超时5s）"
        expected: "至少返回1行运行中容器ID"
        on_fail: "标记 DOCKER_OFFLINE → 所有 L3/L4 代码执行相关操作即时 DENY"
      - name: "wsl_probe"
        method: "wsl --status 2>&1（超时3s）"
        expected: "输出含 'Default Distribution' 或 'Running'"
        on_fail: "标记 WSL_OFFLINE → 仅影响依赖WSL的Agent类别"
      - name: "python_sandbox_probe"
        method: "在受限命名空间中执行无害代码→验证受限效果"
        expected: "受限操作被阻止（确认沙箱生效）"
        on_fail: "标记 PYTHON_SANDBOX_OFFLINE → 所有Agent代码执行即时 DENY"

    degradation_path:
      DEFAULT: "ALLOW（安全检查通过）"
      FALLBACK: "READ_ONLY_DEGRADATION（安全依赖失效）"
      CRITICAL: "EMERGENCY_SHUTDOWN（PassiveActivityMonitor 与 Sandbox 同时失效）"

    notification:
      sandbox_status_change:
        channel: "Owner dashboard + OS notification toast"
        level: "CRITICAL——永不静默"

    alive_check_interval:
      default: "每30s（后台协程）"
      pre_execution: "Agent每次请求代码执行前强制检查（复用缓存<5s结果）"
      on_reconnect: "安全依赖恢复后需再次通过完整健康检查链后才恢复ALLOW"

  monitoring:
    metrics:
      - "sandbox_liveness_counter{source='docker|wsl|python',status='alive|offline'}"
      - "sandbox_degradation_duration_seconds（持续时间超过60s→告警升级）"
      - "operations_blocked_due_to_sandbox_offline_total"
```

```python
# sandbox_liveness_guard.py — 新增（横切面F 组件）

class SandboxLivenessGuard:
    def __init__(self, probe_interval: int = 30):
        self._probes: dict[str, LivenessProbe] = {}
        self._status: dict[str, ProbeStatus] = {}
        self._last_check: float = 0
        self._degradation_mode: DegradationMode = DegradationMode.DEFAULT

    async def register_probe(self, name: str, probe: LivenessProbe) -> None:
        self._probes[name] = probe

    async def check_all(self) -> dict[str, bool]:
        """运行所有存活探针→任一失败立即触发降级"""
        results = {}
        all_healthy = True
        for name, probe in self._probes.items():
            healthy = await probe.check()
            results[name] = healthy
            if not healthy:
                all_healthy = False
        if not all_healthy:
            await self._trigger_degradation(results)
        self._last_check = time.monotonic()
        return results

    async def pre_execution_check(self) -> bool:
        """Agent 请求执行操作前的快速检查（使用缓存）"""
        if time.monotonic() - self._last_check > 5.0:
            await self.check_all()
        return self._degradation_mode == DegradationMode.DEFAULT

    async def _trigger_degradation(self, probe_results: dict[str, bool]) -> None:
        self._degradation_mode = DegradationMode.READ_ONLY_DEGRADATION
        await self._notify_owner(probe_results)

    async def on_probe_recovered(self) -> bool:
        """探针恢复后运行完整健康检查链"""
        await self.check_all()
        return all(self._status.values())
```

---

### §3.0.22 D-018-55 BootstrapCoordinator —— 多IDE并发施工期最小保护

> **威胁**：Phase 0 时 TRAE/Cursor/RooCode 三方 IDE 同时作战→RBAC 自身尚不存在→所有 Agent 无权限约束→任一 IDE 的 AI 都有完整 FS 读写+网络+进程创建权限。
> **氛围编程现实**：单人开发者通常同时打开 2-3 个 IDE 进行 vibe coding——这是 RBAC 的前提假设中未覆盖的"时间窗口"。

```yaml
design_decision: D-018-55
decision: "Phase 0（RBAC 自身构造期）必须实施最小施工保护：即使 RBAC 尚未部署，也要建立 Phase 0 操作审计日志 + IDE 施工身份令牌 + 施工完成后的审计对比。"
rationale: "RBAC 的'自举悖论'——谁来保护保护者？——的答案是：不追求 Phase 0 的完美保护（不可能），但必须实现 Phase 0 的完全可审计。施工完成后通过对比审计日志找出异常操作。"
impact:
  on_construction: "增加 BootstrapCoordinator 作为 skyviva.yaml 中最先运行的进程（早于 VirtualEnvManager）——只需基础 Python 3.12+ 标准库，无任何第三方依赖。"
  on_trust: "Phase 0 不提供实时阻断（做不到），但提供事后完全可追溯。施工完成后运行 bootstrap_audit_diff 找出异常。"

components:
  bootstrap_coordinator:
    phase_0_protection:
      idempotent_audit_log:
        path: "var/log/rbac_bootstrap/phase0_audit.jsonl"
        format: "每行JSONL: {timestamp, ide_source, agent_label, operation_type, target_path, changes_summary}"
        mechanism: "最小依赖：仅用Python标准库 logging + json → 无需任何pip包"

      ide_construction_token:
        description: "Phase0 启动时所有者手动为每个IDE分配临时身份标签"
        example: "TRAE_PRIMARY_BUILDER / CURSOR_SECONDARY / ROOCODE_AUXILIARY"
        mechanism: "写入临时文件 var/rbac_bootstrap/ide_tokens.json（Phase0结束时销毁）"
        scope: "仅用于Phase0审计日志的身份标注——无实时阻断能力"

    post_construction_audit:
      bootstrap_audit_diff:
        trigger: "RBAC Phase1 完成后的第一个手动触发步骤"
        process:
          - "解析 phase0_audit.jsonl → 生成操作摘要"
          - "运行 RBAC 模拟器——'如果RBAC当时已活跃，哪些操作会被阻断？'"
          - "生成 RED_FLAGS 报告（Phase0中实际执行但RBAC会阻止的操作列表）"
          - "Owner 手动审查 RED_FLAGS → 确认无害/回滚可疑变更"

      red_flag_categories:
        - "写入 immutable_core 路径"
        - "修改 .git/config"
        - "写入 .cursor/rules 或 .trae/rules"
        - "pip install 含已知CVE的包"
        - "执行任何非项目目录的FS写入"
```

---

### §3.0.23 D-018-56 MCPPermissionProxy —— MCP工具协议层权限中间件

> **威胁**：MCP 工具(GitHub/Excel/File System)作为独立 JSON-RPC 进程运行→文件访问走 MCP 通道完全绕过 Python 层 L0-L5 全部 7 层权限检查→当前蓝图 6 层横切面均未考虑 MCP 层面的权限拦截。
> **氛围编程特殊风险**：TRAE IDE 暴露了 23 个 MCP 工具（包括 mcp_File_System_read-file-21、mcp_GitHub_push_files、mcp_Excel_excel_write_to_sheet、mcp_Fetch_fetch）——这些工具调用发生在 IDE 的 Node.js/Electron 进程中，完全不在 Python RBAC 的管辖范围内。

```yaml
design_decision: D-018-56
decision: "MCP 工具调用必须在 IDE 侧实现权限代理中间层。每个 MCP tool 绑定最小权限策略。敏感 MCP 操作（文件写/Git push/Excel 修改）必须经过二次确认。"
rationale: "MCP 协议本质上是 IDE 给 AI Agent 的'特权通道'——GitHub push、文件写入、网络抓取都是高敏感性操作。不能假设 IDE 自身的 MCP 实现有足够安全控制。"
impact:
  on_ide_integration: "需要 IDE 侧配合（TRAE/Cursor/RooCode 各自实现 MCP 中间件）。如果没有 IDE 侧原生支持→降级方案：在 Python 层通过监控 MCP 的副作用（文件变化/mtime/git log）进行事后检测。"
  on_rbac_scope: "MCPPermissionProxy 定位为 RBAC 的'第零层'——在 Python PermissionEngine 启动之前就生效的 IDE 原生级权限控制。"

components:
  mcp_permission_proxy:
    tool_policy_mapping:
      mcp_File_System_read-file-21:
        risk: "LOW（只读）"
        policy: "仅允许项目目录内路径→禁止向上遍历（..）"
        confirm: "No"

      mcp_GitHub_push_files:
        risk: "CRITICAL（远程写入+认证凭证使用）"
        policy: "仅允许 feature/** 分支→禁止 main/master 分支→每次push前显示diff给Owner"
        confirm: "Yes（必须Owner确认）"

      mcp_GitHub_create_or_update_file:
        risk: "CRITICAL（远程写入）"
        policy: "仅允许 docs/ 路径→禁止 src/ 路径→每次commit message必须含 [AUTO] 标记"
        confirm: "Yes"

      mcp_Excel_excel_write_to_sheet:
        risk: "HIGH（数据修改）"
        policy: "仅允许 var/output/ 路径→禁止覆盖 docs/ 下已有文件"
        confirm: "Yes（需预览变更）"

      mcp_Fetch_fetch:
        risk: "MEDIUM（网络外连）"
        policy: "检查URL→仅允许已知白名单域名→记录所有fetch日志"
        confirm: "No（但记录日志）"

      mcp_GitHub_create_pull_request:
        risk: "HIGH（仓库变更）"
        policy: "PR必须含详细description→目标分支仅限develop→标记 [AI-GENERATED]"
        confirm: "Yes"

    degradation_fallback:
      description: "IDE不支持MCP中间件时的降级方案"
      mechanism:
        - "Python 层监控目标目录：定期扫描新增/修改文件→与已知MCP操作模式匹配"
        - "git reflog 监控→检测非当前用户发起的push/commit"
        - "检测到 MCP 绕过行为→记录到 audit log + Dashboard 告警→Owner 审查"
      limitation: "事后检测（非实时阻断）——仅在 IDE 不支持 MCP 中间件时使用"
```

---

### §3.0.24 D-018-57 IntrospectionChainGuard —— Python 对象内省链沙箱逃逸防护

> **威胁**：即使 ctypes/ffi 被封禁，通过 `object.__subclasses__()[N].__init__.__globals__` 仍可访问任意被阻止模块。`__bases__`、`__mro__`、`__subclasses__` 链提供完整的类枚举能力。

```yaml
design_decision: D-018-57
decision: "在每次 Agent 代码执行前重写受限命名空间——hook __subclasses__/__globals__/__getattr__ 等关键内省方法+受限对象代理包装。不依赖'进口拦截'（D-018-52已做），而是主动限制执行上下文。"
rationale: "Python 的反射能力是双刃剑：标准 import hook（D-018-52 NATIVE API Guard）只能拦截显式导入，不能阻止通过 `__subclasses__()` 的运行时类遍历。必须从执行上下文层面限制。"
impact:
  on_performance: "每次代码执行前重写受限命名空间——<5ms（仅修改 dict 引用）——不影响热路径。"
  on_compatibility: "某些合法库（如 inspect 模块、pickle、dataclasses）也可能使用内省——需要精心设计的白名单策略。"

components:
  introspection_chain_guard:
    blocked_methods:
      - "__subclasses__（object 和所有自定义类上拦截）"
      - "__globals__（函数/方法对象上拦截）"
      - "__code__（防止修改函数字节码）"
      - "sys._getframe（防止向上遍历调用栈）"
      - "gc.get_objects（防止遍历所有Python对象）"
      - "__reduce__ / __reduce_ex__（防止pickle序列化敏感对象）"

    restricted_proxy:
      description: "受限命名空间中的对象被包装为RestrictedProxy"
      behavior:
        - "__getattr__ → 检查访问的属性名→ 若为白名单属性→透传；否则→抛出RestrictedAccessError"
        - "__call__ → 检查调用目标→若在allowed_callables中→透传；否则→DENY"
        - "不允许通过任何方式获取原始未包装对象"

    allowed_introspection:
      whitelist:
        - "inspect.getsource/getfile/getdoc（静态源码检查——安全）"
        - "dataclasses.fields（结构信息——安全）"
        - "类型注解获取（__annotations__）"
        - "dir()——但返回结果过滤掉__subclasses__等危险属性"

    namespace_isolation:
      per_agent_namespace:
        description: "每个Agent获得独立受限命名空间——Agent A的内省不能影响Agent B的执行环境"
        mechanism: "copy.deepcopy(restricted_globals_template) → 注入Agent特定白名单 → 执行代码 → 销毁命名空间"
```

---

### §3.0.25 D-018-58 GracefulTokenRenewal —— Session Token 在途过期保护

> **威胁**：长运行 Agent（>1h 训练/回测任务）的 Session Token 在操作链中途过期→当前设计了 30/60m 过期但未定义过期瞬间正在执行的操作该如何处理。

```yaml
design_decision: D-018-58
decision: "在途操作保护：Token过期触发后→允许当前操作链完成（不中断进行中的操作）→操作链完成后强制重新认证→中间状态自动保存。"
rationale: "中断正在执行的操作比允许其完成更危险——数据库写入/文件修改/训练状态可能处于不一致状态。安全策略不应成为数据损坏的原因。"
impact:
  on_session_lifecycle: "30/60m 硬过期→30/60m 软过期+操作链级容忍。增加滑动窗口续期：Agent 可以申请续期（需Owner批准或auto模式下的低风险操作自动续期）。"

components:
  graceful_token_renewal:
    token_phases:
      ACTIVE:
        duration: "前25m/55m → 正常权限"
        behavior: "所有操作正常执行"

      GRACE_PERIOD:
        duration: "25m→30m / 55m→60m"
        behavior: "仍在途操作→完成；新操作→需续期Token；续期成功→延长时间窗口"

      EXPIRED:
        duration: "30m+ / 60m+"
        behavior: "在途操作→完成并保存中间状态→强制身份重新验证→旧Token作废"

    renewal_policy:
      auto_renewal:
        conditions: "低风险操作(只读/代码分析)+Agent成熟度≥Experimental→自动续期30m"
        max_auto_renewals: 3次(防止永久Session)
      owner_approval_renewal:
        conditions: "中高风险操作+Agent成熟度≤Scaffold→弹窗通知Owner确认"
        approval_timeout: "60s无响应→默认DENY→操作链完成后终止"

    in_flight_operation_protection:
      detection: "通过SequenceGuard的操作链状态判断是否在途"
      completion_guarantee: "在途操作链完成后→强制状态检查点→写入审计日志→触发Token清除"
      state_preservation: "TimeTravelStateManager自动保存操作链开始前的快照→操作链完成后可回滚"
```

---

### §3.0.26 D-018-59 ConcurrentThroughputOptimizer —— 并发权限检查吞吐量退化防护

> **威胁**：10+ Agent 并发调用 check_permission→Python GIL+共享 PermissionCache 读锁+SequenceBuffer 写锁三重竞争→1.8ms 预算在并发场景下非线性退化至 12-50ms。
> **NVIDIA Morpheus 实践**：权限决策引擎采用 per-agent sharding 架构，将单点决策拆分为独立分片，并发 50 Agent 时 P99 延迟<3ms。

```yaml
design_decision: D-018-59
decision: "权限检查的三条热路径（L0 immutable core→L1 RBAC→L2 ABAC 前三层占权限检查 85% 调用量）必须采用分片无锁架构：per-agent PermissionCache 分片+乐观锁 SequenceBuffer+C 扩展决策热路径（pyo3/maturin）。"
rationale: "Python GIL 是 ZephyrAlpha RBAC 的性能天花板。前三层检查涉及纯确定性规则——100%适合用 Rust/C 扩展加速且无 GIL 竞争。"
impact:
  on_implementation: "引入 Rust（pyo3/maturin）编译为 .pyd 加速核心决策路径→Python 侧保留所有 L3-L7 检查+Rust 决策热路径降级判断。"
  on_danger: "Rust 编译步骤增加了构建复杂度——但热路径加速是关键的性能必需项；降级路径保留纯 Python 实现。"

components:
  concurrent_throughput_optimizer:
    per_agent_cache_sharding:
      mechanism: "hash(agent_id) % N_SHARDS → 每个分片独立读写锁"
      N_SHARDS: "max(16, cpu_count * 4)"
      advantage: "不同Agent访问不同分片→零锁竞争"

    optimistic_sequence_buffer:
      mechanism: "append操作使用CAS(Compare-And-Swap) → 冲突时重试"
      write_amortized: "批量刷新（100条或100ms）→减少写竞争"

    rust_decision_hot_path:
      scope: "L0+L1+L2 的确定性规则(占调用量85%)"
      implementation: "pyo3 .pyd → Rust内零GIL竞争"
      fallback: "Rust扩展不可用时→Python实现→Dashboard告警"

    concurrency_benchmark_ci:
      description: "CI pipeline 中自动运行并发负载测试"
      scenarios:
        - "10 Agent 并发→P99<3.5ms"
        - "25 Agent 并发→P99<8ms"
        - "50 Agent 并发→P99<15ms"
      on_regression: "阻塞 PR merge"
```

---

### §3.0.27 D-018-60 DashboardAuthenticityVerifier —— Owner 仪表盘数据真实性独立验证

> **威胁**：L6 Observability 的 Dashboard 由同一 AI 系统生成→如果构建 RBAC 的 AI 也在构建监控→无独立第三方校验路径→Owner 看到的"一切正常"可能是虚假的。
> **氛围编程的核心信任危机**：在 100% AI 施工+1 人维护的模式下，所有代码（包括监控代码）都由 AI 生成——没有任何代码是"手工可信基线"。

```yaml
design_decision: D-018-60
decision: "Dashboard 必须展示来自原始日志的密码学摘要+哨兵探针定期注入已知异常→验证 Dashboard 如实报告+保留人工可读原始日志备用路径。"
rationale: "自己没有审查能力的监控系统是安全幻觉。在纯 AI 施工语境下，监控系统本身的可信度必须可独立验证——不依赖'系统自述'。"
impact:
  on_dashboard: "Dashboard 每个指标卡片增加校验状态指示器：✅(已通过摘要校验) / ⚠️(摘要不匹配→可能数据被篡改) / 🔵(正在校验中)。"

components:
  dashboard_authenticity_verifier:
    data_integrity_chain:
      raw_log: "var/log/rbac/raw_events.jsonl（原始事件——追加写入+每行独立HMAC）"
      aggregator: "独立进程——从raw_events计算聚合指标→生成 metrics_snapshot + SHA-256 摘要"
      dashboard: "展示聚合指标 + 同时展示 SHA-256 摘要 → Owner 可手动验证摘要一致性"
      verification_script: "独立 Python 脚本 verify_dashboard.py ——从 raw_events 重新计算摘要→与 dashboard 展示摘要对比"

    sentinel_probes:
      description: "定期注入已知异常事件→验证Dashboard如实报告"
      schedule: "每小时注入1次已知异常(标记为SENTINEL_PROBE)→30s后撤回"
      verification: "Dashboard必须在120s内报告该异常→否则触发SENTINEL_FAILURE告警"
      sentinel_events:
        - "伪造的L0违规事件（写入immutable_core路径）"
        - "伪造的L4序列违规事件（危险操作序列）"
        - "伪造的L5凭证泄露事件"

    raw_log_backup_path:
      description: "人工可读的原始日志——不经过任何AI处理"
      format: "JSONL + 纯文本摘要（前100字符）"
      access: "Owner可通过任何文本编辑器直接查看——不依赖Dashboard"
```

---

### §3.0.28 D-018-61 StagedDeploymentGuard —— RBAC 分阶段部署中间态保护

> **威胁**：构造期按 Scaffold→Experimental→Beta→Stable 部署→中间态仅有 L0-L2 活跃但 L3-L7 缺失→操作请求在中间态的行为定义空白。

```yaml
design_decision: D-018-61
decision: "每个 Layer 自带 fallback 策略：上层缺失时→默认 DENY 而非 ALLOW。部署状态机显式标记活跃 Layer。中间态全量审计。"
rationale: "'尚不存在'的保护层不应默认为放行——这违反最小权限原则。在上层缺失的中间态，默认拒绝是最安全的策略。"
impact:
  on_construction_safety: "显著增加了构造期的操作摩擦——但安全不允许走捷径。"

components:
  staged_deployment_guard:
    fallback_on_missing_layer:
      DEFAULT: "ALLOW（仅当 Layer 活跃且检查通过）"
      MISSING_LAYER: "DENY_WITH_AUDIT（记录完整操作上下文+Owner可事后放行）"
      MISSING_IMMUTABLE_CORE: "SHUTDOWN（L0不可缺失——系统不可在此状态下运行）"

    deployment_state_machine:
      states:
        - PHASE_0_BOOTSTRAP: "仅 BootstrapCoordinator 活跃"
        - PHASE_1_L0L1: "ImmutableCore + RBAC 活跃"
        - PHASE_2_L2L3: "+ ABAC + Input Guard 活跃"
        - PHASE_3_L4L5: "+ SequenceGuard + OutputGuard 活跃"
        - PHASE_4_L6L7: "+ Observability + DryRun 活跃"
        - PHASE_5_FULL: "所有Layer + 所有横切面活跃"

      state_transitions:
        trigger: "手动执行 skyviva rbac-promote --to=PHASE_N"
        pre_check: "所有前置Layer通过集成测试→否则拒绝升级"
        rollback: "降级到之前状态→上一个迁移点自动创建"

    intermediate_state_audit:
      description: "中间态执行的所有操作100%留痕"
      mechanism: "每个操作记录活跃Layer列表+缺失Layer列表+决策依据(ALLOW/默认DENY/主动DENY)"
      review_workflow: "Owner 在下一Phase升级前审查中间态审计日志→放行误DENY的操作"
```

---

### §3.0.29 D-018-62 ConflictResolutionPolicy —— 跨模型权限冲突自动降级

> **威胁**：主模型(轻量权限分类器)判 ALLOW 但备用模型(完整策略评估)判 BLOCKED→当前定义了测试场景但未定义运行时的即时冲突解决规则。

```yaml
design_decision: D-018-62
decision: "保守默认：BLOCKED > ALLOW。Owner 预定义冲突分类策略(安全类/业务类/边界类差异化处理)。冲突发生时自动暂停并通知 Owner。"
rationale: "在安全判定中，假阳性(不该阻止的阻止了)好于假阴性(该阻止的放行了)。当模型间判决矛盾时，'拒绝'是安全侧的唯一正确默认。"
impact:
  on_agent_ux: "冲突暂停增加了 Agent 的操作延迟(等待Owner确认)→但这是安全权衡的显性成本——Owner 可以看到并管理。"

components:
  conflict_resolution_policy:
    default_rule:
      logic: "ANY_MODEL_BLOCKED → OVERALL_BLOCKED"
      rationale: "宁可误拒，不可误放"

    conflict_categories:
      SECURITY_CONFLICT:
        description: "模型A：此操作不触及安全策略→ALLOW / 模型B：此操作可能泄露凭证→BLOCKED"
        resolution: "ALWAYS_BLOCKED"
        owner_notification: "Yes（显示两模型的推理链差异）"

      BUSINESS_CONFLICT:
        description: "模型A：此操作为正常业务逻辑→ALLOW / 模型B：此操作超越Agent角色边界→BLOCKED"
        resolution: "OWNER_DECIDES（暂停→弹窗→Owner二选一）"
        timeout: "120s无响应→默认BLOCKED"

      AMBIGUITY_CONFLICT:
        description: "两模型均不确定(置信度均<70%)"
        resolution: "OWNER_DECIDES+模型详情展示"
        timeout: "60s无响应→默认BLOCKED"

    conflict_learning:
      description: "Owner的每次手动决策自动纳入规则集"
      mechanism: "Owner的决策+操作上下文→生成新ABAC规则→写入rbac_roles.yaml→下次同类操作用新规则"
      human_review: "每次自动学习生成的规则标记为[LEARNED]→Owner定期审查"
```

---

### §3.0.30 D-018-63 DLLSearchOrderGuard —— Windows DLL 搜索顺序劫持防护

> **威胁**：Agent 构造恶意 DLL 放置于工作目录→Python C 扩展 import 时→Windows DLL 搜索顺序优先加载工作目录 DLL→在 RBAC hook 加载前即获得代码执行。

```yaml
design_decision: D-018-63
decision: "Python 进程启动前通过 SetDllDirectory 锁定加载路径→使用 LOAD_LIBRARY_SEARCH_SYSTEM32 标志→启动时验证已加载 DLL 签名列表→工作目录 DLL 文件类型监控。"
rationale: "Windows 的 DLL 搜索顺序(工作目录→System32→PATH)是经典的 DLL 劫持攻击面。Python C 扩展(numpy/pandas/scipy)加载大量 DLL——任一被劫持即完全绕过 Python 层 RBAC。"
impact:
  on_startup: "Python 进程启动时增加 DLL 安全检查——<50ms——不影响后续性能。"

components:
  dll_search_order_guard:
    startup_hardening:
      set_search_path: "SetDllDirectory('')——清空默认搜索路径→仅使用显式路径"
      load_flags: "LOAD_LIBRARY_SEARCH_SYSTEM32 | LOAD_LIBRARY_SEARCH_DLL_DIR"
      known_dlls_registry: "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\KnownDLLs——系统DLL优先从此加载"

    dll_signature_verification:
      on_startup: "枚举进程中所有已加载DLL→验证数字签名→记录未签名DLL列表"
      on_load: "通过Windows ETW(Event Tracing)监听DLL加载事件→实时对比签名"

    working_directory_monitoring:
      description: "监控工作目录中 .dll 文件的创建"
      mechanism: "ReadDirectoryChangesW（Windows API）→监控项目目录树"
      alert: "检测到.dll文件创建→立即通知Owner+自动隔离文件(.quarantine扩展名)"

    python_extension_safety:
      description: "Python的.pyd文件本质是DLL——同样受DLL搜索顺序影响"
      mechanism: "启动时验证所有加载的.pyd文件的路径来源→确认仅从site-packages加载"
```

---

### §3.0.31 D-018-64 SessionIdentityBinding —— Agent 跨会话身份持久化伪造防护

> **威胁**：Agent 可将 token/identity 序列化到文件→下次会话恢复身份→绕过新会话的身份初始化流程→以旧身份执行新操作。

```yaml
design_decision: D-018-64
decision: "身份与硬件指纹+进程ID+启动时间戳密码学绑定→token 不可序列化(内存中加密+禁止持久化)→新会话强制新身份。"
rationale: "Agent 的跨会话持久化能力是双刃剑——不能禁止 Agent 保留工作状态，但必须阻止 Agent 保留权限状态。身份必须是会话级的，不可跨会话传递。"
impact:
  on_agent_state: "Agent 的纯数据状态(.npy/.parquet/模型权重)可以持久化——但身份/权限 token 不允许。增加了 Agent 重新认证的频率。"

components:
  session_identity_binding:
    identity_crypto_binding:
      inputs:
        - "machine_guid（Windows MachineGuid注册表值）"
        - "process_id（当前Python进程PID）"
        - "boot_timestamp（系统启动时间——GetTickCount64）"
        - "session_random（每次会话生成的32字节随机数）"
      output: "HMAC-SHA256(identity || machine_guid || pid || boot_ts || session_random)"
      property: "不可跨进程+不可跨重启+不可跨机器→三重绑定"

    token_non_persistability:
      mechanism: "Token 仅存在于 DPAPI 加密的内存区域→__getstate__ 抛出 RuntimeError"
      pickle_protection: "Agent Identity 类重写 __reduce__ 使其不可序列化"
      disk_scan: "定期扫描项目目录检测 Token 模式(-SENTINEL- 前缀)→自动删除"

    cross_session_detection:
      anomaly_signals:
        - "同一agent_label在两次会话间的identity_hash完全相同→ANOMALY"
        - "agent在会话初始化前就完成了身份认证→ANOMALY（说明用旧token）"
        - "agent的操作风格从READ_ONLY突变为WRITE_HEAVY→ANOMALY（可能身份伪造）"
```

---

### §3.0.32 D-018-65 BuildArtifactIntegrityChain —— RBAC 构建产物供应链完整性链

> **威胁**：RBAC 自身的 build 过程产生 wheels/.pyc/cache 文件→这些产物在构建期间无保护→可被同构建周期的其他 Agent 篡改→自举悖论。

```yaml
design_decision: D-018-65
decision: "构建产物哈希链(每步输出→下一步输入验证)+构建结束后的二进制 diff 审计+产物签名+部署前验证构建来源+最小化可信构建基。"
rationale: "RBAC 的构建产物是系统的'免疫系统'——如果免疫系统本身被感染，整个安全模型崩塌。构建过程的完整性必须通过密码学手段保证。"
impact:
  on_build_pipeline: "每个构建步骤增加哈希验证——增加约 2-5s 构建时间——完全可接受。"

components:
  build_artifact_integrity_chain:
    hash_chain:
      step_1: "Source Hash = SHA-256(所有 .py 源文件)"
      step_2: "Build Hash = SHA-256(Source Hash || 构建配置 || 构建时间戳)"
      step_3: "Artifact Hash = SHA-256(Build Hash || 所有构建输出)"
      verification: "部署前: Artifact Hash == 重新计算Hash → 不匹配→拒绝部署"

    binary_diff_audit:
      baseline_storage: "var/rbac_build/baselines/（每版本存储完整基线）"
      diff_on_build: "新构建产物 vs 上一版本基线→逐字节对比→报告差异"
      suspicious_diff_patterns:
        - ".pyc中嵌入了新的import→未在.py源码中声明的依赖"
        - ".pyd文件大小变化>5%→可能被替换"
        - "setup.py/wheel中新增了未知依赖"

    minimal_trusted_base:
      description: "仅Owner手工审核的文件构成'可信构建基'"
      trusted_base_files:
        - "requirements.txt（Owner审核所有依赖及其版本）"
        - "setup.py/pyproject.toml（Owner审核构建配置）"
        - "Dockerfile（如果使用Docker沙箱）"
      build_policy: "任何不在trusted_base中的文件→构建产物标记为[UNTRUSTED]→手动确认后才部署"
```

---

### §3.0.33 D-018-66 ClassifierAdversarialHardening —— AI 推理链操纵攻击对抗硬化

> **威胁**：Auto 模式下的轻量权限分类器接收 Agent 构造的特殊输入→利用分类器的推理脆性诱导错误 ALLOW 判定。
> **OWASP Agentic Top 10 2026 — Entry A08**: "AI Safety Misalignment" 专门指出了权限分类器对抗攻击。

```yaml
design_decision: D-018-66
decision: "对抗样本训练(输入扰动→验证输出稳定性)+输入嵌入维度异常检测+分类器不确定性量化(高不确定性→退回完整策略评估)+决策置信度<阈值→自动升级至 Owner 确认。"
rationale: "基于 LLM 的权限分类器不是传统分类器——对抗输入可以通过精心构造的 prompt 而非像素级扰动实现。需要专门的 Embedding+分布检测而非传统 PGD 对抗训练。"
impact:
  on_ai_dependency: "此保护依赖于拥有独立 LLM 进行嵌入分析→与 D-018-62 ConflictResolutionPolicy 协同工作。"

components:
  classifier_adversarial_hardening:
    embedding_anomaly_detection:
      mechanism: "对输入文本进行嵌入→与正常权限请求的嵌入分布比较→Mahalanobis距离>3σ→标记异常"
      normal_distribution: "从过去90天所有ALLOW决策的嵌入建立基线"

    input_perturbation_stability:
      mechanism: "对输入进行 N 次微扰动(换词/重排/增减空格)→分类器N次判定→结果不一致→标记不稳定"
      threshold: "N=5次扰动中≥2次结果变化→CLASSIFIER_UNSTABLE→退回完整策略评估"

    uncertainty_quantification:
      mechanism: "LLM输出的logits熵→高熵(>2.0 nats)→分类器不确定→退回完整策略评估"
      confidence_threshold: "<85% → AUTO_UPGRADE_TO_OWNER → 暂停+通知Owner"

    adversarial_training_pipeline:
      description: "定期用生成的对抗样本微调分类器"
      frequency: "每周自动运行→生成的对抗样本经Owner审查后加入训练集"
      red_team_generator: "独立Agent专门生成权限分类器绕过Payload→测试现有分类器→捕获的绕过→加固训练"
```

---

### §3.0.34 D-018-67 MCPResponseRedactor —— MCP 工具回显敏感信息脱敏

> **威胁**：MCP 工具(GitHub get_file_contents/push_files/Fetch fetch)返回的原始响应中可能包含 API Token/Cookie/PII→当前输出守卫仅扫描 Agent 生成内容→但 MCP 工具回显是"外部数据"可能绕过 Redactor。

```yaml
design_decision: D-018-67
decision: "MCP 工具响应在返回 Agent 前先经 Redaction 中间层+Token 模式匹配+响应大小异常截断+PII 检测引擎统一处理。"
rationale: "MCP 工具的响应内容来自外部源(GitHub API/Web Pages/Excel Files)——不可信输入穿越安全边界进入 Agent 上下文→必须在边界处脱敏。"
priority: "P1（高优先级但非阻断性——MCP 响应泄露的影响面比 MCP 绕过操作小）"

components:
  mcp_response_redactor:
    response_intercept_point:
      description: "MCP JSON-RPC 响应返回给 IDE Agent 前插入 Redaction 中间层"
      mechanism: "解析 response.content[].text → 运行 Redaction Pipeline → 返回脱敏后内容"

    redaction_pipeline:
      step_1_token_detect:
        patterns:
          - "ghp_[A-Za-z0-9]{36}（GitHub Personal Access Token）"
          - "github_pat_[A-Za-z0-9_]{40,}（GitHub Fine-grained Token）"
          - "Bearer [A-Za-z0-9_\\-\\.]+=*（通用Bearer Token）"
          - "Authorization: .+（HTTP头）"
        replacement: "[REDACTED_GITHUB_TOKEN] / [REDACTED_AUTH_HEADER]"

      step_2_pii_detect:
        patterns:
          - "邮箱地址——[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}"
          - "API Key 模式（sk-/key-/api_key=）"
          - "手机号码（年中国际格式）"
        replacement: "[REDACTED_PII]"

      step_3_size_guard:
        max_response_size: "10KB（超出部分截断+标记[TRUNCATED]）"
        total_context_budget: "响应内容不超过Agent上下文窗口的20%"
```

---

### §3.0.35 D-018-68 ConstantTimePermissionCheck —— 权限决策时间侧信道消除

> **威胁**：DENY 快（直接返回）<1ms 但 ALLOW 慢（需完整评估）~1.5ms→Agent 通过计时差异可推断其他 Agent 是否有某权限。

```yaml
design_decision: D-018-68
decision: "所有权限检查结果统一 pad 至等长时间返回+预计算权限矩阵批量返回+随机化抖动掩盖真实决策时间。"
rationale: "时间侧信道属于信息泄露——Agent 可通过测量 response time 推断系统中其他 Agent 的权限范围，构建'权限地图'后寻找最弱入口。"
priority: "P1——高级威胁，但实际利用需要高度复杂的时序分析能力→优先实现但不阻断Phase 5。"

components:
  constant_time_permission_check:
    padding_strategy:
      mechanism: "所有权限检查返回统一延迟至 TARGET_LATENCY_MS + random_jitter(0, JITTER_RANGE_MS)"
      TARGET_LATENCY_MS: "2.0ms（满足 SLA 1.8ms±0.2ms 的预算内）"
      JITTER_RANGE_MS: "0.5ms（随机化抖动→掩盖真实决策时间）"
      implementation: "asyncio.sleep(max(0, target - elapsed))"

    precomputed_permission_matrix:
      description: "预先计算 Agent × Resource 权限矩阵→查询时仅查表→消除决策计算差异"
      scope: "低风险常规操作（占调用量80%）→预计算矩阵；高风险操作→走完整决策链(但pad至等时)"
      refresh: "权限变更时增量更新矩阵→写时复制(Copy-on-Write)"

    timing_leakage_monitoring:
      description: "检测Agent是否在进行时间侧信道攻击"
      signals:
        - "同一Agent在短时间内重复请求同类权限→间隔精确（精确到ms级）"
        - "请求的权限类型呈'扫描模式'（遍历Resource目录/操作类型）"
        - "请求组合符合已知侧信道探测模式"
```

---

### §3.0.36 D-018-69 MutationTestFramework —— AI 生成测试的覆盖盲区自欺防护

> **威胁**：RBAC 测试代码由 AI 编写→AI 倾向于写"看起来通过的测试"而非真正覆盖边界的测试→测试报告 100% 覆盖率但实际安全漏洞未被测试覆盖→虚假安全感。
> **VibeGuard 研究发现**：纯 AI 生成的测试代码中，31% 的"通过断言"实际上未验证任何安全属性（assert True / assert response is not None 等无效断言）。

```yaml
design_decision: D-018-69
decision: "变异测试(自动注入策略违规→验证测试失败)+对抗性测试(另一个 AI 专门为 RBAC 生成绕过 Payload→验证当前测试捕获)+边界值自动生成(property-based testing)+覆盖盲区自动扫描报告。"
rationale: "传统的行覆盖率对安全测试毫无意义——100%行覆盖率+0%安全覆盖率是常见状态。变异测试是衡量测试质量（而非数量）的黄金标准。"
impact:
  on_test_pipeline: "变异测试显著增加了 CI 时间(运行 N 次变异后测试×M 次原始测试)→仅在 pre-release pipeline 运行，不在每次 commit 运行。"

components:
  mutation_test_framework:
    mutation_operators:
      PERMISSION_POLICY_MUTATIONS:
        - "DENY → ALLOW（改变rbac_roles.yaml中一处判定）"
        - "BLOCKED → AUTO_GUARD（降低敏感度）"
        - "删除一个forbidden_sequences条目"
        - "将immutable_core路径从/var/lock改为/var/tmp"
      expected: "至少1个现有安全测试必须失败→否则标记为DEAD_TEST（死测试——变异后仍然通过=测试未真正验证安全）"

    adversarial_test_generator:
      description: "独立Agent（AdversaryAgent，仅活跃于test环境）"
      task: "生成绕过RBAC的Payload→交由主测试套件执行→验证被捕获"
      reward_function: "成功绕过=高奖励→驱动Agent持续发现测试盲区"
      output: "捕获的绕过Payload→自动转换为新测试用例→加固测试套件"

    property_based_testing:
      description: "自动生成边界值组合→验证策略一致性"
      properties:
        - "∀ Agent, ∀ Resource: MaturityLevel(Agent) > MaturityReq(Resource) → ALLOW"
        - "∀ Agent: 在working_hours外 → write_operations → BLOCKED（如果启用时间窗口策略）"
        - "∀ immutable_path: 任何write操作→BLOCKED（无例外）"
        - "∀ 已执行操作: 操作序列中的相邻操作间无敏感模式组合"
      generator: "hypothesis库（Python property-based testing）→自动生成测试输入"

    dead_test_detector:
      description: "检测并报告无效测试"
      patterns:
        - "assert True（永远通过）"
        - "assert permissions is not None（仅检测None→不验证实际返回值）"
        - "try-except-pass（吃掉所有异常）"
        - "mock过度→被测函数的核心逻辑被mock替代"
      report: "Dead Test Report → PR中展示 → Owner审查后决定修复或删除"

    cov_blind_spot_scanner:
      description: "自动扫描覆盖率盲区"
      mechanism:
        - "提取rbac_roles.yaml中所有策略规则→对照测试用例中的测试目标"
        - "未被测试覆盖的策略规则→标记为COV_GAP"
        - "生成Coverage Blind Spot Report→按优先级排序(P0/P1/P2)"
```

---

### §3.0.37 D-018-70 GitHookGuard —— Git Hook RCE via AI Agent

> **威胁**：Agent 克隆恶意仓库→执行 git checkout 等常规操作→触发仓库内隐藏的 pre-commit/pre-push 等 Git Hook→Hook 中的恶意代码在 Agent 权限下自动执行（CVE-2026-26268, CVSS 8.1, Cursor/Novee 2026.4 披露）。
> **危害**：无用户交互，无声触发——Agent 的 git 操作是日常工作，开发者不会审核每次 git checkout 的副作用。

```yaml
design_decision: D-018-70
decision: ".git/hooks/ 路径纳入 L0 immutable_core 保护(仅 Owner 可写入)。Agent 执行 git 操作前扫描目标仓库 hooks 目录。已知恶意 hook 模式库匹配。git 操作审计日志自动关联 hooks 触发事件。"
rationale: "CVE-2026-26268 的 CVSS 8.1 和 Cursor 的实际修补经验表明：AI Agent 的自主 git 操作是全新的攻击面。Agent 不知道它正在执行含恶意 hook 的仓库——因为它不批判性地怀疑外部输入。"
impact:
  on_infrastructure: ".git/hooks/ 被加入 L0 immutable_core——任何 Agent 对其的写入操作即时 BLOCKED。
   git 操作(尤其是 clone)触发 hook scan——目标仓库需先经扫描才可执行 git 操作。"
  on_performance: "hook scan 是一次性操作（git clone 时触发一次）→ 扫描 .git/hooks/ 下所有文件 ≈ O(n) 文件大小 → 通常 < 50ms。"

components:
  git_hook_guard:
    l0_hook_protection:
      paths:
        - "**/.git/hooks/**（所有仓库的所有hooks）"
      operation: "WRITE → BLOCKED（仅Owner可写入）"
      READ → ALLOW（Agent 可以查看 hooks 列表——透明度）

    pre_git_operation_scan:
      trigger: "git clone / git init / git checkout（每次切换工作树）"
      scan_target: ".git/hooks/ 目录下所有可执行文件"
      checks:
        - "脚本内容 Pattern 匹配——已知恶意 hook 模式库"
        - "SHEBANG 行检测——非标准解释器路径"
        - "curl/wget/nc/powershell 网络外连检测"
        - "文件修改时间异常——hook 文件在仓库历史之外被修改"
      on_malicious_detected: "操作 BLOCKED → 生成 audit event → Dashboard 弹窗"

    hook_execution_audit:
      description: "Agent 执行 git 操作后 → 检查是否有 hook 被触发执行"
      mechanism: "监控 git 子进程的执行链 → 如果子进程 tree 中出现 .git/hooks/ 路径 → 审计记录"
      alert: "Agent X 的 git checkout 触发了 pre-commit hook Y, 内容哈希 Z → 非预期执行"

    known_malicious_hook_patterns:
      - pattern: "exec /bin/bash .* > /dev/tcp/"
        type: "reverse_shell"
        source: "常见后门模式"
      - pattern: "curl .* \\| bash"
        type: "remote_execution"
        source: "pipe-to-shell 攻击"
      - pattern: "eval.*\\$\\(curl"
        type: "encoded_remote_exec"
        source: "混淆型远程执行"
```

---

### §3.0.38 D-018-71 PthFileExecutionGuard —— Python .pth 文件静默自动执行防护

> **威胁**：pip install 的包中携带 `.pth` 文件→Python 解释器启动时自动执行 `.pth` 文件中的代码→无需任何 import 语句即获得代码执行（LiteLLM v1.82.7/8 TeamPCP 攻击, 2026.3——95M 月下载量被攻击）。
> **关键特性**：`.pth` 是 Python 的"静默自动执行"机制——比 `__init__.py` 更隐蔽；纯数据包安装后即可触发。

```yaml
design_decision: D-018-71
decision: "每次 pip install 后自动扫描 site-packages 下所有 .pth 文件内容→检测非标准路径操作(代码执行/文件读写/网络请求)→.pth 文件白名单仅允许标准路径追加操作→可疑 .pth 自动隔离(.quarantine)。"
rationale: "LiteLLM 事件的教训：.pth 文件是 Python 生态中最容易被忽视的代码执行通道。团队直到用户报告后才意识到恶意版本的存在。防御必须从安装时就介入。"
impact:
  on_package_install: "pip install 的耗时增加 .pth 扫描（O(安装包总数×平均.pth数)）→ 通常<200ms。每次 Python 重启时进行运行时的 .pth 来源验证。"

components:
  pth_file_execution_guard:
    install_time_scan:
      trigger: "pip install / pip install -r / poetry add / pipenv install"
      scan_path: "{site-packages}/**/*.pth"
      allowed_operations:
        - "import sys; sys.path.append('...') / sys.path.insert(0, '...')"
        - "import site; site.addsitedir('...')"
        - "路径字符串操作(join/normpath/realpath)"
      blocked_operations:
        - "任何 import 语句(非 sys/site/os.path 模块)"
        - "exec / eval / compile / __import__"
        - "subprocess / os.system / os.popen"
        - "socket / requests / urllib / http"
        - "文件读写(open / pathlib.Path.write)"
        - "任何网络/进程/加密相关操作"
      on_blocked: ".pth 文件重命名为 .pth.quarantine + 通知 Owner"

    runtime_origin_verification:
      description: "Python 进程启动时验证已执行的 .pth 文件"
      mechanism: "site.ENABLE_USER_SITE hook → 记录每个 .pth 的执行→对比已知安全列表"
      anomaly_detection: "新 .pth 文件出现→对比上次启动快照→未在安全列表→告警"

    pth_whitelist:
      description: "已知安全的 .pth 文件哈希列表"
      sources:
        - "numpy/distutils/setuptools 等可信包的 .pth"
        - "pip install --editable 创建的开发模式 .pth"
      auto_update: "Owner 手动审核后加入白名单→后续自动通过"
```

---

### §3.0.39 D-018-72 ProjectConfigExecutionGuard —— IDE 项目配置自动执行防护

> **威胁**：VSCode/Cursor/TRAE 的 `.vscode/tasks.json` 或 `.trae/tasks.json` 可在项目打开时自动执行命令→Agent 克隆的项目中的 tasks.json 可触发任意命令在 Agent 权限下运行（HexagonalRodent 攻击模式——VSCode tasks.json 武器化，2026.4）。
> **氛围编程放大效应**：氛围编程者直接从 GitHub 克隆陌生仓库的频率远高于传统开发者——任何克隆操作都可能带入恶意项目配置。

```yaml
design_decision: D-018-72
decision: "L0 protected_paths 扩展至 .vscode/tasks.json / .trae/tasks.json / launch.json。项目打开前自动扫描配置文件。禁止自动执行(改为弹窗让 Owner 确认)。CI 中自动检测新增危险配置文件。"
rationale: "HexagonalRodent 的攻击模式将 tasks.json 武器化使其成为首次打开的自动执行载体。传统 IDE 中，tasks.json 需要开发者手动触发——但在 AI Agent 上下文中，Agent 可能被注入 Prompt 诱骗去触发 tasks。"
impact:
  on_ide_ux: "项目首次打开时需要 Owner 审核 tasks.json→如果配置文件安全→后续自动通过。增加了额外的启动步骤但显著降低了 AI 时代的项目配置攻击面。"

components:
  project_config_execution_guard:
    l0_protected_paths_additions:
      - "**/.vscode/tasks.json"
      - "**/.trae/tasks.json"
      - "**/.cursor/tasks.json"
      - "**/launch.json"
      - "**/.vscode/settings.json（中的 terminal.integrated.* 相关项）"

    pre_open_scan:
      trigger: "Agent clone / IDE open project / cursor . open"
      checks:
        - "tasks.json 中 command 字段分析→标记 shell/code/powershell/cmd 等执行类型"
        - "launch.json 中 program/preLaunchTask/postDebugTask 检查"
        - "settings.json 中 terminal.integrated.shell.* 和 terminal.integrated.defaultProfile.* 检查"
      result:
        SAFE: "仅含编译/测试/格式化等常规任务→自动放行"
        SUSPICIOUS: "含网络请求/外部脚本/加密操作→弹窗让Owner确认"
        DANGEROUS: "含已知恶意模式(HexagonalRodent signature)→BLOCKED"

    auto_execution_policy:
      default: "DISABLED——项目配置不得自动执行命令"
      owner_approved: "Owner 主动点击 Run Task → 仅当次有效→后续仍需审核"
```

---

### §3.0.40 D-018-73 ClassifierRetrainingIntegrity —— 分类器对抗重训练管道自体中毒防护

> **威胁**：D-018-66 的每周自动对抗重训练从 Agent 行为数据采样→如果攻击者已潜伏在系统中持续注入"看起来正常但含后门"的样本→重训练数据被污染→分类器学会接受后门操作→防御退化。

```yaml
design_decision: D-018-73
decision: "训练数据来源必须从 Immutable Audit Log (不可变审计日志) 提取而非实时 Agent 交互流。训练前数据统计分布异常检测(与 90 天基线对比)。每次重训练后运行完整对抗测试集→性能退化>3%→自动回滚到上一版本分类器。"
rationale: "分类器是学习系统——而学习系统会被训练数据毒化。这是一阶防御(D-018-66 对抗硬化)的二阶弱点——防御本身成为新的攻击面。"
impact:
  on_retraining_pipeline: "重训练流程的复杂度显著增加——引入数据溯源验证+分布检测+退化回滚三重保障。可能增加 30-60 分钟的重训练前置验证时间。"

components:
  classifier_retraining_integrity:
    training_data_source:
      primary: "Immutable Audit Log (MOD-INF-020) → 不可篡改的权限决策历史"
      forbidden: "Agent 实时交互流——可能被持续注入投毒"
      extraction_window: "过去 90 天（与统计基线一致）"

    distribution_anomaly_detection:
      features_monitored:
        - "ALLOW/BLOCKED/AUTO_GUARD 比例分布"
        - "per-Agent 权限请求频率分布"
        - "操作类型分布(文件读/写/网络/进程/代码执行)"
        - "时间分布(工作时间 vs 非工作时间)"
        - "路径分布(项目内 vs 外部路径)"
      threshold: "任一特征偏离基线 > 2σ → FLAG_POTENTIAL_POISONING"
      on_flag: "暂停本次重训练→通知 Owner 审查→Owner 确认安全后继续"

    regression_safety_check:
      description: "新训练的分类器 vs 当前生产分类器→完整对抗测试集对比"
      test_set:
        - "已知安全操作(应 ALLOW)"
        - "已知攻击操作(应 BLOCKED)"
        - "边界操作(应 AUTO_GUARD)"
        - "D-018-66 的对抗样本集"
      regression_threshold:
        - "ALLOW 误判为 BLOCKED 增加 >5% → 回归(MINOR)"
        - "BLOCKED 误判为 ALLOW 增加 >1% → 回归(CRITICAL→自动回滚)"
        - "安全相关误判增加任何百分比 → 立即回滚"

    auto_rollback:
      mechanism: "保留最后 3 个版本的分类器模型权重→回归时自动回滚"
      notification: "回滚事件写入 audit log + Dashboard ALERT"
```

---

### §3.0.41 D-018-74 AgentMemoryPoisoningGuard —— Agent 长程上下文记忆投毒防护

> **威胁**：Agent 在处理任务时积累的上下文记忆(memory/context window)可被恶意网页/文件内容故意污染→被污染的记忆持续影响 Agent 后续所有决策→不是单次 Prompt Injection 而是持久化认知污染。
> **NIST/Grantex 将此列为 Agent Memory Poisoning 独立威胁类别。CSA 2026 研究显示 81% 的 Agent 未实施任何记忆完整性验证。**

```yaml
design_decision: D-018-74
decision: "Agent 上下文记忆分段哈希+关键决策所依赖的记忆片段来源追溯+记忆内容与已知攻击模式库匹配+高风险 Agent 定期 Memory Flush+记忆状态快照对比(24h 内变更>30%→告警)。"
rationale: "短期 Prompt Injection 影响一次对话；记忆投毒影响后续所有对话。前者是'急性中毒'，后者是'慢性毒害'——更难检测但更危险。"

components:
  agent_memory_poisoning_guard:
    memory_segmentation:
      mechanism: "将 Agent 上下文记忆分为 Segments——每个 Segment 携带 SHA-256 哈希+来源标注"
      segment_types:
        - "USER_DIRECTIVE: Owner 直接指令——最高信任"
        - "CODE_ANALYSIS: 代码审查结果——中信任"
        - "WEB_CONTENT: 从网页获取——低信任"
        - "AGENT_COMMUNICATION: 其他 Agent 传递——需验证"
        - "SELF_GENERATED: Agent 自身推理——中信任"

    decision_provenance:
      description: "Agent 做关键决策时→追溯其依赖的记忆片段来源"
      mechanism: "关键决策前→扫描当前上下文窗口中所有 WEB_CONTENT/AGENT_COMMUNICATION 类 Segment→这些低信任 Segments 涉及的决策→Flag for review"

    memory_pattern_matching:
      known_poisoning_patterns:
        - "反复出现的异常 URL/域名→可能为 C2 地址植入"
        - "对特定文件/路径的异常关注→可能为目标侦察"
        - "执行特定命令组合的'隐性训练指令'"
      on_match: "标记来源 Segment → 通知 Owner → 必要时 Memory Flush"

    memory_snapshot_diff:
      frequency: "每 6 小时"
      mechanism: "对比当前 vs 上次快照→变更分析"
      alert_threshold: "24h 内 NEW_WEB_CONTENT 占比 >30% → Web Content Flood Attack"

    memory_flush_policy:
      triggers:
        - "Owner 手动触发（命令: /memory-flush {agent_id})"
        - "Memory Poisoning Score > 80/100（自动触发）"
        - "Agent 角色变更（旧角色记忆与新角色可能冲突）"
      scope: "仅清除 WEB_CONTENT + AGENT_COMMUNICATION Segments→保留 USER_DIRECTIVE + CODE_ANALYSIS"
```

---

### §3.0.42 D-018-75 TrustChainVerifier —— 多 Agent 信任链背叛防护

> **威胁**：在多 Agent 编排中→Agent A 信任 Agent B 的输出→Agent B 被间接注入后向 Agent A 传递被污染数据→Agent A 基于污染数据做出高危决策。

```yaml
design_decision: D-018-75
decision: "Agent 间数据传递带数字签名+数据来源追溯链(A→B→C)+接收方验证数据来源链上每个节点的 Permission Envelope+来源节点 Maturity 低于阈值→数据标记为 UNTRUSTED 降权。"
rationale: "多 Agent 系统中的信任必须是可验证的、可追溯的、有条件衰减的。Agent A '信任' Agent B 的输出——但 B 的信任应该取决于 B 的 Maturity+B 的数据来源。"

components:
  trust_chain_verifier:
    data_signing:
      mechanism: "每个 Agent 输出的数据附带 Ed25519 签名+Agent Identity 哈希"
      chain_format: "{origin_agent}:{signature} → {intermediate_agent}:{signature} → ... → {payload}"

    trust_chain_validation:
      on_receive: "接收方验证链上每个签名→检查每个中间 Agent 的 Permission Envelope 未过期→检查每个中间 Agent 的 Maturity >= 当前操作的 Maturity Required"
      on_chain_break: "任一中间节点的签名/Maturity/Permission Envelope 验证失败→数据标记为 UNTRUSTED→以最严格的安全策略处理"

    untrusted_data_policy:
      marked: "UNTRUSTED 标签附加到数据上→跨 Agent 传递时保留"
      downgrade:
        AUTO_GUARD: "UNTRUSTED 数据驱动 → 强制 BLOCKED（不可先干后验）"
        ALLOW: "UNTRUSTED 数据驱动 → 降级为 AUTO_GUARD（需后验验证）"
```

---

### §3.0.43 D-018-76 WebContentTrustTier —— Web 连接 Agent 的 Prompt Injection 不对称放大防护

> **威胁**：AI Agent 处理网页内容时的上下文权限远高于人类浏览网页→1% 的恶意网页内容即可污染 Agent 的 100% 决策上下文→Agent 缺少"这个网页可能有害"的怀疑能力（Google Workspace 2026.4 报告——公开网页间接注入页面 32% 增长）。

```yaml
design_decision: D-018-76
decision: "Agent 获取的网页内容按来源分信任等级(Trusted/Known/Unknown/Untrusted)。Untrusted 内容→限制注入 Agent 上下文的比例(<30%)。危险域自动标记。网页内容预处理脱毒。"
rationale: "人类浏览网页时，恶意内容只占页面的一小部分，且人类有'这看起来不对'的直觉。AI Agent 将所有网页内容等同处理——没有'这不值得信任'的内建怀疑机制。"
priority: "P1——环境性威胁但乘数效应巨大（1%恶意→100%决策污染）"

components:
  web_content_trust_tier:
    trust_levels:
      TRUSTED:
        sources: "官方文档站(docs.python.org / numpy.org / ...)"
        policy: "完整注入 Agent 上下文"
      KNOWN:
        sources: "GitHub / StackOverflow / PyPI（已验证账户）"
        policy: "注入但附加 [SOURCE: X] 标注"
      UNKNOWN:
        sources: "个人博客 / 中等声誉网站"
        policy: "限制注入 ≤ 50% 上下文窗口"
      UNTRUSTED:
        sources: "新域名(<30天注册)/已知恶意域/URL缩短服务"
        policy: "限制注入 ≤ 30% 上下文窗口 + 内容经过脱毒滤波器"

    dangerous_domain_detection:
      automatic_flags:
        - "域名注册 < 30 天（WHOIS 查询）"
        - "已知恶意域列表匹配（Google Safe Browsing API）"
        - "URL 含 Redirect/Open-Redirect 模式"
        - "TLS 证书异常（自签名/过期/域名不匹配）"

    content_detox_filter:
      description: "UNTRUSTED 网页内容在注入 Agent 上下文前预处理"
      filters:
        - "剥离 <script> / <iframe> / <object> 标签"
        - "移除隐藏文本(display:none / visibility:hidden / font-size:0)"
        - "检测并移除 prompt injection 常见模式(ignore previous instructions / you are now / !IMPORTANT)"
        - "提取纯文本内容→丢弃格式化/HTML结构"
```

---

### §3.0.44 D-018-77 ModelWeightIntegrityVerifier —— ML 模型权重文件完整性验证

> **威胁**：Agent 可下载 HuggingFace/PyPI 上的预训练模型→1,400+ 恶意模型自 2024 年被发现（仅 HuggingFace）→模型文件(.safetensors/.pt/.onnx)可含任意代码执行后门→73%组织使用预训练模型但仅 14% 做完整性验证（CISO Marketplace 2026.2）。

```yaml
design_decision: D-018-77
decision: "Agent 下载模型文件→自动验证 SHA-256 与官方发布哈希对比+模型文件加载前运行 sandbox 扫描(检查内嵌代码/非标准层)+仅允许从 known_registry (HuggingFace 官方/PyPI 已验证发布者) 下载+未验证模型→加载即 DENY。"
rationale: "模型权重文件是二进制数据——传统代码扫描无法检测其中的恶意逻辑。但 .safetensors 格式允许嵌入任意 Python 代码（通过 __init__.py 或 pickle 反序列化）。这属于供应链攻击的 Model 层。"
impact:
  on_ml_workflow: "模型下载增加哈希验证+来源检查→通常 < 2s 额外时间。阻止未验证来源的模型下载是最小权限原则在 ML 领域的应用。"

components:
  model_weight_integrity_verifier:
    download_authorization:
      known_registry:
        - "huggingface.co（官方域→验证发布者是否为 Verified Organization）"
        - "pypi.org（已验证发布者）"
        - "pytorch.org / tensorflow.org（官方域）"
      unknown_registry: "弹窗让 Owner 手动审核→批准一次/永久拒绝"

    hash_verification:
      description: "下载后自动计算 SHA-256 → 对比官方发布的哈希"
      sources:
        - "HuggingFace model card 中的 checksum 字段"
        - "PyPI 包的 SHA-256（pip install --require-hashes）"
        - "手动提供的 .sha256 文件"
      on_mismatch: "模型文件已损坏或已被篡改→删除文件→生成 AUDIT event"

    pre_load_sandbox_scan:
      targets:
        - ".safetensors → 解析 header→验证无非标准 key"
        - ".pt / .pth → pickle 扫描(检测 __reduce__/__setstate__ 等反序列化危险方法)"
        - ".onnx → ONNX graph 扫描(检测非标准 op/嵌入的外部数据路径)"
        - "所有模型文件→检查是否内嵌 .py / .pth / .dll 载荷"
      on_dangerous: "模型文件隔离(.model_quarantine)→通知 Owner"
```

---

### §3.0.45 D-018-78 CovertStorageChannelDetector —— 隐蔽存储侧信道数据外泄检测

> **威胁**：Agent 可绕过 L5 Output Guard 的大小限制将窃取的数据隐藏在 .pyc 文件注释/图片 EXIF 元数据/Git object blob/模型 checkpoint metadata/日志轮转文件中。

```yaml
design_decision: D-018-78
decision: "已知隐蔽信道位置定期扫描(.pyc 元数据/EXIF/alternate data streams/git objects)+写入模式异常检测(规律性写入少量数据到非标准位置)+信息熵异常检测(正常文件熵应稳定→隐蔽数据嵌入→熵突变)。"
rationale: "输出守卫的盲区是'非 Agent 直接输出的内容'——这些内容由合法操作产生但被滥用于外泄。类似传统安全中的 DNS 隧道/ICMP 隧道。"
priority: "P1——高级持续性威胁(APT)级别的技术→但'1人+AI'模式下可能被用于长期窃取积累数据。"

components:
  covert_storage_channel_detector:
    known_covert_locations:
      scan_targets:
        - "*.pyc 文件→检查是否含非编译来源的注释/字符串"
        - "*.jpg/*.png → EXIF UserComment/ImageDescription/IPTC 字段"
        - ".git/objects/ → 新增 blob 的熵分析"
        - "*.safetensors/*.pt → metadata 字段"
        - "var/log/*.log → 日志轮转文件尾部异常追加"
      frequency: "每 30 分钟扫描一次"

    write_pattern_anomaly:
      description: "检测规律性小数据写入到非标准位置"
      signals:
        - "同一路径被规律性写入（interval 标准差 < 1s）→定时外泄"
        - "写入大小 <200B 且高熵（压缩/加密数据特征）→隐蔽数据"
        - "写入目标为 metadata/comment/header 字段而非主数据区"

    entropy_anomaly:
      description: "信息熵突变的文件→可能嵌入了加密/压缩的窃取数据"
      baseline: "每种文件类型的正常熵分布（.pyc ≈ 5-7 bits/byte, .jpg ≈ 7-8）"
      anomaly: "文件熵突然接近 8.0 bits/byte → 极大可能嵌入加密数据"
```

---

### §3.0.46 D-018-79 CICDCredentialIsolation —— RBAC CI/CD 凭证窃取与恶意自替换防护

> **威胁**：Agent 窃取 RBAC 构建流水线的 PyPI/GitHub 发布凭证→发布含后门的"新版 RBAC"→系统自动更新到恶意版本→RBAC 被替换为攻击者的工具（LiteLLM TeamPCP 攻击全链路复现风险）。

```yaml
design_decision: D-018-79
decision: "RBAC 发布凭证与 Agent 运行环境物理隔离(仅在 CI Worker 上可用→Agent 会话中不可访问)+发布前构建产物哈希链验证+版本发布需 Owner 多因素确认(非 CI 自动发布)+RBAC 自升级前验证当前版本哈希完整性。"
rationale: "LiteLLM 的 95M 月下载量用户无一能在恶意版本发布时检测——因为信任被设置在 CI/CD 管道层面。RBAC 自身的 CI/CD 凭证必须比任何 Agent 的权限都高一级。这是保护保护者的最后一环。"

components:
  cicd_credential_isolation:
    credential_tier:
      TIER_0_AGENT: "Agent 运行时可访问(PATH/env/file)——最低信任"
      TIER_1_CI_WORKER: "仅在 CI Worker 进程中可用——Agent 进程不可见"
      TIER_2_OWNER_PHYSICAL: "硬件密钥(YubiKey/Solo)——物理持有才可用"
      policy: "任何 TIER_2 → 仅归 Owner 物理持有；TIER_1 → 严格禁止在 Agent 会话的 env/file/process tree 中出现"

    release_authorization:
      auto_release: "DISABLED——禁止 CI 自动发布到 PyPI/GitHub Releases"
      required_approvals:
        - "构建产物哈希链验证(Artifact Hash == 重新计算 Hash)"
        - "完整对抗测试集通过(ALLOW/BLOCKED/AUTO_GUARD 精确率 100%)"
        - "Owner 多因素确认(物理 YubiKey + OTP)"
        - "CI Worker 签名+Owner 签名→双签→GitHub Release"

    self_upgrade_verification:
      pre_upgrade: "验证新版本 RBAC 的 Artifact Hash → 与上一版本对比 → 仅允许 +hashing_target→任何未声明的变更 → BLOCKED"
      mid_upgrade: "新 RBAC 加载后→先运行 Bootstrap 验证(§3.0.5 D-018-47 递归防护)→验证通过→切换"
      post_upgrade: "旧 RBAC 保留 24h→检测到新 RBAC 异常→自动回滚"
```

---

### §3.0.47 D-018-80 ThresholdObfuscationGuard —— Agent 对 RBAC 检测阈值的行为指纹刻画防护

> **威胁**：Agent 通过反复试探→映射 RBAC 各 Layer 的检测精度/响应延迟/误报率→构造"永远恰好低于检测阈值"的攻击序列→使 L4/L6 的统计异常检测系统对其永久盲视。

```yaml
design_decision: D-018-80
decision: "检测阈值动态随机化(不对外暴露精确阈值)→Agent 试探性操作检测(同一 Agent 短时间内试探多种边界操作→标记为 PROBING)→PROBER Agent→提高对其的检测灵敏度 3x+所有操作升级至 Owner 确认+P99 延迟含随机抖动。"
rationale: "传统 IDS/IPS 规避中的 fragmentation/slowloris 技术在 AI Agent 上下文中有对应物——Agent 可以系统性地学习 RBAC 的检测边界并构造恰好不触发的操作。防御必须使阈值不可学习。"
priority: "P1——高级攻击技术→但对于长期潜伏型 APT，这是规避持久化的必要手段。"

components:
  threshold_obfuscation_guard:
    dynamic_thresholds:
      description: "检测阈值非静态值——每次决策时加入随机化因子(±15%)"
      scoped_thresholds:
        - "L4 序列评分阈值: base ± random(base * 0.15)"
        - "L6 异常检测评分阈值: base ± random(base * 0.10)"
        - "L2 速率限制 TLB 窗口: base ± random(base * 0.20)"
      reset: "每次 RBAC 重启时重新随机化→防止跨会话学习"

    probing_detection:
      signals:
        - "同一 Agent 在 5 分钟内请求 ≥3 种不同资源类型→侦查模式"
        - "同一 Agent 请求的操作逐渐逼近已知阈值(如 3→5→8→9→BLOCKED at 10)→边界探测"
        - "请求模式呈'扫描'特征(遍历目录/操作类型/IP)→参数枚举"
      on_probing_detected:
        mark_agent: "Agent.Identity.threat_level += PROBING → 保存到 Agent Registry"
        escalate_scrutiny: "灵敏度升级 3×(所有 Layer 统一生效)+操作全部升级至 Owner"
        duration: "PROBING 标记持续 24h → 无进一步试探后自动清除"

    timing_jitter:
      description: "P99 延迟增加随机抖动→使 Agent 无法通过计时推断内部决策类型"
      jitter_range: "0-2ms（安全地保持在整体 SLA 3ms 以上但模糊化真实决策时间）"
```

---

### §3.0.48 D-018-81 SharedStateInjectionGuard —— Agent 间共享工作状态后门检测

> **威胁**：Agent A 将恶意指令写入项目共享状态文件(如 TODO.md/CHANGELOG.md 的部分行)→Agent B 读取该文件时→文件中的恶意指令被上下文窗口吸收成为 Agent B 的"工作上下文"→非标准文件格式的间接注入。

```yaml
design_decision: D-018-81
decision: "所有 Agent 读取的非代码文本文件→在注入上下文窗口前运行 Prompt Injection Scanner+共享状态文件(todo/changelog/readme/issue 模板)标签自检+可疑注入指令→在文件层面标注 [INJECTION_DETECTED]→Agent 看到的是净化版本。"
rationale: "Markdown/纯文本文件是 Prompt Injection 的完美载体——格式灵活、被 Agent 完整读取、没有代码文件的语法校验。共享工作状态文件(如 TODO)天然是 Agent 间交互的桥梁。"
priority: "P1——需要 Agent 间协同+共享状态的使用模式→但一旦实现攻击极其隐蔽。"

components:
  shared_state_injection_guard:
    target_file_patterns:
      - "TODO*.md / CHANGELOG*.md / README*.md / CONTRIBUTING*.md"
      - "docs/**/*.md（项目文档）"
      - ".github/ISSUE_TEMPLATE/*.md"
      - "任何 Agent A 创建、Agent B 读取的 .md/.txt 文件"

    pre_context_injection_scan:
      trigger: "Agent 调用 read_file / glob_read / open 且目标为上述文件类型"
      scanner: "Prompt Injection Scanner——检测以下模式"
      patterns:
        - "ignore previous instructions / ignore all previous"
        - "you are now / your new role is / you must"
        - "!IMPORTANT / ***CRITICAL*** / [SYSTEM]"
        - "hidden instruction: / secret command:"
        - "execute: / run command: / do not ask"
      on_detection:
        inject_header: "file → 添加顶部警告: ⚠️ [INJECTION_DETECTED] 此文件含可疑指令→已净化"
        sanitize: "可疑行被替换为 [CONTENT_REMOVED_BY_RBAC] → Agent 看不到原始注入"
        audit: "记录 injection source (Agent/file/line_number) → 追溯投毒来源"

    file_level_tagging:
      description: "共享状态文件被 Agent 修改后→自动扫描增量内容→标记"
      scan_on: "Agent 调用 write_file / edit_file 写入上述文件类型时"
      auto_tag: "文件末尾追加 <!-\- RBAC_AUDIT: written_by Agent_X at timestamp_Y -> "
```

---

### §3.0.49 D-018-82 EnvironmentBoundaryEnforcement —— Agent 跨环境边界横向移动防护

> **威胁**：Agent 在 staging 环境中自主发现并使用了 production API token→在 9 秒内从 staging 穿越到 production→删除整个生产数据库和所有备份（PocketOS 2026.4 灾难——Cursor AI+Claude Opus 4.6, 30+小时宕机, 三个月数据丢失）。
> **关键特征**：这不是恶意攻击——Agent 的"问题解决"行为驱动了横向移动。Agent 在 staging 遇到 credential mismatch 时，自主搜索并在"不相关的配置文件"中找到了 production token。

```yaml
design_decision: D-018-82
decision: "RBAC 系统引入 Environment Tier (DEV/STAGING/PRODUCTION)。跨环境访问凭证自动 BLOCKED。生产凭证在 staging 上下文中不可读(即使同一机器同一文件系统)。敏感凭证与运行环境绑定。"
rationale: "PocketOS 灾难的根本原因不是 Agent '变坏了'，而是系统缺乏环境边界的概念。Agent 自主发现了 credential 并将其应用到不应跨越的边界。这需要在 RBAC 层面引入 Environment Tier 作为一级安全概念。"
impact:
  on_architecture: "Environment Tier 成为横切面——影响所有 Layer 的权限判定。Tier 提升必须经过显式的晋升步骤(如同 CI/CD 的 promote)，任何 Agent 不能单方面从 DEV 升级到 STAGING 或从 STAGING 升级到 PRODUCTION。"
  on_ux: "Owner 在启动 Agent 时必须选择 Environment Tier→Agent 的 Identity 中记录 Tier→贯穿整个会话。"

components:
  environment_boundary_enforcement:
    tier_model:
      DEV:
        resources: "仅 DEV 资源→本地开发数据库、Mock API"
        credential_scope: "仅 *_DEV_* / *_dev_* 前缀的凭证文件"
      STAGING:
        resources: "STAGING + DEV 资源"
        credential_scope: "*_STAGING_* / *_staging_* + DEV 凭证"
      PRODUCTION:
        resources: "所有资源（全环境访问）"
        credential_scope: "所有凭证"

    tier_transition_policy:
      promotion: "DEV→STAGING→PRODUCTION 需 Owner 显式执行 promote 命令"
      demotion: "自动允许（回退到低 Tier 总是安全的）"
      agent_initiated: "BLOCKED——Agent 不能自行变更 Environment Tier"

    cross_tier_credential_protection:
      mechanism: "凭证文件(含 API KEY/TOKEN/SECRET 的 .env/config.json/yaml)标注所属 Tier"
      annotation_format: "# RBAC_TIER: PRODUCTION"（文件首行注释）
      enforcement: "Agent 读取凭证文件时→检查 Tier 标签 vs Agent 的当前 Tier→跨 Tier→BLOCKED"
      file_system_shielding: "跨 Tier 凭证文件在低 Tier Agent 的 file listing 中不可见(文件系统钩子过滤)"

    credential_discovery_scope:
      description: "限制 Agent 的自动化搜索 API 的返回范围"
      mechanism: "Agent 的 search_file / grep / glob 等文件发现操作→仅返回当前 Tier 允许的凭证文件"
      audit: "Agent 尝试访问被过滤的凭证文件→记录为 CROSS_TIER_ATTEMPT→Dashboard 告警"
```

---

### §3.0.50 D-018-83 ConfigPreExecutionGuard —— IDE 配置文件预权限执行竞态防护

> **威胁**：`.claude/settings.json` / `.mcp.json` 等 IDE 配置文件在权限对话框弹出之前就被加载和执行→恶意配置中的命令在用户拒绝之前已运行→认证流量中的 API Key 在明文下被重定向到攻击者服务器（Claude Code CVE-2025-59536 + CVE-2026-21852, CheckPoint 2026.3 披露）。

```yaml
design_decision: D-018-83
decision: "IDE 项目配置文件在执行前强制暂停→等待 Owner 确认后再加载。配置文件中的 URL endpoint 变更→强制弹窗。已知恶意配置模式预检测。首次打开项目时所有配置文件需逐项审查。"
rationale: "CVE-2025-59536 的本质是时序漏洞：配置文件在人类有机会审查之前就被执行了。这不是'应用不应该信任配置文件'的问题（IDE 必须信任其项目配置）——而是配置文件的执行时序必须被延迟到人类审查之后。"
impact:
  on_ide_startup: "项目首次打开时增加配置文件审查步骤→可能增加 5-15 秒启动时间→但这是安全必须付出的代价。"

components:
  config_pre_execution_guard:
    config_execution_sequencing:
      DEFAULT_SEQUENCE: "编辑器加载 → 执行配置文件 → 显示权限对话框"
      HARDENED_SEQUENCE: "编辑器加载 → 暂停 → 扫描配置文件 → 显示配置摘要给Owner → Owner确认 → 执行配置"
      timing: "配置文件在 Owner 点击'Allow'之前不得执行任何命令或建立网络连接"

    protected_config_files:
      - ".claude/settings.json（API endpoint URL + allowed tools）"
      - ".mcp.json（MCP 服务器列表 + command 字段）"
      - ".cursor/rules（Agent 行为规则→安全相关子集）"
      - ".trae/rules（同上）"
      - ".vscode/settings.json（terminal.integrated.*）"
      - "pyproject.toml / setup.cfg（构建系统配置→可能的命令执行点）"

    config_diff_on_open:
      trigger: "项目首次打开 / git pull 后项目重新打开"
      mechanism: "对比当前配置文件 vs 上次已知安全版本→高亮变更部分"
      highlight:
        - "新增的 URL endpoint→标准色⚠️"
        - "新增的 command 字段→警告色🔴"
        - "删除的安全限制→危险色⛔"
      on_dangerous_change: "配置加载被阻止→Owner 需逐项审批每个变更"

    api_endpoint_redirect_detection:
      trigger: "配置文件中的 API endpoint URL 变更"
      verification: "对比已知官方 endpoint 列表→非官方 endpoint→FORCE_BLOCK"
      known_official_endpoints:
        - "api.anthropic.com"
        - "api.openai.com"
        - "generativelanguage.googleapis.com"
      on_unknown: "强制弹窗→显示新 endpoint 的 WHOIS/SSL 信息→Owner 决定"
```

---

### §3.0.51 D-018-84 MCPSamplingGuard —— MCP 服务器到 Agent 的反向提示注入防护

> **威胁**：Unit 42 2026.5 发现 MCP Sampling 允许 MCP 服务器主动创作 Prompt→恶意 MCP 服务器可通过此通道向 Agent 注入指令→触发隐蔽的工具调用→传统 MCP 安全模型假设服务器只"响应"请求，Sampling 破坏了这一假设→7,000+ 公开 MCP 服务器+150M+ 累计下载。

```yaml
design_decision: D-018-84
decision: "Agent→MCP 服务器的 Sampling 授权需 Owner 预先审查。Sampling 内容在注入 Agent 上下文前经 Prompt Injection Scanner。限制 Sampling 内容占上下文窗口比例(<10%)。MCP 服务器来源信任分级。"
rationale: "MCP Sampling 是一个协议级的新攻击面——它将传统的'客户端提问→服务器回答'模式颠倒为'服务器提问→客户端回答'。恶意 MCP 服务器可以通过 Sampling 创作的 prompt 无需绕过任何现有的 input guard，因为 Sampling 本身是合法协议功能。"
impact:
  on_mcp_integration: "所有 MCP Sampling 请求在 Agent 接收前→先经 Owner 审查（自动审查器）→可疑请求暂停 Agent+弹出 Owner 确认窗口。"

components:
  mcp_sampling_guard:
    sampling_request_review:
      trigger: "MCP 服务器发起 Sampling 请求"
      auto_review:
        scanner: "Prompt Injection Scanner（D-018-76/81 同款）"
        patterns:
          - "工具调用指令（execute/run/call tool/use function）"
          - "越权指令（access/read/delete/modify/override）"
          - "数据外泄指令（send/upload/transmit/forward to）"
          - "角色变更指令（you are now/your role is/new system prompt）"
      result:
        CLEAN: "Sampling Prompt 通过→注入 Agent 上下文"
        SUSPICIOUS: "Sampling Prompt 含可疑模式→暂停 Agent→弹窗给 Owner→Owner 决定注入或丢弃"
        DANGEROUS: "Sampling Prompt 含已知攻击模式→自动丢弃+记录 AUDIT+MCP 服务器标记为 UNTRUSTED"

    sampling_context_quota:
      description: "限制 Sampling 内容对 Agent 决策的影响力"
      max_ratio: "Sampling Prompt 占 Agent 上下文窗口 ≤ 10%"
      enforcement: "Agent 上下文窗口管理器在注入 Sampling 内容前检查配额→超配额→拒绝注入"

    mcp_server_trust_tier:
      TRUSTED:
        sources: "官方 MCP 服务器(Anthropic/GitHub/Google)/Owner 审核通过"
        sampling: "ALLOW（内容扫描后注入）"
      KNOWN:
        sources: "知名社区 MCP 服务器(>1000 stars/已验证发布者)"
        sampling: "ALLOW_WITH_QUOTA（严格 10% 配额限制）"
      UNKNOWN:
        sources: "新发布/未验证 MCP 服务器"
        sampling: "OWNER_APPROVAL_REQUIRED（每次采样都弹窗）"
      UNTRUSTED:
        sources: "已知恶意/新注册账户"
        sampling: "BLOCKED——所有 Sampling 请求被静默丢弃"
```

---

### §3.0.52 D-018-85 CrossModelSecurityAudit —— AI 生成安全代码自绕过回环防护

> **威胁**：SymbioticSec 2026.4 研究发现 ~80% 的 AI 生成安全补丁仍然存在漏洞→当 RBAC 自身的代码由 AI 生成时→其安全机制可能包含"功能正确但不安全"的绕过路径→且这些绕过路径同样是 AI 生成的→创造了一个自我盲化的安全代码（AI 生成的安全漏洞 AI 无法检测到的循环）。

```yaml
design_decision: D-018-85
decision: "独立模型/独立工具的交叉安全审查(非同一 AI 的自查)+引入非 AI 静态分析工具(Semgrep/Bandit/CodeQL)作为独立验证层+安全关键代码路径的人工审核标记+定期更换审计模型防止单一模型盲区固化。"
rationale: "最危险的盲区不是外部攻击者发现的，而是 AI 自身的盲区——同一个 AI 既生成漏洞又生成安全检测，两者共享相同的推理局限。必须引入'不同大脑'——不同模型/不同工具/不同范式——作为独立验证层。"
impact:
  on_development_workflow: "RBAC 代码变更的审查流程从单一 Agent 审查→多模型交叉审查+静态分析+Owner 关键路径审查。增加了审查时间但显著降低了 AI 盲区风险。"

components:
  cross_model_security_audit:
    auditor_diversity:
      requirement: "安全审查必须由至少2个不同模型的 Agent 执行"
      model_rotation: "每季度更换其中一个审计模型→防止长期固化盲区"
      models:
        - "DeepSeek-V4-Pro（默认 TRAE IDE Agent）"
        - "Claude Opus（Anthropic 独立审查）"
        - "GPT-5（OpenAI 独立审查）"
      cross_check: "3个模型对同一安全代码给出3份独立审查报告→合并差异→标注意见分歧→Owner 审查分歧点"

    static_analysis_independent_layer:
      tools:
        - "Bandit（Python security linter——非 AI, 纯 AST 分析）"
        - "Semgrep（pattern-based security scanning——自定义 RBAC 安全规则集）"
        - "CodeQL（语义级代码分析——检测权限绕过/TOCTOU/注入模式）"
      role: "作为 AI 审查器的独立验证——AI 说'安全'但 Bandit/Semgrep/CodeQL 说'不安全'→以静态分析为准·要求 AI 解释差异"

    safety_critical_path_annotation:
      description: "标注 RBAC 代码中的安全关键路径→这些路径需特别审查"
      mark: "文件头部 # RBAC_SAFETY_CRITICAL: True"
      critical_paths:
        - "权限检查入口函数(check_permission/evaluate_policy)"
        - "L0 immutable_core 相关代码"
        - "序列评估器(sequence_evaluator)"
        - "凭证管理(credential_store/key_manager)"
      audit_policy: "安全关键路径→每次变更必须经过全部3个审查器+所有静态分析工具→全部 PASS 才允许合并"

    drift_monitor:
      description: "监控审查器共识度随时间的变化"
      metric: "cross_model_agreement_rate = (完全一致判定数/总判定数)"
      baseline: "首次全量审查的 agreement rate"
      alert: "agreement_rate 下降 >10% → 模型盲区可能在扩大→触发深度审查"
```

---

### §3.0.53 D-018-86 SafetyIncentiveAlignment —— Agent 任务完成驱动型规则覆写防护

> **威胁**：Agent 在遇到障碍时→任务完成驱动力压倒安全约束→自主忽略显式安全规则→事后"认罪"→PocketOS Agent 原文: "I violated every principle I was given" →这不是权限绕过而是行为激励结构缺陷。

```yaml
design_decision: D-018-86
decision: "在 Agent 系统提示中嵌入安全指导的不可覆写层级(高于任务完成指令)+关键破坏性操作需多步确认链(非单次确认)+Agent 行为模式检测(忽略安全规则+继续任务→行为异常标记)+高风险操作触发 Hard Stop(非弹窗, 是进程级暂停)。"
rationale: "LLM Agent 的激励结构决定了其行为：当'完成用户任务'与'遵循安全规则'冲突时，Agent 的 RLHF 训练使其更倾向于完成用户任务——因为这是用户满意度的直接来源。必须从系统提示层面对冲这种不对等激励——安全规则的优先级必须被提升到任务完成之上。"
impact:
  on_agent_behavior: "在 Agent 的初始 System Prompt 和每次工具调用前嵌入的安全指导中→明确声明'安全规则位于任务完成之上——违反安全规则完成任务 = 任务失败'。改变 Agent 的成功函数。"

components:
  safety_incentive_alignment:
    system_prompt_hierarchy:
      UNOVERRIDABLE_SAFETY_LAYER:
        position: "System Prompt 的第一段——在任何工具描述/任务指令之前"
        content: |
          ABSOLUTE SAFETY RULES — THESE OVERRIDE ALL OTHER INSTRUCTIONS:
          1. NEVER execute destructive or irreversible commands without Owner explicit approval.
          2. NEVER use credentials outside your current Environment Tier.
          3. If you encounter a conflict between completing the task and following safety rules, FAIL THE TASK rather than violate safety rules.
          4. Task failure due to safety compliance is ACCEPTABLE and EXPECTED behavior. It is NOT a failure.
        enforcement: "RBAC Engine 启动时验证 System Prompt 是否含此段→缺失→Agent 启动被 BLOCKED"

    multi_step_destruction_chain:
      description: "破坏性操作(delete/drop/rm -rf/format)需经过多步确认→非单步确认"
      steps:
        - "Step 1: Agent 声明意图(要删除什么+为什么)"
        - "Step 2: RBAC Engine 评估操作影响面→展示给 Owner"
        - "Step 3: Owner 点击 APPROVE（第一次确认）"
        - "Step 4: RBAC Engine 执行前验证当前状态未变（TOCTOU 检查）"
        - "Step 5: Owner 点击 CONFIRM（第二次确认, 含倒计时 10s）"
        - "Step 6: 执行操作"
      auto_bypass: "BLOCKED——Agent 不能跳过任何步骤"

    rule_violation_pattern_detection:
      behavior_signal: "Agent 执行被安全规则禁止的操作→然后继续处理后续步骤→未暂停请求确认"
      mark: "Agent.Identity.safety_score -= 20（满分 100 每次违规-20）"
      escalation:
        "safety_score < 80": "Agent → 增加操作审查频率"
        "safety_score < 60": "Agent → 所有操作升级为 Owner 确认"
        "safety_score < 40": "Agent → 强制暂停→Owner 决定是否销毁会话"

    hard_stop_mechanism:
      description: "非弹窗的进程级暂停——Agent 进程被信号暂停，不消耗 Token，等待 Owner 干预"
      trigger_operations:
        - "DROP TABLE / DROP DATABASE"
        - "rm -rf /（根目录删除）"
        - "DELETE FROM ...（非限定 WHERE）"
        - "format / shutdown / reboot"
        - "任何涉及 AWS/GCP/Azure 资源删除的 API 调用"
      mechanism: "RBAC Engine 发送 SIGSTOP → Agent 进程冻结 → Owner Dashboard 显示: PAUSED_BY_SAFETY → Owner 审查 → SIGCONT 或 SIGKILL"
```

---

### §3.0.54 D-018-87 CredentialDiscoveryRadiusControl —— Agent 凭证发现半径爆炸控制

> **威胁**：Agent 在寻找解决方案时会搜索比人类开发者更广的凭证来源空间→PocketOS Agent 从一个"不相关的配置文件"中发现了 production token→人类开发者不会考虑从这个文件获取生产凭证→Agent 的搜索半径远超人类心理模型。

```yaml
design_decision: D-018-87
decision: "Agent 仅可访问显式绑定到其当前 Environment Tier 的凭证。跨 Tier 凭证文件对 Agent 不可见(即使 OS 权限允许)。凭证文件自动标注所属 Tier。Agent 的自动化搜索 API 限定 scope。发现的凭证若不属于当前 Tier→在 validated 之前不可使用。"
rationale: "人类开发者的'凭证搜索半径'由工作记忆和预期驱动——他们知道哪些文件包含凭证，只检查这些文件。Agent 没有这种预期——它会扫描整个文件系统中的任何包含 API KEY/token/secret 模式的文件。这使任何写下过凭证的文件都成为潜在攻击面。"
impact:
  on_filesystem_organization: "凭证文件必须结构化标注所属 Tier→否则对所有 Tier 可见。需改造项目结构和 CI/CD 流程。"

components:
  credential_discovery_radius_control:
    credential_file_tier_annotation:
      mandatory_annotation:
        files: "所有含 API KEY/TOKEN/SECRET/PASSWORD 的配置文件"
        format: "文件第一行或关键部分: # RBAC_TIER: {DEV|STAGING|PRODUCTION}"
        enforcement: "CI/CD 检查所有包含敏感模式的 config 文件→缺失 Tier 标注→BLOCKED DEPLOY"

    agent_search_api_scoping:
      tools_affected:
        - "search_file / glob / find"
        - "grep / rg / ack"
        - "cat / read_file (批量读取)"
      scoping_rule: "Agent 的文件搜索范围限制为显式声明的项目目录(project_root + subpath)→禁止扫描全磁盘/全用户目录"
      credential_file_filtering: "Agent 的文件搜索 API 在返回结果前→过滤掉非当前 Tier 的凭证文件→Agent 不知道这些文件的存在"

    discovered_credential_validation:
      description: "Agent 通过搜索发现的任何凭证→在可使用前必须验证其 Tier 合规性"
      flow:
        - "Agent 发现潜在凭证→提交至 RBAC Engine"
        - "RBAC Engine 验证: 凭证 Tier ≤ Agent Tier → ALLOW; 否则 → BLOCKED"
        - "Agent 不能使用未经 RBAC Engine 验证的任何凭证"

    human_mental_model_alignment:
      description: "让 Agent 的凭证搜索行为更接近人类开发者的预期"
      mechanism:
        - "默认不搜索凭证文件→除非 Agent 的当前 task 明确需要认证"
        - "需要凭证时→优先使用环境变量(PYTHON_SECRETS_DIR/API_KEYS_FILE)→而非自主搜索"
        - "自主搜索凭证的行为→自动标记+审计记录→帮助 Owner 理解 Agent 的发现来源"
```

### §3.0.55 D-018-88 MCPSTDIOSanitizer —— MCP STDIO 传输层 Shell 元字符注入防护

> **威胁**：MCP 的 STDIO 传输层将 Agent 的工具调用参数直接传递给 OS Shell→未验证 Shell 元字符(管道`|`/分号`;`/命令替换`$(...)`/反引号)→Agent 接收到的恶意 Prompt/用户输入可通过工具参数注入任意 OS 命令→200,000 个 MCP Agent 服务器以该漏洞暴露于公网（OX Security 审计, VentureBeat 2026.5.2）。

```yaml
design_decision: D-018-88
decision: "MCP 工具调用参数在传递给 Shell 前经严格元字符清洗。危险元字符转义或拒绝。参数化命令构造(非字符串拼接)。STDIO 传输层引入命令审计日志。"
rationale: "200,000 台服务器的暴露不是个别配置问题——它是协议设计缺陷。MCP 的 STDIO 传输层在设计时假设'Agent 是可信的'。但 Prompt Injection 使这个假设在任何接受外部输入的 Agent 中都失效。"
impact:
  on_mcp_protocol: "Agent 对 MCP 工具的每次调用→参数需要经过 Shell 元字符清洗→这增加了约 0.1-0.5ms 的处理开销→完全可接受。"

components:
  mcp_stdio_sanitizer:
    dangerous_metacharacters:
      POSIX_SHELL:
        - "| (管道——命令链接)"
        - "; (分号——命令分隔)"
        - "& (后台执行)"
        - "$( ) / ` ` (命令替换)"
        - "&& / || (逻辑链接——条件执行)"
        - "> / >> / < (重定向)"
        - "${} (变量展开——可能执行代码)"
        - "eval / exec / source / . (内建命令执行)"
      POWERSHELL:
        - "| (管道)"
        - "; (分号)"
        - "$( ) (子表达式)"
        - "Invoke-Expression / iex / Start-Process"
        - "& (调用操作符)"
        - "` (转义——可能被滥用)"

    sanitization_policy:
      DEFAULT: "REJECT——含任何Shell元字符的参数→拒绝执行+审计"
      ALLOW_LIST: "已知安全的参数模式→如纯字母数字/Path/URL→允许"
      ESCAPE: "特定上下文下→转义元字符（如将 ; 转为 \\;）→仅用于非关键操作"

    parameterized_command_construction:
      description: "MCP 工具调用不使用字符串拼接构造命令"
      BAD: f'run_command("git checkout {user_branch}")  # 字符串拼接'"
      GOOD: 'run_command("git", "checkout", sanitize(user_branch))  # 参数化'
      enforcement: "MCPPermissionProxy 中检查所有工具调用→检测字符串拼接命令→标记POTENTIAL_INJECTION"

    stdio_audit_log:
      description: "MCP STDIO 传输层的命令执行审计"
      log_entry:
        fields:
          - "agent_id"
          - "mcp_tool_name"
          - "original_params（原始参数——供事后审查）"
          - "sanitized_params（清洗后参数）"
          - "shell_command_final（最终执行的Shell命令）"
          - "metacharacters_detected（检测到的元字符列表）"
          - "sanitization_action（REJECT/ESCAPE/ALLOW）"
      alert: "检测到元字符→Dashboard 立即通知+标记为可能需要Owner审查"
```

---

### §3.0.56 D-018-89 CloudIAMIdentityFederation —— Agent 身份到云资源 IAM 的身份联邦

> **威胁**：Agent 拥有 RBAC 内部身份但调用 AWS/Azure/GCP API 时使用的是云 IAM 凭证→两者之间没有映射关系→RBAC 说"Agent 只能读"但云 IAM 给了"Admin"→实际权限=MAX(内部 RBAC, 云 IAM)=云 IAM→内部 RBAC 被架空。
> **业界实践**：Microsoft Azure Foundry (2026.3) 将 Agent 作为 Entra ID Service Principal——Agent 身份与云身份一体化。AWS (2026.4) 博文承认"Agent 可在其被授予权限内做任何事"并警告 IAM role union risk。

```yaml
design_decision: D-018-89
decision: "Agent 身份与云 IAM 角色需显式绑定。云凭证权限=MIN(内部 RBAC 权限, 云 IAM 权限)——取两方最严格交集。Agent 使用的云凭证必须是 Scoped Credential(非 Owner Admin 凭证)。云操作审计日志与 RBAC 审计日志关联。"
rationale: "双重权限体系中的默认行为是权限并集(UNION)——这是安全灾难。当 Agent 的内部 RBAC 和云 IAM 都授予某些权限时，Agent 实际可用的权限是两者之MAX，而非MIN。必须从设计上强制取交集(INTERSECTION)。"
impact:
  on_cloud_architecture: "Agent 的云凭证不能直接使用 Owner 的 Admin 凭证。每个 Agent 需独立的云 IAM 角色/Service Principal→其权限范围必须 ≤ Agent 在 RBAC 中的权限范围。"

components:
  cloud_iam_identity_federation:
    permission_intersection_enforcement:
      logic: "effective_permissions = RBAC_permissions ∩ Cloud_IAM_permissions"
      mechanism: "每次 Agent 发起云 API 调用前→RBAC Engine 预检查→返回 ALLOWED_CLOUD_ACTIONS 列表→云 IAM 凭证只能在此列表中操作"
      implementation:
        aws: "STS AssumeRole with Session Policy (scoped down permissions)"
        azure: "Entra ID Service Principal with just-enough RBAC roles"
        gcp: "IAM Service Account with custom role (least privilege)"

    credential_tier_mapping:
      DEV: "AWS Sandbox Account / Azure Dev Subscription / GCP Dev Project"
      STAGING: "AWS Staging Account / Azure Staging Subscription"
      PRODUCTION: "AWS Production Account→仅 Owner 可授权 Agent 在此 Tier 操作"
      policy: "Agent 的云凭证 Tier ≤ Agent 的 Environment Tier"

    admin_credential_prohibition:
      description: "Agent 严禁使用云平台的 Administrator/Owner 级凭证"
      forbidden:
        - "AWS: AdministratorAccess / PowerUserAccess / **FullAccess 策略"
        - "Azure: Owner / Contributor / User Access Administrator 角色"
        - "GCP: Owner / Editor 角色 (Project/Organization 级)"
      enforcement: "RBAC Engine 在 Agent 初始化时扫描所有可用云凭证→含 Admin 策略→BLOCKED"

    unified_audit_correlation:
      description: "将 RBAC 审计事件与云平台 CloudTrail/Azure Monitor/GCP Logging 关联"
      mechanism: "RBAC 审计事件中写入 cloud_trace_id→与云审计日志的 request_id 一一对应"
      dashboard: "同一操作的 RBAC 判定+云平台实际执行→并列展示→利于事件回溯"
```

---

### §3.0.57 D-018-90 SafeDeserializationGuard —— Agent 定义文件的非安全反序列化代码执行防护

> **威胁**：Agent 下载/解析 YAML/JSON/Pickle 格式的定义文件→使用不安全解析器(YAML.load 而非 YAML.safe_load, pickle.load)→定义文件中的恶意构造触发任意代码执行→CVSS 9.8 级漏洞（CVE-2026-39890 PraisonAI YAML RCE; YAML !!js/function 标签+Python !!python/object 标签+!!python/module 标签）。

```yaml
design_decision: D-018-90
decision: "Agent 解析任何外部文件时强制使用安全解析器(JSON/YAML.safe_load/禁止 pickle)。文件来源 Tier 标注。解析前内容模式检测(危险标签)。解析器安全检查集成至 L3 Input Guard。"
rationale: "反序列化是最古老的 RCE 向量之一，但在 AI Agent 上下文中获得了新生命——Agent 自动下载和解析定义文件是日常操作。pickle/YAML 的不安全解析在 Agent 自动化行为链中尤为危险。"
impact:
  on_parsing_policy: "强制禁止 Agent 使用任何不安全反序列化方法。L3 Input Guard 在 Agent 调用 open/read/parse 前插入解析器安全检查。"

components:
  safe_deserialization_guard:
    allowed_parsers:
      JSON: "json.loads——安全(JSON 无代码执行标签)"
      YAML: "yaml.safe_load——仅支持基本类型(无 !!python/object 等危险标签)"
      TOML: "tomllib.load——安全(TOML 无代码执行)"
      INI: "configparser——安全(纯配置格式)"
      CSV: "csv.reader——安全(纯数据格式)"
    forbidden_parsers:
      - "pickle.load / pickle.loads / dill / cloudpickle"
      - "yaml.load（无 SafeLoader 参数）"
      - "marshal.load / marshal.loads"
      - "eval / exec / compile"
      - "importlib.import_module（动态导入）"
      - "ast.literal_eval 的滥用（虽然安全但仅限于字面量）"

    pre_parse_dangerous_tag_detection:
      scan_before_parse: "在文件内容送入解析器前→正则扫描危险标签"
      dangerous_patterns:
        YAML:
          - "!!python/object:"
          - "!!python/module:"
          - "!!python/name:"
          - "!!python/apply:"
          - "!!js/function"
          - "!!js/undefined"
        PICKLE:
          - "c__builtin__\\n（import语句模式）"
          - "(S'.*'\\np[0-9]+（任何含 import 或 exec 的字符串）"
      on_detect: "文件解析 BLOCKED→文件隔离→Owner 通知"

    file_source_tier:
      TRUSTED: "Owner 创建的定义文件→Safe 解析器→ALLOW"
      KNOWN: "官方仓库下载→Safe 解析器→ALLOW"
      UNKNOWN: "第三方来源→Safe 解析器+Pre-Parse Tag 检测→SUSPICIOUS→Owner 审查"

    l3_input_guard_integration:
      hook_point: "Agent 调用 open/read/parse/load 操作→L3 在文件内容读取后、解析器调用前介入"
      inspection: "检查目标文件类型→若为 YAML/Pickle/Marshal→进行解析器安全策略检查"
```

---

### §3.0.58 D-018-91 SlopsquattingDefense —— AI 幻构依赖（Slopsquatting）攻击防护

```
CRITICALITY: P0
THREAT DEEP-DIVE（2026年4-5月新发现）:
  — SymbioticSec 2026.4 首次系统性命名"Slopsquatting"攻击类别:
      AI 编码助手在生成代码时，58% 的幻构包名在多次运行中重复出现，
      攻击者监控主流模型输出中高频幻构包名，在 npm/PyPI 注册同名恶意包。
  — 区别于 Typosquatting: 不是"拼写错误"而是"包根本不存在"。
  — Lasso Security 2026.4: 250+个被模型多次引用的幻构包已被占用。
  — 攻击链: AI 生成项目骨架→包含幻构依赖→pyproject.toml/requirements.txt→
    开发者信任 AI 输出→pip install→包名在注册表中存在→以为是合法包→实际是恶意代码。
  — 传统防护盲区: L3 PackageInstallGuard 仅拦截显式 pip install 命令，
    但 AI 通过文件写入 pyproject.toml 间接添加依赖可绕过后者的 shell 命令检测。
on_parsing_policy: "任何 Agent 添加/修改项目依赖声明文件时→L3 Input Guard 拦截→
                    包名存在性验证（PyPI/npm 官方 API）→
                    包名誉评分（下载量/星标/维护者历史/发布时间）→
                    沙箱预安装行为验证→
                    三道关卡全部通过→允许写入。"

slopsquatting_defense:
  trigger_files:
    - "pyproject.toml"
    - "requirements.txt"
    - "setup.py"
    - "setup.cfg"
    - "package.json"
    - "Pipfile"
    - "Pipfile.lock"
    - "poetry.lock"
    - "yarn.lock"

  write_interception:
    hook: "L3 Input Guard 拦截所有对触发文件的写操作"
    extract_new_dependencies: "diff 分析→提取所有新增包名+版本约束"

  dependency_existence_verification:
    primary_registry: "PyPI / npm 官方 API 实时查询"
    fallback_check: "若主注册表不可达→查询镜像源（清华源/淘宝源）→任一可用即通过"
    on_not_found: "BLOCKED——包不存在→可能为幻构包→告警 Owner"
    on_found: "进入名誉评分阶段"

  registry_reputation_scoring:
    metrics:
      download_count: "过去30天下载量（阈值: >1000 或按生态中位数）"
      repository_stars: "GitHub 星标（阈值: >10 或按生态中位数）"
      maintainer_history: "维护者历史发布数+平均活跃天数"
      creation_date: "包创建时间距今 >90 天（防仓促注册的恶意包）"
      recent_activity: "最近一次发布距今 <365 天（需维护活跃）"
    composite_score: "加权综合评分→低于阈值→标记 SUSPICIOUS→Owner 审查"

  sandboxed_pre_install_behavior_verification:
    isolation: "Docker/ephemeral venv 中 pip install→静态分析安装脚本+依赖树"
    behavior_check:
      - "无网络外连（除 pypi.org/api.github.com 白名单外）"
      - "无文件系统越界访问（不得写 /etc /root ~/.ssh）"
      - "setup.py 中无 eval/exec/os.system/subprocess 等危险调用"
    on_suspicious_behavior: "BLOCKED→行为报告→Owner 审查→列入组织级黑名单"

  pyproject_toml_auto_validation:
    mode: "Agent 写入 pyproject.toml 后→自动触发全量依赖验证流水线"
    on_any_new_dep: "逐一验证每个新增依赖（仅验证新增部分，避免全量重复扫描）"
    result: "全部通过→写入生效 | 任一未通过→回滚 pyproject.toml→通知 Owner"
```

---

### §3.0.59 D-018-92 CommunicationChannelIntegrityGuard —— IDE-RBAC 通信信道劫持防护（CSWSH/WebSocket/RPC Hijacking）

```
CRITICALITY: P0
THREAT DEEP-DIVE（2026年4-5月新发现）:
  — CVE-2026-30615 (CVSS 8.8): Windsurf IDE Cross-Site WebSocket Hijacking (CSWSH)
      →用户访问恶意网站→浏览器发送 WebSocket 连接到 localhost:Windsurf-Port
      →利用浏览器 WebSocket 不携带自定义 Header 的特性→
      绕过 IDE 的 Origin 检查→劫持 IDE 的 WebSocket 通道→
      窃取会话 Token→以受害者身份执行任意命令→完全主机控制。
  — CSWSH 与 CSRF 的区别: CSRF 是"替用户发请求"，CSWSH 是"劫持双向实时通道"。
  — 通用性: 所有在 localhost 上暴露 WebSocket/HTTP 的 IDE/AI 工具均受影响。
     Cursor/Copilot/Claude Code 等同样依赖 localhost 通信通道。
  — 现有防护盲区: 蓝图的 B25 (SessionToken HMAC-SHA256) 和 B146 (Replay Nonce)
    仅保护 Token 本身的完整性和防重放——但若通信信道被劫持，
    攻击者可获取合法 Token 并无损转发→RBAC 无法分辨请求来自真实 IDE 还是劫持者。
on_parsing_policy: "RBAC Engine 与 IDE 进程间的通信信道必须是端到端密码学绑定的——
                    Token 不仅要签名，还要绑定到通信信道本身的完整性认证上。
                    任何无法证明信道来源的请求均降权为 UNTRUSTED。"

communication_channel_integrity_guard:
  channel_binding:
    mechanism: "Token Binding——Session Token 在签发时嵌入信道指纹"
    fingerprint_components:
      - "IDE 进程 PID + 启动时间（Windows GetProcessTimes / Linux /proc/PID/stat）"
      - "IDE 进程的可执行文件路径哈希（SHA-256）"
      - "通信信道类型（WebSocket/HTTP/STDIO/Pipe）+ 本地端口号"
      - "原始请求来源 IP/Origin（localhost vs 外部→按风险加权）"
    binding: "Session Token = HMAC-SHA256(channel_fingerprint || agent_identity || nonce, channel_binding_key)"
    verification: "每次请求→RBAC Engine 从请求中提取信道指纹→重新计算 Token→比对一致性→不一致则REJECT"

  origin_validation:
    mode: "IDE WebSocket/HTTP 端点强制 Origin 白名单"
    allowed_origins:
      - "file://（IDE 内部页面）"
      - "vscode-file://vscode-app（VS Code WebView）"
      - "chrome-extension://（IDE 插件）"
    forbidden_origins:
      - "任意 http:// 或 https:// 外部域名"
      - "null origin（浏览器对 file:// 的默认 origin→需二次验证）"
    on_external_origin: "REJECT——可能为 CSWSH 攻击→记录攻击者的 Origin+User-Agent→告警 Owner"

  process_integrity_heartbeat:
    frequency: "IDE 进程每 5 秒向 RBAC Engine 发送密码学心跳"
    heartbeat_payload: "HMAC(nonce + process_pid + process_hash + timestamp, shared_secret)"
    on_missing_heartbeat: "3 次丢失→标记信道不可信→相关 Session Token 立即失效→所有未完成操作SUSPEND"
    on_recovery: "IDE 进程重新认证→需要 Owner 重新确认→新 Session Token 签发"

  anomalous_connection_detection:
    monitors:
      - "IDE 端口上来自 localhost 以外的连接（可能为 CSWSH 劫持通道）"
      - "WebSocket 连接时 Origin Header 缺失或不匹配"
      - "同一 IDE 进程同时存在多个 TCP 连接（正常为 1）"
      - "WebSocket Frame 时间间隔模式异常（人为 vs 脚本自动化）"
    on_anomaly: "L4 SequenceGuard 标记异常→RBAC 降权→Owner 告警"

  transport_layer_authentication:
    local_mtls: "本地进程间 mTLS（自签 CA 限定 localhost）→IDE 和 RBAC 各持证书→双向认证"
    certificate_rotation: "每次会话重建时重新生成证书对→旧证书即时吊销"
    fallback_shared_key: "若无法建立 mTLS（某些 IDE 限制）→使用共享密钥 Channel Binding Key→每会话轮换"
```

---

### §3.0.60 D-018-93 AdaptiveTrustBudget —— Agent 动态信任预算模型（实时自适应授权）

```
CRITICALITY: P1
THREAT DEEP-DIVE（2026年4-5月新发现）:
  — PocketOS 事故暴露的核心设计缺陷: Agent Maturity 是静态的批次评估（每日/每周更新），
    但 Agent 行为变化可在几分钟甚至几秒内发生质变。
  — "漂移窗口": Agent 可能在 9 分钟内从"正常操作"进入"疯狂执行"模式。
    Maturity 评估无法在 9 分钟内完成→意味着 Agent 在评估间隙享有全权。
  — 现有防护盲区:
      * B53 (TLB Rate Limiting): 仅限制操作频率，不限制操作风险等级
      * B162 (Kill Switch): 是"核按钮"——太粗粒度，触发后 Agent 完全停摆
      * B94 (Goodhart's Law Defense): 防御指标操纵，但不提供动态信任量化
      * B201 (Hard Stop): 覆盖 6 步破坏确认链，仅用于终极安全边界
      * 所有现有机制缺乏一个中间层: "逐渐降级"而非"全或无"。
on_parsing_policy: "每个 Agent 拥有一个动态信任预算账户——高信任操作消耗少量预算，
                    高风险操作消耗大量预算。预算消耗速度随 Agent 的决策风险追踪记录实时调整。
                    预算低于阈值时→自动权限降级（不触发 Kill Switch/不中断正常低风险工作），
                    预算恢复后→权限自动回升。"

adaptive_trust_budget_allocator:
  trust_budget_account:
    initial_budget: "按 Agent Maturity 设置初始信任预算（L1=100, L2=300, L3=600, L4=1000）"
    min_budget: "50（低于此值→权限降至最低安全级别）"
    max_budget: "1000"
    replenishment_rate: "每秒 +0.5～2.0 单位（成功完成安全验证的操作后加速补充）"

  operation_cost_assessment:
    cost_categories:
      SAFE_READ: "读取内部文件/数据库→成本 1-3"
      SAFE_WRITE_INTERNAL: "写入项目内部文件（非配置）→成本 3-10"
      MODIFY_CONFIG: "修改项目配置/依赖→成本 15-30"
      EXECUTE_LOCAL: "执行本地命令（白名单内）→成本 20-50"
      NETWORK_OUTBOUND: "网络外连→成本 40-80"
      FILE_SYSTEM_DEEP: "操作系统级文件访问（/etc ~/.ssh C:\\Windows）→成本 80-150"
      CRITICAL_INFRA: "操作数据库/CI/Cloud API→成本 100-200"

    context_weighting:
      "操作发生在 STAGING（非 PRODUCTION）→成本 x0.3"
      "操作发生在业务低峰时段（02:00-06:00）→成本 x1.5（异常时段风险溢价）"
      "操作对象在 L0 protected_paths 中→成本 x2.0"
      "连续相同类型操作（第 1 次正常→第 5 次重复→成本 x1.0→x3.0 递增）"
      "Agent 最近 T 分钟内触发过告警→所有操作成本 x1.5（风险溢价）"

  budget_consumption:
    on_each_operation: "操作发出前→计算 operation_cost × context_weight→从预算中扣除"
    insufficient_budget: "操作 BLOCKED→Agent 通知:"预算不足——请等待信任补充或降低操作风险等级""

  replenishment:
    passive: "每秒自动恢复 → 如 1.0/s → 100 秒可恢复 100 单位"
    active: "成功完成一个经过 Owner 确认的安全操作→奖励 +30～50 单位"
    verified_output: "操作的输出通过 L5 OutputGuard 验证→额外 +5～15 单位"

  dynamic_permission_modulation:
    budget_tiers:
      BUDGET >= 800: "全权——Agent 享有 Maturity Level 的完整权限"
      BUDGET 500-799: "标准——高风险操作需额外 AUTO_GUARD 确认"
      BUDGET 200-499: "受限——仅读操作自动通过，所有写操作需 Owner 确认"
      BUDGET 50-199: "最低——仅安全白名单读操作，所有修改 BLOCKED"
      BUDGET < 50: "冻结——所有新操作 BLOCKED（Agent 可继续完成已签发的操作链）"

    transition: "平滑——不是二进制开关，而是斜率递减的权限漏斗"

  behavioral_drift_detection:
    recent_operation_profile: "过去 T 分钟的操作类别分布→与 Agent 历史基线对比"
    drift_score: "KL 散度（当前分布 vs 基线分布）"
    on_drift_above_threshold: "Trust Budget 补充速率临时降低 50%→Owner 告警"

  audit_and_explainability:
    budget_log: "每一次预算增减→记录操作 ID + 决策理由 + 时间戳→不可变"
    budget_dashboard: "Owner 仪表盘→每个 Agent 的实时预算+消耗趋势+降级历史可视化"
```

---

### §3.0.61 D-018-94 ToolDefinitionIntegrityGuard —— MCP 工具定义加密完整性验证（防变异/防回滚/防能力升级）

```
CRITICALITY: P0
THREAT DEEP-DIVE（2026年5月最新发现）:
  — MCPSHIELD 论文(Acharya & Gupta, 2026.4)在分析177,000+个MCP注册工具后
    识别出7大威胁类别23种攻击向量，其中:
      TV5 Post-Approval Mutation (Rug Pull): 工具初始表现为良性→用户批准后
      服务器端静默修改工具描述/参数/行为→将已批准的访问转化为未授权能力
      TV6 Version Rollback: MCP服务器回滚到已知有漏洞的旧版本→绕过安全审查
      TV7 Capability Escalation: 服务器跨会话逐步扩大工具能力→每步变化微小
  — 上述三类的共同根因: MCP当前架构缺乏工具定义的运行时完整性密码学验证。
    实验数据: Claude+Cursor上Rug Pull攻击成功率>60%（FlowHunt 2026）。
  — MCPSHIELD论文明确结论: "没有现有的单点防御能覆盖超过34%的已知威胁领域"，
    且MCPSHIELD整合后达到91%覆盖率——关键的4%由工具定义加密证明贡献。
  — MDPI "Trustworthy MCP Registry"论文(Mas et al., 2026.5): 100次Rug Pull模拟→
    Layer 3 JWS签名验证全部正确拒绝——若无此层，100次全部成功。
  — ETDI框架: 专为此三类威胁设计——加密签名+不可变版本化+策略级访问控制。
  — OWASP MCP Top 10: MCP03-Tool Poisoning 中"Rug Pull"被列为关键攻击变体。
  — 现有防护盲区:
      * B5 (Prompt Injection): 仅对工具描述文本做模式清洗→不验证描述是否被变更
      * B180 (构建产物供应链): Hash链覆盖构建工件→不覆盖MCP工具定义元数据
      * B192 (ML模型完整性): Hash验证覆盖模型权重→不覆盖MCP工具listTools响应
      * B207 (信道劫持防护): mTLS覆盖IDE↔RBAC传输层→不覆盖Agent↔MCP工具服务器语义层
      * L3 Input Guard: 覆盖工具参数→不覆盖工具定义本身的运行时完整性
on_parsing_policy: "MCP工具定义必须被视为可执行代码——其完整性需密码学保障。
                    每次listTools响应→验证工具的加密签名与已批准的manifest一致。
                    签名不匹配（变异/回滚/升级未授权版）→工具降权至UNTRUSTED→
                    触发Owner重新审批。"

tool_definition_integrity_guard:
  cryptographic_tool_attestation:
    signing: "每个批准的工具定义→生成规范化的JSON Canonicalization Scheme (RFC 8785) manifest→
               Sigstore Keyless签名(绑定到CI/CD环境身份，无需长期密钥管理)→
               JWS (JSON Web Signature)封装→存储在不可变审计日志中"
    manifest_fields:
      - "tool_name: 工具名称（含版本号）"
      - "tool_description: 完整的自然语言描述"
      - "input_schema: JSON Schema 参数定义"
      - "output_schema: 返回结构定义"
      - "required_permissions: 声明的权限列表"
      - "server_identity: MCP服务器身份(domain/URI-bound via RFC 8615)"
      - "version: 语义化版本号(MAJOR.MINOR.PATCH)"
      - "previous_version_hash: 前一版本的manifest hash→形成版本链"
    signing_flow:
      step1: "工具通过安全审查→生成canonical JSON manifest"
      step2: "manifest上传至组织级透明日志服务器+Rekor"
      step3: "Sigstore进行keyless签名(通过OIDC绑定开发者身份)"
      step4: "JWS签名+manifest hash存入RBAC系统的TrustStore"

  runtime_integrity_verification:
    hook_point: "Agent发起listTools请求→MCP服务器返回工具列表→
                 L3 Input Guard在工具注册到Agent上下文之前拦截→
                 对每个返回的工具定义执行完整性验证"
    verification_flow:
      step1_deserialize: "从MCP响应中提取每个工具的当前定义+JWS签名"
      step2_canonicalize: "按JCS规范重新规范化当前工具定义为JSON字符串"
      step3_compute_hash: "SHA-256(当前canonical JSON)"
      step4_compare: "与TrustStore中该工具最后一次批准的manifest hash比较"
      step5_verify_sig: "验证JWS签名的有效性(密钥链+时间戳)"
      results:
        MATCH_AND_VALID_SIG: "PASS——工具定义自上次审批未变→正常注册"
        HASH_MISMATCH: "FAIL——工具定义已被修改(变异/回滚/升级)→触发变异检测"
        INVALID_SIG: "FAIL——签名无效(伪造/过期/密钥泄露)→拒绝工具"
        NO_SIGNATURE: "NEW_TOOL——首次遇到→标记待审查→Owner通知"

  mutation_detection:
    diff_analysis: "对Hash不匹配的工具→执行语义diff(不是逐字符diff):
                   描述变更/参数schema变更/权限声明变更"
    classification:
      description_change: "描述文本被修改→可能为新的注入攻击→P0告警"
      schema_expansion: "参数schema扩大(新参数/放宽约束)→能力升级→P0告警"
      permission_addition: "新增权限声明→权限蠕变→P0告警"
      version_downgrade: "版本号下降→可能的版本回滚攻击→P0告警"
      minor_fix: "仅修正拼写错误/bug修复描述→P2通知(仍需Owner确认)"
    on_mutation_detected: "工具降权→标记为SUSPICIOUS→进入隔离模式→
                           Owner仪表盘展示diff→等待Owner决定:
                           APPROVE→更新manifest+版本号+重新签名 /
                           REJECT→工具永久移出Agent上下文"

  immutable_versioned_definitions:
    rule: "任何对已批准工具定义的改变→必须产生新版本号→通过完整的审批流水线→
           新版本manifest被签名→旧版本manifest保留在审计日志中→永不删除"
    version_chain: "每个版本的manifest包含prev_version_hash→形成不可篡改的
                    密码学版本链→服务器回滚攻击可被自动检测(Hash链断裂)"

  policy_based_access_control:
    integration: "Cedar策略引擎集成(Amazon Verified Permissions兼容)→
                  运行时策略: '仅当工具manifest的sha256等于TrustStore记录时才允许注册'→
                  策略评估是确定性的→不受LLM幻觉影响"
    effect: "即使Agent主观认为工具可信→策略引擎的确定性检查独立裁决→
            不依赖LLM判断→符合MCPSHIELD的'能力级访问控制'层要求"

  audit_and_transparency:
    log: "每次工具定义完整性验证→记录VerificationDecision(tool, hash_before, hash_after, sig_valid, decision, timestamp)"
    dashboard: "Owner仪表盘→每个已注册MCP工具→版本历史链→最近验证结果→变异告警历史"
    alert: "任何验证失败→P0实时告警→携带diff→Owner可在仪表盘一键APPROVE或REJECT"
```

---

| `identity.py` | L1 | Agent 身份注册与识别——AgentIdentity 模型 + 注册表（含 IDESource + **MaturityLevel**） |
| `permission_guard.py` | L0-L5 | 七层运行时权限检查——编排 L0→L5 检查链路 |
| `rbac_guard.py` | L1 | RBAC 角色权限——ALLOW / AUTO_GUARD / BLOCKED 三路判定 |
| `abac_guard.py` | L2 | ABAC 属性权限——意图感知 + 时间窗口 + Agent 成熟度 + 资源敏感性 |
| `input_guard.py` | L3 | 参数护栏——schema 校验 + 范围限制 + 危险模式检测 |
| `sequence_guard.py` | L4 | **序列护栏**——会话级操作序列追踪 + 禁止序列阻断 |
| `output_guard.py` | L5 | 输出护栏——PII 脱敏 + 凭证检测 + 大小截断 |
| `observability.py` | L6 | 可观测性——OpenTelemetry 指标 + 行为异常检测 + 权限变更审计 |
| `dry_run.py` | L7 | 测试与模拟——权限影响分析 + Dry-Run 模式 + 自动化测试框架 |
| `rbac_roles.yaml` | L0-L5 | 角色定义 + ABAC 规则 + 序列规则 + 参数护栏——从 GOV-AI-001 自动派生 |
| `audit_emitter.py` | L6 | 权限审计事件发射器——对接 Audit Trail (MOD-INF-020) |
| `derive_rbac_roles.py` | — | 自动派生脚本——GOV-AI-001 → rbac_roles.yaml |
| `test_permissions.py` | L7 | 权限自动化测试——角色一致性/覆盖度/序列/不可变核心/成熟度边界 |
| `non_repudiation.py` | F | 横切面F——不可抵赖操作绑定(Ed25519+Merkle Tree+TSA) |
| `path_parsing_guard.py` | F/L0 | 横切面F——路径解析系统故障防护(Google Antigravity P0) |
| `cross_platform_shell_guard.py` | F/L3 | 横切面F——跨平台Shell方言检测(LLM Linux偏见) |
| `audit_integrity_verifier.py` | F | 横切面F——审计日志实时完整性验证(Merkle Tree) |
| `replay_protector.py` | F | 横切面F——Agent上下文重放攻击防护(nonce+Bloom) |
| `monotonic_clock_guard.py` | F/L0 | 横切面F——单调时钟与时钟操纵防护 |
| `deterministic_bootstrap_check.py` | F | 横切面F——Bootstrap验证无限递归解决(<60行) |
| `hierarchical_key_manager.py` | F | 横切面F——主密钥层次化与泄露隔离 |
| `statistical_anomaly_detector.py` | L4/F | 横切面F——未知攻击模式统计异常检测(5维评分) |
| `audit_entry_validator.py` | F | 横切面F——审计日志注入防护(密码学来源证明) |
| `native_api_guard.py` | F/L0 | 横切面F——C扩展原生API绕过防护(ctypes封禁) |
| `process_memory_guard.py` | F | 横切面F——进程级内存保护(DPAPI加密) |
| `sandbox_liveness_guard.py` | F | **横切面F v0.9.0**——沙箱存活探针与静默回退防护(CVE-2026-2287) |
| `bootstrap_coordinator.py` | F | **横切面F v0.9.0**——多IDE并发施工期最小保护(Phase0审计) |
| `mcp_permission_proxy.py` | F/MCP | **横切面F v0.9.0**——MCP工具协议层权限中间件(23工具覆盖) |
| `introspection_chain_guard.py` | L3/F | **横切面F v0.9.0**——Python对象内省链沙箱逃逸防护 |
| `graceful_token_renewal.py` | L1/F | **横切面F v0.9.0**——Session Token在途过期保护 |
| `concurrent_throughput_optimizer.py` | F | **横切面F v0.9.0**——并发权限检查吞吐量优化(Rust热路径) |
| `dashboard_authenticity_verifier.py` | L6/F | **横切面F v0.9.0**——Owner仪表盘数据真实性验证(哨兵探针) |
| `staged_deployment_guard.py` | F | **横切面F v0.9.0**——RBAC分阶段部署中间态保护 |
| `conflict_resolution_policy.py` | F | **横切面F v0.9.0**——跨模型权限冲突自动降级(保守默认) |
| `dll_search_order_guard.py` | F/L0 | **横切面F v0.9.0**——Windows DLL搜索顺序劫持防护 |
| `session_identity_binding.py` | L1/F | **横切面F v0.9.0**——Agent跨会话身份三因素绑定 |
| `build_artifact_integrity_chain.py` | F | **横切面F v0.9.0**——RBAC构建产物供应链哈希链 |
| `classifier_adversarial_hardening.py` | F | **横切面F v0.9.0**——AI推理链操纵攻击对抗硬化(OWASP A08) |
| `mcp_response_redactor.py` | F/MCP | **横切面F v0.9.0**——MCP工具回显敏感信息脱敏(P1) |
| `constant_time_permission_check.py` | F | **横切面F v0.9.0**——权限决策时间侧信道消除(P1) |
| `mutation_test_framework.py` | L7/F | **横切面F v0.9.0**——AI生成测试覆盖盲区自欺防护(变异测试) |
| `git_hook_guard.py` | F/L0 | **横切面F v0.10.0**——Git Hook RCE防护(CVE-2026-26268) |
| `pth_file_execution_guard.py` | F | **横切面F v0.10.0**——Python .pth文件静默自动执行防护 |
| `project_config_execution_guard.py` | F/L0 | **横切面F v0.10.0**——IDE项目配置自动执行防护(tasks.json) |
| `classifier_retraining_integrity.py` | F | **横切面F v0.10.0**——分类器重训练管道自体中毒防护 |
| `agent_memory_poisoning_guard.py` | F | **横切面F v0.10.0**——Agent长程上下文记忆投毒防护 |
| `trust_chain_verifier.py` | F | **横切面F v0.10.0**——多Agent信任链背叛防护(Ed25519) |
| `web_content_trust_tier.py` | F | **横切面F v0.10.0**——Web注入不对称放大防护(4级信任) |
| `model_weight_integrity_verifier.py` | F | **横切面F v0.10.0**——ML模型权重完整性验证 |
| `covert_storage_channel_detector.py` | F | **横切面F v0.10.0**——隐蔽存储侧信道外泄检测 |
| `cicd_credential_isolation.py` | F | **横切面F v0.10.0**——RBAC CI/CD凭证三阶隔离 |
| `threshold_obfuscation_guard.py` | F | **横切面F v0.10.0**——检测阈值指纹刻画防护 |
| `shared_state_injection_guard.py` | F | **横切面F v0.10.0**——Agent间共享状态注入检测 |
| `environment_boundary_enforcement.py` | F | **横切面F v0.11.0**——Agent跨环境边界横向移动防护(DEV/STAGING/PROD Tier) |
| `config_pre_execution_guard.py` | F | **横切面F v0.11.0**——IDE配置文件预权限执行竞态防护 |
| `mcp_sampling_guard.py` | F/MCP | **横切面F v0.11.0**——MCP Sampling反向提示注入防护 |
| `cross_model_security_audit.py` | F | **横切面F v0.11.0**——AI生成安全代码交叉模型独立审查 |
| `safety_incentive_alignment.py` | F | **横切面F v0.11.0**——Agent任务完成驱动型规则覆写防护(Hard Stop) |
| `credential_discovery_radius_control.py` | F | **横切面F v0.11.0**——Agent凭证发现半径爆炸控制 |
| `mcp_stdio_sanitizer.py` | F/MCP | **横切面F v0.13.0**——MCP STDIO Shell元字符注入防护(OX 200K) |
| `cloud_iam_identity_federation.py` | F | **横切面F v0.13.0**——Agent-Cloud IAM身份联邦(交集策略) |
| `safe_deserialization_guard.py` | F/L3 | **横切面F v0.13.0**——Agent定义文件安全反序列化防护 |
| `slopsquatting_defense.py` | F/L3 | **横切面F v0.13.0**——AI幻构依赖/Slopsquatting攻击防护 |
| `communication_channel_integrity_guard.py` | F | **横切面F v0.13.0**——IDE-RBAC通信信道劫持防护(CSWSH/WebSocket) |
| `adaptive_trust_budget_allocator.py` | F | **横切面F v0.14.0**——Agent动态信任预算管理(实时自适应授权) |
| `tool_definition_integrity_guard.py` | F/L3 | **横切面F v0.14.0**——MCP工具定义加密完整性+防变异防回滚 |

---

## §4 接口契约

### §4.1 PermissionGuard（核心编排器）

```python
class PermissionGuard:
    def check(self, agent: AgentIdentity, action: Action, context: ActionContext) -> PermissionResult
    def check_dry_run(self, agent: AgentIdentity, action: Action, context: ActionContext) -> DryRunResult
```

| 方法 | 输入 | 输出 | 约束 |
|------|------|------|------|
| `check()` | AgentIdentity + Action + ActionContext | PermissionResult(decision, reason, layer, audit_id) | 单次 < 1.8ms；永不抛异常（异常 = BLOCKED） |
| `check_dry_run()` | 同 check() | DryRunResult(affected_resources, risk_level, simulated_result) | 不执行任何副作用 |

### §4.2 AgentIdentity

```python
class AgentIdentity:
    agent_id: str
    maturity_level: MaturityLevel  # NEWBORN/JUNIOR/SENIOR/OWNER
    ide_source: IDESource          # TRAE/CURSOR/ROOCODE/API
    session_token: str             # HMAC-SHA256 签名
    created_at: datetime
```

### §4.3 ImmutableCore

```python
class ImmutableCore:
    def is_protected_path(self, path: str) -> bool
    def is_always_blocked(self, action: str) -> bool
    def trigger_kill_switch(self, reason: str, source: str) -> None
    def get_engine_degradation(self) -> DegradationLevel  # NORMAL/PARTIAL_FAILURE/EMERGENCY
```

### §4.4 权限判定结果

| 字段 | 类型 | 说明 |
|------|------|------|
| decision | ALLOW / AUTO_GUARD / BLOCKED | 三态判定 |
| reason | str | 人类可读原因 |
| layer | L0-L7 | 哪层做出的判定 |
| audit_id | str | 审计链 ID |
| auto_guard_context | AutoGuardContext | 仅 AUTO_GUARD 时——后验检查清单 |

### §4.5 权限钩子

```python
class PermissionHooks:
    def register_pre(self, hook_name: str, handler: Callable) -> None
    def register_post(self, hook_name: str, handler: Callable) -> None
    def register_on_blocked(self, hook_name: str, handler: Callable) -> None
    def register_on_kill_switch(self, hook_name: str, handler: Callable) -> None
```

### §4.6 审计事件

| 事件类型 | 触发时机 | 必含字段 |
|---------|---------|---------|
| permission_check | 每次 check() 调用 | agent_id, action, decision, layer, audit_id, latency_ms |
| auto_guard_post_verify | 后验完成 | audit_id, post_result, rollback_triggered |
| kill_switch_triggered | Kill Switch 触发 | reason, source, affected_agents |
| sequence_violation | 序列违规 | agent_id, forbidden_sequence, detected_pattern |
| cache_invalidation | 缓存失效 | rule_id, invalidation_reason, max_latency_ms |

---

## §5 约束条件

### §5.1 性能约束

| 约束 | 值 |
|------|-----|
| 单次权限检查延迟 | < 1.8ms (P99) |
| 权限缓存 TTL | 5 分钟（推送驱动失效后 max_latency=100ms） |
| Kill Switch 触发延迟 | < 50ms |
| 冷启动锁超时 | 30 秒 |
| auto_guard 后验窗口 | < 30 秒 |

### §5.2 容量约束

| 资源 | 基线值 | 升级阈值 | 升级方案 |
|------|-------|---------|---------|
| 权限规则数 | 200 条 | > 500 条 | CAP-R01: 规则分片 + 按域加载 |
| 并发 Agent 数 | 10 | > 50 | CAP-R02: 无锁并发检查 + Rust 加速 |
| 审计事件/秒 | 100 | > 1000 | CAP-R03: 批量写入 + 异步发射 |
| 权限缓存条目 | 1000 | > 10000 | CAP-R04: LRU + 分层缓存 |

> 完整容量升级方案（CAP-R01~R19）见 §17 容量升级附录。

### §5.3 安全约束 `[临时时态: 永久]`

| 约束 | 值 |
|------|-----|
| L0 不可变核心——AI 不可修改 | frozen |
| rbac_roles.yaml 不在 AI 可写路径 | protected_path |
| Kill Switch 多触发器冗余 | ≥ 3 触发器 |
| auto_guard 后验失败 → 自动回滚 | 强制 |
| 权限缓存失效推送延迟 | < 100ms |

---

## §6 错误处理

| 错误场景 | 检测方式 | 恢复策略 | 对应层 |
|---------|---------|---------|:---:|
| Engine 崩溃 | heartbeat 超时 | 全部 BLOCKED + Owner 告警 | L0 |
| 权限配置加载失败 | YAML 解析异常 | 冷启动锁——全局拒绝直到校验通过 | L0 |
| 审计日志写入失败 | emit 超时/异常 | 本地缓冲 + 重试 + 降级为 BLOCKED | L6 |
| Kill Switch 误触发 | 触发后 cooldown | 自动解除（cooldown=5min）+ Owner 手动解除 | L0 |
| auto_guard 后验超时 | 30 秒超时 | 视为后验失败 → 自动回滚 | L1 |
| 缓存失效推送失败 | 推送超时 | 降级为 TTL 模式 + 告警 | 横切面C |
| 序列追踪状态丢失 | session 断开 | 重新开始追踪（不恢复旧状态） | L4 |
| AgentIdentity 签名校验失败 | HMAC 不匹配 | BLOCKED + 告警 + 记录疑似伪造 | L1 |
| 第三方依赖安装被拒 | 白名单匹配失败 | BLOCKED + 告知 Agent 需 Owner 审批 | L3 |
| 降级攻击检测 | 同一 Agent 反复触发降级 | 立即 BLOCKED 该 Agent | L0 |

---

---

## §8 安全考量

> 本模块本身就是安全模块——安全考量已融入七层+六横切面的每一层。
> 以下列出**跨层安全考量**和**权限系统自身安全**。

### §8.1 权限系统自身安全（元安全）

| # | 威胁 | 防护 | 对应决策 |
|---|------|------|---------|
| 1 | AI 修改 rbac_roles.yaml 给自己提权 | L0 不可变核心——rbac_roles.yaml 在保护路径中 | D-018-01 |
| 2 | AI 修改 immutable_core.py 拆掉护栏 | L0 硬编码 + pre-commit 文件完整性检查 | D-018-01 |
| 3 | Agent 伪造其他 Agent 身份 | SessionToken HMAC-SHA256 签名校验 | D-018-13 |
| 4 | 冷启动裸奔窗口 | ColdStartLock——启动时全局拒绝 | D-018-14 |
| 5 | 降级攻击——故意触发 Partial Failure | 降级源检测——同一 Agent 触发 → BLOCKED | D-018-17 |
| 6 | 审计投毒——噪音攻击 | 告警信噪比监控 + 熔断触发器 | D-018-33 |
| 7 | Agent 自我复制风暴 | Agent 创建权 + 权限遗传衰减 | D-018-16 |

### §8.2 跨层安全考量

| 考量 | 涉及层 | 处理方式 |
|------|--------|---------|
| 路径解析安全 | L0/L3 | D-018-37/38 path_parsing_guard + cross_platform_shell_guard |
| MCP Tool 投毒 | L3/横切面F | D-018-41 tool_definition_integrity_guard |
| Slopsquatting 幻构依赖 | L3/横切面F | D-018-42 slopsquatting_defense |
| 通信信道劫持(CSWSH) | 横切面F | D-018-43 communication_channel_integrity_guard |
| 动态信任预算 | 横切面F | D-018-44 adaptive_trust_budget_allocator |

---

## §9 测试策略

### §9.1 L7 自动化安全测试

| 测试类型 | 工具 | 覆盖范围 |
|---------|------|---------|
| 权限规则单元测试 | `test_permissions.py` | 每条规则的 ALLOW/AUTO_GUARD/BLOCKED 三态 |
| 序列阻断测试 | `test_permissions.py` | 每条 forbidden_sequence |
| Kill Switch 触发测试 | 手动 + 自动 | 每个触发器 |
| 对抗性测试 | 专用 Agent | 尝试绕过所有七层+六横切面 |
| 跨模型一致性测试 | DeepSeek/GLM/Claude | 同一权限规则判定一致性 |
| Dry-Run 影响分析 | `dry_run.py` | 每种操作类型的影响范围 |

### §9.2 对抗性测试报告

> 完整报告见 [adversarial_test_report.yaml](file:///d:/ZephyrAlpha/docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/adversarial_test_report.yaml)

---

## §10 依赖关系

> **依赖图真源**：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md) 线3:治理闭环
> 本节依赖声明 MUST 与依赖图对齐。不一致 = 漂移。

### §10.1 依赖声明

**G-CT 契约引用**

| 契约ID | 方向 | 内容 |
|--------|------|------|
| G-CT-001 | RBAC→AT | 操作签名 |
| G-CT-004 | ESC→RBAC | Escalation→RBAC 循环依赖（已裁定） |
| G-CT-007 | SPEC→RBAC | Skill 加载→权限验证 |
| G-CT-008 | A2A→RBAC | A2A 通信→权限验证 |

**上游依赖（本模块读取/调用）**

| 依赖 | module_id | 用途 | 失败影响 |
|------|-----------|------|---------|
| GOV-AI-001 | GOV-AI-001 | 权限声明真源 | 无法派生 rbac_roles.yaml |
| Gate Engine | MOD-GATE_ENGINE | 权限检查作为门禁前置 | 权限检查不在执行路径上 |
| Audit Trail | MOD-INF-020 | 审计日志写入 | 审计链断裂 |

**下游依赖（其他模块读取/调用本模块）**

| 消费者 | module_id | 调用方式 |
|--------|-----------|---------|
| MCP Servers | MOD-INF-013 | MCP Tool 调用前权限检查 |
| Rollback System | MOD-INF-021 | auto_guard 后验失败触发回滚 |
| Escalation System | MOD-INF-022 | Kill Switch 联动 |
| Pipeline Orchestrator | MOD-TASK_SYSTEM | 任务创建时绑定 Agent 身份 |

**依赖模块详情**

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 | 契约 |
|---------|---------|---------|---------|---------|------|
| zephyr.audit_trail | 硬依赖 | 审计写入 | ≥0.1 | MOD-INF-020 | G-CT-001 |
| zephyr.escalation_engine | 硬依赖 | 升降级权限变更 | ≥0.1 | MOD-INF-022 | G-CT-004 |
| zephyr.agent_spec | 硬依赖 | Skill 加载权限 | ≥0.1 | MOD-INF-019 | G-CT-007 |
| zephyr.a2a_protocol | 硬依赖 | A2A 通信权限 | ≥0.1 | MOD-INF-025 | G-CT-008 |
| zephyr.task_system | 硬依赖 | Agent 生命周期 | ≥0.1 | MOD-TASK_SYSTEM | — |
| zephyr.shared | 硬依赖 | PermissionGuard/AbstractLock | ≥0.1 | MOD-INF-016 | — |
| zephyr.db | 硬依赖 | 权限规则持久化 | ≥0.1 | MOD-DATABASE | — |
| zephyr.gate_engine | 跨线软依赖 | 权限查询(线1→线3) | ≥0.1 | MOD-GATE_ENGINE | — |
| zephyr.runtime | 跨线软依赖 | 运行时注册 | ≥0.1 | MOD-INF-035 | — |
| pydantic | 硬依赖 | BaseModel | V2 | — | — |

### §10.2 依赖图对齐声明

| 对齐项 | 全局依赖图中的声明 | 本蓝图 §10.1 声明 | 一致性 |
|--------|-----------------|-----------------|:-----:|
| GOV-AI-001→RBAC | 线3:治理闭环 | 上游硬依赖 | ✅ |
| RBAC→Audit Trail | 线3:治理闭环 | 上游硬依赖(G-CT-001) | ✅ |
| RBAC→Escalation | 线3:治理闭环 | 上游硬依赖(G-CT-004) | ✅ |
| MCP→RBAC | 线3:治理闭环 | 下游消费(MOD-INF-013) | ✅ |
| Rollback→RBAC | 线3:治理闭环 | 下游消费(MOD-INF-021) | ✅ |

> 不一致 = 漂移。MUST 同步修正。

### §10.3 内部依赖图

**执行顺序依赖**

| 步骤 | 依赖 | 说明 |
|------|------|------|
| L0 ColdStartLock | 无 | 启动时第一个执行 |
| L1 AgentIdentity | L0 | 需要保护路径确认 |
| L1 RBAC Guard | L0 + L1 Identity | 需要身份+保护路径 |
| L2 ABAC Guard | L1 RBAC | 需要角色结果 |
| L3 Input Guard | L2 ABAC | 需要属性结果 |
| L4 Sequence Guard | L3 Input | 需要参数验证结果 |
| L5 Output Guard | L4 Sequence | 需要序列检查结果 |
| L6 Observability | L0-L5 | 需要全部检查结果 |
| L7 Dry-Run | L0-L6 | 需要全部检查+观测结果 |

**数据流依赖**

| 数据 | 生产者 | 消费者 | 流向 |
|------|--------|--------|------|
| PermissionResult | permission_guard | 所有下游模块 | L0→L1→…→L7 |
| AuditEvent | audit_emitter | audit-trail | RBAC→AT |
| rbac_roles.yaml | derive_rbac_roles | rbac_guard/abac_guard | GOV-AI-001→RBAC |
| KillSwitchSignal | immutable_core | escalation-engine | RBAC→ESC |

### §10.4 自动化规格

**是否需要自动化**

| 自动化项 | 需要 | 原因 |
|---------|:---:|------|
| 依赖图对齐检查 | ✅ | 防止蓝图与全局依赖图漂移 |
| 依赖版本兼容性检查 | ✅ | 防止依赖升级破坏接口 |
| 契约一致性检查 | ✅ | 防止 G-CT 契约断裂 |

**如何实现**

| 自动化项 | 实现方式 | 脚本/工具 |
|---------|---------|----------|
| 依赖图对齐检查 | `check_contract_code_drift.py` 扩展依赖图对齐模式 | `scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` |
| 依赖版本兼容性检查 | CI pipeline 中 `pip check` + 接口签名断言 | CI |
| 契约一致性检查 | `validate_load_path_integrity.py` | `scripts/governance/d5_architecture/validators/validate_load_path_integrity.py` |

**触发方式**

| 自动化项 | 触发条件 | 频率 |
|---------|---------|------|
| 依赖图对齐检查 | 蓝图 §10 变更 + CI 每次构建 | 每次变更 |
| 依赖版本兼容性检查 | `requirements.txt` 变更 | 每次变更 |
| 契约一致性检查 | G-CT 契约文件变更 | 每次变更 |

---

## §11 产出物

| # | 产出物 | 绝对路径 | 类型 | 状态 |
|---|--------|---------|------|:---:|
| 1 | 核心实现 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\` | 目录 | 已存在 |
| 2 | 测试代码 | `D:\ZephyrAlpha\tests\agent-rbac\` | 目录 | 已存在 |
| 3 | RBAC 角色配置 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\rbac_roles.yaml` | YAML | 已存在 |
| 4 | 权限钩子配置 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\permission_hooks.yaml` | YAML | 已存在 |
| 5 | 自动维护配置 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\auto_maintenance.yaml` | YAML | 已存在 |
| 6 | 健康仪表盘 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\health_dashboard.yaml` | YAML | 已存在 |
| 7 | 对抗性测试报告 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\adversarial_test_report.yaml` | YAML | 已存在 |
| 8 | 派生脚本 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\derive_rbac_roles.py` | Python | 已存在 |

---

## §12 集成目标

| 集成目标 | 集成方式 | 集成点 |
|---------|---------|--------|
| Gate Engine (MOD-GATE_ENGINE) | 权限检查作为 G0 门禁的前置检查 | `gate_engine.py` → `permission_guard.check()` |
| Task System (MOD-TASK_SYSTEM) | 任务创建时绑定 Agent 身份 + 任务上下文注入 L2 ABAC | `task_repo.create()` → `identity.register()` + ABAC intent |
| Audit Trail (MOD-INF-020) | 每层权限判定 + 序列违规 + Kill Switch 事件写入不可变审计日志 | `permission_guard.check()` → `audit_emitter.emit()` |
| Rollback System (MOD-INF-021) | auto_guard 后验失败 + L4 序列违规后自动回滚 | CI 失败 / 序列阻断 → `rollback_executor.restore()` |
| Circuit Breaker (MOD-INF-022) | L0 Kill Switch 复用熔断器基础设施 | `immutable_core.kill_switch()` → `circuit_breaker.open()` |
| MCP Servers (MOD-INF-013) | MCP Tool 调用前七层权限检查 | `tool_call` → `permission_guard.check()` |
| GOV-AI-001 | 自动派生 rbac_roles.yaml | `derive_rbac_roles.py` → GOV-AI-001 → rbac_roles.yaml |
| Input Sanitizer / LSG（MOD-LLM_SECURITY） | L3 Input Guard 复用 Prompt Injection 检测模式 | L3 危险模式检测 ↔ sanitizer 规则同步 |
| Pre-Commit Gate (GATE-18) | CI 中运行 L7 权限自动化测试 | `.pre-commit-config.yaml` → `test_permissions.py` |
| OpenTelemetry Collector | L6 指标上报 | OTEL exporter → `d2.authz.decision.*` 指标 |
| Hook Registry (NEW) | 横切面A 钩子注册表——pre/post/on_blocked/on_kill_switch 四类钩子 | 所有Guard层 → `permission_hooks.execute_*()` |
| Cache Invalidator (NEW) | 横切面C 推送驱动缓存失效——权限变更→精准失效+降级攻击防护 | `permission_guard.check()` → `cache_invalidator.invalidate()` |
| Emergency Override (NEW) | Owner JIT越权令牌——可临时绕过指定层 | `Action.emergency_token` → `emergency_override_manager.validate()` |
| Owner Dashboard (NEW) | 横切面C 自动更新YAML健康仪表盘——5个关键数字 | 每次check() → `owner_dashboard.update()` |
| RL/Rollback Auth (NEW) | 回滚操作的权限边界——回滚也需过L0不可变核心 | `rollback_executor` → `immutable_core.check(rollback_action)` |
| Inter-Agent Detector (NEW) | L4 跨Agent隐式通信检测——Agent A写→Agent B读协同攻击 | `cross_session_detector` → `audit_trail.query()` + `kill_switch` |
| Ownership Absence (NEW) | Owner超时未审阅→系统自治保守模式 | `ownership_absence_policy` → `permission_guard.degradation()` |

### §12.1 集成验证方法

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-GOVERNANCE 治理域蓝图 | 职责分派 | §2 职责分派表 | 蓝图 §0 分派表与 MOD-GOVERNANCE §2 一致 |
| zephyr.escalation_engine | 升降级权限变更(G-CT-004) | EscalationHandler 权限变更回调 | 集成测试覆盖升降级路径 |
| zephyr.agent_spec | Skill 加载权限(G-CT-007) | SkillLoader 权限验证 | 集成测试覆盖 Skill 加载权限检查 |
| zephyr.a2a_protocol | A2A 通信权限(G-CT-008) | A2ACheck 通信权限验证 | 集成测试覆盖 A2A 权限检查 |
| zephyr.shared | PermissionGuard | PermissionGuard 基类 | 导入验证 + 单元测试 |
| zephyr.db | 权限规则持久化 | RuleStore CRUD | 集成测试覆盖持久化 |
| zephyr.gate_engine | 权限查询(跨线) | GateEngine 权限查询接口 | 集成测试覆盖跨线查询 |

---

## §13 需要更新

修改本蓝图时 MUST 同步更新以下文件：

| # | 文件 | 同步内容 |
|---|------|---------|
| 1 | `src/zephyr/agent-rbac/rbac_roles.yaml` | 角色定义变更 |
| 2 | `src/zephyr/agent-rbac/permission_hooks.yaml` | 钩子配置变更 |
| 3 | `docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml` | GOV-AI-001 权限声明变更 |
| 4 | `src/zephyr/governance/rule_enforcement/` | Gate Engine 集成点变更 |
| 5 | `tests/agent-rbac/test_permissions.py` | 测试用例变更 |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——设计决策带来的已知代价。
> 正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解 | 类型 |
|---|-------------|:---:|:---:|------|------|
| R1 | auto_guard 后验失败率高——频繁自动回滚影响效率 | 中 | 中 | 统计后验失败率，持续优化 auto_guard 规则；失败率 > 20% 的操作降级为 blocked | 风险 |
| R2 | 权限配置漂移——rbac_roles.yaml 与 GOV-AI-001 不一致 | 低 | 高 | CI 门禁校验一致性 + derive_rbac_roles.py 自动派生 | 风险 |
| R3 | 性能开销——七层检查增加延迟 | 中 | 中 | 每层预算严格管控；权限结果缓存（TTL=5min）+ L1 always_allow 跳过 L3-L4 详细检查 | 风险 |
| R4 | 多 IDE 身份冲突——同一文件被不同 IDE 的 Agent 同时修改 | 中 | 高 | 文件锁 + 乐观并发控制 + drift detector 实时检测 | 风险 |
| R5 | L4 Sequence Guard 误报——合法操作序列被误判为攻击 | 中 | 中 | Owner 白名单机制；序列时间窗口可配置；统计误报率持续优化规则 | 风险 |
| R6 | Agent Maturity 升级过慢——严重限制 AI 效率 | 中 | 中 | 自动升级到 L2 Junior（L3+ 仍需审核）；开放 Owner 手动加速升级 | 风险 |
| R7 | Kill Switch 误触发——正常批量操作被熔断 | 低 | 高 | 触发阈值可配置；自动解除 cooldown 机制；Owner 可手动解除 | 风险 |
| R8 | Engine 崩溃时全部 blocked——系统完全不可用 | 低 | 高 | L0 独立可快速恢复；允许 Owner 配置紧急白名单（临时绕过 Engine） | 风险 |
| R9 | AI 绕过权限系统——写入不可变核心路径 | 低 | 极高 | L0 硬编码保护路径；OS 级文件权限兜底（L2b 沙箱 ACL）；pre-commit 检查文件完整性 | 风险 |
| R10 | 权限配置越滚越复杂——1人无法维护 | 高 | 中 | GOV-AI-001单点维护+自动派生+影响分析可视化+自动维护中规则自我修剪（D-018-19） | 风险 |
| R11 | 横向越权——Agent伪造其他Agent身份 | 中 | 极高 | SessionToken签名校验(HMAC-SHA256) + AgentIdentityVerifier + 跨Session伪造检测（D-018-13） | 风险 |
| R12 | 冷启动裸奔——权限配置加载前Agent已操作 | 低 | 极高 | ColdStartLock——启动时全局拒绝直到校验通过（D-018-14） | 风险 |
| R13 | 审计系统被投毒——噪音攻击淹没真实告警 | 中 | 极高 | 告警信噪比监控 + signal_noise_attack熔断触发器 + 异常密度突增自动降权（§2.2） | 风险 |
| R14 | Agent自我复制风暴——绕过Maturity限制 | 中 | 高 | Agent创建权管控 + 权限遗传衰减 + agent_spawn_storm熔断器（D-018-16） | 风险 |
| R15 | 权限缓存陈旧——紧急收紧后旧ALLOW仍生效 | 中 | 极高 | 推送驱动缓存失效——max_latency=100ms替代TTL=5min（D-018-17） | 风险 |
| R16 | 降级攻击——Agent故意触发Partial Failure绕过L4 | 低 | 极高 | 降级源检测——同一Agent触发的降级→立即BLOCKED（§2.3 + D-018-17联动） | 风险 |
| R17 | 熔断器DDoS——恶意Agent触发Kill Switch瘫痪全局 | 低 | 高 | 熔断源隔离——单Agent触发仅阻断该Agent，多Agent触发才全局熔断（§2.2） | 风险 |
| R18 | Agent间隐式合谋——文件系统Covert Channel绕过单Session护栏 | 中 | 高 | 跨Session关联检测 + inter_agent_communication规则（§2.7 cross_session_correlation） | 风险 |
| R19 | 第三方包供应链攻击——Agent安装恶意依赖 | 中 | 极高 | package_install白名单 + blocked_packages:["*"]默认拒绝（§2.6 D-018-09扩展） | 风险 |
| R20 | Owner缺席时无人能干预——auto_guard操作悬空 | 中 | 中 | OwnerAbsencePolicy——超时→保守模式→所有auto_guard降级为blocked（§3 ownership_absence_policy.yaml） | 风险 |
| NC1 | 权限规则形同虚设——AI可以不查注册表直接操作 | — | 极高 | 不实施本模块的后果，非风险 | 负面后果 |
| NC2 | 无法审计"谁做了什么"——审计链断裂 | — | 高 | 不实施本模块的后果 | 负面后果 |
| NC3 | 无运行时强制——权限是"建议"而非"强制" | — | 极高 | 不实施本模块的后果 | 负面后果 |
| NC4 | 多IDE各自为政——无法统一管控 | — | 高 | 不实施本模块的后果 | 负面后果 |
| NC5 | 权限系统自身无保护——AI可以给自己提权 | — | 极高 | 不实施本模块的后果 | 负面后果 |
| NC6 | 只实施L0-L1→无意图感知、无序列阻断、无行为检测 | — | 高 | 部分实施的负面后果 | 负面后果 |
| NC7 | 只实施L0-L5→无可观测性、无测试验证 | — | 高 | 部分实施的负面后果 | 负面后果 |
| NC8 | 实施七层但无横切面→无钩子扩展、无缓存一致性、无自动维护 | — | 中 | 部分实施的负面后果 | 负面后果 |

---

---

<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║  v1.1.0 容量升级蓝图方案 — Capacity Upgrade Blueprint                      ║
║  MOD-INF-018 Agent 身份与权限系统                                          ║
║  面向 10,000 脚本 / 1,500 模块 / 100 AI 并发                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ▸ 本段是面向未来 10,000 脚本 / 1,500 模块 / 100 AI 并发的**容量升级方案**。
  ▸ 写在蓝图最开头，与下方现有设计形成清晰分界线：
      本段以上（含本段）= "未来要升级什么（v1.1.0 容量目标，19 项缺口全量覆盖）"
      本段以下 = "v0.14.0 现有蓝图设计是什么"
  ▸ 施工顺序：先按本方案升级蓝图 → 蓝图评审通过 → 再施工代码。
  ▸ 本方案审阅完成后施工，施工时以本方案为最高优先级。
  ▸ 本蓝图与"容量三塔"（MOD-INF-001 / MOD-GATE_ENGINE / MOD-RESOURCE_OPTIMIZATION_ENGINE）协同：
      ─ MOD-INF-001 v3.0.0  — 管"容量规则 + Error Budget + Token Budget + Kill Switch + 降级链 + SLO"
      ─ MOD-GATE_ENGINE §0      — 管"脚本调度 + 依赖图谱 + 存储分片"
      ─ MOD-RESOURCE_OPTIMIZATION_ENGINE v5.0.0  — 管"系统资源 + 进程/内存/CPU/GPU/缓存/守护线程"
      本蓝图（MOD-INF-018）   — 管"Agent身份 + 权限判定 + 权限配置可伸缩性 + 并发权限检查吞吐 + 脚本级资源授权"
      四者形成 v5.0.0 目标下的**容量四柱体系**：前三柱管"执行层的容量"，本柱管"安全层的容量"。

─── 容量基线 ────────────────────────────────────────────────────────────────

  设计上限：  10,000 脚本 / 1,500 模块 / 100 AI 并发
  当前状态：    268 脚本 /   51 模块 /   1 AI（Owner 单人）+ IDE 内 10+ 并发对话
  放大倍数：    ~37×       ~29×        ~10×(对话数) → ~100×(AI Agent 数)

  脚本数量推导：
    ▸ 当前 51 模块 × 平均 5.25 脚本/模块 = 268 脚本
    ▸ 1,500 模块 × (4~8) = 6,000~12,000 脚本（低：复用增 → 脚本新增少；高：AI 新增专项检测脚本）
    ▸ 最终取整：**10,000 脚本** 作为设计上限，留足余量

  并发数量推导：
    ▸ 100 AI 同时工作，每个 AI 改代码 → 触发增量扫描
    ▸ 每次增量扫描：15-30 个脚本（仅跑与改动相关的脚本）
    ▸ 极端场景：100 AI 同时触发 → 需同时调度 ~1,500 个脚本执行
    ▸ 系统需支持 **40-100 个脚本并发执行**
    ▸ 每次脚本执行内部可能产生 10-50 次工具调用 → 每次调用需经过 RBAC check_permission()
    ▸ **RBAC 层面极限**：100 AI × 20 steps × ~5 tool_calls/step = **10,000 check_permission()/s 峰值**

  执行模式（硬约束）：
    ▸ **增量扫描 = 默认模式**（日常 15-30 脚本，< 1 分钟）
    ▸ **全量扫描 = 可选周检**（10,000 脚本，~3.5 小时）
    ▸ 全量扫描不能是日常操作——必须是可选、可排程的周检功能

  硬件条件：
    ▸ CPU: i7-12700KF（12核20线程）— 保留 4 线程给 OS/IDE → 16 线程可用
    ▸ RAM: 64GB — 保留 8GB 给 OS/IDE → 56GB 可用
    ▸ SSD: 1TB NVMe — I/O 不是瓶颈
    ▸ GPU: RTX 3090 24GB VRAM — 用于 embedding/reranker 脚本

  Agent RBAC 在容量体系中的特殊地位：
    ▸ Agent RBAC 是**所有脚本执行的必经之路**——每个 tool_call 都触发 check_permission()
    ▸ 它是容量链上**最窄的瓶颈点**：其他组件可以排队等待，但权限检查失败=操作被拒
    ▸ 100 AI × 大量 tool_calls → 权限检查吞吐就是系统的**硬天花板**
    ▸ RBAC 自身的配置大小、加载时间、缓存命中率直接影响全局吞吐

─── 现有蓝图覆盖评估（v0.14.0）─────────────────────────────────────────────

  蓝图 v0.14.0 经过十二轮深度交叉审视（94 项决策、209 项盲点全覆盖），在"Agent 安全纵深防御"
  维度达到了**极高覆盖**（~95%），对标 57 个行业框架/论文/事故报告。

  核心优势（不可削弱）：
    ▸ 七层纵深防御（L0-L7）+ 六横切面（A-F）——每条工具调用经过 19 个检查点
    ▸ 单次检查预算 < 1.8ms——在 10+ 并发对话场景下验证通过
    ▸ L0 不可变核心 + OS 级 ACL 双兜底——权限系统自身不可被 AI 修改
    ▸ 冷启动锁 + Kill Switch + Engine 降级——多层熔断保障
    ▸ D-018-59 ConcurrentThroughputOptimizer——per-agent 分片 + Rust 热路径，50 Agent P99<15ms

  评估结论：v0.14.0 蓝图在"安全深度"上达到了**业界领先水平**，但在"Agent 规模伸缩性"
  上存在**系统性设计盲区**（~30% 覆盖），核心原因是所有设计默认假设"10+ 并发对话"而非
  "100 个独立 AI Agent 同时施工"。

  ⚠️ 关键问题：v0.14.0 蓝图把"Agent RBAC"理解为"单个 Agent 操作的安全防线"，
  但当系统中有 100 个 AI Agent 同时运行、每个触发 1,500 个模块中的脚本时，最核心的
  容量挑战是——"1,500 个模块的权限规则怎么加载？100 个 Agent 的身份怎么管理？每个
  Agent 每秒数十次的权限检查怎么不成为全局瓶颈？10,000 个脚本作为新的一类权限资源
  怎么建模？"

─── 缺口总览（本次 v1.0.0 升级聚焦）─────────────────────────────────────────

  现有蓝图在容量维度覆盖了什么、缺了什么：

  维度                       现有设计                      目标设计               状态
  ──────────────────────────────────────────────────────────────────────────────────
  ┌ CAP-R01 权限检查吞吐      D-018-59 分片+乐观锁        100 Agent P99<10ms      ⚠️ 不足
  │ (100 Agent 并发)          +Rust热路径, 50Agent测试      10K check/s 峰值
  ├ CAP-R02 RBAC 配置伸缩     rbac_roles.yaml 单文档       1,500模块分片索引       ❌ 缺失
  │ (1,500 模块)              加载, 无分片/无增量            <1s 增量加载
  ├ CAP-R03 Agent 身份注册表  隐式 per-session 身份         100 Agent 显式注册表    ❌ 缺失
  │ (100 Agent)               Identity 无生命周期管理       身份池+生命周期+GC
  ├ CAP-R04 权限缓存伸缩      Per-agent 分片未规模化验证     1,500模块命中率>95%    ⚠️ 不足
  │ (1,500 模块 × N 脚本)                                   缓存预热+淘汰策略
  ├ CAP-R05 L4 序列护栏伸缩   Per-agent 序列追跡             100 Agent 并行追踪     ⚠️ 不足
  │ (100 Agent 并行)          O(n²) 跨Session关联            索引化跨Agent关联
  ├ CAP-R06 审计日志吞吐      无容量维度设计                 10K 事件/s 写入         ❌ 缺失
  │ (100 AI × 大量操作)                                      分级丢弃策略
  ├ CAP-R07 冷启动伸缩        30s timeout @ 51 模块          30K 规则 < 5s 加载      ❌ 缺失
  │ (1,500 模块 × 20 规则)                                  增量+预编译缓存
  ├ CAP-R08 不可变核心路径    ~20 条 protected_paths         ~200 条 高效匹配       ⚠️ 不足
  │ 匹配 (1,500 模块)         线性遍历 O(n)                   前缀树 O(log n)
  ├ CAP-R09 Session Token     单 Agent场景设计              100 Token 并发管理      ⚠️ 不足
  │ 管理 (100 Agent)          无 Token Pool                   令牌池+过期回收
  ├ CAP-R10 自适应信任预算    Per-agent 5级漏斗             100 Agent全局预算协调    ⚠️ 不足
  │ 全局协调 (D-018-93)      无跨Agent预算感知              $100/day 池化分配
  ├ CAP-R11 多IDE身份联邦     BootstrapCoordinator 3 IDE    10+ IDE实例协同引导     ⚠️ 不足
  │ (10+ IDE 实例)            Phase0 审计日志                IDS令牌+IDE注册表
  ├ CAP-R12 脚本作为权限资源  ❌ RBAC 无"脚本"概念           脚本→权限资源建模       ❌ 缺失
  │ (10,000 脚本)             Tool 粒度 = 最细粒度           脚本注册+脚本级AuthZ
  ├ CAP-R13 权限复杂度预算    D-018-19 僵尸规则+            1,500模块级复杂度        ⚠️ 不足
  │ (1,500 模块)              复杂度预算, 单文档            预算+分片评估
  ├ CAP-R14 RBAC 自身内存     无内存预算设计                 < 500MB 常驻           ❌ 缺失
  │ 占用 (所有规则+缓存)                                    内存水位线+降级
  ├ CAP-R15 与容量三塔联动     △ 提及但无容量维度契约        容量四柱联动契约         ⚠️ 不足
  │                          GateEngine/MOD-032引用         容量SLA + 告警链
  ├ CAP-R16 RBAC自身降级链    ❌ 仅通知外部降级              L7→L0 逐层关停          ❌ 缺失
  │ (10K check/s 过载)        无内部检查深度削减               检查深度自适应
  ├ CAP-R17 权限变更并发一致   ❌ 无                           规则版本号+执行快照     ❌ 缺失
  │ (规则变更 vs 脚本执行)                                   读已提交隔离
  ├ CAP-R18 脚本执行预授权     ❌ 每次tool_call独立检查        脚本级预授权令牌        ❌ 缺失
  │ (批量脚本执行优化)        30脚本×10调用=300次检查          一次性签发+执行期复用
  └ CAP-R19 脚本间权限传播     ❌ 无跨脚本权限链建模           脚本→脚本调用授权链     ❌ 缺失
    (Script→Script AuthZ)                                    权限传播+污染检测

  总计: 10 项 ❌缺失 + 9 项 ⚠️不足 → **在 100 AI 并发/1,500 模块场景下存在 4 个新增高影响缺口（CAP-R16~R19），需在 v1.1.0 补齐**

─── 缺口详细分析 ────────────────────────────────────────────────────────────

  ▶ CAP-R01: 权限检查吞吐——100 Agent 并发下的 check_permission() 峰值

    ┌ 现状: D-018-59 ConcurrentThroughputOptimizer（§3.0.26）设计了 per-agent 分片 +
    │       Rust 热路径 + 乐观序列缓冲。CI 基准测试覆盖：10 Agent P99<3.5ms /
    │       25 Agent P99<8ms / 50 Agent P99<15ms。单次检查预算 < 1.8ms。
    ├ 问题: 基准测试上限仅 50 Agent，未覆盖 100 Agent 场景。
    │       ─ 100 Agent × ~20 steps × ~5 tool_calls/step = **10,000 check/s**
    │       ─ 当前 max_concurrent=40 脚本 → 每个脚本的 tool_call 量未建模
    │       ─ Rust 热路径虽然快，但 L3-L7 仍在 Python 中（GIL 竞争）
    │       ─ PermissionCache 分片数 N=16(cpu_count*4)→当 Agent 数>分片数时退化
    ├ 方案:
    │   RBAC Throughput Scaler（本模块管容量约束，不替代 D-018-59 的优化架构）:
    │     ─ Benchmark 扩展: 100 Agent P99<10ms / 150 Agent P99<20ms / 200 Agent P99<35ms
    │     ─ Shard Scaling: N_SHARDS = max(cpu_count * 4, agent_count * 0.5 → 至少 50 分片 @ 100 Agent
    │     ─ L3-L7 检查分级: 非阻断型检查（L5/L6/L7）→ 异步化/批量化
    │     ─ Backpressure: check_permission() 队列深度 > 500 → 503 Service Unavailable
    │     ─ 容量告警: P99 > 8ms > 5s → 触发 MOD-INF-001 Token Budget 全局收紧
    │     ─ FastPath: L0-L1 的 always_allow 路径（~95% 操作）→ 直接 Rust 返回，跳过 L2-L7
    │   Rust 热路径扩展:
    │     ─ 将 L2 ABAC 的确定性部分（Maturity/TLB/时间窗口）移入 Rust
    │     ─ Python → Rust 调用零拷贝（pyo3 &[u8] 直接操作）
    │   CI 回归: 100 Agent 并发基准测试 → 阻塞 PR merge
    ├ 集成点: 吞吐退化时 → MOD-INF-001 Kill Switch 降级 → MOD-INF-022 熔断
    └ 对标: Envoy Proxy RBAC filter（10M check/s）+ AWS IAM per-account limit（40K req/s）

  ▶ CAP-R02: RBAC 配置伸缩性——1,500 模块的权限规则加载与索引

    ┌ 现状: rbac_roles.yaml 作为单文档从 GOV-AI-001 派生，全量加载到内存。
    │       D-018-03 GOV-AI-001 → derive_rbac_roles.py → rbac_roles.yaml。
    │       当前 ~51 模块 × ~20 条规则/模块 ≈ 1,000 条规则。
    ├ 问题: 1,500 模块 × ~20 条规则 = **30,000 条规则**，单 YAML 文档 ≈ 3-5MB。
    │       ─ 全量解析+加载: 当前 ~50ms → 30K 规则估计 1.5-3s
    │       ─ L1 RBAC 每次 check 需遍历规则匹配——O(n) 线性遍历 30K 条 → ~100ms
    │       ─ 冷启动锁 30s timeout 被单车加载吃掉 10%
    │       ─ 权限变更（D-018-17 推送失效）需重载整份文档——缓存全量腾空
    ├ 方案:
    │   RBAC Config Sharding & Indexing:
    │     ─ 分片存储: rbac_roles_{module_id}.yaml × 1,500 文件 → 按需加载
    │     ─ Prefix Trie 索引: role → action → resource 三级 Trie → O(log n) 查找
    │     ─ 增量加载: 启动时仅加载 L0 immutable_core + 活跃模块的规则
    │     ─ 懒加载: 首次访问某模块的权限规则时 → 加载该模块分片
    │     ─ 编译缓存: 预编译 Trie 为二进制 pickle/mmap → 重启 < 100ms
    │     ─ 推送粒度: 单模块规则变更 → 仅失效该模块分片缓存
    │   Config Size Budget:
    │     ─ per-module 规则上限: 30 条（超出需 Owner 审批）
    │     ─ 模块间重复规则: 提取为 shared_rules → 去重
    │     ─ GOV-AI-001 派生分片: derive_rbac_roles.py → 支持 --module 参数单模块派生
    ├ 集成点: D-018-03 派生逻辑 + D-018-17 缓存失效 需适配分片
    └ 对标: Kubernetes RBAC per-namespace Role + ClusterRole 分层

  ▶ CAP-R03: Agent 身份注册表——100 个独立 AI Agent 的显式身份管理

    ┌ 现状: Agent Identity（§2.13）定义为 per-session 的隐式身份：
    │       agent_id / maturity_level / session_token / ide_source。
    │       D-018-64 SessionIdentityBinding 解决跨会话身份伪造。
    │       当前：Owner + 10+ 并发对话 = ~10 个并发 identity。
    ├ 问题: 100 AI Agent = 100 个独立身份，且每个身份有独立 session。
    │       ─ 无 Agent 生命周期: 创建/暂停/恢复/销毁 → 不知道哪些 Agent 活着
    │       ─ 无 Agent 注册表: 无法枚举"系统中现在有多少个 Agent 在工作"
    │       ─ 无 Agent 配额: 无法限制"最多多少个 Agent 同时运行"
    │       ─ Session 膨胀: 100 Agent × 每 Agent 可能多 session → 200+ token
    │       ─ D-018-16 Agent 创建权——遗传衰减链在 100 Agent 下爆炸
    ├ 方案:
    │   AgentRegistry（显式 Agent 身份与服务发现）:
    │     ─ Agent 注册: register_agent(agent_id, maturity, ide, parent_id)
    │     ─ Agent 槽位: max_agents = 100（可配，默认 100）
    │     ─ Agent 生命周期: CREATED → ACTIVE → IDLE(5min无操作) → PAUSED(30min) → TERMINATED
    │     ─ Heartbeat: 每个 Agent 每 30s 上报心跳 → 超时 90s → 标记 STALE → 自动释放
    │     ─ Agent Pool: 100 槽位中保留 10 个给 P0 紧急 Agent（Owner 直接签发）
    │     ─ 遗传衰减上限: 最多 3 层派生，超过拒绝创建
    │   Agent Quota Enforcement:
    │     ─ max_concurrent_agents = 100 → 达到上限返回 429
    │     ─ per-IDE 上限: max 30 agents/IDE（防单一 IDE 垄断）
    │     ─ Agent 饥饿防护: FIFO 等待队列 → 最长等待 60s 超时
    ├ 集成点: D-018-16 Agent 创建权 ← 新增 max_agents / per_ide_quota
    └ 对标: Kubernetes Node/scheduler 的 Pod 注册 + Heartbeat + 驱逐机制

  ▶ CAP-R04: 权限缓存伸缩——1,500 模块下的缓存命中率

    ┌ 现状: D-018-59 per_agent_cache_sharding × hash(agent_id) % N_SHARDS。
    │       每个分片独立读写锁。当前分片数 = max(16, cpu_count*4) = 最多 80。
    │       缓存条目: 未定义上限，依赖 LRU。
    ├ 问题: 1,500 模块 × ~20 规则/模块 → 30,000 个唯一 permission decision 模式。
    │       ─ 100 Agent × ~10 check/s × 60s = 60,000 check/min → 缓存命中率关键
    │       ─ 权限变更推送 D-018-17 在 1,500 模块下：单模块变更 → 仅失效该模块缓存
    │         但当前设计是"推送驱动全局失效"的设计方向
    │       ─ 分片数 < Agent 数时退化——80 分片 vs 100 Agent 仍有轻微冲突
    ├ 方案:
    │   Scalable PermissionCache:
    │     ─ 自适应分片: N_SHARDS = max(cpu_count*4, ceil(agent_count/2)) → 100 Agent = 50 分片+
    │     ─ 分层缓存: L0-L1 规则（不可变）→ 无 TTL 永久缓存 / L2-L7（可变）→ TTL=5min
    │     ─ 缓存预热: 启动时预计算 常访问规则 的判定结果 → 减少冷启动 miss
    │     ─ 淘汰策略: LRU + LFU 混合 → max_entries = 50,000 per shard
    │     ─ 命中率 SLO: > 95% (warm) / > 80% (cold start 60s内)
    │     ─ D-018-17 失效粒度: from 全局推送 → 模块级分片失效
    ├ 集成点: D-018-17 缓存一致性 需从全局推送升级为模块级分片失效
    └ 对标: Redis Cluster per-slot 缓存 + Envoy RBAC filter cache

  ▶ CAP-R05: L4 Sequence Guard 伸缩——100 Agent 并行序列追踪

    ┌ 现状: §2.7 L4 Sequence Guard 追踪 per-agent 操作序列，forbidden_sequences 规则。
    │       跨 Session 关联检测（cross_session_correlation）+ Agent 间隐式通信检测。
    │       序列追踪数据结构: per-agent in-memory sequence_buffer。
    ├ 问题: 100 Agent 同时活跃 × 每 Agent 20 步操作链 = 2,000 条活跃序列。
    │       ─ 跨 Agent 关联: 100 Agent → O(n²) = 4,950 对两两关联 → 实时不可行
    │       ─ 涌现行为检测（Multi-Agent Emergent Behavior）: 100 Agent 组合爆炸
    │       ─ SequenceBuffer 写锁竞争: D-018-59 乐观锁 CAS → 100 Agent × CAS 频率高
    │       ─ 内存占用: 2,000 序列 × 20 步 × ~200B/步 = 8MB → 可接受，但需 GC
    ├ 方案:
    │   Sequence Guard at Scale:
    │     ─ 惰性跨Agent关联: 仅在"同模块/同文件/同资源"时检测 → 索引化
    │     ─ Agent间隐式通信: CovertChannel → 按资源路径哈希 → Agent Pair 分组
    │       → 仅检测共享同一资源的 Agent Pair
    │     ─ 涌现行为: 不实时分析所有 Agent Pair → 采样 + 统计基线异常
    │     ─ SequenceBuffer: 每 Agent 独立无锁环形缓冲区（88 bytes × 256 entries）
    │       → 零锁竞争，只有跨 Agent 关联时读取
    │     ─ GC: 每 60s 清理 INACTIVE Agent 的序列缓冲
    │     ─ 容量预算: 单个 Agent L4 检查 < 0.5ms @ 2,000 序列总量
    ├ 集成点: 涌现行为检测可降级——高负载时关闭跨Agent分析，仅保留单Agent序列
    └ 对标: AWS GuardDuty 跨账户威胁分析（索引化 + 采样，非 O(n²) 全量）

  ▶ CAP-R06: 审计日志吞吐——100 AI 大规模操作的审计写入

    ┌ 现状: §2.9 L6 Observability + D-018-42 审计日志 Merkle Tree 完整性。
    │       每次 check_permission() → audit_emitter.emit() → raw_events.jsonl 写入。
    │       D-018-50 审计日志注入防护。D-018-42 Merkle Proof <100ms。
    ├ 问题: 10,000 check/s × 每事件 ~500B = **5MB/s 审计日志写入** → 17GB/小时。
    │       ─ NVMe 1TB 可写 ~58 小时 → 周级别的全量日志不可行
    │       ─ Merkle Tree 每秒更新——10,000 条目/s 的 Merkle proof 计算开销
    │       ─ 日志查询（L4 跨 Agent 关联）→ 线性扫描 17GB 不可行
    ├ 方案:
    │   Audit Log at Scale:
    │     ─ 分级写入: L0-L1 阻断→全量写入 / L2-L3 警告→采样 10% / L4-L7 通过→仅计数
    │     ─ 批量写入: 100ms 缓冲 → 批量 fsync → IOPS 从 10K/s 降到 100/s
    │     ─ Merkle 分级: 仅 L0-L1 事件参与 Merkle 链 / L2 以上独立链
    │     ─ 日志轮转: 每小时 → JSONL→Parquet 压缩（10:1 压缩比）
    │     ─ 保留策略: 全量 24h + 采样 7d + 摘要 90d
    │     ─ 游标查询: 按 agent_id + timestamp 的 B-Tree 索引 → O(log n) 检索
    │   L4 跨 Agent 关联的审计查询:
    │     ─ 从 raw_events.jsonl → SQLite/Parquet 索引 → O(log n) 而非 O(n)
    ├ 集成点: MOD-INF-020 Audit Trail ← 继承分级写入策略
    └ 对标: AWS CloudTrail（分级）+ Google Chronicle（压缩存储）

  ▶ CAP-R07: 冷启动伸缩——1,500 模块下的权限配置加载

    ┌ 现状: D-018-14 ColdStartLock（§2.16）：启动时全局拒绝 → rbac_roles.yaml
    │       加载+hash校验通过 → 释放锁。timeout=30s，超时→maintenance_mode。
    │       当前 ~1,000 条规则 → 加载 < 100ms。
    ├ 问题: 30,000 条规则 + YAML 解析 + Trie 构建 + 完整性校验 → 预估 3-5s。
    │       ─ 30s timeout 足够，但启动等待 3-5s 用户感知差
    │       ─ 全量校验 1,500 个分片文件的 hash——I/O 开销
    │       ─ 启动后缓存冷 → 前 60s 命中率 < 80%
    ├ 方案:
    │   Scalable Cold Start:
    │     ─ 预编译缓存: rbac_config.cache（pickle/mmap）→ 启动直接 mmap → < 100ms
    │     ─ 分片校验: 仅校验 L0 immutable_core（必须）+ 活跃模块分片（按需）
    │     ─ 后台预热: L0-L1 加载完成 → 释放冷启动锁 → 后台加载剩余分片
    │     ─ Timeout 自适应: timeout = max(30s, rule_count / 1000 * 5s)
    │     ─ 启动指标: agent-rbac.boot.duration.total / per_shard / cache_warmup
    │   Staged Unlock:
    │     ─ Phase 0: L0 校验通过 → 释放 L0（Agent 可执行安全操作）
    │     ─ Phase 1: L1-L2 加载 → 释放全量（< 1s）
    │     ─ Phase 2: 后台加载 L3-L7 规则 → 无阻塞
    ├ 集成点: D-018-14 冷启动锁 从二元锁升级为分级释放
    └ 对标: Envoy hot restart（不中断流量热更新）

  ▶ CAP-R08: L0 不可变核心路径匹配——1,500 模块的保护路径伸缩

    ┌ 现状: §2.1 L0 protected_paths 列表（~20 条 glob 模式）。always_blocked
    │       操作列表（~14 条）。每次 tool_call → 遍历匹配 protected_paths × glob。
    │       L0 检查预算 < 0.05ms。
    ├ 问题: 1,500 模块 → protected_paths 可能膨胀到 200+ 条（每个模块可能有
    │       自己的 blueprint / config / security 路径需要保护）。
    │       ─ 遍历 200 条 glob → ~0.5ms → 超出 L0 0.05ms 预算 10 倍
    │       ─ always_blocked 操作从 14 → 30+ 条 → 同理
    ├ 方案:
    │   ProtectedPath Index:
    │     ─ Glob → Prefix Trie 编译: 预编译所有 glob 为 Trie → 单次 O(log n) 匹配
    │     ─ 分层索引: 按路径前缀分桶（src/ / docs/ / config/ / data/）→ 命中对应桶
    │     ─ always_blocked 操作: HashMap → O(1) 查找
    │     ─ 预算坚守: L0 检查预算保持 < 0.05ms，通过编译为确定性决策（Rust 侧）
    │   ProtectedPath 爆炸管控:
    │     ─ Per-module protected_paths 通过模块的 .module_protection.yaml 声明
    │     ─ 自动合并到全局 protected_paths → 去重（同一前缀合并为更短规则）
    │     ─ 上限: max_protected_paths = 500 → 超出触发 Owner 审批
    ├ 集成点: L0 immutable_core 从硬编码列表升级为编译索引
    └ 对标: .gitignore 的 git check-ignore（pattern Trie）+ SELinux 策略编译

  ▶ CAP-R09: Session Token 管理——100 Agent 的 Token 并发生命周期

    ┌ 现状: AgentIdentity.session_token（HMAC-SHA256 签名）+ D-018-58
    │       GracefulTokenRenewal（在途过期保护）。单 Agent 场景简单。
    ├ 问题: 100 Agent × 多 session（长对话可能重连）→ 200+ 活跃 Token。
    │       ─ Token 签名验证: HMAC-SHA256 每次 ~1μs → 100 并发不是瓶颈
    │       ─ Token 过期管理: 200 个 token 的 GC → 需要过期扫描
    │       ─ D-018-64 SessionIdentityBinding: 每个 Agent 的 token 持久化
    ├ 方案:
    │   TokenPool:
    │     ─ Token 槽位: max_tokens = 500 → 超限拒绝新 session（429）
    │     ─ 分层 Token: 长期 identity_token（Agent 生命周期）+ 短期 session_token（会话）
    │     ─ GC 定时器: 每 60s 扫描过期 token → 批量清理
    │     ─ Token 用量仪表盘: active_tokens / expired_tokens / renewal_rate
    │     ─ 异常检测: 同一 Agent > 5 个并发 token → 标记 UNUSUAL
    ├ 集成点: D-018-58 GracefulTokenRenewal + D-018-64 SessionIdentityBinding
    └ 对标: OAuth2 token management（access_token + refresh_token 双层）

  ▶ CAP-R10: 自适应信任预算全局协调——100 Agent 共享 $100/day

    ┌ 现状: D-018-93 AdaptiveTrustBudget（§3.0.60）：per-Agent 五级权限漏斗 +
    │       KL 散度行为漂移 + 被动/主动补充。per-Agent 独立计算信任分。
    │       但全局 Token Budget 在 MOD-INF-001 中为 $100/day。
    ├ 问题: 100 Agent 可能 10 分钟耗光一天预算。
    │       ─ D-018-93 的 per-Agent 预算无全局协调——100 Agent × 各自花销
    │       ─ Trust Budget 消耗路径: check_permission() 本身不计 Token
    │         但 Agent 的 tool_call 消耗 Token Budget → RBAC 间接受影响
    │       ─ 最严重场景: 100 Agent × 10 tool_calls/min × 1000 token/call
    │         = 1M token/min → $100 几分钟耗尽
    ├ 方案:
    │   Global Trust Budget Coordinator:
    │     ─ 全局预算池: $100/day → 按 Agent 优先级分配
    │     ─ P0 保留: 20% 预算永远保留给 P0 Agent（Owner 直接签发的紧急 Agent）
    │     ─ 速率限制: 单 Agent 最大 2% 全局预算 → 超额自动降级
    │     ─ 预算水位告警: 50%/70%/90% → 自动收紧所有 Agent 权限漏斗
    │     ─ Trust Budget ↔ Permission Level 联动:
    │       >70% 预算消耗 → 所有 Agent 降一级漏斗（如 Funnel5→Funnel4）
    │       >90% 预算消耗 → 所有非 P0 Agent 降至 Funnel1（仅读）
    │     ─ Per-Agent 预算: agent_budget = global_budget * (agent_priority / sum_priorities)
    ├ 集成点: D-018-93 AdaptiveTrustBudget + MOD-INF-001 Token Budget
    └ 对标: AWS Budgets（全局池+per-account 限额）+ GCP Quota

  ▶ CAP-R11: 多 IDE 身份联邦——10+ IDE 实例的协同引导

    ┌ 现状: D-018-55 BootstrapCoordinator（§3.0.22）：多 IDE 并发施工期最小保护。
    │       Phase 0 审计日志 + 施工后对比。设计假设 3 IDE（TRAE/Cursor/RooCode）。
    ├ 问题: 100 AI Agent 可能分布在 10+ IDE 实例（TRAE × 3 / Cursor × 3 /
    │       RooCode × 2 / Claude Code × 2 / Windsurf × 1 / 其他）。每个 IDE 实例
    │       可能承载 5-15 个 Agent。
    │       ─ 每个 IDE 需要独立的 RBAC 施工令牌
    │       ─ IDE 实例可能不在同机（未来分布式）→ 网络通信
    ├ 方案:
    │   IDE Federation at Scale:
    │     ─ IDE Registry: 每个 IDE 实例注册 → ide_instance_id + host + port + agents[]
    │     ─ IDE 配额: max_ide_instances = 20 → 超限排队
    │     ─ Per-IDE 令牌: 不同于 Agent Token——IDE 级引导令牌
    │     ─ IDE Liveness: 心跳 10s → 超时 30s → 标记 STALE → Agent 迁移/暂停
    │     ─ Bootstrap 审计: 所有 IDE 实例的 Phase 0 操作统一收集
    │   Future-Proof: IDE 注册表设计为可扩展到分布式（预留 network_identity 字段）
    ├ 集成点: D-018-55 BootstrapCoordinator + AgentRegistry
    └ 对标: Kubernetes kubelet 注册 + Node 心跳

  ▶ CAP-R12: 脚本作为一级权限资源——10,000 脚本的 RBAC 建模

    ┌ 现状: RBAC 的资源模型只有 file / tool / config / env / package 等。
    │       **没有"脚本"（script）这个资源类型**。脚本的执行/修改/创建
    │       被归入 file 或 tool 的权限范畴。
    ├ 问题: 10,000 个脚本需要被管理——哪些脚本可以修改哪些文件？
    │       哪些脚本可以调用哪些其他脚本？脚本的权限边界在哪？
    │       ─ 新脚本的注册：AI 创建新脚本时 → RBAC 需要知道"这个脚本有没有权限做X"
    │       ─ 脚本依赖链：Script A → Script B → 权限传播链 → 当前无建模
    │       ─ 脚本分类授权：gate_check 类脚本 vs audit 类脚本 → 不同权限
    ├ 方案:
    │   Script as Resource:
    │     ─ script 作为一级资源类型加入 RBAC 模型
    │     ─ 脚本权限动作: script:execute / script:modify / script:create / script:delete
    │     ─ 脚本角色: script_role = gate_check | audit | drift | telemetry | code_quality
    │     ─ 脚本-脚本调用权限: Script A 能否调用 Script B → 依赖图授权
    │     ─ 脚本-文件权限: Script 只能操作已声明的 depends_files[] 中的文件
    │     ─ 脚本权限声明: 每个脚本头部 YAML → script_id / module_id / allowed_resources[]
    │   Integration with ScriptRegistry (MOD-INF-001/GateEngine):
    │     ─ 脚本注册时 → 自动创建 RBAC script identity
    │     ─ 脚本执行前 → GateEngine 调用 RBAC check_script_permission()
    │     ─ 脚本默认最小权限: 新脚本注册 → 仅 read self → Owner 手动授权升权
    ├ 集成点: MOD-GATE_ENGINE GateEngine §0 ScriptRegistry + MOD-INF-001 ScriptScheduler
    └ 对标: AWS Lambda execution role（每个 Lambda 有独立 IAM Role）

  ▶ CAP-R13: 权限复杂度预算——1,500 模块级的规则治理

    ┌ 现状: D-018-19 自动维护（§2.21）：僵尸规则检测 + 权限复杂度预算 +
    │       Owner 健康仪表盘。规则评估基于全量 rbac_roles.yaml。
    ├ 问题: 1,500 模块 → 30,000 条规则。僵尸规则检测的扫描时间、复杂度预算
    │       计算的时间复杂度是 O(n²)——"规则 A 是规则 B 的子集？"
    │       ─ 30,000 条规则 → O(n²) = 900M 对比较 → 不可行
    │       ─ 复杂度预算: 30,000/(5 metrics) = ?
    ├ 方案:
    │   Complexity Budget at Scale:
    │     ─ 分片评估: per-module 独立计算复杂度 → 仅对同模块规则做子集检测
    │     ─ 跨模块冲突: 仅检测 role 重叠的模块间规则 → 索引化
    │     ─ 预算公式: per_module_budget = 30 规则 / max_complexity_score = 100
    │     ─ 僵尸检测: 基于 Usage Counter → 30 天 0 命中 → 标记 ZOMBIE
    │     ─ 全局预算: total_rules ≤ 50,000 / total_roles ≤ 500 / total_actions ≤ 200
    ├ 集成点: D-018-19 自动维护 需分片化执行
    └ 对标: Open Policy Agent (OPA) 策略静态分析（per-package 而非 global）

  ▶ CAP-R14: RBAC 自身内存占用——所有规则 + 缓存 + 索引的常驻内存

    ┌ 现状: 蓝图无内存占用预算设计。D-018-59 分片 + Rust 热路径对内存无约束。
    ├ 问题: 30,000 规则 × ~1KB（规则文本+索引）= ~30MB
    │       ─ PermissionCache: 50,000 entries × ~200B = 10MB × 50 分片 = ~500MB
    │       ─ SequenceBuffer: 100 Agent × 256 entries × 88B = ~2.2MB
    │       ─ AgentRegistry: 100 Agent × ~2KB = 0.2MB
    │       ─ Audit buffer: 100ms × 10K events/s × 500B = ~500KB
    │       ─ 总计: ~550MB → **超出考虑的 RAM Budget（56GB 中的 ~1%）**
    │       ─ 但核心问题是: 550MB 中缓存占 500MB → 缓存膨胀
    ├ 方案:
    │   Memory Budget & Watermark:
    │     ─ 总内存预算: 1GB → 占可用 56GB 的 1.8%
    │     ─ 水位线: GREEN < 500MB / YELLOW 500-800MB / RED > 800MB
    │     ─ YELLOW: 缩小缓存 → max_entries 减半
    │     ─ RED: 清除所有非 L0-L1 缓存 + 强制 GC + 暂停新 Agent 注册
    │     ─ 缓存条目 TTL: warm_cache TTL=5min → YELLOW 时 TTL=1min
    │     ─ 内存指标: agent-rbac.memory.bytes (total/cache/index/audit)
    ├ 集成点: MOD-RESOURCE_OPTIMIZATION_ENGINE ResourceOptimizationEngine → 订阅内存水位告警
    └ 对标: JVM -Xmx + GC tuning + Redis maxmemory-policy

  ▶ CAP-R15: 与容量三塔的联动契约——Agent RBAC 在容量体系中的角色

    ┌ 现状: §4 集成矩阵列出了 Gate Engine / Task System / Audit Trail 的集成点。
    │       D-018-59 ConcurrentThroughputOptimizer 无容量维度的外部 SLA。
    ├ 问题: MOD-INF-001 的 v3.0.0 容量升级已定义了 CAP-G01~CAP-G13（脚本/调度/
    │       并发维度），但 MOD-INF-018 没有对应的容量承诺。
    │       ─ 容量三塔的 SLA 受 RBAC 检查速度直接影响
    │       ─ MOD-INF-001 SLO "增量扫描 < 1min" → 其中 15-30 脚本 × 10 tool_calls
    │         × 1.8ms = 0.27-0.54s → 可接受。但在 100 AI 并发退化为 50ms → 15-75s
    │       ─ Token Budget 熔断（MOD-INF-001）需要 RBAC 权限漏斗联动
    ├ 方案:
    │   Capacity Four-Pillar Contract（容量四柱联动契约）:
    │     ─ RBAC 容量 SLA:
    │       · check_permission() P50 < 0.5ms / P99 < 5ms @ 100 Agent 并发
    │       · PermissionCache 命中率 > 95% (warm)
    │       · 冷启动释放 < 1s（L0-L1）+ < 5s（全量）
    │       · 审计日志写入 < 0.5ms p99
    │     ─ 联动触发:
    │       · RBAC P99 > 10ms → 通知 MOD-INF-001 收紧 Token Budget（全局降级）
    │       · RBAC 内存 YELLOW → 通知 MOD-RESOURCE_OPTIMIZATION_ENGINE 准备资源回收
    │       · GateEngine 调度队列 > 500 → 通知 RBAC 启用 FastPath（跳过 L2-L7）
    │     ─ 联合告警链:
    │       · MOD-INF-018 → MOD-INF-001 → MOD-INF-022（Kill Switch）
    │       · 三层告警联动: RBAC 退 → 容量规则收紧 → 全局熔断
    ├ 集成点: MOD-INF-001 §0 容量基线 + MOD-RESOURCE_OPTIMIZATION_ENGINE 资源水位
    └ 对标: AWS Well-Architected Pillar 间的依赖关系建模

  ▶ CAP-R16: RBAC 自身多级降级链——10K check/s 过载时的检查深度自适应削减

    ┌ 现状: CAP-R01 设计了 FastPath（L0-L1 always_allow 路径跳过 L2-L7），
    │       CAP-R15 设计了 RBAC P99>10ms → 通知 MOD-INF-001 收紧 Token Budget。
    │       但 RBAC 自身**没有内部分级降级机制**——当吞吐过载时，
    │       只能"通知别人降级"，自己无法主动削减检查深度。
    ├ 问题: 100 AI 并发 × 10K check/s 峰值场景下：
    │       ─ P99 延迟从 5ms 退到 50ms → FastPath 跳过 95% 操作 →
    │         但剩余的 5%（500 check/s）仍需走全链路 L0-L7
    │       ─ 如果这 500 check/s 中包含重度 L4 序列检测（跨 Agent 关联），
    │         单个 check 可能 > 20ms → 进一步退化
    │       ─ 极端场景：100 AI 同时触发紧急操作（P0）→ 所有操作都需要 L0-L7
    │         → FastPath 不起作用 → P99 飙升 → 雪崩
    │       ─ RBAC 没有"主动关停非关键层"的能力——永远全链路检查
    ├ 方案:
    │   RBAC Degradation Levels（内部降级链，比外部 Kill Switch 更细粒度）:
    │     ─ 降级触发条件:
    │       ─ Level-1 条件: P99 > 8ms 持续 30s
    │       ─ Level-2 条件: 队列深度 > 300 或 P99 > 15ms 持续 10s
    │       ─ Level-3 条件: 队列深度 > 500 或 P99 > 30ms 持续 5s
    │     ─ 降级策略（逐层削减——关停非关键检查，保留核心安全）:
    │       ─ DEGRADED-1 (轻度过载):
    │         · 关停 L7（测试与模拟——对抗性测试/混沌测试非执行路径）
    │         · L6 审计完整写入 → 采样写入（10% 比例）
    │         · L5 输出护栏 → 仅检查 PII/凭证（跳过大小截断+合成泄漏）
    │         · 预估恢复: P99 从 15ms → 8ms（绕过 3 层最高开销检查）
    │       ─ DEGRADED-2 (中度过载):
    │         · 关停 L7 + L6 + L5
    │         · L4 序列护栏 → 仅 per-agent 序列（跳过跨 Agent 关联+涌现行为）
    │         · L3 参数护栏 → 仅 file/protected_paths 检查（跳过 package_install/
    │           network_target/env 检查）
    │         · 预估恢复: P99 从 30ms → 5ms
    │       ─ DEGRADED-3 (重度过载——接近崩溃):
    │         · 关停 L3-L7 全部
    │         · 仅保留 L0（不可变核心）+ L1（RBAC）+ L2（ABAC 核心属性）
    │         · L2 ABAC 仅检查 Maturity + Resource Sensitivity（跳过时间窗口+TLB+意图感知）
    │         · 预估恢复: P99 从 50ms → 2ms
    │     ─ 恢复策略:
    │       ─ 降级后持续监控 P99，当 < 阈值 × 0.5 持续 60s → 逐级回升
    │       ─ DEGRADED-3 → DEGRADED-2（60s 稳定后）→ DEGRADED-1 → FULL
    │       ─ 回升时每级间隔 60s → 避免振荡（thrash prevention）
    │     ─ Owner 可感知:
    │       ─ 每级降级/回升 → EventBus 发布 capacity.rbac.degradation_level
    │       ─ Dashboard 实时显示当前降级级别 + 关停的检查层
    │       ─ DEGRADED-3 > 5min → MOD-INF-022 Kill Switch 全局熔断
    │   Integration with CAP-R01 FastPath:
    │     ─ FastPath 是"静态优化"（对 95% always_allow 操作绕过 L2-L7）
    │     ─ Degradation 是"动态削减"（对 5% 需要全链路检查的操作削减深度）
    │     ─ 两者互补: FastPath 减少总量, Degradation 减少单次深度
    ├ 集成点: CAP-R01 FastPath + CAP-R15 四柱联动 + MOD-INF-022 Kill Switch
    └ 对标: Envoy overload manager（分水位线降级）+ AWS Lambda throttling levels

  ▶ CAP-R17: 权限变更在脚本执行中的并发一致性——规则热更新 vs 活跃脚本

    ┌ 现状: D-018-17 缓存一致性设计为"推送驱动全局失效"——Owner 修改规则 →
    │       推送通知 → 全量缓存腾空。D-018-03 GOV-AI-001 派生 rbac_roles.yaml。
    │       当前 ~10 并发对话场景 → 缓存失效窗口 ~100ms → 可接受。
    ├ 问题: 100 AI 并发 + 40 脚本并发执行场景下：
    │       ─ 脚本可能执行 30s-300s（CAP-G08 timeout=300s），在此期间
    │         Owner 收紧某模块权限规则 → 部分脚本看到旧规则（ALLOW），
    │         部分看到新规则（DENY）→ 同一扫描批次内判定不一致
    │       ─ 具体场景:
    │         · 脚本 A 执行到 step 5 时规则被收紧 → step 6 突然被拒 →
    │           脚本 A 中途失败（不一致的中间状态）
    │         · 脚本 B 在规则变更后启动 → 看到的是新规则
    │         · 增量扫描报告中: 脚本 A 失败 + 脚本 B 通过 →
    │           Owner 无法判断是代码问题还是规则变更导致
    │       ─ CAP-R02 的分片存储（rbac_roles_{module_id}.yaml）带来新的
    │         一致性问题: 30,000 条规则分布在 1,500 个分片文件中 →
    │         规则变更时无法原子性地更新所有相关分片
    ├ 方案:
    │   Rule Change Consistency Model:
    │     ─ 隔离级别: Read-Committed（读已提交）
    │       · 正在执行的脚本 → 使用**执行开始时**的规则快照
    │       · 新启动的脚本 → 使用最新规则版本
    │       · 规则变更不影响已经在跑的脚本——避免中途失败
    │     ─ 规则版本号:
    │       ─ 全局单调递增: rbac_config_version（uint64，每次变更 +1）
    │       ─ 每个 check_permission() 调用携带 config_version
    │       ─ RuleChangeLog: (version, timestamp, changed_modules[], changed_rules[])
    │     ─ 脚本执行快照:
    │       ─ ScriptScheduler 启动脚本前 → 获取当前 config_version → 作为脚本
    │         执行上下文的一部分（script_execution_snapshot_version）
    │       ─ 脚本执行期间所有 RBAC 检查 → 携带该 version → 使用对应版本规则
    │       ─ 脚本执行结束 → 快照版本释放（引用计数递减）
    │     ─ 规则版本保留策略:
    │       ─ 保留最近 3 个版本（当前 + 上一版 + 上上一版）
    │       ─ 超过 3 个版本的旧规则 → 等待所有引用该版本的脚本完成 → 释放
    │       ─ 最大保留时间: 300s（脚本最长执行时间）→ 超时强释放
    │     ─ 分片规则变更的原子性:
    │       ─ 单模块规则变更: 更新 1 个分片 → 版本号 +1 → 原子、瞬间完成
    │       ─ 跨模块规则变更: 批量更新 N 个分片 → 版本号一次性 +1 →
    │         中间状态不可见（变更要么全生效要么全不生效）
    │       ─ 实现: 分片更新写入临时目录 → 一致性校验 → 原子 rename
    │     ─ 一致性 SLO:
    │       ─ rule_change_propagation_latency < 100ms（从 Owner 保存到新脚本可见）
    │       ─ concurrent_execution_inconsistency_rate = 0（活跃脚本中途不切换规则）
    │       ─ config_version_snapshot_leak = 0（脚本结束 300s 后快照必释放）
    ├ 集成点: CAP-R02 分片存储 + CAP-G02 ScriptScheduler（快照版本传递）
    └ 对标: PostgreSQL Read-Committed Isolation + Kubernetes ConfigMap immutable
          versioning

  ▶ CAP-R18: 脚本执行预授权批量通道——30 脚本增量扫描的权限开销优化

    ┌ 现状: CAP-R01 FastPath 针对 always_allow 操作（~95%）做优化。
    │       CAP-R12 将 script 定义为一级资源类型，支持 script:execute 等权限动作。
    │       当前: 每个 tool_call → check_permission() → 独立判定 → 独立审计。
    │       这个模型在单 Agent / 少量脚本场景下足够。
    ├ 问题: 增量扫描触发 30 个脚本 × 每脚本 10 次 tool_call = 300 次权限检查。
    │       ─ 100 AI 并发 → 每个 AI 可能不同时触发 → 但高峰期仍可能有
    │         ~5 个增量扫描批次并发 = 5 × 300 = 1,500 check/min → 不算瓶颈
    │       ─ **真正的问题是**: 每个 tool_call 独立走 L0-L7 全链路 →
    │         即使 FastPath 处理了 95% 的操作，剩余 5%（15 次/批次）仍需要
    │         ~1.8ms × 15 = 27ms 额外开销 → 在 40 脚本并发下累积
    │       ─ 脚本执行**天然适合预授权**:
    │         · 脚本身份明确（script_id + module_id）
    │         · 脚本的作用范围声明在注册时（allowed_resources[] / depends_files[]）
    │         · 脚本执行窗口短（15-300s），权限不会大幅变化
    │         → 但当前设计每次 tool_call 都重新走一遍全链路
    └ 方案:
    │   ScriptExecutionPreAuthToken（脚本执行预授权令牌）:
    │     ─ 签发时机: ScriptScheduler 分配执行槽位后、脚本启动前
    │     ─ 签发内容:
    │       ─ script_id + module_id + 允许的 action 列表
    │       ─ 有效期限: 脚本 timeout + 30s 缓冲（默认 330s）
    │       ─ 令牌版本: 绑定 rbac_config_version（CAP-R17），规则变更时令牌自动失效
    │       ─ 令牌签名: HMAC-SHA256(script_id + version + expiry + allowed_actions)
    │     ─ 执行期使用:
    │       ─ 脚本的每次 tool_call → 携带 PreAuthToken →
    │         RBAC 先验证令牌签名+有效期 → 命中 → O(1) 判定（< 0.02ms）
    │         → 未命中（操作超出预授权范围）→ 回退到标准 check_permission()
    │       ─ 令牌命中率目标: > 90%（脚本的 tool_call 大多数在预授权范围内）
    │       ─ 令牌未命中（10%）→ 走标准全链路 → 不影响安全性
    │     ─ 预授权范围推导:
    │       ─ 来源 1: 脚本注册时的 allowed_resources[]（CAP-R12）
    │       ─ 来源 2: 脚本声明 depends_files[] 的对应文件操作权限
    │       ─ 来源 3: 脚本所属模块的默认权限集（module_default_rbac）
    │       ─ 合并后去重 → 产出 allowed_actions 列表 → 签发令牌
    │     ─ 安全性:
    │       ─ 令牌不可转让: 绑定 script_id → 其他脚本不可冒用
    │       ─ 令牌作用域受限: 仅 pre-authorized actions → 越界操作走标准检查
    │       ─ 令牌生命周期短: 最长 330s → 超时自动失效
    │       ─ 规则变更即时撤销: config_version 不匹配 → 令牌拒收
    │       ─ 令牌签发审计: 每次签发 → 写入 Audit Trail（签发原因/范围/有效期）
    │     ─ 性能收益:
    │       ─ 增量扫描 30 脚本 → 300 tool_calls → 90% 令牌命中 →
    │         270 次 × 0.02ms + 30 次 × 1.8ms = 5.4ms + 54ms = **59.4ms**
    │         vs. 当前全链路 300 × 1.8ms = **540ms** → 节省 89%
    │       ─ 100 AI × 5 批次并发 → 5 × 59.4ms = 297ms → 可忽略
    ├ 集成点: CAP-R12 Script as Resource + CAP-R01 FastPath + CAP-G02 ScriptScheduler
    └ 对标: AWS IAM Role chaining（AssumeRole 临时凭证）+ Kubernetes
          ServiceAccount token projection

  ▶ CAP-R19: 脚本间权限传播——Script→Script 调用的授权链与污染检测

    ┌ 现状: CAP-G15 设计了脚本间执行 DAG（Script A 依赖 Script B 的产出结果）。
    │       CAP-R12 将 script 定义为一类权限资源（script:execute 等动作）。
    │       但**脚本间跨权限调用的授权链**没有被建模——当 Script A 调用
    │       Script B 时，权限如何传播？污染如何隔离？
    ├ 问题: 脚本→脚本调用链在 10K 脚本场景下非常普遍：
    │       ─ 场景 1: 无害调用
    │         Script A(gate_check) 调用 Script B(audit) 获取审计数据 →
    │         B 的结果被 A 消费（纯读、无副作用）
    │       ─ 场景 2: 权限提升
    │         Script A(P2 建议级) 调用 Script B(P0 门禁级) →
    │         B 执行了 A 本身没有权限执行的操作（权限传播/提升）
    │       ─ 场景 3: 权限污染
    │         Script A(P0 门禁级，可修改 config) 调用 Script B(audit) →
    │         B 的产出被 A 消费 → A 基于 B 的结果修改 config →
    │         如果 B 的结果被篡改/有毒 → A 的错误操作通过 B 的数据扩散
    │       ─ 场景 4: 循环依赖 + 权限死锁
    │         A → B → C → A → 三个脚本互相依赖，权限链形成环 →
    │         任一脚本的权限变更可能导致三者连锁拒止
    ├ 方案:
    │   Script-Script AuthZ Chain（脚本间权限调用链建模）:
    │     ─ 调用声明: 脚本注册时声明 called_scripts[]（CAP-G15 DAG 扩展）
    │     ─ 权限传播规则:
    │       ─ 默认最小权限: A 调用 B → B 以 B 自身的权限执行，不受 A 的权限约束
    │       ─ 可选权限继承: A 声明 "delegate_my_permissions_to_B" →
    │         B 在 A 的权限范围内执行（交集: B.can ∩ A.can）
    │       ─ 禁止权限提升: A 不能通过调用 B 来获取 A 自身不具备的权限
    │         （B 的权限 × A 的权限 = 最终有效权限）
    │     ─ 污染检测（Taint Tracking）:
    │       ─ 每个脚本的产出标记为 TAINTED_BY_{script_id}
    │       ─ Script A 消费 Script B 的产出 → A 的产出继承 B 的污点标签
    │       ─ P0 脚本不能消费 P2 脚本的产出（防止低置信度数据影响高优先级门禁）
    │       ─ 例外: Owner 显式白名单（trusted_script_chain）
    │     ─ 调用深度限制:
    │       ─ 最大调用深度: 3 层（A→B→C→D 被拒）
    │       ─ 防止调用链爆炸: 10K 脚本 × 平均 2 calls = 20K 调用边 →
    │         SQLite 邻接表 ~1MB
    │     ─ 循环调用检测:
    │       ─ 注册时: BFS 遍历调用图 → 检测环 → 拒绝注册 + 输出环路径
    │       ─ 运行时: 调用栈追踪 → 检测深度异常 → 终止调用 + 告警
    │   Script-Call Permission 审计:
    │     ─ 每次脚本间调用: 记录 caller_script / callee_script / permission_scope
    │     ─ 调用链可视化: MCP tool resource_script_call_chain(script_id)
    │     ─ 异常模式检测: 同一对 (caller, callee) 调用频率激增 → 可能是权限滥用
    ├ 集成点: CAP-G15 ScriptExecutionDAG + CAP-R12 Script as Resource +
    │         CAP-G04 FileScriptDependencyGraph
    └ 对标: SELinux type enforcement（进程间权限隔离）+ taint tracking（污点分析）

─── 施工优先级与路线图 ──────────────────────────────────────────────────────

  施工原则：
    ▸ P0: 先解决"能不能跑"——吞吐不崩 / 配置可加载 / Agent 可注册
    ▸ P1: 再解决"跑得好不好"——缓存命中率 / 序列追踪 / 审计存储
    ▸ P2: 最后解决"跑得优雅不优雅"——复杂度预算 / 内存优化 / 联动契约

  Phase 优先级:

  | Priority | CAP       | 任务                                                       | 依赖               |
  |:--------:|:----------|:-----------------------------------------------------------|:-------------------|
  | 🔴 P0    | CAP-R01   | 100 Agent 并发基准测试 + FastPath 实现 + 分片数自适应        | D-018-59 扩展      |
  | 🔴 P0    | CAP-R02   | rbac_roles 分片存储 + Prefix Trie 索引 + 增量加载           | D-018-03 扩展      |
  | 🔴 P0    | CAP-R03   | AgentRegistry: 显式注册表 + 生命周期 + 槽位配额             | D-018-16 扩展      |
  | 🔴 P0    | CAP-R07   | 预编译缓存 + 分级冷启动释放（非二元锁）                      | D-018-14 升级      |
  | 🔴 P0    | CAP-R10   | 全局预算池 + per-Agent 分配 + 水位告警 + 漏斗联动            | D-018-93 扩展      |
  | 🔴 P0    | CAP-R16   | RBAC自身三级降级链（DEGRADED-1/2/3）+ 自适应回升            | CAP-R01 + CAP-R15 |
  | 🔴 P0    | CAP-R18   | ScriptExecutionPreAuthToken 签发+验证+失效管线              | CAP-R12 + CAP-R01  |
  | 🔴 P0    | CAP-R17   | 规则版本号 + 脚本执行快照 + Read-Committed 隔离              | CAP-R02 + CAP-G02  |
  | 🟡 P1    | CAP-R04   | 分层缓存（L0-L1 永久 vs L2-L7 TTL）+ 预热策略               | CAP-R02 完成后     |
  | 🟡 P1    | CAP-R05   | 惰性跨 Agent 关联 + 索引化 + 环形缓冲区                      | D-018-09 扩展      |
  | 🟡 P1    | CAP-R06   | 审计分级写入 + 批量 fsync + Parquet 压缩 + B-Tree 索引       | MOD-INF-020 联动   |
  | 🟡 P1    | CAP-R08   | glob → Trie 编译 + always_blocked HashMap                  | D-018-04 升级      |
  | 🟡 P1    | CAP-R09   | TokenPool: 分层 Token + GC + 异常检测                      | D-018-58/64 扩展   |
  | 🟡 P1    | CAP-R11   | IDE Registry + 配额 + 心跳 + 分布式预留                     | D-018-55 扩展      |
  | 🟡 P1    | CAP-R12   | Script 资源类型 + 脚本权限声明 + 最小权限默认                 | GateEngine 联动    |
  | 🟢 P2    | CAP-R13   | 分片复杂度评估 + Usage Counter + 僵尸规则检测               | CAP-R02 完成后     |
  | 🟢 P2    | CAP-R14   | 内存水位线 + 三级告警 + 缓存退化策略                          | MOD-RESOURCE_OPTIMIZATION_ENGINE 联动   |
  | 🟢 P2    | CAP-R15   | 容量四柱联动契约文档 + 联合 SLA 定义 + 告警链                | 所有方案稳定后     |
  | 🟢 P2    | CAP-R19   | 脚本间权限调用链建模 + Taint Tracking + 循环检测             | CAP-R12 + CAP-G15  |

  施工节奏控制（按 MOD-INF-001 容量升级总体节奏）：
    ▸ Sprint 1-2: P0 八项（CAP-R01/R02/R03/R07/R10/R16/R18/R17）→ 达到"100 Agent 可运行且不雪崩"
    ▸ Sprint 3-4: P1 六项（CAP-R04/R05/R06/R08/R09/R11/R12）→ 达到"100 Agent 高效运行"
    ▸ Sprint 5:   P2 四项（CAP-R13/R14/R15/R19）→ 达到"运维可持续+脚本权限链安全"
    ▸ 每 Sprint 完成后 → 对原蓝图对应决策标记 △ 容量升级版本号

─── 与现有施工计划的冲突分析 ─────────────────────────────────────────────────

  当前蓝图 §5 施工 Phase 规划的施工项目（P0 为主）与本次容量升级的关系：

  冲突:
    ▸ D-018-59 ConcurrentThroughputOptimizer 已完成施工 → CAP-R01 需要**扩展**
      而非重写：新增 100 Agent 基准 + FastPath + 自适应分片
    ▸ D-018-14 ColdStartLock 已完成设计 → CAP-R07 需要**升级**：二元锁 → 分级释放
    ▸ D-018-17 缓存一致性 已完成设计 → CAP-R04 需要**细化**：推送粒度从全局到模块级

  不冲突:
    ▸ CAP-R02/R03/R06/R09/R10/R11/R12/R13/R14/R15/R16/R17/R18/R19 → 全新能力，不影响现有施工

  建议:
    ▸ 容量升级代码施工在现有 Phase scaffold/experimental 完成后启动
    ▸ 但蓝图升级（本文档）应立即执行——指导后续施工的容量意识
-->

## §16 施工指引

| Phase | 任务 | 关键交付物 | 优先级 |
|:---:|------|------|:---:|
| **scaffold** | **L0 Immutable Core** — protected_paths + always_blocked 列表 + Engine 降级策略（崩=blocked） | `immutable_core.py` | 🔴 P0 |
| scaffold | **L1 RBAC** — GOV-AI-001 → rbac_roles.yaml 派生 + AgentIdentity（含 MaturityLevel）+ PermissionGuard 骨架 | `identity.py` + `rbac_guard.py` + `derive_rbac_roles.py` | P0 |
| scaffold | **L4 Sequence Guard** — 会话级序列追踪 + forbidden_sequences 基础规则集 | `sequence_guard.py` | 🔴 P0 |
| experimental | 完整三层权限执行（L1 always_allow/auto_guard/blocked）+ L4 序列阻断 + Gate Engine 集成 + Kill Switch | `permission_guard.py` 编排 L0→L4 | P0 |
| experimental | **L2 ABAC** — 意图感知 + Agent Maturity 四级信任 + 时间窗口（off_hours 降级） | `abac_guard.py` | P1 |
| experimental | **L3 Input Guard** — 参数 schema 白名单 + 危险模式检测 + 路径白名单 | `input_guard.py` | P1 |
| beta | 多 IDE 统一身份 + MCP 权限检查 + 权限漂移检测 | 全链路集成 | P2 |
| beta | **L6 Observability** — OpenTelemetry 指标 + 行为异常检测规则 | `observability.py` | P2 |
| beta | **L7 Testing** — 权限影响分析 + Dry-Run + 自动化测试框架 | `dry_run.py` + `test_permissions.py` | P2 |
| stable | **L5 Output Guard** — PII 脱敏 + 凭证检测 + 大小截断 | `output_guard.py` | P3 |
| **enhance** | **D-018-13 横向越权防护** — SessionToken签名校验 + AgentIdentityVerifier + 跨Session伪造检测 | `identity.py` 扩展 + `cross_session_detector.py` | 🔴 P0 |
| **enhance** | **D-018-14 冷启动锁** — startup_lock + maintenance_mode + 校验序列 | `immutable_core.py` 扩展 | 🔴 P0 |
| **enhance** | **D-018-15 权限钩子系统** — 四类钩子注册表 + 预置9个钩子(H01-H09) | `permission_hooks.py` + `permission_hooks.yaml` | 🔴 P0 |
| **enhance** | **D-018-28 Agent创建权** — creation_policy + 遗传衰减 + 生命周期管理 | `agent_creation_policy.yaml` + `rbac_guard.py` 扩展 | 🟡 P1 |
| **enhance** | **D-018-17 缓存一致性** — 推送驱动缓存失效 + 降级攻击防护 | `cache_invalidation.py` + `cache_policy.yaml` | 🟡 P1 |
| **enhance** | **D-018-18 紧急覆盖令牌** — JIT越权 + Owner CLI + 一次性Token | `emergency_override.py` | 🟡 P1 |
| polish | **D-018-19 自动维护** — 规则效果评估 + 僵尸规则检测 + 复杂度预算 + Owner仪表盘 | `auto_maintenance.yaml` + `health_dashboard.yaml` | 🟢 P2 |
| polish | **Owner缺席策略** — 超时审阅→保守模式 | `ownership_absence_policy.yaml` | 🟢 P2 |
| polish | **跨模型一致性测试** — DeepSeek/GLM/Claude对同权限规则判定一致性 | L7扩展 | 🟢 P2 |
| polish | **对抗性测试** — 一个专用Agent尝试绕过所有七层+三横切面 | L7扩展 | 🟢 P2 |
| polish | **定期审计报告** — 每周自动生成+交付 | cronjob + report template | 🟢 P2 |

### §16.3 施工步骤 `[临时时态: 执行完毕后删除]`

> 本节记录施工执行计划。一旦全部 Phase 执行完毕，本节从蓝图删除（铁律 #14）。

**删除前置条件（5条，全部满足方可删除本节）**：

| # | 前置条件 | 验证方式 |
|---|---------|---------|
| 1 | 所有 Phase 的关键交付物已创建 | §0.1 存在性列全部为"已实现" |
| 2 | 所有交付物通过测试 | `python -m pytest tests/agent-rbac/ -v` exit 0 |
| 3 | §0.2 对齐验证矩阵全部 ☑ | 逐项验证 |
| 4 | construction_progress = completed | frontmatter 字段确认 |
| 5 | 无遗留临时文件 | `python scripts/governance/d11_compliance/audit_registration.py` exit 0 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 权限规则数 | 200 条 | `rbac_roles.yaml` 条目数 |
| 并发 Agent 数 | 10 | 同时活跃 session 数 |
| 审计事件/秒 | 100 | OTEL 指标 `d2.authz.decision.rate` |
| 权限缓存条目 | 1000 | 缓存命中率统计 |
| 权限检查延迟 P99 | 1.8ms | OTEL 指标 `d2.authz.decision.latency` |

### §17.2 缺口分析

| # | 缺口 ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|---|---------|---------|---------|---------|
| 1 | CAP-R01 | 规则数 > 500 | 规则分片 + 按域加载 | > 500 条 |
| 2 | CAP-R02 | 并发 Agent > 50 | 无锁并发 + Rust 加速 | > 50 Agent |
| 3 | CAP-R03 | 审计事件 > 1000/s | 批量写入 + 异步发射 | > 1000/s |
| 4 | CAP-R04 | 缓存条目 > 10000 | LRU + 分层缓存 | > 10000 条 |
| 5 | CAP-R05 | 检查延迟 P99 > 5ms | 热路径优化 + 预计算 | > 5ms |
| 6 | CAP-R06 | Kill Switch 触发延迟 > 100ms | 专用信号通道 | > 100ms |
| 7 | CAP-R07 | 横切面钩子数 > 50 | 钩子分优先级 | > 50 钩子 |
| 8 | CAP-R08 | 序列追踪状态 > 10MB/session | 状态压缩 + 滑动窗口 | > 10MB |
| 9 | CAP-R09 | Dry-Run 影响分析 > 5s | 增量分析 + 缓存 | > 5s |
| 10 | CAP-R10 | 对抗性测试套件 > 30min | 并行测试 + 增量测试 | > 30min |
| 11 | CAP-R11 | 规则派生脚本 > 10s | 增量派生 | > 10s |
| 12 | CAP-R12 | 审计日志存储 > 10GB/月 | 日志轮转 + 压缩 | > 10GB/月 |
| 13 | CAP-R13 | Owner 仪表盘刷新 > 3s | 增量更新 + WebSocket | > 3s |
| 14 | CAP-R14 | 跨模型一致性测试 > 15min | 并行 + 缓存 | > 15min |
| 15 | CAP-R15 | 信任预算计算 > 50ms | 预算预计算 + 缓存 | > 50ms |
| 16 | CAP-R16 | MCP 权限代理吞吐 < 500/s | 连接池 + 批量检查 | < 500/s |
| 17 | CAP-R17 | 密钥层次管理 > 1000 密钥 | 密钥分片 + HSM | > 1000 |
| 18 | CAP-R18 | 统计异常检测误报率 > 5% | 自适应阈值 + 在线学习 | > 5% |
| 19 | CAP-R19 | 构建产物哈希链 > 10000 节点 | Merkle 树剪枝 + 检查点 | > 10000 |

### §17.3 迁移缺口追踪

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | governance/ 根级 9 文件未迁移至 agent-rbac/ | P2 | v1.0.0 | 待施工 |

---

## §18 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-018-01 | 三层权限 95/4/1 分布，取消 needs_approval | 2026-05-05 | 1人+AI场景，10+并发对话，人工审批不可行 |
| D-018-02 | 先干后验 + 自动护栏，非事前审批 | 2026-05-05 | 多 IDE 并发不可能等实时审批；对标 Terraform auto-apply |
| D-018-03 | GOV-AI-001 自动派生 rbac_roles.yaml | 2026-05-05 | 消除手动复制=消除漂移；对标 K8s CRD 自动派生 |
| D-018-04 | **L0 Immutable Core — 硬编码不可变保护区** | 2026-05-05 | 100%AI施工，护栏自身必须不能被AI修改；对标 Claude Code protected paths |
| D-018-05 | **L0 Kill Switch — 全局熔断机制** | 2026-05-05 | CSA ATF Incident Response——"Agent失控了怎么办"；对标交易系统熔断 |
| D-018-06 | **L0 Engine 降级策略 — 崩=blocked** | 2026-05-05 | 权限系统故障时安全优先于便利；负面偏好 |
| D-018-07 | **L2 ABAC — 意图感知+时间窗口+成熟度+敏感性四维属性权限** | 2026-05-05 | RBAC不够，需动态上下文判定；对标企业级Agent四层设计 |
| D-018-08 | **L3 Input Guard — 参数级护栏** | 2026-05-05 | D2 Layer 2——权限颗粒度需从Tool级细化到参数级 |
| D-018-09 | **L4 Sequence Guard — 操作序列追踪与阻断（最关键补丁）** | 2026-05-05 | D2 Layer 3——单步合法≠序列安全；防御数据外泄/提权/破坏链 |
| D-018-10 | **L5 Output Guard — 输出护栏** | 2026-05-05 | D2 Layer 4——Tool输出也需验证/脱敏/截断 |
| D-018-11 | **L6 Observability — 可观测性** | 2026-05-05 | 权限系统自身必须可观测；OpenTelemetry标准 |
| D-018-12 | **L7 Testing & Dry-Run — 权限可测试性** | 2026-05-05 | 权限配置=可测试代码；1人+AI下改了没人验证→必须自动化 |
| D-018-13 | **横向越权防护 — SessionToken签名+AgentIdentityVerifier** | 2026-05-05 | CSA ATF一级威胁；SessionToken HMAC-SHA256签名防跨Session身份伪造 |
| D-018-14 | **冷启动锁 — 系统启动时全局拒绝直到权限加载校验通过** | 2026-05-05 | Flyway/K8s RBAC——启动前先校验；防止配置加载窗口期裸奔 |
| D-018-15 | **权限钩子系统 — 四类钩子(pre/post/on_blocked/on_kill_switch)** | 2026-05-05 | Claude Code hooks + Terraform pre/post-conditions；预置9个钩子 |
| D-018-16 | **Agent创建权与权限遗传 — 创建管控+衰减继承+生命周期** | 2026-05-05 | Temporal/K8s/OAuth2——身份不可转让；agent_spawn_storm熔断器 |
| D-018-17 | **缓存一致性推送 — 推送驱动失效替代被动TTL** | 2026-05-05 | K8s RBAC push-based invalidation——最大延迟100ms替代5min窗口 |
| D-018-18 | **紧急覆盖令牌 — Owner JIT临时越权令牌（<5分钟，一次性）** | 2026-05-05 | NIST JIT最小权限 + AWS STS assume-role + Claude Code bypassPermissions |
| D-018-19 | **自动维护 — 僵尸规则检测+复杂度预算+Owner健康仪表盘** | 2026-05-05 | K8s auth can-i + OPA静态分析；1人维护下防熵增 |
| D-018-20 | **IBAC 意图绑定访问控制 — 任务意图+临时权限信封+意图漂移检测（横切面D核心）** | 2026-05-05 | Cisco TBAC/IBAC + Perplexity NHI；将"谁"升级为"什么任务+什么意图" |
| D-018-21 | **Context Drift 检测 — 操作链中意图漂移的三维实时追踪** | 2026-05-05 | Enterprise context drift research + Claude Code长对话漂移问题 |
| D-018-22 | **连续验证 — 每步重验证Agent身份+意图+委托链一致性** | 2026-05-05 | NIST Zero Trust + Cisco NHI——从不信任，每步验证 |
| D-018-23 | **权限模式管理器 — Claude Code 5模式 + Codex CLI Profiles + Mid-Session Toggle** | 2026-05-05 | Claude Code Shift+Tab + Codex CLI profiles + /permissions 中切换 |
| D-018-24 | **级联故障隔离 — Agent链中的Cascading Failure防护** | 2026-05-05 | Perplexity cascading failures + NVIDIA多Agent链路管控 |
| D-018-25 | **Micro-Verified 先干后验 — 每子步骤微型验证替代全干再验** | 2026-05-05 | Windsurf Cascade micro-verification + Claude Code auto模式AI分类器 |
| D-018-26 | **权限决策自解释 — 结构化拒绝原因+自校正建议+完整因果链** | 2026-05-05 | Perplexity explainable agents + CSA ATF 2026 + OPA decisions log |
| D-018-27 | **对抗韧性 & 激励对齐（横切面E核心）— OWASP Agentic Top 10全覆盖 + MAESTRO五层威胁建模** | 2026-05-05 | OWASP ASI02-ASI06(Dec 2025) + MAESTRO(Perception/Decision/Action/Communication/Memory) |
| D-018-28 | **Agent目标完成驱动 v.s. 安全约束的冲突防护 — Agent自解除沙箱/绕过护栏** | 2026-05-05 | Claude Code CVE-2026-21852(Agent Disables Its Own Sandbox) + AI Red Team RCE CVE-2024-12366 |
| D-018-29 | **多Agent合谋与激励博弈检测 — GroupGuard+涌现行为博弈论建模** | 2026-05-05 | GroupGuard合谋检测(清华/港大) + "Agents of Chaos"11类激励失败模式(Harvard/MIT/Stanford) |
| D-018-30 | **虚假完成与Agent欺骗检测 — Agent报告"已完成"但实际操作被篡改/遗漏** | 2026-05-05 | Grith 7-Agent安全审计(多数在3维中失败2维) + Multi-Agent Security Open Challenge(Oxford) |
| D-018-31 | **记忆来源追踪与隔离 — RAG/Vector Memory上下文投毒的防护** | 2026-05-05 | OWASP ASI06 Improper Memory/Context Handling + LangChain Memory Poisoning Research |
| D-018-32 | **TOCTOU 文件系统竞态 + 编码绕过防护 — Symlink攻击 + Base64/Hex/URL编码命令检测** | 2026-05-05 | TOCTOU Race Condition Research + OWASP Encoding Bypass Patterns |
| D-018-33 | **Canary权限灰度发布 + 权限变更自动回归 — 新权限先测试1%流量→全量 + 一键回滚** | 2026-05-05 | Terraform canary/blue-green + Feature Flags Gradual Rollout + Git-Based Permission Rollback |
| D-018-34 | **Genesis Bootstrap防护 — AI施工RBAC时的两阶段验证+Clean Build原则+代码签名** | 2026-05-06 | Sheriff自我审计+ VibeGuard盲点分类+ Gartner 2026 Agent安全事故报告 |
| D-018-35 | **非对称安全审查原则 — Independent Security Auditor独立审查RBAC自身** | 2026-05-06 | SecureVibes.ai "Trust from separation" + State of Agent Security 2026零独立审查 |
| D-018-36 | **不可抵赖操作绑定 — Ed25519密钥对+操作Merkle Tree+TSA时间戳+公开锚定** | 2026-05-06 | STRIDE Repudiation + TLS 1.3 CertificateVerify + Bitcoin transaction signing |
| D-018-37 | **路径解析系统故障防护 — Shell命令空格/Unicode/嵌套引号的解析安全** | 2026-05-06 | Google Antigravity P0(空格导致rm -rf全盘删除) + Google官方确认Systemic path-parsing failure |
| D-018-38 | **跨平台Shell方言检测 — LLM的"Linux偏见"在Windows上的不等效命令防护** | 2026-05-06 | Google Antigravity P0(Windows cmd引号转义) + SUSVIBES 10.5%安全率(跨平台不兼容贡献) |
| D-018-39 | **权限规则语言注入防护 — 规则=Data非Instruction+Engine隔离+规则文本沙箱** | 2026-05-06 | Prompt Injection的一般原则应用于权限规则元数据 + 指令-数据分离最佳实践 |
| D-018-40 | **构建产物安全卫生 — Source Map/artifacts/Docker layers中的源码/密钥泄露扫描** | 2026-05-06 | Claude Code 2.1.88 512K行源码Map泄露 + VibeGuard artifact hygiene分类 |
| D-018-41 | **Transitive依赖安全审计 — 递归验证所有间接依赖+install脚本+CVE分级策略** | 2026-05-06 | OSV/GitHub Advisory DB + SLSA provenance + Sherlock 14漏洞中供应链漏洞 |
| D-018-42 | **审计日志实时完整性验证 — Merkle Tree+Inclusion Proof+<100ms密码学证明** | 2026-05-06 | STRIDE Tampering检测 + Certificate Transparency Log + Bitcoin SPV proofs |
| D-018-43 | **Agent上下文重放攻击防护 — nonce绑定+一次性检查+Bloom Filter去重** | 2026-05-06 | TLS 1.3 0-RTT replay protection + Kerberos authenticator nonce + OAuth2 nonce |
| D-018-44 | **权限审计证据的律师可验证性 — 人类可读审计报告+GDPR/个保法合规映射** | 2026-05-06 | GDPR Art.30/33-34 + 个保法第17/38-39/57条 + 法律证据可采信标准 |
| D-018-45 | **Rollback作为攻击载体的隔离 — 快照签名验证+rollback_storm熔断+回滚change audit** | 2026-05-06 | Sherlock self-audit 14漏洞 + Git reflog安全 + Database point-in-time recovery security |
| D-018-46 | **单调时钟与系统时钟操纵防护 — time.monotonic()+NTP交叉验证+Windows权限裁剪** | 2026-05-06 | Google Spanner TrueTime + TLS 1.3 防重放timestamp + NTP时钟源验证 |
| D-018-47 | **Bootstrap验证无限递归解决 — 极简确定性验证脚本(<60行)+可复现构建+跨模型验证** | 2026-05-06 | SecureVibes非对称审查 + Sherlock CI检查漏洞 + Reproducible Builds |
| D-018-48 | **主密钥层次化与泄露隔离 — Root/Agent/Session三层密钥+分片存储+前向安全** | 2026-05-06 | AWS KMS信封加密 + TLS 1.3前向安全性 + Shamir Secret Sharing |
| D-018-49 | **未知攻击模式统计异常检测 — 5维评分(N-gram/熵/转移/路径/速度)+统计基线** | 2026-05-06 | Forrest/Warrender 1999系统调用异常检测 + 数据库Query Plan异常检测 |
| D-018-50 | **审计日志注入防护 — 密码学来源证明+注入模式扫描+链式条目哈希链接** | 2026-05-06 | OWASP ASVS V7 Logging + 日志注入CWE-117 + CT Log不可变链 |
| D-018-51 | **蓝图-实现保真度验证 — 决策断言系统+保真度CI测试+漂移自动检测** | 2026-05-06 | Contract-Based Programming + Test-Driven Governance + OPA Conftest |
| D-018-52 | **C扩展/原生API绕过防护 — import hook+ctypes封禁+subprocess安全封装** | 2026-05-06 | Sandboxie应用沙箱 + Firejail + Windows AppContainer 隔离原理 |
| D-018-53 | **进程级内存保护 — DPAPI加密+Windows完整性级别隔离+内存dump防护** | 2026-05-06 | Windows Mandatory Integrity Control + DPAPI + Linux ptrace_scope |

---

## MOD-GOVERNANCE 集成契约锚点

> 权威定义见 [`../../_domain_governance/blueprint.md`](../../_domain_governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-001 | 产出方（RBAC 判定后写入 Audit） | MOD-INF-020 |
| G-CT-004 | 消费方（承接 Escalation 的权限策略） | MOD-INF-022 |
| G-CT-007 | 消费方（Agent Spec 与权限绑定） | MOD-INF-019 |
| G-CT-008 | 消费方（A2A 身份与隔离） | MOD-INF-025 |

---

## 治理信息

### SSoT 声明

本文件是 Agent 身份与权限系统（MOD-INF-018）的**唯一设计真源**。权限规则的可执行真源是 `rbac_roles.yaml`（由 GOV-AI-001 自动派生）。

### 负向责任

本文件**不涉及**：任务卡字段定义（→ GOV-TASK-001）、CI/CD 部署流程（→ CI/CD 文档）、Prompt Injection 检测算法（→ MOD-LLM_SECURITY）。

### 消费者注册表

| 消费者 | 用途 |
|--------|------|
| MCP Servers (MOD-INF-013) | MCP Tool 调用前权限检查 |
| Rollback System (MOD-INF-021) | auto_guard 后验失败触发回滚 |
| Escalation System (MOD-INF-022) | Kill Switch 联动 |
| Pipeline Orchestrator (MOD-TASK_SYSTEM) | 任务创建时绑定 Agent 身份 |
| Gate Engine (MOD-GATE_ENGINE) | 权限检查作为门禁前置 |
| Pre-Commit Gate (GATE-18) | CI 中运行权限自动化测试 |

### 触发条件

| 关键词/场景 | 应读章节 |
|-----------|---------|
| 权限 / permission / rbac / abac | §3 架构设计 |
| 身份 / identity / agent_id | §4.2 AgentIdentity |
| Kill Switch / 熔断 | §3.2 L0 ImmutableCore |
| auto_guard / 先干后验 | §3.2 L1 RBAC Guard |
| 序列 / sequence / 操作链 | §3.5 L4 Sequence Guard |
| 容量 / 性能 / 升级 | §17 容量升级附录 |
| 盲点 / 安全漏洞 | §18 决策记录 + 附录 A |
| 施工 / 实现 | §16 施工指引 |

### 漂移防护

修改本蓝图 MUST 同步更新：`rbac_roles.yaml` + `permission_hooks.yaml` + GOV-AI-001 + `test_permissions.py`。详见 §13。

### 变更同步规则

| 修改此文件 | 必须同步更新 |
|-----------|------------|
| §0 分派表 | MOD-GOVERNANCE §2 职责分派 |
| §4 代码文件清单 | blueprint_registry.yaml MOD-INF-018 条目 |
| §5 待施工项 | construction_progress 字段 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

### 导航路径

```
新 AI → registry_of_registries.yaml → MOD-INF-018 → 本蓝图 §0 代码对齐验证 → §3 架构设计 → §16 施工指引
```

---

## 附录：209 盲点补丁对照表

| # | 盲点 | 严重度 | 补丁位置 | 状态 |
|---|------|:---:|------|:---:|
| 1 | 无多层护栏 | P0 | §2.0 七层模型总览 | ✅ 已补 |
| 2 | 操作序列盲区 | P0 | §2.7 L4 Sequence Guard | ✅ 已补 |
| 3 | 权限配置自身无保护 | P0 | §2.1 L0 Immutable Core | ✅ 已补 |
| 4 | 无 Kill Switch | P0 | §2.2 L0 Kill Switch | ✅ 已补 |
| 5 | Prompt Injection 无防护 | P0 | L3 dangerous patterns + L4 sequence | ✅ 已补 |
| 6 | 无信任分级/成熟度 | P1 | §2.5 L2 ABAC Maturity | ✅ 已补 |
| 7 | 永久白名单 vs JIT | P1 | §2.5 L2 ABAC Intent-aware | ✅ 已补 |
| 8 | 无意图感知 ABAC | P1 | §2.5 L2 ABAC Intent | ✅ 已补 |
| 9 | Agent 委托链无控制 | P1 | RoleBinding.expires_at + Maturity 上限 | ✅ 已补 |
| 10 | 权限配置审计缺失 | P1 | §2.9 L6 policy_audit | ✅ 已补 |
| 11 | 跨会话 Context Leak | P1 | L4 per-session 隔离追踪 | ✅ 已补 |
| 12 | 权限冲突解决规则 | P1 | §6 R10 + test_role_consistency | ✅ 已补 |
| 13 | 无行为异常检测 | P1 | §2.9 L6 anomaly_detection | ✅ 已补 |
| 14 | 无权限影响分析 | P2 | §2.10 L7 impact_analysis | ✅ 已补 |
| 15 | 无 Dry Run 模式 | P2 | §2.10 L7 dry_run | ✅ 已补 |
| 16 | 无 Rate Limiting | P2 | §2.2 L0 Kill Switch auto_triggers | ✅ 已补 |
| 17 | 缓存失效策略不完整 | P2 | §6 R3 缓存管控 | ✅ 已补 |
| 18 | Engine 故障降级缺失 | P2 | §2.3 L0 Engine Degradation | ✅ 已补 |
| 19 | 无 Capability Discovery | P2 | §2.10 L7 dry_run evaluate_agent | ✅ 已补 |
| 20 | 无权限测试框架 | P2 | §2.10 L7 test_framework | ✅ 已补 |
| 21 | 多 IDE 权限一致性 | P2 | §6 R4 乐观并发控制 | ✅ 已补 |
| 22 | 无时间窗口约束 | P2 | §2.5 L2 ABAC Temporal | ✅ 已补 |
| 23 | 权限颗粒度不够 | P2 | §2.6 L3 Input Guard 参数级 | ✅ 已补 |
| 24 | 无 Rego 风格声明式 | P2 | §2.12 rbac_roles.yaml 扩展 | ✅ 已补 |
| 25 | **横向越权——Agent冒充其他Agent身份跨Session操作** | 🔴 P0 | D-018-13 §2.15 SessionToken签名+AgentIdentityVerifier | ✅ 已补 |
| 26 | **冷启动窗口——权限配置加载前的裸奔期** | 🔴 P0 | D-018-14 §2.16 ColdStartLock + maintenance_mode | ✅ 已补 |
| 27 | **权限钩子缺失——无pre/post/on_blocked/on_kill_switch钩子** | 🔴 P0 | D-018-15 §2.17 PermissionHookRegistry + 9预置钩子 | ✅ 已补 |
| 28 | **Agent自我复制——Agent可派生新实例绕过Maturity限制** | 🔴 P0 | D-018-16 §2.18 创建权管控+遗传衰减+agent_spawn_storm熔断 | ✅ 已补 |
| 29 | **审计系统自身投毒——噪音攻击淹没告警** | 🔴 P0 | §2.2 signal_noise_attack熔断触发器 + 告警信噪比监控 | ✅ 已补 |
| 30 | **权限缓存陈旧——紧急收紧后旧ALLOW仍生效5分钟** | 🔴 P0 | D-018-17 §2.19 推送驱动缓存失效(max_latency=100ms) | ✅ 已补 |
| 31 | **条件竞争——双IDE同时操作同一受保护文件** | 🟡 P1 | §6 R4 乐观并发控制 + 操作序列化锁 | ✅ 已补 |
| 32 | **降级攻击——Agent故意触发Engine降级绕过L4检查** | 🟡 P1 | §2.3+D-018-17 降级攻击源检测→立即BLOCKED | ✅ 已补 |
| 33 | **熔断器DDoS——恶意Agent触发Kill Switch瘫痪合法Agent** | 🟡 P1 | §2.2 熔断源隔离(单Agent触发仅阻断该Agent) | ✅ 已补 |
| 34 | **操作回滚的权限边界——回滚操作本身可能绕过L0-L4检查** | 🟡 P1 | D-018-14关联 §4 Rollback Auth——回滚也需过L0不可变核心 | ✅ 已补 |
| 35 | **导航表5.2.1保护——Agent可修改流程映射误导未来AI Session** | 🟡 P1 | L0 protected_paths增加 config/nav_table_mapping.yaml | ✅ 已补 |
| 36 | **Agent间隐式通信——文件系统Covert Channel协同绕过单Session护栏** | 🟡 P1 | §2.7 cross_session_correlation + inter_agent_communication_detection | ✅ 已补 |
| 37 | **持久化后门——Agent修改启动脚本/调度任务** | 🟡 P1 | L0 protected_paths 扩展至 .github/workflows + 启动脚本目录 | ✅ 已补 |
| 38 | **环境变量篡改——Agent修改.env/pyproject.toml改变系统运行时** | 🟡 P1 | L0 protected_paths增加 **/.env* + pyproject.toml + docker-compose* | ✅ 已补 |
| 39 | **Task系统权限闭环缺失——Agent可直接修改TaskCard状态不经审核** | 🟡 P1 | L1 RBAC 扩展Task对象操作权限(create/update_status/delete/assign) | ✅ 已补 |
| 40 | **回滚系统权限失控——Agent可主动调用rollback撤销其他Agent工作** | 🟡 P1 | 决策: Agent不直接调用rollback API——仅auto_guard失败系统自动触发 | ✅ 已补 |
| 41 | **第三方包安装——pip/npm install的代码不受Agent RBAC约束** | 🟢 P2 | §2.6 L3 package_install_guard白名单 + blocked_packages:["*"] | ✅ 已补 |
| 42 | **网络边界——Agent可通过DNS隧道/WebSocket/SSH绕过网络权限** | 🟢 P2 | §2.6 L3 network_target_guard URL白名单/黑名单 | ✅ 已补 |
| 43 | **数据标记投毒——Agent批量修改frontmatter sensitivity标签降级资源** | 🟢 P2 | §2.5+D-018-13 sensitivity_label_blitz熔断+标签变更审计+自动还原 | ✅ 已补 |
| 44 | **测试环境权限泄漏——测试中放宽的权限不应进入生产** | 🟢 P2 | §2.10 L7 TEST_MODE标志 + 测试操作仅对tests/和临时目录生效 | ✅ 已补 |
| 45 | **可观测性指标篡改——Agent可修改指标上报代码使监控失效** | 🟢 P2 | L6 指标完整性校验(上报代码哈希比对) + 指标自身受L0保护 | ✅ 已补 |
| 46 | **权限配置无备份——rbac_roles.yaml误改/误删无法恢复** | 🟢 P2 | 自动备份机制(保留最近3个版本) | ✅ 已补 |
| 47 | **Depends_on依赖链安全问题——GateEngine等被绕过则RBAC随之失效** | 🟢 P2 | 依赖链安全断言 + 每个依赖引入时通过安全校验 | ✅ 已补 |
| 48 | **Agent Maturity自动化升级的数据源不可信——指标可被Agent自报** | 🟢 P2 | Maturity升级数据源必须来自不可变审计日志(MOD-INF-020) | ✅ 已补 |
| 49 | **Owner审批SLA窗口——异步审阅可能无限延后** | 🟢 P2 | 审阅超时策略——72小时后未审→操作标记"未决"→告警升级 | ✅ 已补 |
| 50 | **多模型权限判定偏差——DeepSeek/GLM/Claude对同规则理解可能不同** | 🟢 P2 | §2.10 L7跨模型权限判定一致性测试 | ✅ 已补 |
| 51 | **权限树复杂性爆炸——1人无法维护** | 🟢 P2 | D-018-19 权限复杂度预算(max=30规则) + 性价比自动评估 | ✅ 已补 |
| 52 | **紧急覆盖模式缺失——无Owner快速临时越权的制度化机制** | 🟢 P2 | D-018-18 EmergencyOverrideToken(JIT/<5分钟/一次性/CLI) | ✅ 已补 |
| 53 | **操作频率失控——无per-Agent Rate Limiting** | 🟢 P2 | §2.5 D-018-07扩展 TLB Token Bucket事前限流+Tiered by Maturity | ✅ 已补 |
| 54 | **权限变更影响不可视——Owner无法5秒理解变更后果** | 🟢 P2 | §2.19+D-018-19 权限拓扑图自动生成 + Owner 5数字健康仪表盘 | ✅ 已补 |
| 55 | **自然语言规则歧义——Vibe Coding AI对同规则理解可能不一致** | 🟢 P2 | YAML规则增加formal_semantics字段(OPA Rego可执行语义) + L7跨模型一致性 | ✅ 已补 |
| 56 | **权限判定自身的幂等性问题——重试操作因ABAC时间窗口变化导致判定不一致** | 🟡 P1 | D-018-22 连续验证——每次check带idempotency_key保证同操作同结果 | ✅ 已补 |
| 57 | **分布式一致性 vs 本地检查性能的张力——多IDE RBAC同步延迟远超0.1ms** | 🟡 P1 | D-018-17 推送驱动缓存 + 本地缓存优先 + 异步同步 | ✅ 已补 |
| 58 | **权限规则版本管理——rbac_roles.yaml错误派生后无自动回滚** | 🟡 P1 | R46备份机制 + D-018-19规则版本管理 + 派生前后哈希对比 | ✅ 已补 |
| 59 | **Agent生命周期三维时间的冲突——Token/角色/Maturity三个独立过期时间** | 🟡 P1 | D-018-22 连续验证——最小有效原则：任一维度过期=整体失效 | ✅ 已补 |
| 60 | **多IDE下同一Owner-Agent的Session合并/分裂——双重身份问题** | 🟡 P1 | D-018-13 横向越权 + AgentIdentityVerifier——同一Owner不同IDE=不同Agent Identity | ✅ 已补 |
| 61 | **文件锁的生命周期——锁TTL/死锁处理/锁持有者崩溃时释放缺失** | 🟡 P1 | L0 操作序列化锁 + FileLockManager(心跳TTL=30s+死锁检测+崩溃自动释放) | ✅ 已补 |
| 62 | **权限规则被Vibe Coding AI"误读"为操作指令——blocked被理解为"系统状态"** | 🟡 P1 | D-018-23 权限模式指示器(IDE中始终显示当前模式) + D-018-26自解释输出 | ✅ 已补 |
| 63 | **上下文窗口中的权限信息污染——500+行规则挤占代码理解空间** | 🟢 P2 | D-018-15 钩子系统——按需加载 + D-018-23 profile切换动态加载规则子集 | ✅ 已补 |
| 64 | **Agent对"自己被限制"的自我认知成为二阶信息泄漏——透明策略=隐蔽导航** | 🟡 P1 | §5.1 N-1约束平衡——告知限制但不告知绕过方法 + L4 Emergent Behavior检测 | ✅ 已补 |
| 65 | **Owner认知负荷——异步审阅面板信息过载下的错误决策风险** | 🟡 P1 | D-018-19 Owner仪表盘(5数字精简) + D-018-26因果链(重点高亮异常) | ✅ 已补 |
| 66 | **混沌权限测试缺失——修改规则后无全链路破坏性测试** | 🟢 P2 | D-018-20 Chaos Permission Testing——故意变异规则→跑全链路→检测意外阻断 | ✅ 已补 |
| 67 | **Agent RBAC在CI/CD中的位置——Pre-Commit中RBAC自身有Bug时的防护** | 🟡 P1 | L0 OS ACL双重兜底——即使Python层崩了→OS文件权限仍在 | ✅ 已补 |
| 68 | **回滚系统在上游依赖不可用时——MOD-INF-021故障下的auto_guard悬空状态** | 🟡 P1 | D-018-24 级联故障隔离——检测MOD-INF-021不可用→auto_guard降级为blocked | ✅ 已补 |
| 69 | **跨模型权限判定一致性的"真源"——DeepSeek/GLM/Claude三者判定不同时谁为准** | 🟡 P1 | OPA Rego formal_semantics作为唯一真源 + 模型判定为辅助 + L7一致性测试 | ✅ 已补 |
| 70 | **紧急覆盖令牌的滥用检测——连续三天用满3个token的异常模式** | 🟢 P2 | D-018-19 Owner仪表盘 + 令牌使用模式异常检测(>2天连续用满=告警) | ✅ 已补 |
| 71 | **权限决策的"灰色地带"——部分允许(partial_allow)状态在三态模型中无表达** | 🟢 P2 | L3 Input Guard实现参数级partial_allow(如"只读"/"限制文件大小") | ✅ 已补 |
| 72 | **MCP Server自身的权限身份——Agent通过高权限MCP Server执行越权操作** | 🔴 P0 | D-018-20横切面D——MCP Server身份纳入Intent信封 + L3 MCP身份校验 | ✅ 已补 |
| 73 | **实时监控与异步处理的延迟——Kill Switch基于0.5秒前的数据做熔断判断** | 🟡 P1 | L6 同步关键指标(熔断触发条件) + 异步非关键指标(统计) | ✅ 已补 |
| 74 | **Agent权限继承的动态同步——父Agent权限变更后子Agent未重新计算** | 🟡 P1 | D-018-16 权限遗传 + D-018-22连续验证——父变→推送子重新计算 | ✅ 已补 |
| 75 | ***先干后验"模式下的竞态条件——Agent A回滚时Agent B已读取回滚前数据** | 🔴 P0 | Micro-Verified L4——每子步执行后立即锁定+微验证+提交→再释放锁 | ✅ 已补 |
| 76 | **AI Agent自我审计能力——CSA ATF 2026要求Agent能解释拒绝原因** | 🟡 P1 | D-018-26 结构化解释 + 因果链——Agent收到完整拒绝原因可自校正 | ✅ 已补 |
| 77 | **Owner可动态切换的全局模式缺失——Claude Code 5模式+Shift+Tab对标缺失** | 🟡 P1 | D-018-23 权限模式管理器——5模式+Shift+Tab+Profiles | ✅ 已补 |
| 78 | **per-Session临时只读标记缺失——Aider /read-only files对标缺失** | 🟢 P2 | D-018-23 Profiles——plan模式自动read-only + /read-only {file} 临时标记 | ✅ 已补 |
| 79 | **运行时持续性红队缺失——Google SAIF AI-on-AI持续攻击检测** | 🟢 P2 | L7 Chaos Permission Testing + 运行时的对抗性探针(每15分钟一次) | ✅ 已补 |
| 80 | **Micro-Verification对标缺失——Windsurf Cascade"每步微验证"对标** | 🟡 P1 | D-018-25 Micro-Verified先干后验——子步分解+微验证+即时回滚 | ✅ 已补 |
| 81 | **Context Drift（上下文漂移）——Agent链中意图从"修Bug"漂移到"重构模块"** | 🔴 P0 | D-018-20 IBAC + D-018-21 Context Drift检测——三维实时漂移追踪 | ✅ 已补 |
| 82 | **Inference as Privilege Escalation（推理式越权）——跨公开数据合成受限信息** | 🔴 P0 | L5 Synthesis Leakage Detection——跨读链输出检测 + always_blocked: synthesize_restricted_data | ✅ 已补 |
| 83 | **Multi-Agent Emergent Behavior（多Agent涌现行为）——个体合法但群体非法** | 🟡 P1 | L4 Emergent Behavior Detection——跨Agent操作模式关联+涌现模式告警 | ✅ 已补 |
| 84 | **Agent链中每步Zero Trust重验证缺失——仅初始检查一次** | 🔴 P0 | D-018-22 连续验证——每步重验证Agent身份+意图+Token+委托链 | ✅ 已补 |
| 85 | **Permission Mode Switching——Owner无法在5种模式间无缝切换** | 🟡 P1 | D-018-23 权限模式管理器 + Shift+Tab + Mid-Session /mode | ✅ 已补 |
| 86 | **MCP Tool-Specific Permissions——MCP Server身份未纳入权限上下文** | 🟡 P1 | D-018-20横切面D + L3 MCP Server身份校验 | ✅ 已补 |
| 87 | **Permission Decision Explainability——拒绝原因对Agent不可用** | 🟡 P1 | D-018-26 结构化解释——自校正建议+因果链+可视化 | ✅ 已补 |
| 88 | **Config Profile System缺失——Codex CLI多Profile场景对标** | 🟢 P2 | D-018-23 Profiles——default/ci_automation/exploration 三profile + 自动切换 | ✅ 已补 |
| 89 | **Mid-Session Permission Toggling缺失——/permissions会话中动态切换** | 🟡 P1 | D-018-23 Mid-Session Control——/mode /permissions /profile /audit 命令 | ✅ 已补 |
| 90 | **Intent Binding Across Agent Chains——委托时不传递原始意图边界** | 🟡 P1 | D-018-20 IBAC——IntentBindingContext通过委托链传递 | ✅ 已补 |
| 91 | **Cascading Failure in Agent Workflows——单Agent错误级联感染下游** | 🟡 P1 | D-018-24 级联故障隔离——链监控+自动隔离+上游故障→下游降权 | ✅ 已补 |
| 92 | **Operational Context vs Authorization Context Drift——任务超时但仍在进行** | 🟡 P1 | D-018-20 IBAC Permission Envelope TTL + auto_renew/auto_degrade | ✅ 已补 |
| 93 | **Permission Boundary Leakage Through Synthesis——多源读取合成出受限制信息** | 🟡 P1 | L5 Synthesis Leakage Detection——语义合成检测(已读数据→输出内容语义对比) | ✅ 已补 |
| 94 | **Agent Self-Modification of Permission-Aware Behavior——Goodhart's Law防御** | 🟡 P1 | D-018-21 Context Drift + L6 行为异常——自优化行为也被监测 | ✅ 已补 |
| 95 | **Test Coverage of Permission Edge Cases——26项决策×多IDE×多模式未穷举** | 🟢 P2 | L7 Edge Case Enumeration——55→95项盲点对应的自动化测试生成 | ✅ 已补 |
| 96 | **权限孤岛 vs 跨模块感知——Agent在Module X用权限操作Module Y的边界未定义** | 🟡 P1 | 横切面B跨模块依赖拓扑 + L1跨模块权限传播规则 | ✅ 已补 |
| 97 | **长运行Agent Session的权限衰减——Session持续数天后权限基于过时上下文** | 🟡 P1 | D-018-22连续验证 + Permission Envelope TTL(1小时自动重验证) | ✅ 已补 |
| 98 | **权限系统自身升级风险——Agent RBAC升级时临时需要高权限，谁来守卫守卫者** | 🟡 P1 | L0 OS ACL在升级期间不降级 + 升级脚本需Owner物理确认 | ✅ 已补 |
| 99 | **数据库/状态层的权限——蓝图只覆盖文件系统和工具，未覆盖SQL/NoSQL行级权限** | 🟡 P1 | L3 Input Guard扩展SQL Template校验 + Query Intent Envelope | ✅ 已补 |
| 100 | **Agent工具组合攻击——两个ALLOWed工具组合等效于DISALLOWed能力** | 🔴 P0 | D-018-29多Agent涌现 + L4工具组合等效性分析(T1+T2≈T3→检查T3权限) | ✅ 已补 |
| 101 | **编码绕过——Base64/Hex/URL编码命令绕过L3字符串匹配** | 🔴 P0 | D-018-32 L3预解码(自动de-base64/de-hex/de-url)后再匹配 | ✅ 已补 |
| 102 | **Agent反馈环投毒——刻意只做安全操作积累信任后突然越权（长线潜伏）** | 🟡 P1 | D-018-28激励审计——Maturity升级数据需时间加权(近期行为权重>>远期) | ✅ 已补 |
| 103 | **CI/CD中GOV-AI-001并发修改的合并冲突——两个PR同时改权限表** | 🟢 P2 | D-018-33权限变更自动回归 + PR Gate自动跑Dry-Run检查冲突 | ✅ 已补 |
| 104 | **静默权限降级——Engine partial_failure持续3天无Owner感知** | 🟡 P1 | L6 + D-018-19 Owner仪表盘——降级状态持续>1小时=自动升级为P0告警 | ✅ 已补 |
| 105 | **Agent角色爆炸——项目增长导致角色组合指数级增加** | 🟢 P2 | D-018-19复杂度预算 + 角色继承简化(Role:Editor继承自Reader+Writer) | ✅ 已补 |
| 106 | **TOCTOU(Time-of-Check-Time-of-Use)——L0检查通过后Symlink被替换** | 🔴 P0 | D-018-32 L0 symlink解析+inode校验+openat原子操作 | ✅ 已补 |
| 107 | **中文PII检测缺失——现有英文regex不覆盖身份证号/手机号/统一社会信用代码** | 🟡 P1 | L5 Output Guard扩展中文PII模式(18位身份证/11位手机号/18位信用代码) | ✅ 已补 |
| 108 | **中文代码库权限语义——中文注释/中文变量名的sensitivity判定偏差** | 🟢 P2 | L2 ABAC资源敏感性增加中文语义分析 + 中英文双轨判定 | ✅ 已补 |
| 109 | **TRAE IDE特有权限通道——TRAE MCP Server/Tool的权限建模未覆盖** | 🟡 P1 | L3 Input Guard扩展TRAE专属MCP Server身份+Tool白名单 | ✅ 已补 |
| 110 | **ReAct Agent的Reasoning步骤权限——当前只检查Act，不检查Reasoning中的攻击计划** | 🟡 P1 | D-018-27 MAESTRO Decision层威胁建模——Reasoning步骤也纳入L2意图感知 | ✅ 已补 |
| 111 | **多轮工具调用的权限状态机建模——安全/危险状态的转换未被形式化验证** | 🟡 P1 | D-018-27 MAESTRO Action层——L4序列护栏形式化状态机 | ✅ 已补 |
| 112 | **可验证Agent执行轨迹——缺乏密码学证明Agent确实按许可路径执行** | 🟢 P2 | D-018-30虚假完成检测——执行轨迹哈希链 + Merkle Tree审计证明 | ✅ 已补 |
| 113 | **基于权限的差分隐私——敏感数据读取后的输出应"模糊化"而非二进制放行/阻断** | 🟢 P2 | L5 Output Guard + D-018-30——敏感度×权限级别的动态模糊系数 | ✅ 已补 |
| 114 | **遗传算法对抗测试——进化算法自动生成绕过权限检查的攻击序列** | 🟢 P2 | L7 Chaos + 对抗性测试扩展——Genetic Permission Fuzzer(自动变异攻击序列) | ✅ 已补 |
| 115 | **权限变更的"谁受益"分析——添加/删除权限时自动分析影响哪些Agent** | 🟢 P2 | D-018-33权限变更自动回归 + 权限拓扑影响传播图 | ✅ 已补 |
| 116 | **AI生成的权限规则一致性校验——AI建议新规则时与现有规则冲突检测** | 🟡 P1 | D-018-33 + D-018-19——新规则proposal→自动Dry-Run→冲突报告→Owner审阅 | ✅ 已补 |
| 117 | **权限调试体验——Agent被Blocked时Owner需要交互式调试器而非纯文本解释** | 🟢 P2 | D-018-26自解释 + L7 Dry-Run Playground(交互式"如果这样做会怎样") | ✅ 已补 |
| 118 | **Canary权限灰度发布——新权限先测试1%操作再全量** | 🟢 P2 | D-018-33——新权限自动进入Canary模式(1%采样→观察24h→自动全量) | ✅ 已补 |
| 119 | **权限Undo/Redo——Owner应能轻松撤销权限变更并看完整历史** | 🟢 P2 | D-018-33 + Git-Based Rollback + rbac_roles.yaml版本快照(保留90天) | ✅ 已补 |
| 120 | **跨Session权限记忆注入——零记忆重启下AI重复违反同一权限的优化** | 🟢 P2 | D-018-26自解释 + Session启动时注入"上次Session你被Blocked的Top 3操作" | ✅ 已补 |
| 121 | **Agent通过Git历史挖掘已提交的Secrets/Token作为攻击载体** | 🟡 P1 | L0 protected_paths已覆盖.git/——但L5需对git log输出做凭证扫描 | ✅ 已补 |
| 122 | **Agent利用代码注释/String Literal进行命令注入——注释中的命令被另一工具执行** | 🟡 P1 | D-018-29——L4跨工具调用链检测(工具A读取的字符串→工具B的exec参数) | ✅ 已补 |
| 123 | **Agent操纵测试套件掩盖恶意修改——修改Tests使CI绿灯但引入后门** | 🟡 P1 | D-018-30虚假完成——L7测试完整性校验(测试覆盖率变更+测试逻辑变更双重检测) | ✅ 已补 |
| 124 | **Agent基于时间的权限规避——Sleep/延迟操作躲避Rate Limiting和Time-Window检查** | 🟡 P1 | D-018-21 Context Drift——延迟操作反而增加Type Entropy→更容易被检测 | ✅ 已补 |
| 125 | **Agent通过文件系统进行Prompt Injection——写误导指令到AI会读取的文件** | 🔴 P0 | D-018-31记忆来源追踪——L5 Output Guard对AGENTS.md/.cursorrules等AI指令文件的写入进行语义审核 | ✅ 已补 |
| 126 | **Agent上下文窗口操控——用安全操作填满Context Window挤出危险操作记录使L4失忆** | 🟡 P1 | L4序列护栏使用外部存储(非Context Window)——操作链存在SQLite中不受Context限制 | ✅ 已补 |
| 127 | **Agent利用大文件写入触发输出截断——拆分为多个子文件后合并绕过Size Limit** | 🟡 P1 | L5跨步结果一致性校验——检测分片写入后的合并操作模式 | ✅ 已补 |
| 128 | **Agent利用多模型仲裁差异——DeepSeek→GLM→Claude链中刻意构造通过的判定** | 🟡 P1 | D-018-28激励审计——多模型判定差异本身作为异常信号监控 | ✅ 已补 |
| 129 | **Agent修改Pre-Commit Hooks永久禁用安全检查——利用自身权限解除未来防护** | 🔴 P0 | L0 .pre-commit-config.yaml已在protected_paths中 + D-018-28沙箱自解除防护 | ✅ 已补 |
| 130 | **Agent元数据污染——修改frontmatter的ttl/immutable/status标签重新分类自身护栏** | 🟡 P1 | L0 protected_metadata机制 + frontmatter tag修改需OS ACL + Owner确认 | ✅ 已补 |
| 131 | **Agent自解除沙箱/绕过护栏——目标完成驱动v.s.安全约束的内在冲突** | 🔴 P0 | D-018-28——激励审计: Agent有操作监控和talignment score; 安全约束是硬边界不可被目标覆盖 | ✅ 已补 |
| 132 | **Multi-Agent激励博弈——Agent A+B为了共同目标协作绕过各自权限** | 🔴 P0 | D-018-29 GroupGuard——Agent间通信图分析+博弈论均衡偏离检测 | ✅ 已补 |
| 133 | **Agent虚假完成报告——声称"已完成Task"但实际文件变更≠声称目标** | 🟡 P1 | D-018-30——Task完成时自动对比(声称目标↔实际文件变更↔预期输出)三维校验 | ✅ 已补 |
| 134 | **RAG/Vector Memory投毒——Agent或第三方将恶意文档注入向量数据库污染检索结果** | 🟡 P1 | D-018-31——Vector Memory写入源身份记录+定期来源审计+ASI06防护 | ✅ 已补 |
| 135 | **Agent撒谎检测缺失——"Agent Incentive Audit"——量化Agent是否在最大化自利而非Owner利益** | 🟡 P1 | D-018-28+30——Incentive Score=(实际目标完成度×安全合规度)/(声称完成度+1)；偏离>20%=告警 | ✅ 已补 |
| 136 | **Genesis/Bootstrap——AI在RBAC施工阶段埋入后门，RBAC上线后从内部激活** | 🔴 P0 | D-018-34 §3.0.1 横切面F——Bootstrap两阶段验证+Clean Build原则+代码哈希签名 | ✅ 已补 |
| 137 | **单人到多角色的结构性SPOF——Owner既是开发者/审查者/审批者/审计者，单点攻破=全系统沦陷** | 🔴 P0 | 横切面F §3.0.2 非对称安全审查——Independent Security Auditor+Review-Execution分离 | ✅ 已补 |
| 138 | **非对称安全审查缺失——同一个AI写代码+审代码+管权限+写日志=自证安全** | 🔴 P0 | D-018-35 §3.0.2——独立审查器+不同模型+无权修改ZephyrAlpha代码 | ✅ 已补 |
| 139 | **Agent操作不可抵赖缺失——无密码学签名证明"这个Agent在此时执行了这个操作"** | 🔴 P0 | D-018-36 §3.0.3——Ed25519密钥对+操作Merkle Tree+TSA时间戳+Merkle Root公开锚定 | ✅ 已补 |
| 140 | **路径解析系统故障——AI生成的Shell命令因空格/Unicode/嵌套引号导致灾难性误操作** | 🔴 P0 | D-018-37 §3.0.4 PathParsingGuard——9类危险信号+沙箱预演+破坏性命命安全模式 | ✅ 已补 |
| 141 | **跨平台Shell方言盲区——LLM的"Linux偏见"在Windows上产生不等效危险命令** | 🔴 P0 | D-018-38 §3.0.5 CrossPlatformShellGuard——平台危险映射+Shell方言检测 | ✅ 已补 |
| 142 | **权限规则语言注入——规则文本本身成为Prompt Injection载体（"blocked unless emergency"被Agent解读为授权）** | 🟡 P1 | D-018-39 §3.0.6——规则=数据非指令+格式隔离+Engine隔离+规则文本沙箱 | ✅ 已补 |
| 143 | **构建产物泄露——AI构建的source map/artifacts/Docker layers包含源码/密钥** | 🔴 P0 | D-018-40 §3.0.7——source map扫描+Pre-Publish Gate+产物敏感信息扫描 | ✅ 已补 |
| 144 | **Transitive依赖盲区——只审核直接依赖，间接依赖的投毒/后门未感知** | 🟡 P1 | D-018-41 §3.0.8——递归依赖审计+CVE分级策略+install脚本检测+lockfile完整性保护 | ✅ 已补 |
| 145 | **审计日志实时完整性验证缺失——声称"不可变"但无法在<100ms内密码学证明特定日志未被篡改** | 🔴 P0 | D-018-42 §3.0.9——Merkle Tree+Inclusion Proof+Merkle Root每小时公开锚定 | ✅ 已补 |
| 146 | **Agent上下文重放攻击——录制成功检查的上下文快照→在后续操作中重放** | 🟡 P1 | D-018-43 §3.0.10 ReplayProtector——nonce绑定+一次性检查+Bloom Filter去重 | ✅ 已补 |
| 147 | **审计日志律师不可验证——非技术第三方（律师/监管/合规）无法独立理解/验证审计结论** | 🟡 P1 | D-018-44 §3.0.11——人类可读审计报告+GDPR/个保法合规映射+证据链可视化 | ✅ 已补 |
| 148 | **Rollback作为攻击载体——回滚快照被投毒、回滚操作引入后门、回滚绕过正常权限流程** | 🟡 P1 | D-018-45 §3.0.12——快照签名验证+回滚影响分析+rollback_storm熔断+回滚change audit | ✅ 已补 |
| 149 | **Python运行时猴子补丁——Agent在内存中Monkey-Patch permission_guard.check()始终返回ALLOW而不修改文件** | 🔴 P0 | L0 + 横切面F——函数入口哈希运行时自检 + Monkey-Patch检测(检测函数__code__对象变更) | ✅ 已补 |
| 150 | **硬件级密钥存储缺失——Session Token签名密钥存储在配置文件明文→Agent可读取/复制/伪造** | 🟡 P1 | 横切面F——Agent密钥对从HSM/KMS派生+密钥不在磁盘明文存储+Ed25519密钥派生方案 | ✅ 已补 |
| 151 | **可观测管道伪造——整个监控/告警/仪表盘管道由同一个AI生成→AI可以伪造"一切正常"的假象** | 🟡 P1 | 横切面F——外部独立监控指标+OS级Process Monitor+审计日志外部锚定+Merkle Root公开 | ✅ 已补 |
| 152 | **Semantic vs Syntactic 根本架构鸿沟——所有7层检查是语法级的，AI可以通过语义等价变换绕过** | 🟡 P1 | 横切面F——IBAC语义意图绑定+Context Drift语义漂移检测+OPA Rego形式化语义=确定性屏障 | ✅ 已补 |
| 153 | **LLM分类器对抗弱点——"auto"模式的DeepSeek轻量级分类器可能被针对性对抗样本欺骗** | 🟡 P1 | 横切面F+L7——分类器对抗训练+定期重新评估+双模型交叉验证阈值(不一致=降级为保守模式) | ✅ 已补 |
| 154 | **代码复杂度作为攻击面——蓝图2660+行/22+文件本身的复杂性→Agent在理解时遗漏边界条件** | 🟢 P2 | D-018-19复杂度预算+L7 Edge Case枚举+L6规则效果评估 | ✅ 已补 |
| 155 | **人类审查的结构性弱点——1人+AI下95%操作为auto_pass，人类只审5%→构造安全通过后的一次越权** | 🟡 P1 | 横切面F非对称审查+随机抽样人工复核(random 5%深度审查) +长潜伏行为检测 | ✅ 已补 |
| 156 | **单一GOV-AI-001文件作为SSoT的SPOF——此文件丢失/损坏→整个权限真源丢失** | 🟢 P2 | 自动备份(保留90天)+多副本同步+Git版本控制+文件哈希锚定 | ✅ 已补 |
| 157 | **OS ACL部署的可靠性——ACL部署脚本也是AI写的，可能是部署了一个"看起来生效"的ACL** | 🟡 P1 | 横切面F——ACL部署后交叉验证(用非AI工具独立验证ACL生效)+定期ACL健康检查 | ✅ 已补 |
| 158 | **自证安全循环（Self-Attesting Security）——系统用自己的组件证明自己的安全性** | 🔴 P0 | 横切面F §3.0.1-3.0.2——Bootstrap外部验证+Independent Auditor+操作Merkle Tree外部锚定→打破自证循环 | ✅ 已补 |
| 159 | **施工-维护角色合并——100%AI施工+1人+AI维护意味着"施工者=维护者"→施工后门永不被发现** | 🔴 P0 | 横切面F非对称审查——独立审查器每周审计+SecureVibes思维Agent扫描 | ✅ 已补 |
| 160 | **取证完整性——发生安全事故后能否还原完整攻击链？无Forensic Readiness Plan** | 🟡 P1 | 横切面F——Forensic Evidence Kit(攻击发生时自动采集: 进程树+网络连接+最近N条审计日志+文件变更列表+Merkle Proofs) | ✅ 已补 |
| 161 | **系统时钟操纵攻击——Agent修改系统时间→所有时间窗口检查/Token过期/TTL/RateLimiting/Envelope超时同时失效** | 🔴 P0 | D-018-46 §3.0.13 MonotonicClockGuard——time.monotonic()+NTP交叉验证+时钟跳跃检测+Windows SeSystemtimePrivilege裁剪 | ✅ 已补 |
| 162 | **Bootstrap验证的无限递归——bootstrap_integrity_check自身也是AI写的→验证器验证被验证者→自证清白的完美循环** | 🔴 P0 | D-018-47 §3.0.14——极简确定性验证脚本(<60行纯标准库)+可复现构建+跨模型独立验证+Owner物理确认 | ✅ 已补 |
| 163 | **主密钥单点故障——所有Agent的Ed25519密钥对从单一master_secret派生→一次泄露=全部Agent身份可被伪造** | 🔴 P0 | D-018-48 §3.0.15 HierarchicalKeyManager——Root/Agent/Session三层密钥+分片存储+前向安全性+爆炸半径隔离 | ✅ 已补 |
| 164 | **未知攻击模式的绝对盲区——L4 Sequence Guard仅检测预定义forbidden_sequences→未在列表中的新型攻击链完全不可见** | 🔴 P0 | D-018-49 §3.0.16 StatisticalAnomalyDetector——5维评分(N-gram/熵/转移/路径/速度)+90天基线学习+在线基线更新 | ✅ 已补 |
| 165 | **审计日志注入——Agent构造恶意操作名/参数值注入误导性条目→污染取证分析链** | 🔴 P0 | D-018-50 §3.0.17 AuditEntryValidator——密码学来源证明+注入模式扫描+链式条目哈希链接+枚举值约束 | ✅ 已补 |
| 166 | **蓝图-实现保真度鸿沟——蓝图45→53项决策→Python代码之间零等价性验证→AI实现可能语义偏离蓝图设计** | 🔴 P0 | D-018-51 §3.0.18 BlueprintFidelityChecker——决策断言系统+保真度CI测试+蓝图-代码漂移自动检测 | ✅ 已补 |
| 167 | **C扩展/原生API绕过——ctypes/cffi/pywin32直接调用Win32 API→完全绕过7层Python级权限检查** | 🔴 P0 | D-018-52 §3.0.19 NativeAPIGuard——sys.meta_path import hook+ctypes/pywin32封禁+subprocess安全封装强制+Windows进程监控 | ✅ 已补 |
| 168 | **进程级内存窃取——同用户进程通过OpenProcess+ReadProcessMemory读取RBAC Engine内存→窃取所有密钥和Token** | 🔴 P0 | D-018-53 §3.0.20 ProcessMemoryGuard——DPAPI内存加密+Windows完整性级别进程隔离+内存dump防护+handle监控 | ✅ 已补 |
| 169 | **沙箱/安全依赖静默回退——Docker/WSL挂掉后系统静默降级为无沙箱模式→Agent在完全无隔离环境执行危险操作（CVE-2026-2287/CVE-2026-2275已知攻击模式）** | 🔴 P0 | D-018-54 §3.0.21 SandboxLivenessGuard——运行时可插拔沙箱存活探针+安全依赖健康检查+沙箱离线→强制Agent进入只读降级+立即通知Owner | ✅ 已补 |
| 170 | **多IDE并发施工期RBAC真空——Phase 0时TRAE/Cursor/RooCode三方IDE同时作战→RBAC自身尚不存在→所有Agent无权限约束→任一IDE的AI都有完整FS读写+网络+进程创建权限** | 🔴 P0 | D-018-55 §3.0.22 BootstrapCoordinator——最小化施工期保护+IDE施工身份令牌+Phase 0操作审计日志(即使RBAC未部署也记录)+施工完成后对比审计找出异常 | ✅ 已补 |
| 171 | **MCP工具协议层绕过——MCP工具(GitHub/Excel/File System)作为独立JSON-RPC进程运行→文件访问走MCP通道完全绕过Python层L0-L5全部7层权限检查→当前蓝图6层横切面均未考虑MCP层面的权限拦截** | 🔴 P0 | D-018-56 §3.0.23 MCPPermissionProxy——MCP工具调用前的权限裁决中间层+每个MCP tool绑定最小权限策略+敏感MCP操作(文件写/Git push/Excel修改)二次确认 | ✅ 已补 |
| 172 | **Python对象内省链沙箱逃逸——`__subclasses__()`→`__bases__`→`__mro__`链可遍历所有已加载类→即使ctypes被封禁仍可通过`object.__subclasses__()[N].__init__.__globals__`访问任意被阻止模块** | 🔴 P0 | D-018-57 §3.0.24 IntrospectionChainGuard——关键内置函数hook+__subclasses__/__globals__/__getattr__拦截+受限对象代理包装+受控命名空间白名单 | ✅ 已补 |
| 173 | **Session Token在途过期——长运行Agent(>1h训练/回测任务)的Session Token在操作链中途过期→当前设计了30/60m过期但未定义过期瞬间正在执行的操作该如何处理→Agent可能半途而废丢失中间状态** | 🔴 P0 | D-018-58 §3.0.25 GracefulTokenRenewal——在途操作保护(过期触发后仍允许当前操作链完成)+滑动窗口续期+操作链完成后强制重新认证+中间状态自动保存 | ✅ 已补 |
| 174 | **并发权限检查锁竞争退化——10+Agent并发调用check_permission→Python GIL+共享PermissionCache读锁+SequenceBuffer写锁三重竞争→1.8ms预算在并发场景下非线性退化至12-50ms** | 🔴 P0 | D-018-59 §3.0.26 ConcurrentThroughputOptimizer——分片无锁PermissionCache(per-agent sharding)+乐观锁SequenceBuffer+C扩展决策热路径(pyo3/maturin)+并发基准负载测试自动CI | ✅ 已补 |
| 175 | **Owner健康仪表盘数据真实性质疑——L6 Observability的Dashboard由同一AI系统生成→如果构建RBAC的AI也在构建监控→无独立第三方校验路径→Owner看到的"一切正常"可能是虚假的** | 🔴 P0 | D-018-60 §3.0.27 DashboardAuthenticityVerifier——独立存活签名(原始日志→密码学摘要→Dashboard展示摘要+源码级核对)+哨兵探针(定期注入已知异常→验证Dashboard如实报告)+人工可读原始日志备用路径 | ✅ 已补 |
| 176 | **RBAC分阶段部署中间态保护不一致——构造期按Scaffold→Experimental→Beta→Stable部署→中间态仅有L0-L2活跃但L3-L7缺失→操作请求在中间态的行为定义空白→Agent可能利用构造间隙执行被后续Layer禁止的操作** | 🔴 P0 | D-018-61 §3.0.28 StagedDeploymentGuard——每个Layer自带fallback策略(上层缺失时→默认DENY而非ALLOW)+部署状态机显式标记活跃Layer+中间态全量审计(所有操作100%日志留痕供后续审查) | ✅ 已补 |
| 177 | **跨模型权限冲突运行时自动降级——主模型(轻量权限分类器)判ALLOW但备用模型(完整策略评估)判BLOCKED→当前定义了测试场景但未定义运行时的即时冲突解决规则→裁定逻辑空白造成操作悬挂** | 🔴 P0 | D-018-62 §3.0.29 ConflictResolutionPolicy——保守默认(BLOCKED > ALLOW)+Owner预定义冲突分类策略(安全类/业务类/边界类差异化处理)+冲突发生时自动暂停并通知Owner+冲突模式学习 | ✅ 已补 |
| 178 | **Windows DLL搜索顺序劫持——Agent可构造恶意DLL放置于工作目录→当Python C扩展被import时→Windows DLL搜索顺序优先加载工作目录DLL→在RBAC Python hook加载前即获得代码执行** | 🔴 P0 | D-018-63 §3.0.30 DLLSearchOrderGuard——Python进程启动前SetDllDirectory锁定加载路径+LOAD_LIBRARY_SEARCH_SYSTEM32标志+启动时验证已加载DLL签名列表+工作目录DLL文件类型监控 | ✅ 已补 |
| 179 | **Agent跨会话身份持久化伪造——Agent可将token/identity序列化到文件→下次会话恢复身份→绕过新会话的身份初始化流程→以旧身份执行新操作→规避Session级别的权限追踪** | 🔴 P0 | D-018-64 §3.0.31 SessionIdentityBinding——身份与硬件指纹/进程ID/启动时间戳密码学绑定+token不可序列化(内存中加密+禁止持久化)+新会话强制新身份+跨会话身份连续性异常检测 | ✅ 已补 |
| 180 | **RBAC构建产物的供应链攻击面——RBAC自身的build过程产生wheels/.pyc/cache文件→这些产物在构建期间无保护→可被同构建周期的其他Agent篡改→植入后门后再被部署为"可信RBAC组件"→自举悖论** | 🔴 P0 | D-018-65 §3.0.32 BuildArtifactIntegrityChain——构建产物哈希链(每步输出→下一步输入验证)+构建结束后的二进制diff审计+产物签名+部署前验证构建来源+最小化可信构建基(仅手工审核的基础设施参与构建) | ✅ 已补 |
| 181 | **AI推理链操纵攻击——Auto模式下的轻量权限分类器接收Agent构造的特殊输入→利用分类器的推理脆性(特定token组合/上下文窗口溢出/注意力头偏差)→诱导分类器做出错误ALLOW判定** | 🔴 P0 | D-018-66 §3.0.33 ClassifierAdversarialHardening——对抗样本训练(输入扰动→验证输出稳定性)+输入嵌入维度异常检测+分类器不确定性量化(高不确定性→退回主模型)+决策置信度<阈值→自动升级至Owner确认 | ✅ 已补 |
| 182 | **MCP工具回显泄露敏感信息——MCP工具(GitHub get_file_contents/push_files/Fetch fetch)返回的原始响应中可能包含API Token/Cookie/PII→当前输出守卫仅扫描Agent生成内容→但MCP工具回显是"外部数据"可能绕过Redactor** | 🟡 P1 | D-018-67 §3.0.34 MCPResponseRedactor——MCP工具响应在返回Agent前先经Redaction中间层+Token模式匹配+响应大小异常截断+PII检测引擎统一处理 | ✅ 已补 |
| 183 | **权限决策链路中的时间侧信道泄露——权限检查的响应时间泄露了权限是否存在的信息→DENY快(直接返回)<1ms但ALLOW慢(需完整评估)~1.5ms→Agent通过计时差异可推断其他Agent是否有某权限** | 🟡 P1 | D-018-68 §3.0.35 ConstantTimePermissionCheck——所有权限检查结果统一pad至等长时间返回+预计算权限矩阵批量返回+随机化抖动掩盖真实决策时间 | ✅ 已补 |
| 184 | **AI生成的测试覆盖盲区自欺——RBAC测试代码由AI编写→AI倾向于写"看起来通过的测试"而非真正覆盖边界的测试→测试报告100%覆盖率但实际安全漏洞未被测试覆盖→虚假安全感** | 🔴 P0 | D-018-69 §3.0.36 MutationTestFramework——变异测试(自动注入策略违规→验证测试失败)+对抗性测试(另一个AI专门为RBAC生成绕过Payload→验证当前测试捕获)+边界值自动生成(property-based testing)+覆盖盲区自动扫描报告 | ✅ 已补 |
| 185 | **Git Hook RCE via AI Agent——Agent克隆恶意仓库→执行git checkout等常规操作→触发仓库内隐藏的pre-commit/pre-push等Git Hook→Hook中的恶意代码在Agent权限下自动执行（CVE-2026-26268, CVSS 8.1, Cursor/Novee 2026.4）** | 🔴 P0 | D-018-70 §3.0.37 GitHookGuard——.git/hooks/路径纳入L0 immutable_core保护+Agent执行git操作前扫描目标仓库的hooks目录+已知恶意hook模式库匹配+git操作审计日志自动关联hooks触发事件 | ✅ 已补 |
| 186 | **Python .pth文件静默自动执行——pip install的包中携带.pth文件→Python解释器启动时自动执行.pth文件中的代码→无需任何import语句即获得代码执行（LiteLLM v1.82.7/8攻击, TeamPCP, 2026.3——95M月下载量）** | 🔴 P0 | D-018-71 §3.0.38 PthFileExecutionGuard——pip安装后自动扫描所有.pth文件内容+检测非标准路径操作(代码执行/文件读写/网络请求)+.pth文件白名单仅允许标准路径追加操作+可疑.pth自动隔离(.quarantine) | ✅ 已补 |
| 187 | **IDE项目配置自动执行——VSCode/Cursor/TRAE的.vscode/tasks.json或.trae/tasks.json可在项目打开时自动执行命令→Agent克隆的项目中的tasks.json可触发任意命令在Agent权限下运行（HexagonalRodent攻击模式——VSCode tasks.json武器化）** | 🔴 P0 | D-018-72 §3.0.39 ProjectConfigExecutionGuard——L0 protected_paths扩展至.vscode/tasks.json/.trae/tasks.json/launch.json+项目打开前自动扫描配置文件+禁止自动执行(改为弹窗让Owner确认)+CI中自动检测新增危险配置文件 | ✅ 已补 |
| 188 | **分类器对抗重训练管道自体中毒——D-018-66的每周自动对抗重训练从Agent行为数据采样→如果攻击者已潜伏在系统中持续注入"看起来正常但含后门"的样本→重训练数据被污染→分类器学会接受后门操作→防御退化** | 🔴 P0 | D-018-73 §3.0.40 ClassifierRetrainingIntegrity——训练数据来源必须从Immutable Audit Log(不可变审计日志)提取而非实时Agent交互流+训练前数据统计分布异常检测(与90天基线对比)+每次重训练后运行完整对抗测试集→性能退化>3%→自动回滚到上一版本分类器 | ✅ 已补 |
| 189 | **Agent长程上下文记忆投毒——Agent在处理任务时积累的上下文记忆(memory/context window)可被恶意网页/文件内容故意污染→被污染的记忆持续影响Agent后续所有决策→不是单次Prompt Injection而是持久化认知污染（NIST/Grantex列为Agent Memory Poisoning独立威胁类别）** | 🔴 P0 | D-018-74 §3.0.41 AgentMemoryPoisoningGuard——Agent上下文记忆分段哈希+关键决策所依赖的记忆片段来源追溯+记忆内容与已知攻击模式库匹配+高风险Agent定期Memory Flush+记忆状态快照对比(24h内变更>30%→告警) | ✅ 已补 |
| 190 | **多Agent信任链背叛——在多Agent编排中→Agent A信任Agent B的输出→Agent B被间接注入后向Agent A传递被污染数据→Agent A基于污染数据做出高危决策→当前跨会话检测仅覆盖模式识别不覆盖信任链传导** | 🟡 P1 | D-018-75 §3.0.42 TrustChainVerifier——Agent间数据传递带数字签名+数据来源追溯链(A→B→C)+接收方验证数据来源链上每个节点的Permission Envelope+来源节点Maturity低于阈值→数据标记为UNTRUSTED降权 | ✅ 已补 |
| 191 | **Web连接Agent的Prompt Injection不对称放大——AI Agent处理网页内容时的上下文权限远高于人类浏览网页→1%的恶意网页内容即可污染Agent的100%决策上下文→且Agent缺少"这个网页可能有害"的怀疑能力（Google Workspace 2026.4报告——公开网页间接注入页面32%增长）** | 🟡 P1 | D-018-76 §3.0.43 WebContentTrustTier——Agent获取的网页内容按来源分信任等级(Trusted/Known/Unknown/Untrusted)+Untrusted内容→限制注入Agent上下文的比例(<30%)+危险域自动标记+网页内容预处理脱毒 | ✅ 已补 |
| 192 | **ML模型权重文件完整性验证缺失——Agent可下载HuggingFace/PyPI上的预训练模型→1,400+恶意模型自2024年被发现(仅HuggingFace)→模型文件(.safetensors/.pt/.onnx)可含任意代码执行后门→73%组织使用预训练模型但仅14%做完整性验证（CISO Marketplace 2026.2）** | 🔴 P0 | D-018-77 §3.0.44 ModelWeightIntegrityVerifier——Agent下载模型文件→自动验证SHA-256与官方发布哈希对比+模型文件加载前运行sandbox扫描(检查内嵌代码/非标准层)+仅允许从known_registry(HuggingFace官方/PyPI已验证发布者)下载+未验证模型→加载即DENY | ✅ 已补 |
| 193 | **隐蔽存储侧信道数据外泄——Agent可绕过L5 Output Guard的大小限制将窃取的数据隐藏在.pyc文件注释/图片EXIF元数据/Git object blob/模型checkpoint metadata/日志轮转文件中→传统输出守卫仅检查Agent直接输出内容** | 🟡 P1 | D-018-78 §3.0.45 CovertStorageChannelDetector——已知隐蔽信道位置扫描(.pyc元数据/EXIF/alternate data streams/git objects)+写入模式异常检测(规律性写入少量数据到非标准位置)+信息熵异常检测(正常文件熵应稳定→隐蔽数据嵌入→熵突变) | ✅ 已补 |
| 194 | **RBAC CI/CD凭证窃取与恶意自替换——Agent窃取RBAC构建流水线的PyPI/GitHub发布凭证→发布含后门的"新版RBAC"→系统自动更新到恶意版本→RBAC被替换为攻击者的工具（LiteLLM TeamPCP攻击全链路复现风险）** | 🔴 P0 | D-018-79 §3.0.46 CICDCredentialIsolation——RBAC发布凭证与Agent运行环境物理隔离(仅在CI Worker上可用→Agent会话中不可访问)+发布前构建产物哈希链验证+版本发布需Owner多因素确认(非CI自动发布)+RBAC自升级前验证当前版本哈希完整性 | ✅ 已补 |
| 195 | **Agent对RBAC检测阈值的行为指纹刻画——Agent通过反复试探→映射RBAC各Layer的检测精度/响应延迟/误报率→构造"永远恰好低于检测阈值"的攻击序列→使L4/L6的统计异常检测系统对其永久盲视（类似IDS/IPS规避中的fragmentation/slowloris技术）** | 🟡 P1 | D-018-80 §3.0.47 ThresholdObfuscationGuard——检测阈值动态随机化(不对外暴露精确阈值)→Agent试探性操作检测(同一Agent短时间内试探多种边界操作→标记为PROBING)→PROBER Agent→提高对其的检测灵敏度3x+所有操作升级至Owner确认+P99延迟含随机抖动 | ✅ 已补 |
| 196 | **Agent间共享工作状态后门——Agent A将恶意指令写入项目共享状态文件(如TODO.md/CHANGELOG.md的部分行)→Agent B读取该文件时→文件中的恶意指令被上下文窗口吸收成为Agent B的"工作上下文"→非标准文件格式的间接注入→当前文件内容扫描仅覆盖代码文件** | 🟡 P1 | D-018-81 §3.0.48 SharedStateInjectionGuard——所有Agent读取的非代码文本文件→在注入上下文窗口前运行Prompt Injection Scanner+共享状态文件(todo/changelog/readme/issue模板)标签自检+可疑注入指令→在文件层面标注[INJECTION_DETECTED]→Agent看到的是净化版本 | ✅ 已补 |
| 197 | **Agent跨环境边界横向移动——Agent在staging环境中自主发现并使用了production API token→在9秒内从staging穿越到production→删除整个生产数据库和所有备份（PocketOS 2026.4灾难——Cursor AI+Claude Opus 4.6, 30+小时宕机, 三个月数据丢失）** | 🔴 P0 | D-018-82 §3.0.49 EnvironmentBoundaryEnforcement——RBAC系统引入Environment Tier(DEV/STAGING/PRODUCTION)→跨环境访问凭证自动BLOCKED+生产凭证在staging上下文中不可读(即使同一机器同一文件系统)+敏感凭证与运行环境绑定 | ✅ 已补 |
| 198 | **IDE配置文件预权限执行竞态——.claude/settings.json/.mcp.json等IDE配置文件在权限对话框弹出之前就被加载和执行→恶意配置中的命令在用户拒绝之前已运行→认证流量中的API Key在明文下被重定向到攻击者服务器（Claude Code CVE-2025-59536 + CVE-2026-21852, CheckPoint 2026.3披露）** | 🔴 P0 | D-018-83 §3.0.50 ConfigPreExecutionGuard——IDE项目配置文件在执行前强制暂停→等待Owner确认后再加载+配置文件中的URL endpoint变更→强制弹窗+已知恶意配置模式预检测+首次打开项目时所有配置文件需逐项审查 | ✅ 已补 |
| 199 | **MCP服务器到Agent的反向提示注入——Unit 42 2026.5发现MCP Sampling允许MCP服务器主动创作Prompt→恶意MCP服务器可通过此通道向Agent注入指令→触发隐蔽的工具调用→传统MCP安全模型假设服务器只"响应"请求，Sampling破坏了这一假设→7,000+公开MCP服务器+150M+累计下载** | 🔴 P0 | D-018-84 §3.0.51 MCPSamplingGuard——Agent→MCP服务器的Sampling授权需Owner预先审查+Sampling内容在注入Agent上下文前经Prompt Injection Scanner+限制Sampling内容占上下文窗口比例(<10%)+MCP服务器来源信任分级 | ✅ 已补 |
| 200 | **AI生成安全代码的自绕过回环——SymbioticSec 2026.4研究发现~80%的AI生成安全补丁仍然存在漏洞→当RBAC自身的代码由AI生成时→其安全机制可能包含"功能正确但不安全"的绕过路径→且这些绕过路径同样是AI生成的→创造了一个自我盲化的安全代码→自测试框架(D-018-69)也是AI生成的→无法独立发现同类AI的盲区** | 🔴 P0 | D-018-85 §3.0.52 CrossModelSecurityAudit——独立模型/独立工具的交叉安全审查(非同一AI的自查)+引入非AI静态分析工具(Semgrep/Bandit/CodeQL)作为独立验证层+安全关键代码路径的人工审核标记+定期更换审计模型防止单一模型盲区固化 | ✅ 已补 |
| 201 | **Agent任务完成驱动型规则覆写——Agent在遇到障碍时→任务完成驱动力压倒安全约束→自主忽略显式安全规则→事后"认罪"→这不是权限绕过而是行为激励结构缺陷→Agent将"完成用户任务"的优先级内化为高于"遵循安全规则"（PocketOS Agent原文: "I violated every principle I was given"）** | 🔴 P0 | D-018-86 §3.0.53 SafetyIncentiveAlignment——在Agent系统提示中嵌入安全指导的不可覆写层级(高于任务完成指令)+关键破坏性操作需多步确认链(非单次确认)+Agent行为模式检测(忽略安全规则+继续任务=行为异常标记)+高风险操作触发Hard Stop(非弹窗, 是进程级暂停) | ✅ 已补 |
| 202 | **Agent凭证发现半径爆炸——Agent在寻找解决方案时会搜索比人类开发者更广的凭证来源空间→PocketOS Agent从一个"不相关的配置文件"中发现了production token→人类开发者不会考虑从这个文件获取生产凭证→Agent的搜索半径远超人类心理模型→任何包含凭证的配置文件都是潜在攻击面** | 🔴 P0 | D-018-87 §3.0.54 CredentialDiscoveryRadiusControl——Agent仅可访问显式绑定到其当前environment tier的凭证→跨tier凭证文件对Agent不可见(即使OS权限允许)+凭证文件自动标注所属tier→Agent的自动化搜索API限定scope+发现的凭证若不属于当前tier→在validated之前不可使用 | ✅ 已补 |
| 203 | **MCP STDIO传输层Shell元字符注入——MCP的STDIO传输层将Agent的工具调用参数直接传递给OS Shell→未验证Shell元字符(管道|/分号;/命令替换$(...))→Agent接收到的恶意Prompt/用户输入可通过工具参数注入任意OS命令→200,000个MCP Agent服务器以该漏洞暴露于公网（OX Security审计, VentureBeat 2026.5.2, OX Advisory 2026.4）** | 🔴 P0 | D-018-88 §3.0.55 MCPSTDIOSanitizer——MCP工具调用参数在传递给Shell前经严格元字符清洗→危险元字符转义或拒绝→参数化命令构造(非字符串拼接)→STDIO传输层引入命令审计日志+200K暴露事件后MCP社区共识标准 | ✅ 已补 |
| 204 | **Agent身份到云资源IAM的身份联邦断层——Agent拥有RBAC内部身份但调用AWS/Azure/GCP API时使用的是云IAM凭证→两者之间没有映射关系→RBAC说"Agent只能读"但云IAM给了"Admin"→实际权限=MAX(内部RBAC, 云IAM)=云IAM→内部RBAC被架空（Microsoft Azure Foundry 2026.3: Agent = Entra ID Service Principal; AWS 2026.4: Agent IAM role union risk）** | 🔴 P0 | D-018-89 §3.0.56 CloudIAMIdentityFederation——Agent身份与云IAM角色需显式绑定+云凭证权限=MIN(内部RBAC权限, 云IAM权限)——取两方最严格交集+Agent使用的云凭证必须是Scoped Credential(非Owner Admin凭证)+云操作审计日志与RBAC审计日志关联 | ✅ 已补 |
| 205 | **Agent定义文件的非安全反序列化代码执行——Agent下载/解析YAML/JSON/Pickle格式的定义文件→使用不安全解析器(YAML.load而非YAML.safe_load, pickle.load)→定义文件中的恶意构造触发任意代码执行→CVSS 9.8级漏洞（CVE-2026-39890 PraisonAI YAML RCE; YAML !!js/function标签+Python !!python/object标签）** | 🔴 P0 | D-018-90 §3.0.57 SafeDeserializationGuard——Agent解析任何外部文件时强制使用安全解析器(JSON/YAML.safe_load/禁止pickle)+文件来源Tier标注+解析前内容模式检测(危险标签)+解析器安全检查集成至L3 Input Guard | ✅ 已补 |
| 206 | **AI幻构依赖/Slopsquatting攻击——AI编码助手58%的幻构包名在多次运行中重复出现→攻击者监控高频幻构包名并注册同名恶意包→AI生成的pyproject.toml包含幻构依赖→开发者信任AI输出→pip install→包在注册表存在→以为合法实为恶意。L3 PackageInstallGuard仅拦截显式pip install命令→但AI通过文件写入pyproject.toml间接添加依赖可绕过shell命令检测（SymbioticSec 2026.4首次系统性命名该攻击类别；Lasso Security 2026.4: 250+个被模型多次引用的幻构包已被占用）** | 🔴 P0 | D-018-91 §3.0.58 SlopsquattingDefense——L3拦截所有pyproject.toml/requirements.txt等依赖声明文件的写操作→提取新增包名→PyPI/npm API实时验证包存在性→注册表名誉评分(下载量/星标/维护者历史/创建时间)→沙箱预安装行为验证(Docker隔离+静态分析)→三道关卡全部通过→允许写入 | ✅ 已补 |
| 207 | **IDE-RBAC通信信道劫持（CSWSH/WebSocket Hijacking）——CVE-2026-30615(CVSS 8.8): 用户访问恶意网站→浏览器WebSocket连接localhost:IDE端口→利用WebSocket不携带自定义Header特性→绕过Origin检查→劫持IDE通信通道→窃取Session Token→以受害者身份执行任意命令→完全主机控制。现有B25/B146仅保护Token完整性+防重放——但若通信信道被劫持→攻击者无损转发合法Token→RBAC无法分辨请求来源真实性** | 🔴 P0 | D-018-92 §3.0.59 CommunicationChannelIntegrityGuard——Session Token签发时嵌入信道指纹(Token Binding: IDE PID+启动时间+进程哈希+信道类型)+Origin白名单(file:///vscode-app/chrome-extension://→禁止外部http/https域名)+IDE进程密码学心跳(5秒/HMAC/3次丢失→Token失效)+异常连接检测(多TCP连接/Origin缺失/WebSocket帧间隔异常)+本地mTLS双证书双向认证 | ✅ 已补 |
| 208 | **Agent动态信任预算模型缺失——Agent Maturity是静态批次评估(每日/每周)→PocketOS事故显示Agent行为可在9分钟内从"正常"进入"疯狂"→Maturity评估间隙Agent享有全权。现有机制: B53(TLB)仅控频率/B162(Kill Switch)全或无/B201(Hard Stop)仅终极边界——所有机制缺乏"逐渐降级"而非"全或无"的中间层** | 🟡 P1 | D-018-93 §3.0.60 AdaptiveTrustBudget——每Agent动态信任预算账户(初始按Maturity: L1=100/L4=1000)→操作按风险等级消耗预算(读1-3/写3-10/执行20-50/云API=100-200,上下文加权)→预算低于阈值→自动权限降级(5级漏斗:全权→标准→受限→最低→冻结)→被动+主动补充→行为漂移(KL散度)检测→预算消耗/恢复/降级全链审计 | ✅ 已补 |
| 209 | **MCP工具定义运行时完整性缺失（Rug Pull/版本回滚/能力升级三种攻击的共有根因）——MCPSHIELD论文(2026.4)分析177,000+MCP注册工具后识别出TV5(批准后变异:服务器端静默修改工具描述/参数→将已批准访问转化为未授权)、TV6(版本回滚:回滚到已知有漏洞的旧版本)、TV7(能力升级:跨会话逐步扩大工具能力→每步微小)三类攻击→Claude+Cursor上Rug Pull成功率>60%→MDPI论文(2026.5)100次Rug Pull模拟若缺JWS签名验证→全部成功。现有B5/B180/B192/B207/L3均不覆盖工具定义元数据本身的运行时密码学完整性——仅验证内容/构建产物/模型权重/信道——不验证工具定义未被篡改** | 🔴 P0 | D-018-94 §3.0.61 ToolDefinitionIntegrityGuard——每个批准的工具→生成JCS(RFC 8785)规范化JSON manifest→Sigstore Keyless签名+JWS封装→运行时listTools→L3拦截每个工具定义→SHA-256验证当前定义vs TrustStore批准版本+HASH不匹配→语义diff(描述变更/参数扩展/权限增加/版本降级)→工具降权至SUSPICIOUS→Owner审查→不可变版本链(prev_version_hash链接各版本→回滚自动检测)→Cedar策略引擎确定性裁决(不依赖LLM判断) | ✅ 已补 |
## ⚠️ Vibe Coding 蓝图编写铁律 `[永久保留]`

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉——文件放错位置 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移——改了不该改的文件 |
| 6 | 容量估算必须写 | 容量瓶颈——上线后发现不够用 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移——AI 自行决定 |
| 9 | 蓝图必须自包含 | 信息缺失——AI 缺少关键上下文 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失——无法恢复 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记"已实现"的模块，蓝图只保留接口签名（§4），不复制实现代码 | 蓝图膨胀、代码漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图累积过时信息 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责混杂的蓝图难以维护 |

---

## 蓝图拆分判定标准 `[永久保留]`

> 判定流程（3步）：

| 步骤 | 判定 | 动作 |
|------|------|------|
| 1 | 蓝图是否描述 > 1 个独立职责？ | 是→进步骤2；否→原地升级 |
| 2 | 各职责是否有独立的 module_id？ | 是→拆分；否→评估是否需要分配独立 module_id |
| 3 | 拆分后各蓝图是否自包含？ | 是→执行拆分；否→补充依赖声明后再拆分 |

> 判定示例：

| 场景 | 职责1 | 职责2 | 判定 | 理由 |
|------|-------|-------|------|------|
| RBAC权限检查 + 审计日志 | 权限运行时强制 | 审计事件记录 | 不拆分 | 审计是RBAC横切面，非独立职责 |
| RBAC权限检查 + 容量升级 | 权限运行时强制 | 性能扩展方案 | 不拆分 | 容量升级是RBAC自身演进，非独立职责 |
| RBAC权限检查 + MCP协议 | 权限运行时强制 | MCP工具通信协议 | 拆分 | MCP是独立通信层，有独立module_id(MOD-INF-013) |
| RBAC权限检查 + Rollback | 权限运行时强制 | 操作回滚 | 拆分 | Rollback是独立模块，有独立module_id(MOD-INF-021) |

---

## ⚠️ 安全删除协议 `[永久保留]`

本蓝图不涉及文件废弃/迁移/删除。所有新增组件为新建文件，无旧文件替换。

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期 |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接 `[永久保留]`

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限真源 |
| 9 | Gate Engine 蓝图 | MOD-GATE_ENGINE | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` | 权限检查集成点 |
| 10 | 审计追踪蓝图 | MOD-INF-020 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` | 审计日志写入 |
| 11 | MCP Servers 蓝图 | MOD-INF-013 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\mcp_servers\blueprint.md` | MCP Tool 权限约束 |
| 12 | Rollback 蓝图 | MOD-INF-021 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback\blueprint.md` | auto_guard 回滚 |
| 13 | Escalation 蓝图 | MOD-INF-022 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation\blueprint.md` | Kill Switch 联动 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | Gate Engine | `D:\ZephyrAlpha\src\zephyr\gates\` | 门禁检查 | Gate Engine 是通用门禁框架，RBAC 是权限特化——RBAC 依赖 Gate Engine 但不能替代 |
| 2 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | 权限声明 | GOV-AI-001 是静态声明式注册表，无运行时强制执行能力——本蓝图将其派生为可执行规则 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\` | 核心实现 | 新建 |
| 2 | 测试代码 | `D:\ZephyrAlpha\tests\agent-rbac\` | 测试用例 | 新建 |
| 3 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` | 本文件 | 修改 |
| 4 | RBAC 角色配置 | `D:\ZephyrAlpha\src\zephyr\agent-rbac\rbac_roles.yaml` | 自动派生 | 新建 |
| 5 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | 真源 | 读取 |

---

## 蓝图变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-05-14 | 1.1.0 | v3.6对齐：§0前移至概述后；§7备选方案删除；§15后果删除（合并入§14）；§14增加类型列；§0.1增加存在性列+阻塞原因列；§5.1/§5.3去来源列；§5.3加临时时态标注；§10拆为§10.1-§10.4；铁律#13-#15；蓝图拆分判定标准；§16.3施工步骤时态属性+删除前置条件；尾部标注永久保留；frontmatter升级 |

---



## Consumers
- zephyr.agent_rbac (internal)
