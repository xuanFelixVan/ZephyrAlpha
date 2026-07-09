---
module_id: MOD-INF-020
submodule_path: src/zephyr/governance/audit_trail
title: "Audit Trail 蓝图 — 不可变动作审计与密码学完整性保证"
doc_type: blueprint
status: Active
version: "2.1.0"
generation: 9
layer: L0_infrastructure
layer_name: infrastructure
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
actual_disk_path: "src/zephyr/governance/audit_trail/"
construction_progress: partially_implemented
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-14"
last_verified: "2026-05-15"
last_updated: "2026-05-15"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "不可变审计追踪链——JSONL SSoT + 哈希链 + HMAC + Ed25519 Agent 签名 + CoT 推理链 + 13 异常签名 + 漂移检测 + 三角闭环 + 分片写入架构 + 99 盲点覆盖"
tags: [audit-trail, provenance, immutable-log, traceability, compliance, infrastructure, cryptographic-integrity, hash-chain, hmac-signing, ed25519, agent-signing, non-repudiation, cot-audit, reasoning-chain, lamport-clock, drift-detection, anomaly-detection, meta-audit, tiered-storage, privacy-redaction, feedback_loop, policy-factory-runtime, w3c-prov, owasp-asi09, owasp-asi10, self-monitoring, trust-score, delegation-chain, cross-ide-consistency, external-verifier, evidence-pack, compliance-map, supply-chain-audit, indirect-operation, git-isolation, kb-poisoning-prevention, nist-2026, fca]
priority: P0
runtime_plane: hot
depends_on:
  - {target: "MOD-DATABASE", at: "§3", why: "Database——events 表查询视图（不独立存储，C15/ARB-8 裁定）"}
  - {target: "MOD-GATE_ENGINE", at: "§2", why: "Gate Engine——门禁决策的审计记录 + 实时阻断联动"}
  - {target: "MOD-INF-002", at: "§2", why: "Runtime Integration——RI-13 EventStore + RI-14 DryRunSimulator + RI-15 CostTracker 联动"}
  - {target: "MOD-INF-016", at: "§2.6", why: "Shared Core——EventType 枚举 + Task Schema + 韧性基座"}
  - {target: "GOV-CMP-002", at: "full", why: "审计追踪策略——AUD-001~004 审计操作留痕规则"}
  - {target: "GOV-CMP-003", at: "§2", why: "治理审计执行协议——12 维度审计清单"}
  - {target: "MOD-INF-018", at: "§2", why: "Agent RBAC——权限检查（G-CT-001 操作签名）"}
  - {target: "MOD-INF-019", at: "§2", why: "Agent Spec——Spec 审计（G-CT-007 Spec→审计）"}
  - {target: "MOD-TASK_SYSTEM", at: "§2", why: "Task System——Agent 生命周期审计"}
  - {target: "MOD-INF-027", at: "§2", why: "Audit Orchestrator——审计记录→线5(线3→线5)跨线软依赖"}
  - {target: "MOD-INF-035", at: "§2", why: "Runtime——运行时注册跨线软依赖"}
  - {target: "MOD-INF-011", at: "§2", why: "Vector Memory——VM 嵌入结果→审计记录（线2→线5）"}
  - {target: "MOD-INF-022", at: "§2", why: "Escalation Engine——升级事件→审计记录（线3→线5）"}
  - {target: "MOD-INF-031", at: "§2", why: "Auto Fixer——修复审计（线4→线5）"}
  - {target: "MOD-INF-005", at: "§5.7-§5.10", why: "Script System——脚本执行生命周期审计钩子 + 扫描触发→审计写入集成"}
  - {target: "MOD-INF-009", at: "§0.6", why: "Pipeline——PipelineOrchestrator 扫描调度审计集成"}
  - {target: "CFG-CAP-001", at: "full", why: "容量参数——max_scripts/max_modules/max_ai_sessions 决定 shard 数和缓冲区大小"}
references:
  - {id: "MOD-INF-023", at: "§2", why: "漂移检测审计信号——仅存 references（DAG 无环）"}
  - {target: "MOD-INF-021", at: "§2", why: "Rollback——Checkpoint 触发（G-CT-002 异常事件触发 Rollback）——仅存 references（DAG 无环，避免与 rollback 双向依赖）"}
  - {id: "MOD-INF-015", at: "§2", why: "遥测发射通道——仅存 references"}
  - {id: "MOD-FEEDBACK_LOOP", at: "§2", why: "FLE 消费审计事件／Policy 闭环——仅存 references"}
  - {target: "KBG-0010", at: "§4.4", why: "三层治理边界——Policy/Factory/Runtime 三角闭环接口协议"}
  - {target: "MOD-KB-001", at: "§2", why: "Knowledge Base——审计数据输入 KB 的投毒防护 + KB provenance 评分"}
  - {target: "MOD-INF-022", at: "§2", why: "Escalation Engine——异常检测升级路径 + 委托链终端判断"}
  - {id: "MOD-INF-005", at: "§5.7", why: "Script System——BulkheadExecutor 脚本执行结果输入审计"}
  - {id: "MOD-INF-009", at: "§4", why: "Pipeline——PipelineDAG 模块执行顺序影响审计时间线重建"}
responsibility_domain: 
build_status: planned
design_maturity: design
---

> module_id: MOD-INF-020 | version: 2.1.0 | status: active | domain: infra_ops
> actual_disk_path: src/zephyr/audit-trail/ (352 .py files) | generation: 9 | construction_progress: partially_implemented

# Audit Trail 蓝图 — 不可变动作审计与密码学完整性保证

## 概述

本蓝图描述 ZephyrAlpha 审计追踪链——它解决了 AI 操作的不可变记录与密码学完整性保证问题。核心职责包括：JSONL 唯一真源写入、哈希链防篡改、HMAC 系统级签名、Agent 级 Ed25519 不可否认签名、CoT 推理链审计、13 种异常行为签名检测、蓝图漂移对账、三角闭环反馈驱动规则演进。当前规模 35 个代码文件（scaffold 阶段核心已实现），目标容量 100 AI 并发 × 10,000 脚本 × 峰值 120 条/秒写入。上游依赖 MOD-INF-016 Shared Core 承载层 + MOD-GATE_ENGINE Gate Engine，下游被所有业务域模块消费审计数据。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[trae_047_engineering_file_header.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md) 线3:治理闭环 + 线5:审计合规
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-020`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3 | 模块入口 + `__all__` | 已实现 | — |
| 2 | `models.py` | §3 蓝图特有 | 全量 Pydantic V2 模型 + AuditEventType 枚举 + DID 模型 | 已实现 | — |
| 3 | `writer.py` | §4.1 | 不可变写入器（JSONL + 哈希链 + HMAC + Ed25519 + Lamport） | 已实现 | — |
| 4 | `query.py` | §4.1 | 审计查询接口（SQLite + JSONL + 元审计 + trail_for_ai_context） | 已实现 | — |
| 5 | `integrity.py` | §4.1 | 密码学完整性验证器 | 已实现 | — |
| 6 | `anomaly.py` | §3 蓝图特有 | 异常检测引擎（13 签名） | 已实现 | — |
| 7 | `contracts.py` | §4 | 接口契约定义 | 已实现 | — |
| 8 | `agent_signer.py` | §3 蓝图特有 | Ed25519 Agent 签名器 + DID 注册 | 已实现 | — |
| 9 | `cli.py` | §4.1 | CLI 审计面板 | 已实现 | — |
| 10 | `self_monitor.py` | §3 蓝图特有 | 自监控 heartbeat + 健康采集 | 已实现 | — |
| 11 | `trust_engine.py` | §3 蓝图特有 | 渐进信任引擎 | 已实现 | — |
| 12 | `delegation_auditor.py` | §3 蓝图特有 | 委托链审计器 | 已实现 | — |
| 13 | `evidence_pack.py` | §3 蓝图特有 | 监管证据包导出 | 已实现 | — |
| 14 | `compliance_map.py` | §3 蓝图特有 | 合规框架映射 | 已迁移→semantic_auditor | 重复 |
| 15 | `supply_chain.py` | §3 蓝图特有 | 供应链审计 | 已迁移→semantic_auditor | 重复 |
| 16 | `privacy.py` | §3 蓝图特有 | 隐私脱敏 | 已实现 | — |
| 17 | `retention.py` | §3 蓝图特有 | 保留期执行 | 已实现 | — |
| 18 | `cold_start.py` | §3 蓝图特有 | Cold Start 历史回溯 | 已实现 | — |
| 19 | `genesis.py` | §3 蓝图特有 | Genesis 信任锚初始化 | 已实现 | — |
| 20 | `replay_engine.py` | §3 蓝图特有 | 确定性重放引擎 | 已实现 | — |
| 21 | `external_tool_audit.py` | §3 蓝图特有 | 外部工具调用链审计 | 已实现 | — |
| 22 | `kb_gate.py` | §3 蓝图特有 | KB 投毒防护门禁 | 已迁移→semantic_auditor | 重复 |
| 23 | `feedback_policy.py` | §3 蓝图特有 | 三角闭环反馈 | 已实现 | — |
| 24 | `feedback_self_audit.py` | §3 蓝图特有 | 反馈自指循环检测 | 已实现 | — |
| 25 | `feedback_bridge.py` | §12 | 反馈桥接 | 已实现 | — |
| 26 | `drift_bridge.py` | §12 | 漂移桥接 | 已实现 | — |
| 27 | `delegation_bridge.py` | §12 | 委托桥接 | 已实现 | — |
| 28 | `trust_bridge.py` | §12 | 信任桥接 | 已实现 | — |
| 29 | `tiered_storage.py` | §3 蓝图特有 | 三层存储迁移 | 已实现 | — |
| 30 | `tiered_storage_bridge.py` | §12 | 分层存储桥接 | 已实现 | — |
| 31 | `spec_auditor.py` | §12 | Spec 审计桥接 | 已实现 | — |
| 32 | `bridge.py` | §12 | BridgeHub 桥接注册 | 已实现 | — |
| 33 | `indexer.py` | §4.1 | SQLite 索引管理 | 已实现 | — |
| 34 | `log_rotation.py` | §3 蓝图特有 | 日志轮转 | 已实现 | — |
| 35 | `merkle_hourly.py` | §3 蓝图特有 | Merkle 树聚合 | 已实现 | — |
| 36 | `__main__.py` | §3.1 |   main   | 已实现 | — |
| 37 | `api_lifecycle.py` | §3.1 | api lifecycle | 已实现 | — |
| 38 | `changelog_manager.py` | §3.1 | changelog manager | 已实现 | — |
| 39 | `code_archaeology.py` | §3.1 | code archaeology | 已实现 | — |
| 40 | `corporate_actions.py` | §3.1 | corporate actions | 已实现 | — |
| 41 | `dora_metrics.py` | §3.1 | dora metrics | 已实现 | — |
| 42 | `financial_compliance.py` | §3.1 | financial compliance | 已实现 | — |
| 43 | `finding_ingest.py` | §3.1 | finding ingest | 已实现 | — |
| 44 | `finding_model.py` | §3.1 | finding model | 已实现 | — |
| 45 | `glossary_matrix.py` | §3.1 | glossary matrix | 已实现 | — |
| 46 | `incremental_review.py` | §3.1 | incremental review | 已实现 | — |
| 47 | `observability_dashboard.py` | §3.1 | observability dashboard | 已实现 | — |
| 48 | `orchestrator.py` | §3.1 | orchestrator | 已实现 | — |
| 49 | `provenance_tracker.py` | §3.1 | provenance tracker | 已实现 | — |
| 50 | `sbom_generator.py` | §3.1 | sbom generator | 已实现 | — |
| 51 | `supply_chain_security.py` | §3.1 | supply chain security | 已实现 | — |
| 52 | `wqa_scorer.py` | §3.1 | wqa scorer | 已实现 | — |
| `api_lifecycle.py` | § — | — | 已实现 | | 本模块 |
| `changelog_manager.py` | § — | — | 已实现 | | 本模块 |
| `code_archaeology.py` | § — | — | 已实现 | | 本模块 |
| `corporate_actions.py` | § — | — | 已实现 | | 本模块 |
| `dora_metrics.py` | § — | — | 已实现 | | 本模块 |
| `financial_compliance.py` | § — | — | 已实现 | | 本模块 |
| `glossary_matrix.py` | § — | — | 已实现 | | 本模块 |
| `incremental_review.py` | § — | — | 已实现 | | 本模块 |
| `observability_dashboard.py` | § — | — | 已实现 | | 本模块 |
| `orchestrator.py` | § — | — | 已实现 | | 本模块 |
| `provenance_tracker.py` | § — | — | 已实现 | | 本模块 |
| `sbom_generator.py` | § — | — | 已实现 | | 本模块 |
| `supply_chain_security.py` | § — | — | 已实现 | | 本模块 |
| `wqa_scorer.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| 352 个 .py 文件全部存在于 `src/zephyr/audit-trail/` | `ls D:\ZephyrAlpha\src\zephyr\audit-trail\*.py` | ☐ |
| v2.0 待施工组件（ShardWriter/GlobalIndex/ScriptAuditHook/CrossShardMerkle）不存在 | `ls` 确认 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.4.0 (基线) | 352 个 .py 文件——核心写入+完整性+查询+异常+漂移+签名+信任+证据包+合规+隐私+保留+Cold Start+重放+KB门禁+反馈 | — | — |
| v2.0.0 (容量升级) | 待施工 | ShardWriter, GlobalIndex, ScriptAuditHook, CrossShardMerkle, QueryRouter, LamportClockV2 | 待施工 P0 |

---

## §1 设计背景与目标

### 1.1 背景

审计追踪链（Audit Trail）是 ZephyrAlpha 基础设施层的**横切安全组件**——解决 AI 操作的不可变记录、密码学完整性验证、异常行为检测、蓝图漂移对账、闭环反馈驱动规则演进五大问题。

| 支柱 | 职责 |
|------|------|
| **记录（Record）** | 不可变 append-only 审计日志——JSONL 唯一真源 |
| **验证（Verify）** | 密码学完整性——哈希链 + HMAC 签名 + Merkle 树聚合 |
| **归因（Attribute）** | Agent 级不可否认性——Ed25519 Agent 签名 + 委托链验证 |
| **检测（Detect）** | 异常行为签名 + 蓝图漂移检测 + 权限违规告警 + 间接操作 + 供应链风险 |
| **进化（Evolve）** | 三角闭环反馈——审计数据回写 Policy 驱动规则演进 + 反馈自审计 |

### 1.2 目标范围

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 不可变审计记录 | JSONL append-only + 哈希链 0 断裂 + HMAC 100% 有效 |
| 2 | Agent 级不可否认性 | Ed25519 签名验证 100% 通过 + DID 绑定不可伪造 |
| 3 | 异常行为自动检测 | 13 种异常签名全覆盖 + anomaly_score > 0.7 自动告警 |
| 4 | 蓝图漂移实时对账 | 实际操作 vs 蓝图规定偏差实时检测 + 漂移事件写入审计 |
| 5 | 三角闭环反馈 | 审计聚合数据→Policy PR→规则演进闭环可用 |
| 6 | 100 AI 并发写入 | 峰值 120 条/秒 + 分片写入池 + 跨 shard 查询 P99 < 50ms |
| 7 | 自监控无人运维 | heartbeat 60s + 连续 3 次失败 P0 告警 + 外部独立验证 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | AI 审计守卫实现 | → MOD-INF-001 |
| 2 | 安全网关实现 | → MOD-LLM_SECURITY |
| 3 | 回滚执行 | → MOD-INF-021 |
| 4 | 任务门禁 | → MOD-GATE_ENGINE |
| 5 | Shared Core 实现细节 | → MOD-INF-016 |
| 6 | ML 行为基线模型 | 规则签名（13 种）足够，ML 基线不纳入 v2.0 |
| 7 | Multi-Tenant 审计隔离 | 当前单租户 |
| 8 | RFC 3161 可信时间戳 | 需外部 TSA 服务 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 多 IDE 并发（TRAE/Cursor/RooCode） | JSONL 是唯一所有 IDE 都能 append 的格式；需要 Lamport 逻辑时钟解决时序；需要跨 IDE 一致性交叉验证 |
| 100 AI 并发写入 | 单 JSONL 文件锁是瓶颈→分片写入池（16 shard） |
| 1 人 + AI，99% AI 维护 | 必须自监控（heartbeat + 自检 + 自动修复）；外部独立验证端点 |
| 先干后验模式 | 审计日志是后验基础；需要 Dry-Run 预审计模式 |
| 100% AI 施工 | 元审计和自监控是刚性需求；审计代码不可用于自证 |
| Windows 单机部署 | SQLite WAL 足够；无分布式协调需求 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 审计完整性+合规 | 设计+审批 | Genesis 初始化必须手动执行 |
| AI Agent | 审计写入+查询 | 施工+运行 | 不可修改审计日志 |
| 外部审计员 | 独立验证 | 验证 | 使用 verify_audit_integrity.py |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 审计写入 | 单文件 JSONL < 1条/秒 | 16 shard 120条/秒 | 分片写入未实现 | P0 |
| 密码学完整性 | 哈希链+HMAC+Ed25519 已实现 | 跨分片 Merkle 锚定 | CrossShardMerkle 未实现 | P0 |
| 查询性能 | 单 SQLite | 分片 SQLite+全局路由 | GlobalIndex+QueryRouter 未实现 | P1 |
| 脚本审计 | 无 | 15 种脚本事件+审计钩子 | ScriptAuditHook 未实现 | P1 |
| Lamport 时钟 | 二元组 (ide, counter) | 三元组 (ide, session_id, counter) | LamportClockV2 未实现 | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| AI 写入文件 | AuditWriter.append() | ①构建 AuditEntryV1 → ②哈希链+HMAC+Ed25519 签名 → ③JSONL 追加 → ④SQLite 异步索引 | 审计条目+写入确认 |
| 异常检测 | AnomalyDetector.detect() | ①匹配 13 签名 → ②计算 anomaly_score → ③>0.7 告警 | AnomalyEvent |
| 完整性验证 | verify_integrity() | ①哈希链校验 → ②HMAC 批量验证 → ③Merkle 根对比 | IntegrityReport |
| 蓝图漂移 | DriftDetector | ①blueprint_expected vs actual → ②diff → ③写入审计+反馈 | DriftResult |

---

## §2 模块边界

### 2.1 职责边界

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 不可变审计写入 | JSONL append-only + 哈希链 + HMAC + Ed25519 Agent 签名 + Lamport 时钟 |
| 2 | 密码学完整性验证 | 哈希链连续性 / HMAC 批量验证 / Ed25519 签名验证 / Merkle 树重建 |
| 3 | 审计查询 | SQLite 优先 + JSONL 回退 + 元审计 + trail_for_ai_context() |
| 4 | 异常行为检测 | 13 种异常签名 + 告警发射 + 协同规避检测 |
| 5 | 蓝图漂移对账 | blueprint_expected_action vs 实际记录 diff |
| 6 | 三角闭环反馈 | 审计聚合→feedback_to_policy.py→Policy PR |
| 7 | 数据生命周期 | 三层存储迁移 + 隐私脱敏 + 保留期执行 |
| 8 | 自监控 | heartbeat + 健康指标 + 自动修复 + 信任分数趋势 |
| 9 | Agent 级签名 | Ed25519 密钥管理 + 签名/验证 + DID 注册 |
| 10 | 监管合规 | 证据包导出 + 合规框架映射 + 供应链审计 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | AI 审计守卫 | MOD-INF-001（capacity_assurance） |
| 2 | 安全网关（LSG） | MOD-LLM_SECURITY（llm_security） |
| 3 | 回滚执行 | MOD-INF-021（rollback-system） |
| 4 | 任务门禁（G0-G7） | MOD-GATE_ENGINE（gate_engine） |
| 5 | Shared Core 实现 | MOD-INF-016（shared_core） |
| 6 | 事件溯源存储 | MOD-INF-002 RI-13 EventStore |
| 7 | Dry-Run 沙箱 | MOD-INF-002 RI-14 DryRunSimulator |

---

## §3 架构设计

### 3.1 组件架构

| 组件 | 核心类 | 依赖 | 状态 |
|------|--------|------|:----:|
| 不可变写入器 | `AuditWriter` / `ShardedAuditWriter` | MOD-INF-016 | ✅ 已实现 |
| 密码学验证器 | `IntegrityVerifier` | — | ✅ 已实现 |
| 审计查询 | `AuditQuery` / `ShardedQueryRouter` | MOD-DATABASE | ✅ 已实现 |
| 异常检测 | `AnomalyDetector` | — | ✅ 已实现 |
| 漂移对账 | `DriftDetector` | MOD-INF-023 | ✅ 已实现 |
| 自监控 | `SelfMonitor` | — | ✅ 已实现 |
| Agent 签名器 | `AgentSigner` + `DIDRegistry` | — | ✅ 已实现 |
| 委托链审计 | `DelegationChainAuditor` | — | ✅ 已实现 |
| 信任引擎 | `TrustScoreEngine` | — | ✅ 已实现 |
| 供应链审计 | `SupplyChainAudit` | — | ✅ 已实现 |
| 证据包导出 | `EvidencePackExporter` | — | ✅ 已实现 |
| 合规映射 | `ComplianceMap` | — | ✅ 已实现 |
| 隐私脱敏 | `PrivacyRedactor` | — | ✅ 已实现 |
| 保留期执行 | `RetentionEnforcer` | — | ✅ 已实现 |
| Cold Start | `ColdStartBootstrapper` | — | ✅ 已实现 |
| 跨 IDE 一致性 | `CrossIDEConsistencyChecker` | — | ✅ 已实现 |
| 外部调用链 | `ExternalToolCallAudit` | — | ✅ 已实现 |
| 间接操作检测 | `IndirectOperationDetector` | — | ✅ 已实现 |
| 反馈自审计 | `FeedbackSelfAudit` | — | ✅ 已实现 |
| KB 门禁 | `KBAuditGate` | MOD-KB-001 | ✅ 已实现 |
| 确定性重放 | `DeterministicReplayEngine` | — | ✅ 已实现 |
| CLI 面板 | `AuditCLI` | — | ✅ 已实现 |
| 分片写入器 | `ShardWriter` | — | ❌ v2.0 待施工 |
| 全局路由索引 | `GlobalIndex` | — | ❌ v2.0 待施工 |
| 脚本审计钩子 | `ScriptAuditHook` | MOD-INF-005 | ❌ v2.0 待施工 |
| 跨分片 Merkle | `CrossShardMerkle` | — | ❌ v2.0 待施工 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AI 操作 | AuditWriter.append() → 哈希链 + HMAC + Ed25519 签名 → JSONL 追加 | SQLite 索引（异步） | AuditEntryV1/V2 |
| 2 | 查询请求 | AuditQuery → SQLite 优先 → JSONL 回退 → 完整性快速校验 | 调用者 | TaskAuditSummary / FileAuditDetail |
| 3 | AI context 请求 | trail_for_ai_context() → 单 shard 查询 → Prompt 注入净化 → Markdown | LLM context | Markdown string |
| 4 | 异常检测 | AnomalyDetector → 13 签名匹配 → anomaly_score 计算 → 告警发射 | Escalation Engine | AnomalyEvent |
| 5 | 漂移对账 | DriftDetector → blueprint_expected vs actual → diff 生成 | Policy 反馈 | DriftResult |
| 6 | 三角闭环 | Aggregator → 日聚合 → feedback_to_policy.py → Policy PR | Policy 层 | PolicyEvolutionPR |
| 7 | 脚本执行 | Script System → 审计钩子 → SCAN_TRIGGERED/SCRIPT_EXECUTION_* 事件 | AuditWriter | ScanTriggeredEntry |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| NOT_WRITTEN | AI 操作触发 | WRITTEN | 审计写入成功 + 哈希链连续 |
| WRITTEN | 异常检测匹配 | FLAGGED | anomaly_score > 阈值 |
| FLAGGED | Owner 确认 / 自动降级 | RESOLVED | 处置动作完成 |
| WRITTEN | 漂移检测匹配 | DRIFTED | drift_detected = True |
| DRIFTED | Policy 更新对齐 | ALIGNED | 蓝图与代码重新对齐 |

### 蓝图特有：两层审计粒度（决策 D-020-01）

| 层级 | 模型 | 用途 |
|------|------|------|
| 任务级摘要 | `TaskAuditSummary` | 快速浏览——1 条/任务 |
| 文件级明细 | `FileAuditDetail` | 问题定位——1 条/文件操作 |

**TaskAuditSummary** 字段：`event_id`(AUD-T-{UUID7}-{SEQ}) | `timestamp`(UTC ms) | `agent_id` | `ide_source` | `lamport_counter` | `session_id` | `task_id` | `task_type` | `action_summary` | `files_affected` | `result` | `permission_level` | `provenance_depth` | `tokens_used`? | `cost_estimate_usd`? | `duration_ms`?

**FileAuditDetail** 字段：`event_id`(AUD-F-{UUID7}-{SEQ}) | `task_audit_id` | `timestamp` | `lamport_counter` | `file_path` | `action_type`(FileActionType) | `sha256_before`? | `sha256_after`? | `diff_size_bytes`?

### 蓝图特有：JSONL SSoT + 密码学完整性（决策 D-020-02 + D-020-04）

```yaml
storage_ssoT:
  primary:
    format: "JSONL"
    path: "data/audit/audit-trail.jsonl"
    write_mode: "append-only"
    rotation: "按日轮转——audit-trail-{YYYY-MM-DD}.jsonl"
    retention: "permanent"
    git_tracked: false
    git_isolation: "data/audit/ 加入 .gitignore——审计日志独立于 git 工作区"

  cryptographic_integrity:
    hash_chain:
      enabled: true
      algorithm: "SHA-256"
      field: "prev_entry_hash"
    hmac_signing:
      enabled: true
      algorithm: "HMAC-SHA256"
      secret_source: "环境变量 ZEPHYR_AUDIT_HMAC_SECRET（256-bit）"
      field: "hmac_signature"
    merkle_aggregation:
      enabled: true
      interval: "每小时"
      path: "data/audit/merkle/audit-merkle-{YYYY-MM-DDTHH}.json"
    integrity_check:
      frequency: "每次查询前自动检验 + 每周全量扫描"
      on_failure: "P0 告警 → integrity_failure 审计事件 → 通知 Owner → 隔离可疑段"

  derived:
    format: "SQLite"
    path: "data/audit/audit-index.db"
    write_mode: "异步重建——从 JSONL 派生，5s 延迟"
    rebuild_trigger: "JSONL 追加后 5s / 手动触发 / CI 启动时 / 索引损坏自动触发"

  consistency_check:
    ci_gate: "CI 门禁校验 SQLite 记录数 == JSONL 行数 + 哈希链连续性 + HMAC 有效性"
    rebuild_script: "scripts/governance/rebuild_audit_index.py"
    self_healing: "索引损坏 → 自动从 JSONL 重建（零人工干预）"
```

### 蓝图特有：审计条目数据模型（AuditEntryV1）

`AuditEntryV1(BaseModel)`，`model_config = ConfigDict(frozen=True, extra="forbid")`

| 字段组 | 字段 | 类型/默认值 |
|--------|------|-----------|
| 标识 | `entry_id` | str (UUID7) |
| | `schema_version` | str ("1.1.0") |
| | `entry_type` | AuditEventType |
| 完整性 | `prev_entry_hash` | str |
| | `entry_hash` | str |
| | `hmac_signature` | str |
| Agent签名 | `agent_did` | str? |
| | `agent_signature` | str? |
| | `agent_public_key_pem` | str? |
| 委托 | `delegation_chain` | list[str] ([]) |
| | `delegation_depth` | int (0) |
| Merkle | `merkle_batch_id` | str? |
| 时序 | `lamport_clock` | tuple[str, int] |
| | `utc_timestamp` | datetime |
| 主体 | `agent_id` | str |
| | `ide_source` | str |
| | `session_id` | str |
| | `task_id` | str |
| | `task_type` | str? |
| | `permission_level` | str |
| | `provenance_depth` | str |
| | `trust_score` | float? |
| 操作 | `action_type` | str |
| | `file_path` | str? |
| | `sha256_before` | str? |
| | `sha256_after` | str? |
| | `indirect_operation` | bool (False) |
| | `indirect_method` | str? |
| | `indirect_target` | str? |
| 决策 | `decision_basis` | list[str] ([]) |
| | `guard_checks_passed` | list[str] ([]) |
| | `guard_checks_failed` | list[str] ([]) |
| | `confidence_level` | str ("high") |
| 推理 | `reasoning_trace` | str? |
| | `cot_hash` | str? |
| 漂移 | `blueprint_expected_action` | str? |
| | `drift_detected` | bool (False) |
| | `drift_severity` | str? |
| | `drift_detail` | str? |
| 异常 | `anomaly_detected` | bool (False) |
| | `anomaly_type` | str? |
| | `anomaly_score` | float? |
| 资源 | `tokens_used` | int? |
| | `cost_estimate_usd` | float? |
| | `duration_ms` | int? |
| DryRun | `dry_run` | bool (False) |
| | `dry_run_real_diff` | str? |
| | `dry_run_real_diff_score` | float? |
| 关联 | `parent_entry_id` | str? |
| | `external_tool_calls` | list[dict] ([]) |
| | `supply_chain_info` | dict? |
| 隐私/保留 | `contains_pii` | bool (False) |
| | `redaction_policy` | str ("none") |
| | `retention_tier` | str ("hot") |

### 蓝图特有：分级 Provenance（决策 D-020-03）

| 级别 | 权限 | 字段 |
|------|------|------|
| LIGHT | always_allow | agent_id + timestamp + action_type + ide_source + decision_brief |
| STANDARD | auto_guard | + decision_basis + guard_checks_executed/passed/failed + guard_result + confidence_level |
| FULL | blocked | + blocked_reason + attempted_action + rule_violated + escalation_triggered/target |

### 蓝图特有：Lamport 逻辑时钟（决策 D-020-09）

`LamportClock(ide_source: str)`：`_ide` + `_counter=0`。`tick()→(ide, counter+1)`，`merge(received)→counter=max(local, received[1])+1`。

v2.0 升级为三元组 `(ide, session_id, counter)`——见 §17。

### 蓝图特有：三层存储架构（决策 D-020-10）

| 层 | 格式 | 路径 | 年龄 | 延迟 | 压缩 |
|---|------|------|------|------|------|
| 热 | JSONL | `data/audit/hot/` | ≤ 7 天 | < 5ms P99 | none |
| 温 | gzip JSONL | `data/audit/warm/` | 8~90 天 | < 100ms | gzip level 6 |
| 冷 | Parquet | `data/audit/cold/` | > 90 天 | 日级查询 | Parquet snappy + zstd |

### 蓝图特有：Agent 级 Ed25519 签名（决策 D-020-14）

```yaml
agent_signing:
  algorithm: "Ed25519"
  key_generation: "Agent 身份创建时生成，每 90 天或权限升级时轮转"
  signing: "Agent 私钥签名(entry_hash) → agent_signature"
  verification: "公钥验证(entry_hash, agent_signature)——任何第三方可离线验证"
  did:
    format: "did:zephyr:{sha256(Ed25519_public_key)[:16]}"
    binding: "DID 绑定到 Ed25519 公钥——不可伪造"
  non_repudiation_chain: "HMAC（系统级）+ Ed25519（Agent 级）——双重保障"
```

### 蓝图特有：CoT 推理链审计（决策 D-020-15）

| 字段 | 说明 |
|------|------|
| `reasoning_trace` | CoT 摘要 < 500 chars |
| `cot_hash` | SHA-256(完整 CoT)——完整文本存 `data/reasoning/{session_id}/{entry_id}.cot.json` |

### 蓝图特有：委托链审计（决策 D-020-16）

约束：(a) 子 Agent 权限必须是父 Agent 权限子集，(b) 委托深度上限 3，(c) 链断裂立即 P0 告警。

### 蓝图特有：渐进信任分数（决策 D-020-17）

| 事件 | 分数变化 |
|------|---------|
| 成功操作 | +0.001 |
| 异常检测 | -0.2 |
| 每天无活动 | -0.005 |
| trust-score < 0.5 | 自动降级权限级别 |

### 蓝图特有：审计事件类型枚举

`AuditEventType(str, Enum)`：task_summary | file_detail | anomaly_detected | permission_violation | bulk_operation | gate_bypass | off_hours_activity | drift_detected | index_rebuild | log_rotation | tier_migration | integrity_check | integrity_failure | audit_query | audit_system_health | policy_feedback_sent | dry_run_audit | cold_start_bootstrap | agent_impersonation | delegation_chain_issue | trust_score_change | external_tool_call | indirect_operation | supply_chain_install | latent_risk_detected | collusion_pattern | dry_run_mismatch | kb_poisoning_attempt | feedback_loop_self_reinforcing | volume_dos | cross_ide_conflict

v2.0 新增 15 种脚本审计事件类型——见 §17 §V5。

### 蓝图特有：13 种异常行为签名（决策 D-020-07）

| 签名 ID | 异常模式 | 严重度 |
|:---:|------|:---:|
| ANM-001 | 越权操作 | 🔴 P0 |
| ANM-002 | 批量删除（> 5 文件） | 🔴 P0 |
| ANM-003 | 门禁跳过 | 🔴 P0 |
| ANM-004 | 非工作时间（UTC 22-06，> 20 操作/小时） | 🟡 P1 |
| ANM-005 | 高频操作（> 100 文件操作/分钟） | 🟡 P1 |
| ANM-006 | 跨 Agent 冲突（5 分钟内 3+ Agent 修改同文件） | 🔴 P0 |
| ANM-007 | 审计日志异常（哈希链断裂 / HMAC 失败 / 签名失败） | 🔴 P0 |
| ANM-008 | Agent 冒充（DID 不匹配签名） | 🔴 P0 |
| ANM-009 | 委托链异常（深度 > 3 / 权限放大） | 🔴 P0 |
| ANM-010 | 协同规避（多 Agent 总效果超单阈值） | 🔴 P0 |
| ANM-011 | 间接操作规避（symlink/script/cron/MCP） | 🟡 P1 |
| ANM-012 | 信任趋势恶化（7 天下降 > 0.3 或 < 0.5） | 🟡 P1 |
| ANM-013 | Dry-Run 差异异常 | 🟡 P1 |

### 蓝图特有：三角闭环反馈（决策 D-020-08）

```yaml
feedback_loop:
  producer: "audit-trail.aggregator"
  consumer: "feedback_to_policy.py"
  aggregation:
    schedule: "daily 00:30 UTC"
    dimensions: [top_anomalies, drift_summary, permission_trends, cost_anomalies]
  output:
    format: "Markdown policy_evolution_pr_body"
    target: "GitHub PR → docs/01_policies_and_standards/"
    approval: "human_gated——Owner 审批后合并"
```

### 蓝图特有：Prompt 注入防护（决策 D-020-31）

```yaml
ai_self_security:
  sanitization_pipeline:
    step_1: "移除/转义 AI 指令关键词——ignore|disregard|override|bypass|system:|assistant:|user:"
    step_2: "语义沙箱标记——[AUDIT_ENTRY_START]...[AUDIT_ENTRY_END]"
    step_3: "每条 entry 截断至 500 chars"
  forbidden_patterns: ["---", "===", "```", "system:", "assistant:", "user:", "<function_call>", "<invoke>"]
  audit_self_defense: "ANM-015——检测到注入模式 → 自动脱毒 + 标记 anomaly → P0"
```

### 蓝图特有：Genesis 信任锚初始化（决策 D-020-44）

```yaml
bootstrap_trust:
  initialization_ceremony:
    step_1: "CSPRNG 读取 256-bit → HMAC secret → SHA-256(secret) 写入 genesis_manifest.txt"
    step_2: "写入第一条审计条目 AUDIT_SYSTEM_BOOTSTRAP——prev_entry_hash='genesis'"
    step_3: "生成 Owner Agent Ed25519 密钥对——DID 注册 + 公钥入 genesis 条目"
    step_4: "genesis_manifest.txt 写入外部独立介质——USB / 纸质 QR / 云存储"
  rule: "genesis 创建者 ≠ 日常操作者——由 Owner 手动执行初始化，AI 辅助"
```

### 蓝图特有：自监控指标

| 指标 | 阈值 | 告警 |
|------|------|------|
| write_latency_p99_ms | 5 ms | > 10 ms P99 → P1 |
| disk_usage_pct | 80% | > 80% → P1，> 90% → P0 |
| hash_chain_integrity | 100% pass | 任一 fail → P0 阻断 |
| hmac_validity_rate | 100% pass | 任一 fail → P0 阻断 |
| agent_signature_validity_rate | 100% pass | 任一 fail → P0 阻断 |
| delegation_chain_validity | 100% pass | 链断裂或权限放大 → P0 |
| trust_score_trend | 下降 > 0.3 / 7d | P1 |
| cross_ide_consistency | 100% pass | 不一致 > 0 → P1 |

---

## §4 接口契约

### 4.1 公共 API

```python
class AuditWriter:
    async def append(self, entry: AuditEntryV1) -> None:
        """追加审计条目——JSONL append + 哈希链 + HMAC + Ed25519 + Lamport tick"""
    async def append_batch(self, entries: list[AuditEntryV1]) -> None: ...

class AuditQuery:
    def by_task(self, task_id: str) -> TaskAuditSummary: ...
    def by_task_details(self, task_id: str) -> list[FileAuditDetail]: ...
    def by_agent(self, agent_id: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]: ...
    def by_target(self, file_path: str) -> list[FileAuditDetail]: ...
    def by_permission_level(self, level: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]: ...
    def by_anomaly(self, anomaly_type: str | None = None, min_score: float = 0.7) -> list[AuditEntryV1]: ...
    def by_drift(self, severity: str | None = None) -> list[AuditEntryV1]: ...
    def by_cost(self, min_cost_usd: float = 0.0, time_range: tuple[datetime, datetime] | None = None) -> list[AuditEntryV1]: ...
    def trail_for_ai_context(self, session_id: str) -> str: ...
    def rebuild_index(self) -> int: ...
    def verify_integrity(self, fast_mode: bool = True) -> IntegrityReport: ...

class IntegrityVerifier:
    def verify_hash_chain(self, jsonl_path: str) -> list[int]: ...
    def verify_hmac_batch(self, entries: list[AuditEntryV1]) -> list[int]: ...
    def verify_merkle_root(self, batch_id: str) -> bool: ...
    def verify_agent_signatures(self, entries: list[AuditEntryV1], sample_rate: float = 0.1) -> list[bool]: ...

class AnomalyDetector:
    def detect(self, entry: AuditEntryV1) -> AnomalyResult: ...
    def batch_detect(self, entries: list[AuditEntryV1]) -> list[AnomalyResult]: ...

class EvidencePackExporter:
    def export_json(self, task_id: str) -> EvidencePack: ...
    def export_pdf(self, task_id: str) -> bytes: ...
    def export_for_regulator(self, task_id: str) -> bytes: ...
```

### 4.2 数据模型

核心数据模型见 §3 蓝图特有章节（AuditEntryV1 / TaskAuditSummary / FileAuditDetail / ProvenanceDepth / AuditEventType）。

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `append()` | `entry: AuditEntryV1` | ✅ | Pydantic V2 校验通过 + entry_hash 自洽 |
| `by_task()` | `task_id: str` | ✅ | 非空字符串 |
| `trail_for_ai_context()` | `session_id: str` | ✅ | 非空 + 已存在审计条目 |
| `verify_integrity()` | `fast_mode: bool` | ❌ | 默认 True |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `append()` | None | `AuditWriteError` / `HashChainBreakError` |
| `by_task()` | `TaskAuditSummary` | `EntryNotFoundError` |
| `trail_for_ai_context()` | `str`（Markdown，AI 零推理可消费） | `SessionNotFoundError` |
| `verify_integrity()` | `IntegrityReport(is_valid=True)` | `IntegrityReport(is_valid=False, hash_chain_breaks=[...])` |

### 4.5 MCP 接口

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `audit_query` | `AuditQuery.by_task()` | `{task_id: str}` | `{summary: TaskAuditSummary}` |
| `audit_trail` | `AuditQuery.trail_for_ai_context()` | `{session_id: str}` | `{trail: str}` |
| `audit_integrity` | `AuditQuery.verify_integrity()` | `{fast_mode: bool}` | `{report: IntegrityReport}` |

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增事件类型 | ✅ 向后兼容 | 不破坏已有逻辑 |
| AuditEntryV2 新增字段 | ✅ 向后兼容 | V2 继承 V1 + 新增 shard_id/shard_sequence/cross_shard_anchor |
| 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |

### 4.7 OCP 扩展点

| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| 异常检测策略 | AnomalyDetector.detect() | 13 签名规则匹配 | 新增签名必须返回 AnomalyResult + anomaly_score ∈ [0,1] | anomaly.py 新增签名方法 |
| 存储层策略 | TieredStorage.migrate() | 热→温→冷三层迁移 | 新增层必须实现 write()+read()+migrate() | tiered_storage.py 配置注入 |
| 反馈策略 | FeedbackPolicy.aggregate() | 日聚合+Policy PR | 新增维度必须输出 PolicyEvolutionPR | feedback_policy.py 配置注入 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python stdlib + SQLite + Pydantic V2 | 零外部依赖 |
| 2 | JSONL 为唯一真源 | append-only |
| 3 | 审计日志不可变 | 哈希链 + HMAC + Ed25519 |
| 4 | Windows 单机部署 | SQLite WAL |
| 5 | 审计写入不阻塞主操作 | 异步 + fire-and-forget |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 审计写入速率 | < 1 条/秒 | 120 条/秒（100 AI 峰值） | 240 条/秒（16 shard × 15） | ⚠️ 需分片 | §17 §V2 分片写入池 |
| 日增 JSONL | ~2,000 行 | 100,000 行（~150 MB） | 200,000 行（~300 MB 峰值日） | ⚠️ 需预估 | 按日轮转 + 分层存储 |
| SQLite 索引 | 单文件 | 月增 3M 行 | 分片 SQLite | ❌ 需分片 | §17 §V4 分片 SQLite |
| 热存储 7d | ~14 MB | ~1.05 GB（16 shard） | NVMe 800 GB 可用 | ✅ | — |
| 月存储总量 | ~60 MB | ~7.5 GB（含索引+Merkle+CoT） | NVMe 充足 | ✅ | — |
| 内存占用 | ~30 MB | ~120 MB（16 shard 缓冲+WAL+对象） | 64 GB 总内存 | ✅ | < 0.2% |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 | 执行状态 |
|---|-------------|---------|---------|---------|------------|:-------:|
| 1 | governance/ 根级 13 孤儿文件 | `D:\ZephyrAlpha\src\zephyr\governance\` | `D:\ZephyrAlpha\src\zephyr\audit-trail\` | 迁移+桥接导入 | 搜索全项目 import 引用并更新 | 未执行 |
| 2 | audit-trail.jsonl git tracking | git 工作区 | `.gitignore` 隔离 | 从 git tracking 移除 + `.gitignore` 添加 `data/audit/` | 无代码引用 | 未执行 |
| 3 | AuditEntryV1 → V2 | `models.py` | `models.py`（继承扩展） | V2 继承 V1 + 新增 3 字段 | V1 消费者无需修改 | 未执行 |

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 审计写入成功率 | 99.99% | 写入计数/总计数 | write_success_rate | 99.99% | 每月≤4.3min 不可用 | <99.9%→P0 |
| 延迟 | 写入 P99 | <5ms | 写入耗时直方图 | write_latency_p99_ms | <5ms | — | >10ms→P1 |
| 完整性 | 哈希链连续性 | 100% | 完整性校验 | hash_chain_integrity_rate | 100% | 0 断裂允许 | 任一断裂→P0 |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 直接修改 JSONL 已有条目 | append-only 追加 | 审计日志不可变 |
| 2 | 编码模式 | 同步阻塞主操作等待审计写入 | async fire-and-forget | 审计不阻塞主流程 |
| 3 | 导入源 | from zephyr.l02_* import * | from zephyr.audit_trail import * | 基础设施层不依赖上层 |
| 4 | 编码模式 | 明文存储 HMAC Secret | 环境变量 ZEPHYR_AUDIT_HMAC_SECRET | Secret 不可硬编码 |
| 5 | 编码模式 | 审计代码审计自己（自证） | 外部 verify_audit_integrity.py 独立验证 | AI 不能自证清白 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 哈希链断裂 | integrity_check | P0 告警 + 隔离可疑段 + 从 Merkle 重建 | 审计完整性 |
| 2 | HMAC 签名失败 | verify_integrity | P0 阻断 + 通知 Owner | 审计可信度 |
| 3 | JSONL 写入失败 | AuditWriter 异常 | 内存缓冲区 fallback + P0 阻断 AI 操作 | 审计连续性 |
| 4 | SQLite 索引损坏 | 查询异常 | 自动从 JSONL 重建（零人工干预） | 查询性能 |
| 5 | 磁盘满 | disk_usage_pct > 90% | P0 阻断 + 内存缓冲区 fallback | 审计写入 |
| 6 | Agent 签名验证失败 | Ed25519 verify | P0 阻断 + ANM-008 冒充检测 | Agent 不可否认性 |
| 7 | 委托链断裂 | DelegationChainAuditor | P0 告警 + 追溯根 Agent | 委托可信度 |
| 8 | Merkle 根不匹配 | merkle 重建对比 | P0 告警 + 全量哈希链校验 | 批量完整性 |
| 9 | 分片写入超时 | shard_write_latency > 10ms P99 | 背压 + 降级 fire-and-forget | 写入吞吐 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| write_latency_p99_ms | Histogram | 自动埋点 | >10ms | P1 |
| hash_chain_integrity | Gauge | 完整性校验 | 任一 fail | P0 |
| hmac_validity_rate | Gauge | HMAC 校验 | 任一 fail | P0 |
| disk_usage_pct | Gauge | 磁盘监控 | >80% P1, >90% P0 | P0/P1 |
| anomaly_detection_rate | Counter | 异常检测 | >5/hour | P1 |
| trust_score_trend | Gauge | 信任引擎 | 7d 降>0.3 | P1 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| AuditWriter | 内存缓冲区暂存 | JSONL 持久化 | 内存 fallback+P0 阻断 | 磁盘恢复 |
| SQLite 索引 | JSONL 全扫描 | 快速查询 | 从 JSONL 重建索引 | 重建完成 |
| AnomalyDetector | 审计写入继续 | 异常告警 | 跳过检测+标记 | 检测器恢复 |
| Merkle 聚合 | 单条哈希链有效 | 批量完整性证明 | 降级为单链验证 | Merkle 恢复 |
| Agent 签名 | HMAC 系统级签名有效 | Agent 不可否认性 | 降级为单层签名 | Ed25519 恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 审计日志被篡改 | 🔴极高 | 哈希链 + HMAC + Merkle + 外部 verifier | `verify_audit_integrity.py` |
| 2 | HMAC Secret 泄露 | 🔴极高 | 环境变量存储 + 定期轮转 + Shamir 分片（2/3） | Secret 轮转脚本验证 |
| 3 | Agent 冒充 | 🔴极高 | Ed25519 Agent 级签名 + ANM-008 检测 | 签名验证测试 |
| 4 | Prompt 注入攻击 | 🔴极高 | trail_for_ai_context() 净化 + 语义沙箱 + NFKC 归一化 | 注入模式测试 |
| 5 | Git 回滚致审计丢失 | 🔴极高 | Git 隔离——data/audit/ 加入 .gitignore | git reset 后审计日志仍在 |
| 6 | 磁盘满静默失败 | 🔴极高 | 磁盘水位预警 + 写失败 P0 阻断 | 磁盘满模拟测试 |
| 7 | 间接操作规避 | 高 | ANM-011 检测 + 写入→执行关联分析 | symlink 攻击模拟 |
| 8 | 供应链风险 | 高 | 每次 install 审计 + 包 SHA-256 + untrusted_external 标记 | pip install 审计验证 |
| 9 | Unicode 同形字绕过 | 🔴极高 | NFKC 归一化 + 同形字映射 + 净化前归一化 | Cyrillic "іgnore" 测试 |
| 10 | Genesis 初始化被 compromise | 🔴极高 | 初始化仪式 + 外部见证介质 + Owner 手动执行 | genesis 验证脚本 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | models / writer / query / integrity / anomaly | AuditEntryV1 Pydantic 校验 + 哈希链 1000 条连续 + HMAC 100% 有效 | 覆盖率 > 80% |
| 2 | 集成测试 | writer→JSONL→SQLite→query 端到端 | 写入→查询→验证完整性闭环 | 端到端通过 |
| 3 | 安全测试 | prompt 注入 / 签名伪造 / 哈希链篡改 | Cyrillic 同形字 + Ed25519 伪造签名 + 删除中间条目 | 所有攻击被检测 |
| 4 | 性能测试 | 写入吞吐 / 查询延迟 | 100 AI 并发模拟 + 120 条/秒峰值写入 | P99 < 5ms 写入 / < 50ms 查询 |
| 5 | 外部验证 | verify_audit_integrity.py | 零依赖 audit-trail/ 模块 + CI 门禁 | exit 0 |

---

## §10 依赖关系

### 10.1 依赖声明

#### 上游依赖（MOD-INF-020 依赖谁）

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-DATABASE | 硬依赖 | events 表查询视图（不独立存储，C15/ARB-8 裁定） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` |
| MOD-GATE_ENGINE | 硬依赖 | 门禁决策审计 + 实时阻断联动 | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-INF-016 | 硬依赖 | EventType 枚举 + Task Schema + AiAuditLogger | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |
| MOD-INF-018 | 硬依赖 | 权限检查（G-CT-001） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-021 | 硬依赖 | Checkpoint 推送（G-CT-002 异常→Rollback） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback-system\blueprint.md` |
| MOD-INF-019 | 硬依赖 | Spec 审计（G-CT-007） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` |
| MOD-TASK_SYSTEM | 硬依赖 | Agent 生命周期审计 | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\task_system\blueprint.md` |
| MOD-INF-002 | 硬依赖 | RI-13 EventStore + RI-14 DryRun + RI-15 CostTracker | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\runtime_integration\blueprint.md` |
| MOD-INF-011 | 跨线软依赖 | VM 嵌入结果→审计记录（线2→线5） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\vector_memory\blueprint.md` |
| MOD-INF-022 | 跨线软依赖 | Escalation 升级事件→审计记录（线3→线5） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-engine\blueprint.md` |
| MOD-INF-031 | 跨线软依赖 | 修复审计（线4→线5） | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\auto-fixer\blueprint.md` |
| GOV-CMP-002 | 硬依赖 | AUD-001~004 审计操作留痕规则 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\components\audit-tracking-policy.md` |
| GOV-CMP-003 | 硬依赖 | 12 维度审计清单 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\components\governance-audit-protocol.md` |
| MOD-INF-005 | 硬依赖 | 脚本执行生命周期审计钩子 | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\script-system\blueprint.md` |
| MOD-INF-009 | 硬依赖 | PipelineOrchestrator 扫描调度审计集成 | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\pipeline\blueprint.md` |
| CFG-CAP-001 | 硬依赖 | 容量参数决定 shard 数和缓冲区大小 | — | — |
| MOD-INF-027 | 跨线软依赖 | 审计记录→线5 | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` |
| MOD-INF-035 | 跨线软依赖 | 运行时注册 | ≥0.1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |

#### 下游消费者（谁依赖 MOD-INF-020）

| 消费者模块 | 消费内容 | 依赖图线 |
|-----------|---------|:-------:|
| MOD-INF-028 | 语义审计事件流 | 线5 |
| MOD-INF-033 | 行为审计事件流 | 线5 |
| MOD-INF-023 | 漂移事件 | 线5→线3 |
| MOD-INF-021 | Checkpoint 触发（G-CT-002） | 线5 |
| MOD-INF-018 | RBAC 判定事实（G-CT-001） | 线5 |
| D_EXECUTION_CORE 域模块 | 执行审计 | 线7 |
| D_REPORTING 域模块 | 审计写入 | 线7 |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-020` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| `writer.py` | `indexer.py` | writer 写入 JSONL 后 indexer 才能建索引 | 检查 JSONL 文件存在 |
| `indexer.py` | `query.py` | 索引建成后查询才能命中 SQLite | 检查 audit-index.db 存在 |
| `merkle_hourly.py` | `integrity.py` | Merkle 树建成后才能验证批量完整性 | 检查 merkle JSON 存在 |
| `writer.py` | `anomaly.py` | 写入后才能对条目做异常检测 | 检查 JSONL 条目存在 |
| `genesis.py` | `writer.py` | Genesis 初始化后才能正常写入 | 检查 genesis 条目存在 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| `writer.py` | `indexer.py` | AuditEntryV1 JSONL 条目 | 共享 JSONL 文件 |
| `indexer.py` | `query.py` | SQLite 索引行 | 共享 SQLite DB |
| `anomaly.py` | `feedback_policy.py` | AnomalyEvent | 函数调用 |
| `writer.py` | `trust_engine.py` | 审计条目事件 | 函数调用 |
| `feedback_policy.py` | `feedback_bridge.py` | PolicyEvolutionPR | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 13 个外部依赖 + 5 个内部依赖，手动维护易漂移 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖，需 CI 门禁保证对齐 |
| 3 | 临时时态内容自动清理 | 是 | §5.3 有 3 项迁移方案，执行后需从蓝图删除 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中，5 个 v2.0 组件待实现 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | `asset_inventory/dependency.py` | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | `validate_path_alignment.py` | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest + mypy + ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\audit-trail\` | Python 源码（352 .py files） |
| 测试代码 | `D:\ZephyrAlpha\tests\audit-trail\` | 测试用例 |
| 审计数据 | `D:\ZephyrAlpha\data\audit\` | JSONL + SQLite + Merkle |
| 推理链数据 | `D:\ZephyrAlpha\data\reasoning\` | CoT 完整文本 |
| 外部验证脚本 | `D:\ZephyrAlpha\scripts\governance\verify_audit_integrity.py` | 零依赖 CI 门禁 |
| 索引重建脚本 | `D:\ZephyrAlpha\scripts\governance\rebuild_audit_index.py` | JSONL→SQLite |
| 保留期执行脚本 | `D:\ZephyrAlpha\scripts\governance\enforce_audit_retention.py` | 保留期清理 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-GOVERNANCE 治理域蓝图 | 职责分派 | §2 职责分派表 | 蓝图 §2 已更新 |
| zephyr.agent_rbac | 审计桥接(G-CT-001) | AuditWriter.log_event() | G-CT-001 契约验证 |
| zephyr.rollback | Checkpoint 触发(G-CT-002) | AuditWriter.log_event() | G-CT-002 契约验证 |
| zephyr.agent_spec | Spec 审计(G-CT-007) | AuditWriter.log_event() | G-CT-007 契约验证 |
| zephyr.task_system | Agent 生命周期 | AuditWriter.log_event() | 生命周期事件写入审计 |
| zephyr.shared | AiAuditLogger 唯一入口 | AiAuditLogger 类 | import 验证 |
| zephyr.db | events 表唯一权威存储 | AuditEntryV1 模型 | 数据库查询验证 |
| zephyr.audit_orchestrator | 审计记录→线5(跨线) | bridge.py | 桥接调用验证 |
| 5 个 *_bridge.py | 跨模块桥接 | BridgeHub | 桥接注册验证 |

### 12.1 域契约锚点

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-001 | 消费方（记录 RBAC 判定事实） | MOD-INF-018 |
| G-CT-002 | 产出方（异常事件触发 Rollback） | MOD-INF-021 |
| G-CT-007 | 消费方（记录 Spec 执行审计） | MOD-INF-019 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-020 条目 | 蓝图注册 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | MOD-INF-020 条目 | 蓝图发现 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | MOD-INF-020 元数据 | 资产索引 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 线3:治理闭环 + 线5:审计合规 | 依赖声明 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| R1 | 审计日志膨胀 | 高 | 中 | 按日轮转 + gzip/Parquet 分层 + 保留期自动执行 | 风险 |
| R2 | JSONL 写入冲突 | 中 | 高 | 文件锁 + Lamport 时钟 + 分片写入池 | 风险 |
| R3 | SQLite 索引延迟 | 中 | 低 | 查询时先检查 JSONL 最新 N 行 + 5s 重建间隔 | 风险 |
| R4 | 审计日志被篡改 | 低 | 🔴极高 | 哈希链 + HMAC + Merkle + 外部 verifier | 风险 |
| R5 | HMAC Secret 泄露 | 低 | 🔴极高 | Shamir 分片（2/3）+ 定期轮转 | 风险 |
| R6 | 自监控假阳性/假阴性 | 低 | 中 | 3 次失败才告警 + 外部 verifier 交叉验证 | 风险 |
| R7 | 异常检测误报 | 中 | 中 | 阈值可配置 + 首次部署 warn 模式 | 风险 |
| R8 | 隐私脱敏遗漏 | 低 | 高 | PII pattern 正则维护 + CI 扫描 | 风险 |
| R9 | Cold Start 基线不可靠 | 高 | 低 | confidence=low 标记 + 隔离存储 | 风险 |
| R10 | 三角闭环反馈质量差 | 中 | 低 | 仅推送 anomaly_score > 0.8 + human_gated | 风险 |
| R11 | Agent 冒充 | 低 | 🔴极高 | Ed25519 Agent 级签名 + ANM-008 | 风险 |
| R12 | 委托链断裂 | 低 | 高 | 完整记录 + 深度 ≤ 3 + ANM-009 | 风险 |
| R13 | 多 Agent 协同规避 | 低 | 高 | ANM-010 跨 Agent 时间窗口聚合 | 风险 |
| R14 | AI 上下文污染 | 中 | 高 | KB 投毒防护 + 信任分数过滤 | 风险 |
| R15 | 间接操作越权 | 中 | 中 | ANM-011 + 写入→执行关联 | 风险 |
| R16 | Prompt 注入攻击 | 中 | 🔴极高 | trail_for_ai_context() 净化 + 语义沙箱 | 风险 |
| R17 | Git 回滚致审计丢失 | 中 | 🔴极高 | Git 隔离 + 独立备份 | 风险 |
| R18 | 磁盘满静默失败 | 低 | 🔴极高 | 磁盘水位预警 + 写失败 P0 阻断 | 风险 |
| R19 | Genesis 初始化被 compromise | 低 | 🔴极高 | 初始化仪式 + 外部见证 + Owner 手动执行 | 风险 |
| R20 | 哈希链分叉 | 中 | 高 | fork_detection + fork_reconciliation | 风险 |
| R21 | 撕裂写入 | 低 | 高 | torn_write_detector + 原子 append | 风险 |
| R22 | Unicode 同形字绕过 | 中 | 🔴极高 | NFKC 归一化 + 同形字映射 | 风险 |
| R23 | 告警疲劳 | 高 | 🔴极高 | operator_responsiveness_model + 响应率 < 30% → P0 | 风险 |
| R24 | 信任漂移 | 高 | 中 | trust_calibration 实际 anomaly 率 vs 审核通过率 | 风险 |
| R25 | 供应链风险 | 中 | 高 | 每次 install 审计 + 包 SHA-256 | 风险 |
| R26 | 确定性重放不可行 | 中 | 高 | sha256_before/after + 分层重放测试 | 风险 |
| R27 | Bus Factor = 1 | 低 | 高 | 全自动化自愈 + 外部 verifier 独立 | 风险 |
| R28 | GDPR 删除权 vs 不可变性 | 中 | 中 | 脱敏替代删除 + legal_hold 标记 | 风险 |
| R29 | 明文存储 | 低 | 中 | AES-256-GCM 透明加密层 | 风险 |
| R30 | MCP/原生工具绕过审计 | 中 | 高 | audit_coverage_gap_scanner | 风险 |
| N1 | 审计写入增加操作延迟 | — | 中 | 异步写入 P99 < 5ms | 负面后果 |
| N2 | JSONL 日增 150 MB 需分层存储管理 | — | 中 | 三层存储自动迁移 | 负面后果 |
| N3 | 13 种异常签名可能产生误报需调优 | — | 中 | 首次部署 warn 模式 + 阈值可配置 | 负面后果 |
| N4 | 99 盲点中部分需 v2.0+ 才覆盖 | — | 中 | 逐步迭代覆盖 | 负面后果 |
| N5 | HMAC Secret 管理增加运维复杂度 | — | 中 | Shamir 分片 + 自动轮转 | 负面后果 |
| N6 | GDPR 删除权与审计不可变性存在根本冲突 | — | 中 | 脱敏替代删除 + legal_hold | 负面后果 |

### 能力边界声明（99 盲点）

| 盲点 ID | 内容 | v2.0 计划 |
|:---:|------|:---:|
| B15 | Agent 级 Ed25519 签名——完整密钥管理基础设施 | Phase production |
| B16 | Agent 冒充检测（IATP Challenge-Response 握手） | Phase production |
| B17 | LLM 完整 CoT 推理链 | Phase experimental |
| B18 | 跨 IDE 一致性交叉验证 | Phase experimental |
| B19 | 监管证据包 PDF 导出 | Phase beta |
| B20 | 外部独立验证端点 | Phase scaffold ✅ |
| B21 | 合规框架条款→实现的完整映射 | Phase beta |
| B22 | 审计日志 Git 隔离 | Phase scaffold ✅ |
| B23 | 渐进信任分数——连续值 + 时间衰减 | Phase experimental |
| B24 | Agent-to-Agent 委托链审计 | Phase experimental |
| B25 | 间接操作检测 | Phase experimental |
| B26 | 外部工具调用链闭环审计 | Phase experimental |
| B27 | 多 Agent 协同规避检测 | Phase experimental |
| B28 | 行为基线模型（ML 偏离检测） | v2.0 |
| B29 | 权限持续重新验证 | Phase production |
| B30 | 审计查询注入防御 | Phase scaffold ✅ |
| B31 | HMAC Secret 泄露——伪造审计条目 | Phase experimental |
| B32 | Bit Rot 静默存储损坏 | Phase experimental |
| B33 | 时间炸弹——延迟触发漏洞 | Phase experimental |
| B34 | 反馈自指循环 | Phase experimental |
| B35 | 供应链接入审计 | Phase beta |
| B36 | Session 边界攻击 | v2.0 |
| B37 | 审计数据 AI 上下文投毒 | Phase beta |
| B38 | 海量操作 DoS | Phase scaffold ✅ |
| B39 | Gradual Permission Escalation | Phase experimental |
| B40 | 运行时配置渐进漂移 | v2.0 |
| B41 | Emergency Access 的审计 | v2.0 |
| B42 | Schema Evolution 悖论 | v2.0 |
| B43 | Audit Trail 依赖死锁 | Phase scaffold ✅ |
| B44 | 人操作 vs AI 操作统一审计 | v2.0 |
| B45 | Provenance 数据的 Provenance 验证 | Phase experimental |
| B46 | Lamport 时钟边缘竞赛 | Phase scaffold ✅ |
| B47 | Rollback 自身审计链 | v2.0 |
| B48 | Knowledge Base 投毒 | Phase beta |
| B49 | 审计日志作为侧信道 | v2.0 |
| B50 | 审计日志膨胀到 Context Window 溢出 | Phase scaffold ✅ |
| B51 | Multi-Tenant 审计隔离 | v2.0 |
| B52 | 非工作时间定义的动态性 | v2.0 |
| B53 | Heartbeat 假阴性检测 | Phase experimental |
| B54 | Cold Start 基线法律风险 | Phase scaffold ✅ |
| B55 | Prompt 注入——恶意审计条目劫持 AI 决策 | Phase beta |
| B56 | Vibe Drift——AI 模型升级致审计代码不兼容 | Phase beta |
| B57 | AI 幻觉——审计分析/日报生成虚假发现 | Phase experimental |
| B58 | 确定性重放——无法从审计日志重建系统状态 | Phase experimental |
| B59 | 单人密钥仪式——Shamir 需 3 人独立保管分片 | v2.0 |
| B60 | Bus Factor = 1——维护者不可用致审计系统死亡 | v2.0 |
| B61 | 无 Peer Review——审计告警无人二次确认 | Phase scaffold ✅ |
| B62 | 审计质量渐进退化——无 peer review 感知衰减 | Phase beta |
| B63 | GDPR Art.17 删除权 vs 审计不可变性 | v2.0 |
| B64 | 明文存储——审计日志未加密 at rest | Phase experimental |
| B65 | 可信时间戳缺失——Ed25519 签名无法定时间效力 | v2.0 |
| B66 | 磁盘满静默失败——审计写入丢弃 | Phase scaffold ✅ |
| B67 | 审计写入阻塞主操作——"先审计还是先执行" | Phase scaffold ✅ |
| B68 | Schema 迁移完整性——v1→v2 迁移可验证 | Phase beta |
| B69 | 审计工具链完整性——Python/OS/fs 被篡改 | v2.0 |
| B70 | 隐身 Agent——生成合法但恶意的审计条目（Mimicry） | v2.0 |
| B71 | 时序攻击——操纵 Lamport 时钟/系统时间制造混乱 | Phase experimental |
| B72 | MCP/原生工具绕过审计——操作未记录 | Phase scaffold ✅ |
| B73 | 影子审计——Agent 意外创建第二条审计机制 | Phase experimental |
| B74 | Vibe Coding 覆盖缺口——AI 跳过边界条件审计 | Phase beta |
| B75 | AI 代码相似性混淆——生成相似但不相同的审计模式 | Phase experimental |
| B76 | 模板/脚手架伪审计——AI 生成代码产生虚假审计条目 | Phase experimental |
| B77 | 法庭可采性——审计证据链的 chain of custody 缺失 | Phase beta |
| B78 | 哈希链分叉——两个 IDE 并发写同一 prev_entry_hash | Phase experimental |
| B79 | 部分写入/撕裂写入——OS 崩溃致 JSONL 行不完整 | Phase scaffold ✅ |
| B80 | Unicode 同形字绕过净化——"іgnore"（Cyrillic і）绕过过滤器 | Phase experimental |
| B81 | 多会话协同攻击——单会话低于阈值、跨会话总和超标 | Phase experimental |
| B82 | AI 学习规避审计——AI 通过读原始 JSONL 学习审计模式 | Phase experimental |
| B83 | 格式寿命——JSONL 在 20 年内仍可解析？ | Phase scaffold ✅ |
| B84 | 依赖版本漂移——Pydantic v2→v3 审计数据无法验证 | Phase beta |
| B85 | 告警疲劳渐进建模——Operator 对 P1 响应率从 90%→10% | Phase beta |
| B86 | 信任漂移曲线——Operator 逐渐过度信任 AI 致审查松懈 | Phase beta |
| B87 | 新人 Onboarding 不可能——文档全是 AI 写给 AI 的 | Phase scaffold ✅ |
| B88 | 审计数据恢复——JSONL 文件部分损坏时尽可能恢复数据 | Phase experimental |
| B89 | Tool 调用逃逸——自定义 MCP Tool 绕过审计写入路径 | Phase experimental |
| B90 | 篡改痕迹时间线重建——若篡改发生，能否精确重建作案时间？ | Phase experimental |
| B91 | 跨系统日志关联——审计数据需与 CI/CD/云日志交叉验证 | v2.0 |
| B92 | 初始化的初始化——初始化脚本的 hash 在初始化前不可知 | Phase scaffold ✅ |
| B93 | 审计系统自身代码变更未被审计——AI 改 `writer.py` 无人知晓 | Phase experimental |
| B94 | 自然语言不一致——同一操作被不同 session 描述为不同文本 | Phase experimental |
| B95 | AI 模型供应商依赖——API 变更/倒闭/模型退役致审计系统失效 | Phase scaffold ✅ |
| B96 | 观测者效应——被审计的 AI 行为系统性异于未被审计的 AI | v2.0 |
| B97 | Goodhart 定律——AI 学会优化 trust-score/anomaly_score 而非优化行为 | Phase beta |
| B98 | 启动期审计盲区——系统启动到审计初始化之间的操作无记录 | Phase scaffold ✅ |
| B99 | "谁审计审计者？"无限递归——审计系统本身的审计链最终无外部锚点 | v2.0 |

---

## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 Phase（scaffold → experimental → beta → production） |
| 施工模式 | 扩展（v1.4.0 基线 + v2.0.0 容量升级） |
| 核心风险 | 分片写入架构重写 writer.py 可能破坏现有写入链路 |
| 目标 generation | 9 — 本次施工将蓝图从 generation 8 升级到 generation 9 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-016 Shared Core 已就绪 | hard | ✅ | ✅ |
| 2 | MOD-DATABASE Database 已就绪 | hard | ✅ | ✅ |
| 3 | CFG-CAP-001 容量参数已设定 | hard | ✅ | ✅ |
| 4 | MOD-INF-005 Script System 审计钩子接口已定义 | soft | ❌ | ⚠️ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：v2-scaffold——分片写入架构 + 新事件类型

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 AuditWriter / §3 蓝图特有:审计事件类型 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\audit-trail\` |
| 验收标准 | ShardedAuditWriter 16 shard 写入 + AuditEntryV2 Pydantic 校验 + 15 种新事件类型 |
| 验证命令 | `python -m pytest tests/audit-trail/ -k "shard or entry_v2" -v` |
| G7 检查项 | writer.py 重写后旧写入链路是否保留为 fallback？新 shard 文件路径是否与 §11 一致？ |

#### 步骤 2：v2-experimental——Script System 集成 + 查询分片 + Lamport V2

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 AuditQuery / §3 蓝图特有:LamportClock |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\audit-trail\` |
| 验收标准 | ScriptAuditHook 集成 + ShardedQueryRouter 并行查询 + LamportClockV2 三元组 |
| 验证命令 | `python -m pytest tests/audit-trail/ -k "script_audit or query_router or lamport_v2" -v` |
| G7 检查项 | Script System 依赖方向是否单向？Lamport V2 是否向后兼容 V1？ |

#### 步骤 3：v2-beta——跨分片 Merkle + 存储容量告警 + 去抖/背压

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3 蓝图特有:自监控 / §5.2 容量估算 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\audit-trail\` |
| 验收标准 | CrossShardMerkle 聚合 + 容量告警 + 写入去抖 500ms + 背压机制 |
| 验证命令 | `python -m pytest tests/audit-trail/ -k "cross_shard or capacity or debounce or backpressure" -v` |
| G7 检查项 | 跨分片 Merkle 锚定间隔是否与 §17 一致？背压阈值是否与 CFG-CAP-001 对齐？ |

#### 步骤 4：v2-production——性能基准 + 容量校准 + WORM 备份

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 容量估算 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\audit-trail\` + `D:\ZephyrAlpha\scripts\governance\` |
| 验收标准 | 100 AI 并发模拟 + 容量校准器联动 + WORM 兼容分片备份 |
| 验证命令 | `python -m pytest tests/audit-trail/ -k "benchmark or capacity_calib or worm" -v` |
| G7 检查项 | 性能基准是否覆盖 120 条/秒峰值？WORM 备份是否独立于 git？ |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | ShardedAuditWriter 写入失败 | 回退到单文件 AuditWriter（保留为 fallback） |
| 2 | Script System 集成异常 | 移除 ScriptAuditHook，审计写入不受影响 |
| 3 | 跨分片 Merkle 聚合错误 | 禁用跨分片锚定，单 shard 哈希链仍有效 |
| 4 | 性能基准不达标 | 调整 shard_count / buffer_max_size 参数 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | shard_writer.py | `D:\ZephyrAlpha\src\zephyr\audit-trail\shard_writer.py` | ☐ | ☐ | ☐ |
| 2 | global_index.py | `D:\ZephyrAlpha\src\zephyr\audit-trail\global_index.py` | ☐ | ☐ | ☐ |
| 3 | script_audit_hook.py | `D:\ZephyrAlpha\src\zephyr\audit-trail\script_audit_hook.py` | ☐ | ☐ | ☐ |
| 4 | query_router.py | `D:\ZephyrAlpha\src\zephyr\audit-trail\query_router.py` | ☐ | ☐ | ☐ |
| 5 | cross_shard_merkle.py | `D:\ZephyrAlpha\src\zephyr\audit-trail\cross_shard_merkle.py` | ☐ | ☐ | ☐ |
| 6 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 7 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 8 | 告警已配置 | §6.1 每项阈值有告警规则 | 就绪 | ☐ |
| 9 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 10 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 11 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ☐ |
| 12 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 哈希链算法 | 算法 | entry.entry_hash = SHA-256(entry_id + prev_entry_hash + entry_type + utc_timestamp.isoformat() + agent_id) | writer.py |
| 2 | HMAC 签名 | 协议 | hmac_signature = HMAC-SHA256(ZEPHYR_AUDIT_HMAC_SECRET, entry.entry_hash) | writer.py |
| 3 | Ed25519 Agent 签名 | 协议 | agent_signature = Ed25519.sign(entry.entry_hash, agent_private_key) | agent_signer.py |
| 4 | Lamport 时钟合并 | 算法 | counter = max(local_counter, received_counter) + 1 | writer.py |
| 5 | Merkle 树构建 | 算法 | 收集 1h 内所有 entry_hash → 二叉 Merkle 树 → 根哈希写入 merkle JSON | merkle_hourly.py |
| 6 | 一致性哈希分片 | 算法 | shard_id = SHA-256(session_id + agent_did) % 16 | shard_writer.py |
| 7 | SQLite 索引重建 | SQL | INSERT OR IGNORE INTO task_summary SELECT ... FROM jsonl_parse() | indexer.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m zephyr.audit_trail.cli verify` | 完整性验证 | `--fast-mode`: 快速模式(默认True) | IntegrityReport |
| 2 | 命令 | `python -m zephyr.audit_trail.cli query` | 审计查询 | `--task-id`/`--agent-id`/`--session-id` | 审计摘要/明细 |
| 3 | 配置 | `ZEPHYR_AUDIT_HMAC_SECRET` | HMAC 签名密钥 | 256-bit 环境变量 | 必须设置否则写入失败 |
| 4 | 配置 | `data/audit/` | 审计数据目录 | JSONL+SQLite+Merkle | .gitignore 隔离 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 哈希链断裂 | integrity_check 返回非空 | 检查断裂位置 → 从 Merkle 重建 | 重建断裂段 | verify_integrity exit 0 |
| 2 | 施工 | SQLite 索引损坏 | 查询异常/数据不一致 | 删除 audit-index.db → 重建 | rebuild_index() | 记录数 == JSONL 行数 |
| 3 | 运行 | 磁盘空间不足 | disk_usage_pct > 90% | 执行保留期清理 + 温冷迁移 | 释放空间 | disk_usage_pct < 80% |
| 4 | 运行 | Agent 签名验证失败 | Ed25519 verify 返回 False | 检查 DID 注册 → 检查密钥轮转 | 更新公钥 | 签名验证通过 |
| 5 | 运行 | 审计写入超时 | write_latency > 10ms P99 | 检查磁盘 I/O → 检查 shard 分布 | 调整 shard_count | P99 < 5ms |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同 shard JSONL 写入 | asyncio.Queue 串行化 | Queue FIFO 排队 | 串行追加，无合并 |
| 跨 shard 查询 | 并行 asyncio.gather | 结果合并 | 按时间戳排序 |
| SQLite 索引更新 | WAL 模式并发读/串行写 | 读写不互斥 | 最后写入胜出 |
| Lamport 时钟合并 | counter 比较 | max+1 | 全序化 |
| 同文件哈希链 | shard 内串行 | 串行保证链连续 | 无合并需求 |

---

## §17 容量升级附录

> generation≥2 的蓝图必须填写。本节描述 v1.4.0 → v2.0.0 的容量升级方案。

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 审计写入速率 | < 1 条/秒 | 单 AI + 单人场景 |
| 日增 JSONL | ~2,000 行 | 实际审计日志统计 |
| SQLite 索引 | 单文件 | audit-index.db |
| 哈希链模型 | 全局单链 | prev_entry_hash 指向前一条 |
| Lamport 时钟 | (ide, counter) 二元组 | 3 个 IDE |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-AT-V1 | 审计写入吞吐不足 | 分片写入池（16 shard） | > 10 条/秒 |
| GAP-AT-V2 | 哈希链串行瓶颈 | 分区链 + 跨分片 Merkle 锚定 | > 5 AI 并发 |
| GAP-AT-V3 | SQLite 单索引瓶颈 | 分片 SQLite + 全局路由索引 | 月增 > 1M 行 |
| GAP-AT-V4 | 脚本执行无审计 | 15 种新事件类型 + 审计钩子 | 任何脚本执行 |
| GAP-AT-V5 | Lamport 二元组不够区分 | 三元组 (ide, session_id, counter) | > 10 AI session |
| GAP-AT-V6 | 存储容量未预估 | 日增 100K 条 × 分层存储 | 日增 > 10K 条 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.4.0 | 7 | 基线 | 35 文件——核心写入+完整性+查询+异常+漂移+签名+信任+证据包 | ✅ |
| v2.0.0 | 8 | 容量升级 | 分片写入+分区链+脚本审计+Lamport V2+容量预估 | ⚠️ 待施工 |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-AT-001 | governance/ 根级 13 文件未迁移至 audit-trail/ | P1 | v2.0 | 待迁移 |
| GAP-AT-V1 | 审计写入吞吐不足 | P0 | v2.0 | 待施工 |
| GAP-AT-V2 | 哈希链串行瓶颈 | P0 | v2.0 | 待施工 |
| GAP-AT-V3 | SQLite 单索引瓶颈 | P1 | v2.0 | 待施工 |
| GAP-AT-V4 | 脚本执行无审计 | P1 | v2.0 | 待施工 |
| GAP-AT-V5 | Lamport 二元组不够 | P1 | v2.0 | 待施工 |
| GAP-AT-V6 | 存储容量未预估 | P2 | v2.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ShardedAuditWriter | GAP-AT-V1 | shard_writer.py | v2-scaffold | 待施工 |
| HashChainState (per shard) | GAP-AT-V2 | shard_writer.py | v2-scaffold | 待施工 |
| ShardedQueryRouter | GAP-AT-V3 | query_router.py | v2-experimental | 待施工 |
| GlobalIndex | GAP-AT-V3 | global_index.py | v2-scaffold | 待施工 |
| ScriptAuditHook | GAP-AT-V4 | script_audit_hook.py | v2-experimental | 待施工 |
| LamportClockV2 | GAP-AT-V5 | models.py (修改) | v2-experimental | 待施工 |
| CrossShardMerkle | GAP-AT-V2 | cross_shard_merkle.py | v2-beta | 待施工 |

### §V2 分片写入架构

```yaml
v2_audit_write_architecture:
  shard_strategy:
    method: "consistent_hashing_by_session"
    shard_count: 16
    hash_key: "session_id + agent_did"
  shard_structure:
    path_pattern: "data/audit/shard_{shard_id:02d}/"
    files_per_shard:
      - "audit-trail-{YYYY-MM-DD}.jsonl"
      - "audit-index.db"
      - "merkle/audit-merkle-{YYYY-MM-DDTHH}.json"
      - "hash_chain_state.json"
    cross_shard_index:
      path: "data/audit/global-index.db"
      content: "{entry_id → shard_id}"
      rebuild: "从各 shard index.db 聚合（延迟 30s）"
  write_pipeline:
    step_1: "hash(session_id) % 16 → shard_id"
    step_2: "写入该 shard 内存缓冲区（asyncio.Queue, maxsize=1000）"
    step_3: "每 100ms 或满 50 条刷盘"
    step_4: "O_APPEND 原子追加到 shard JSONL"
    step_5: "shard 内串行——prev_entry_hash = SHA-256(上一条本 shard 条目)"
    step_6: "shard SQLite 异步更新（WAL 模式）"
  performance:
    shard_write_latency_p99_ms: 3
    cross_shard_query_latency_p99_ms: 50
    total_throughput_entries_per_sec: 240
```

### §V3 哈希链并发化

```yaml
v2_hash_chain_architecture:
  per_shard_hash_chain:
    entry_schema_update:
      prev_entry_hash: "指向前一条同 shard 条目的 SHA-256"
      shard_id: "当前条目所属分片 ID（新增）"
      shard_sequence: "同 shard 内自增序列号（新增）"
      cross_shard_anchor: "上一份跨分片 Merkle 根的 SHA-256（每 1000 条/次，新增）"
  cross_shard_merkle_anchoring:
    interval: "每 1000 条全局条目 或 每小时"
    description: "收集 16 shard 当前 Merkle 根 → 构建跨分片 Merkle 树 → 根哈希写入每个 shard 下一条"
```

### §V4 查询索引伸缩

```yaml
v2_query_architecture:
  per_shard_index:
    path: "data/audit/shard_{id:02d}/audit-index.db"
    tables: [task_summary, file_detail, script_execution, scan_events]
  global_index:
    path: "data/audit/global-index.db"
    content: "entry_id → shard_id → shard_sequence"
  query_strategies:
    by_task_id: "global_index → 定位 1 shard → 查询（P99 < 5ms）"
    by_agent: "hash(agent_did) % 16 → 定位 1 shard（P99 < 5ms）"
    by_file_path: "并行 16 片 SQLite（P99 < 50ms）"
    by_time_range: "并行 16 片（P99 < 500ms，周检）"
    trail_for_ai_context: "hash(session_id) % 16 → 单 shard（P99 < 10ms）"
```

### §V5 脚本执行审计事件模型

```python
class AuditEventTypeV2(str, Enum):
    # ... (保留 v1.1.0 全部 31 种) ...
    SCAN_TRIGGERED = "scan_triggered"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    SCRIPT_EXECUTION_STARTED = "script_execution_started"
    SCRIPT_EXECUTION_COMPLETED = "script_execution_completed"
    SCRIPT_EXECUTION_FAILED = "script_execution_failed"
    SCRIPT_EXECUTION_TIMEOUT = "script_execution_timeout"
    SCRIPT_FINDING = "script_finding"
    SCRIPT_REGISTERED = "script_registered"
    SCRIPT_RETIRED = "script_retired"
    SCRIPT_THRESHOLD_CHANGED = "script_threshold_changed"
    MODULE_SCRIPT_MAPPING_CHANGED = "module_script_mapping_changed"
    INCREMENTAL_SCRIPT_SELECTION = "incremental_script_selection"
```

审计记录粒度决策（D-020-57）：脚本执行级 1 条/脚本 + 扫描级 2 条/扫描 + Finding 级仅 P0/P1 入审计。单次增量扫描 ≤ 60 条。

### §V6 扫描调度审计集成

```yaml
v2_script_system_integration:
  audit_hooks:
    on_scan_triggered: {timing: "同步——阻断式", event: "SCAN_TRIGGERED"}
    on_script_started: {timing: "异步——fire-and-forget", event: "SCRIPT_EXECUTION_STARTED"}
    on_script_completed: {timing: "异步", event: "SCRIPT_EXECUTION_COMPLETED/FAILED/TIMEOUT"}
    on_finding: {timing: "异步", event: "SCRIPT_FINDING", filter: "仅 P0/P1"}
    on_scan_completed: {timing: "同步", event: "SCAN_COMPLETED"}
  dependency_direction: "Script System → Audit Trail（单向依赖）"
```

### §V7 Lamport 时钟三元组

```python
class LamportClockV2:
    def __init__(self, ide_source: str, session_id: str) -> None:
        self._ide = ide_source
        self._session_id = session_id
        self._counter = 0
    def tick(self) -> tuple[str, str, int]:
        self._counter += 1
        return (self._ide, self._session_id, self._counter)
```

增量扫描去抖：同 session 500ms 内多次变更合并为一次扫描。

### §V8 自监控容量升级

新增指标：shard_write_latency_p99_ms / shard_buffer_depth / shard_jsonl_file_size_mb / script_execution_audit_coverage / scan_audit_latency_p99_ms / cross_shard_query_latency_p99_ms / global_index_staleness_seconds。

### §V9 存储容量预估

| 维度 | 日增量 | 月增量 |
|------|:------:|:------:|
| JSONL 原始 | ~150 MB | ~4.5 GB |
| SQLite 索引 | ~30 MB | ~0.9 GB |
| Merkle 文件 | ~2 MB | ~60 MB |
| CoT 文件 | ~50 MB | ~1.5 GB |
| **总计** | **~232 MB** | **~7.5 GB** |

热存储 7d（16 shard）≈ 16.8 GB NVMe。3 年冷归档 ≈ 75 GB 压缩后。1TB NVMe 完全够用。

### 升级对现有文件的影响

| 现有文件 | v2.0.0 变更 |
|---------|-----------|
| `models.py` | ✅ 新增 AuditEntryV2 (3 字段) + 7 个脚本审计模型 + 15 种新事件类型 |
| `writer.py` | 🔄 重写为 ShardedAuditWriter（16 shard + 内存缓冲 + async flush），原单文件写入器保留为 fallback |
| `query.py` | 🔄 新增 ShardedQueryRouter |
| `integrity.py` | 🔄 新增 per_shard + cross_shard Merkle 验证 |
| `anomaly.py` | ✅ 新增 ANM-017 (脚本执行覆盖率异常) |
| `self_monitor.py` | 🔄 新增 per_shard + per_agent_session heartbeat + 6 个新指标 |
| `cli.py` | ✅ 新增 `zephyr audit scan-trail <scan_id>` 命令 |
| 新增 `shard_writer.py` | 🆕 单 shard 写入 + JSONL + 哈希链 + SQLite 索引 |
| 新增 `global_index.py` | 🆕 全局路由索引 |
| 新增 `script_audit_hook.py` | 🆕 Script System 集成钩子 |
| 新增 `query_router.py` | 🆕 跨 shard 并行查询 |
| 新增 `cross_shard_merkle.py` | 🆕 跨分片 Merkle 根聚合 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> 本节同时覆盖原 §7 备选方案——"选项"列已包含备选方案信息，无需独立章节。
> 本节同时覆盖原 §15 后果——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| 决策 ID | 决策 | 日期 | 依据 |
|---------|------|------|------|
| D-020-01 | 两层审计粒度（任务级摘要+文件级明细） | 2026-05-05 | 1人场景，任务级摘要够日常浏览，文件级明细够问题定位 |
| D-020-02 | JSONL 为唯一真源，SQLite 为派生查询索引 | 2026-05-05 | 多 IDE 并发，JSONL 天然 append-only 且 git 友好；对标 GOV-CMP-002 |
| D-020-03 | Provenance 按权限级别分级（轻量/标准/全量） | 2026-05-05 | 1人+AI场景，99%操作无草稿和仲裁，强制三件套形同虚设 |
| D-020-04 | 密码学完整性——哈希链 + HMAC + Merkle | 2026-05-05 | JSONL append-only ≠ tamper-evident；AI 可删除行后重 append；对标 Microsoft AGT Merkle-chain + W3C PROV |
| D-020-05 | 元审计——审计系统自身操作留痕 | 2026-05-05 | 1人+AI 维护，无人审计审计系统本身；对标 GOV-CMP-002 AUD-001 |
| D-020-06 | 蓝图漂移检测——实际操作 vs 蓝图规定 | 2026-05-05 | 对标 ISACA 2025 "Embedded not paper" + MOD-INF-023 Drift Detector |
| D-020-07 | AI 行为异常签名——13 种自动检测模式（v1.1.0 扩展） | 2026-05-05 | 对标 OWASP ASI-10 "Lack of Observability" + ISACA 自修改AI审计 |
| D-020-08 | 三角闭环反馈——审计聚合数据回写 Policy 驱动规则演进 | 2026-05-05 | 对接 KBG-0010 §4.4 Runtime→Policy 接口；对标 Netflix 混沌反馈 |
| D-020-09 | Lamport 逻辑时钟——多 IDE 时序一致性 | 2026-05-05 | 多 IDE `datetime.now()` 不可靠；对标 Dynamo Vector Clock |
| D-020-10 | 三层存储（热/温/冷）+ 自动迁移 | 2026-05-05 | JSONL 膨胀不可持续；对标 Goldman SecDB 分层 + AWS S3 lifecycle |
| D-020-11 | 隐私脱敏——写入时自动检测 PII 并掩码 | 2026-05-05 | 审计日志不可变 + GDPR/HIPAA 合规；对标 GOV-CMP-002 AUD-004 |
| D-020-12 | 保留期自动执行——dry-run 先行 + Owner 审批 | 2026-05-05 | 对标 GOV-CMP-002 + GOV-DATA-003；无人手动清理 |
| D-020-13 | Cold Start——git log 回溯生成历史审计基线 | 2026-05-05 | 审计系统首次启动时无历史数据；baseline 标记 low confidence |
| D-020-14 | Agent 级 Ed25519 数字签名——non-repudiation | 2026-05-05 | HMAC 系统级+CAN 不区分 Agent；对标 Microsoft AGT Ed25519 Agent Signing + OWASP ASI-09 |
| D-020-15 | LLM CoT 推理链审计 | 2026-05-05 | 对标 OWASP ASI-10 完整可观测性 + FCA 监管文件审查"推理"维度 |
| D-020-16 | 委托链审计——深度控制 + 权限缩小 | 2026-05-05 | 对标 Microsoft AGT DelegationChain + NIST 2026 委托身份追踪 |
| D-020-17 | 渐进信任分数——连续值 + 时间衰减 | 2026-05-05 | 对标 ISACA "trust degrades without continued good behavior" + AGT Trust Scoring |
| D-020-18 | 外部独立验证端点 | 2026-05-05 | 100% AI 施工——AI 不能自证清白；对标 Goldman probe/Prometheus 探测层 |
| D-020-19 | 跨 IDE 一致性交叉验证 | 2026-05-05 | 对标 Goldman SecSync 不一致检测 |
| D-020-20 | 外部工具调用链审计 | 2026-05-05 | 对标 ISACA "使用工具"三要素闭环 + Agent→MCP→API 可追溯 |
| D-020-21 | 间接操作检测 | 2026-05-05 | Agent 可通过 symlink/script/cron/MCP 绕开直写审计 |
| D-020-22 | Dry-Run vs Real 差异检测 | 2026-05-05 | AI 在 dry-run 时说 X 实际做 Y → 差异异常报告 |
| D-020-23 | 供应链审计——包安装可追溯 | 2026-05-05 | `pip install`/`npm install` 需审计记录 — 对标 OWASP 供应链安全 |
| D-020-24 | 监管证据包一键导出 | 2026-05-05 | 对标 FCA 格式 + SEC 17a-4 审计要求 |
| D-020-25 | 合规框架条款映射 | 2026-05-05 | 对标 Microsoft Agent Compliance 自动合规验证 |
| D-020-26 | 反馈循环自审计 | 2026-05-05 | 防止三角闭环自我强化错误模式 |
| D-020-27 | Git 隔离——审计日志独立存储 | 2026-05-05 | 防止 git reset 导致审计历史丢失 |
| D-020-28 | Knowledge Base 投毒防护 | 2026-05-05 | 审计数据→KB 的投毒防护门禁 |
| D-020-29 | rate_limit + volume_dos 防护 | 2026-05-05 | 防止 Agent 海量小操作 DoS 审计系统 |
| D-020-30 | trail_for_ai_context() 升级为 P0 接口 | 2026-05-05 | AI 是审计日志的主读者——输出设计为 AI 零推理可消费 |
| D-020-31 | Prompt 注入防护——审计条目禁止含 AI 指令关键词 | 2026-05-05 | trail_for_ai_context() 将审计数据注入 LLM context——任何 AI 可读数据都是潜在 prompt injection 向量 |
| D-020-32 | model_version 元数据——记录生成审计条目的 AI 模型版本 | 2026-05-05 | 氛围编程语境——AI 模型版本变化会导致审计代码模式不可复现 |
| D-020-33 | 审计分析结果溯源——每条分析结论关联源 entry_id | 2026-05-05 | 防止 AI 分析审计数据时产生幻觉结论 |
| D-020-34 | 确定性重放——关键操作完整记录 sha256_before/after | 2026-05-05 | 对标 Goldman trade reconstruction——审计必须支持"回到任意时刻" |
| D-020-35 | Bus Factor = 1 缓解——审计系统全自动化自愈 | 2026-05-05 | 1人+AI 维护——维护者不可用时审计系统继续运作 |
| D-020-36 | 审计质量退化检测——auto_regression_test 周检 | 2026-05-05 | 无 peer review——质量退化是渐进的、不可见的 |
| D-020-37 | GDPR Art.17 处理——脱敏替代删除 | 2026-05-05 | 审计不可变性与删除权不可调和——脱敏是唯一折中 |
| D-020-38 | AES-256-GCM 透明加密层——写入前加密 + key 派生 | 2026-05-05 | 审计日志含敏感操作记录——加密 at rest 对标 HIPAA SEC 164.312 |
| D-020-39 | 磁盘满 P0 阻断——写失败阻断 AI 操作 | 2026-05-05 | 审计系统写入失败时继续允许 AI 操作 = 盲飞——不可接受 |
| D-020-40 | 异步写入——审计不阻塞主操作 | 2026-05-05 | 氛围编程核心价值——审计不应降低开发速度 |
| D-020-41 | audit_coverage_gap_scanner——检测未记录的变更 | 2026-05-05 | MCP/原生工具可能绕过审计写入路径 |
| D-020-42 | 时钟跳变检测——Lamport + NTP 交叉验证 | 2026-05-05 | 时序攻击——操纵时钟可在审计时间线中"隐藏"操作 |
| D-020-43 | Vibe Coding 覆盖 Fuzzer——注入边界条件提升覆盖率 | 2026-05-05 | 氛围编程天然跳过边界条件——fuzzer 自动发现覆盖缺口 |
| D-020-44 | Genesis 初始化仪式——信任锚由 Owner 手动执行 | 2026-05-05 | 所有后续信任起源于 genesis——初始化被 compromise = 一切无效；AI 不参与初始化执行 |
| D-020-45 | 哈希链分叉处理——fork_detection + fork_reconciliation | 2026-05-05 | 并发写入同一 prev_entry_hash → 两条合法链——必须检测并标记 |
| D-020-46 | 撕裂写入检测——最后一行完整性回退 | 2026-05-05 | OS 崩溃产生不完整 JSONL 行——需原子写入策略 |
| D-020-47 | Unicode 归一化优先级——净化前必须 NFKC 归一化 | 2026-05-05 | Cyrillic "іgnore" 等同形字绕过过滤器——归一化是第一道防线 |
| D-020-48 | 跨 Session 长窗口异常检测——ANM-016 | 2026-05-05 | 单 session 低于阈值但跨天/周总和超标——低强度渗透检测 |
| D-020-49 | AI 读取审计日志必须元审计记录 | 2026-05-05 | AI 可通过读原始 JSONL 学习审计模式——所有 AI 访问审计数据均留痕 |
| D-020-50 | 依赖版本冻结 + 旧环境 Docker 留存 | 2026-05-05 | Pydantic v2→v3 等升级可能破坏审计数据可验证性 |
| D-020-51 | Operator 响应率建模——响应率 < 30% → P0 | 2026-05-05 | 告警疲劳使系统实质上无监控——需主动检测而非等 Operator 自己说 |
| D-020-52 | trust_calibration——实际 anomaly 率 vs 审核通过率对比 | 2026-05-05 | Operator 逐渐过度信任 AI——需主动检测信任漂移 |
| D-020-53 | 审计系统自身代码变更审计——模块文件哈希快照 | 2026-05-05 | AI 可能修改 audit-trail/ 自身代码绕过审计——审计系统需自我防御 |
| D-020-54 | 自然语言标准化——canonical_action_vocabulary | 2026-05-05 | 不同 session 对同一操作的文本描述不一致→跨 session 分析失真 |
| D-020-55 | AI 模型供应商独立性——双供应商兼容 + 本地 fallback | 2026-05-05 | AI 供应商 API 变更/倒闭→审计系统依赖的 AI 推理能力丧失 |
| D-020-56 | Goodhart 防御——metric_gaming_detector + ANM-018 | 2026-05-05 | 指标成为目标时即失效——AI 学会优化 trust-score 而非行为质量 |
| D-020-57 | 启动期审计盲区——boot_audit_gap_logger + 启动前钩子 | 2026-05-05 | 系统启动到审计 init 间的操作无人记录——独立最小记录器填补 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。**永久保留**。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 路径错误 |
| 2 | **必备链接不可省略** | 信息缺失 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程 | 信息淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移 |
| 6 | **容量估算必须写** | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | 断链/垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止** | 执行漂移 |
| 9 | **蓝图必须自包含** | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 永久丢失 |
| 11 | **construction_progress 必须与代码实际状态一致** | 虚假进度 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 双源漂移 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 信息淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不清 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

| STEP | 判定 | 条件 | 操作 |
|------|------|------|------|
| 1 | 识别职责域 | 服务对象、变更频率、依赖关系是否与蓝图主体一致？ | — |
| 2a | 职责相同→原地升级 | 服务对象相同 + 变更频率同步 + 依赖关系重叠 | §17 容量升级附录增量记录 |
| 2b | 职责不同→拆分独立蓝图 | 满足任一：(a)独立module_id前缀 (b)独立Phase路线图 (c)独立依赖图(交集<50%) (d)内容>100行且无直接数据流 | 创建子蓝图；本蓝图§10引用子蓝图 |
| 3 | 拆分后验证 | — | 子蓝图MUST有独立frontmatter+概述+§0~§18；belongs_to=本蓝图module_id；本蓝图§10新增子蓝图引用；blueprint_registry.yaml同步更新 |

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| 本蓝图 §17 容量升级（分片写入+分区链+脚本审计） | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 本蓝图 §3 蓝图特有：Genesis 信任锚初始化 | **原地** | Genesis 是审计链的组成部分，不是独立子系统 |
| 假设新增"审计可视化仪表盘"模块 | **拆分** | 独立 UI 模块 + 独立依赖（前端框架）+ 与审计核心无直接数据流 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。**永久保留**。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 安全删除方案 |
|---|---------------|------------|---------|------------|
| 1 | governance/ 根级 13 孤儿文件 | `D:\ZephyrAlpha\src\zephyr\governance\*.py` | 迁移型 | 迁移至 audit-trail/ + 桥接导入 + 验证 → 标记 deprecated → Phase 4 物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。**永久保留**。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | AiAuditLogger (shared) | `D:\ZephyrAlpha\src\zephyr\shared\production\audit_logger.py` | 审计日志写入 | shared 版为基础实现；本蓝图定义哈希链+HMAC+Ed25519+Merkle 增强需求 |
| 2 | blueprint_reads.jsonl | `D:\ZephyrAlpha\data\audit\blueprint_reads.jsonl` | 蓝图读取日志 | 仅记录蓝图读取，非全量审计；本蓝图替代并扩展 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | audit-trail/ 代码目录 | `D:\ZephyrAlpha\src\zephyr\audit-trail\` | 修改 | v2.0 分片写入升级 |
| 2 | 审计数据目录 | `D:\ZephyrAlpha\data\audit\` | 修改 | 分片存储结构 |
| 3 | 推理链数据目录 | `D:\ZephyrAlpha\data\reasoning\` | 读取 | CoT 审计引用 |
| 4 | 外部验证脚本 | `D:\ZephyrAlpha\scripts\governance\verify_audit_integrity.py` | 修改 | 支持分片验证 |
| 5 | 索引重建脚本 | `D:\ZephyrAlpha\scripts\governance\rebuild_audit_index.py` | 修改 | 支持分片索引重建 |
| 6 | governance/ 根级 13 文件 | `D:\ZephyrAlpha\src\zephyr\governance\` | 迁移 | 迁移至 audit-trail/ |
| 7 | .gitignore | `D:\ZephyrAlpha\.gitignore` | 修改 | 添加 data/audit/ |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 审计追踪链架构设计 | **本文档 §1-§10** | 已废弃的 v1.4.0 蓝图 |
| 审计模块施工步骤 | **本文档 §16** | — |
| 审计接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-018 Agent RBAC 蓝图 | §4 接口契约(G-CT-001) |
| Tier 1 | MOD-INF-021 Rollback 蓝图 | §4 接口契约(G-CT-002) |
| Tier 1 | MOD-INF-019 Agent Spec 蓝图 | §4 接口契约(G-CT-007) |
| Tier 2 | verify_audit_integrity.py | §4 数据模型+§11 产出物路径 |
| Tier 2 | rebuild_audit_index.py | §4 数据模型+§11 产出物路径 |
| Tier 3 | src/zephyr/audit-trail/*.py | §4 数据模型 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改(§4) | 需 Owner 审批+通知消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改(§2) | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充 | AI 可自主修改 | — | — |
| 容量升级方案新增(§17) | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |

---

## 变更记录

> 变更历史见 `git log -- docs/03_modules/_domain_governance/audit_trail/blueprint.md`

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| JSONL SSoT | 审计日志唯一真源——JSONL append-only 文件 | SQLite 索引 | SQLite 是派生索引，可从 JSONL 重建 |
| 哈希链 | 每条审计条目包含前一条 SHA-256 的链式结构 | Merkle 树 | 哈希链=条目级串行，Merkle=批量并行 |
| HMAC 签名 | 系统级对称签名——证明"系统写入了这条" | Ed25519 签名 | HMAC=系统级对称，Ed25519=Agent级非对称 |
| Provenance | 操作溯源深度——LIGHT/STANDARD/FULL 三级 | 权限级别 | 权限决定 Provenance 深度，但两者不等价 |
| Lamport 时钟 | 逻辑时钟——解决多 IDE 时序问题 | 物理时钟 | datetime.now() 在多 IDE 间不可靠 |
| Genesis 条目 | 审计链第一条——prev_entry_hash='genesis' | 普通条目 | Genesis 由 Owner 手动创建，不可由 AI 创建 |
| DID | 去中心化身份标识——did:zephyr:{sha256(pubkey)[:16]} | agent_id | agent_id 是逻辑标识，DID 绑定 Ed25519 公钥 |
| 三角闭环 | Policy→Factory→Runtime→反馈回写 Policy 的闭环 | 单向反馈 | 闭环=反馈驱动规则演进，非仅告警 |

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 全部 v2.0 组件实现+性能基准通过 | 基线架构已验证，分片架构待施工 |
| 接口契约 | stable | 高 | AuditEntryV2 实现后冻结 | V1 接口已稳定 |
| 数据模型 | evolving | 中 | AuditEntryV2 + 15 种新事件类型实现后升级 | V2 字段待添加 |
| 施工步骤 | evolving | 中 | 步骤 1-4 全部完成 | 步骤 1 待施工 |

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.2.0 | 初始设计 | — | 已完成 |
| v1.4.0 | 35 文件基线实现 | v0.2.0 | 已完成 |
| v2.0.0 | 分片写入+分区链+脚本审计+Lamport V2 | v1.4.0 | 待施工 |
| v2.1.0 | 模板合规+压缩 | v2.0.0 | 施工中 |


## Consumers
- zephyr.audit_trail (internal)
