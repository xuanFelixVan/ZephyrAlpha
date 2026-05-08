---
module_id: "MOD-INF-020"
title: "审计追踪链蓝图 — 不可变动作审计 + 密码学 Provenance + Agent 级签名 + CoT 推理链 + 漂移检测 + 三角闭环"
doc_type: blueprint
status: Draft
version: "1.4.0"
generation: 7
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: phase_1_scaffold_partial
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha 审计追踪链蓝图 v1.1.0——每个 AI 动作的不可变、密码学完整性保证的审计记录。JSONL 为唯一真源 + 哈希链防篡改 + HMAC 系统级签名 + Agent 级 Ed25519 数字签名（non-repudiation）+ CoT 推理链审计 + Lamport 逻辑时钟 + 分级 Provenance + 蓝图漂移检测 + 异常行为签名 + 元审计自监控 + 三角闭环反馈（Policy→Factory→Runtime→反馈回写 Policy）+ 渐进信任分数 + 委托链审计 + 跨 IDE 一致性交叉验证 + 外部独立验证端点 + 监管证据包导出 + 合规框架条款映射。三层存储（热/温/冷）+ 隐私脱敏策略 + 供应链审计 + 间接操作检测 + Dry-Run 预审计 + Cold Start 历史回溯 + Git 隔离审计日志。对标 Goldman SecDB immutable audit log + ISACA 2025 Agentic AI 三要素 + OWASP ASI-09/10 2026 + Microsoft AGT Merkle-chain integrity + Agent DID/Ed25519 + IATP 握手 + W3C PROV 三元组模型 + NIST 2026 AI Agent Standards + FCA 监管文件审查格式。"
tags: [audit-trail, provenance, immutable-log, traceability, compliance, infrastructure, cryptographic-integrity, hash-chain, hmac-signing, ed25519, agent-signing, non-repudiation, cot-audit, reasoning-chain, lamport-clock, drift-detection, anomaly-detection, meta-audit, tiered-storage, privacy-redaction, feedback-loop, policy-factory-runtime, w3c-prov, owasp-asi09, owasp-asi10, self-monitoring, trust-score, delegation-chain, cross-ide-consistency, external-verifier, evidence-pack, compliance-map, supply-chain-audit, indirect-operation, git-isolation, kb-poisoning-prevention, nist-2026, fca]
priority: P0
depends_on:
  - {target: "MOD-INF-012", at: "§3", why: "Database——SQLite 派生查询索引的存储"}
  - {target: "MOD-INF-007", at: "§2", why: "Gate Engine——门禁决策的审计记录 + 实时阻断联动"}
  - {target: "MOD-INF-002", at: "§2", why: "Runtime Integration——RI-13 EventStore + RI-14 DryRunSimulator + RI-15 CostTracker 联动"}
  - {target: "MOD-INF-016", at: "§2.6", why: "Shared Core——EventType 枚举 + Task Schema + 韧性基座"}
  - {target: "GOV-CMP-002", at: "full", why: "审计追踪策略——AUD-001~004 审计操作留痕规则"}
  - {target: "GOV-CMP-003", at: "§2", why: "治理审计执行协议——12 维度审计清单"}
references:
  - {id: "MOD-INF-023", at: "§2", why: "漂移检测审计信号——仅存 references（DAG 无环）"}
  - {id: "MOD-INF-015", at: "§2", why: "遥测发射通道——仅存 references"}
  - {id: "MOD-INF-010", at: "§2", why: "FLE 消费审计事件／Policy 闭环——仅存 references"}
  - {target: "ADR-0010", at: "§4.4", why: "三层治理边界——Policy/Factory/Runtime 三角闭环接口协议"}
  - {target: "MOD-KB-001", at: "§2", why: "Knowledge Base——审计数据输入 KB 的投毒防护 + KB provenance 评分"}
  - {target: "MOD-INF-022", at: "§2", why: "Escalation Engine——异常检测升级路径 + 委托链终端判断"}
---

## DOM-GOV-001 集成契约锚点

> 权威定义见 [`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-001 | 消费方（记录 RBAC 判定事实） | MOD-INF-018 |
| G-CT-002 | 产出方（异常事件触发 Rollback） | MOD-INF-021 |
| G-CT-007 | 消费方（记录 Spec 执行审计） | MOD-INF-019 |

# 审计追踪链蓝图 — 不可变动作审计 + 密码学 Provenance + Agent 级签名 + CoT 推理链 + 漂移检测

> **module_id**: MOD-INF-020 | **version**: 1.1.0 | **status**: draft | **layer**: cross_layer

> **对标**：Goldman SecDB immutable audit log（分布式 replication ring + SecSync 不一致检测）+ ISACA 2025 Agentic AI 审计三要素（agent身份+执行动作+使用工具）+ OWASP ASI-09/10 2026（代理身份管理 + 审计追踪缺失）+ Microsoft AGT Merkle-chain integrity + Agent DID/Ed25519 signing + IATP（Inter-Agent Trust Protocol）+ W3C PROV 三元组（Entity/Activity/Agent）+ NIST 2026 AI Agent Standards（agent identity + 持续重验证 + 跨系统动作重建）+ FCA 监管文件审查格式（数据源+规则+推理+置信度+最终动作）。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-020 |
| 代码落位 | `src/zephyr/audit_trail/` |
| 运行时平面 | Hot memory（每个操作同步写入，延迟 < 5ms P99） |
| 核心职责 | **"法医实验室 + 免疫系统 + 公证处"**：记录"谁在什么时候用什么工具做了什么基于什么决策"，不可变、不可篡改、密码学可验证、Agent 级不可否认、推理链可回溯、异常可检测、漂移可对账 |
| 设计哲学 | **"会计账本 → 法医实验室 → 免疫系统 → 公证处"** 四级跃迁——不只是记录，更要检测异常、驱动规则演进、提供不可否认的证据 |

### 1.2 核心职能（一句话 + 五支柱）

**Audit Trail 是系统的黑匣子 + 免疫系统 + 公证处**——每个 AI 动作都有密码学完整性保证的审计记录。出了问题可以回溯到任意时刻的任意操作，找到根因。异常行为自动检测并告警。蓝图漂移实时对账。闭环反馈驱动规则演进。Agent 级签名保证不可否认性。

| 支柱 | 职责 | 对标 |
|------|------|------|
| **记录（Record）** | 不可变 append-only 审计日志——JSONL 唯一真源 | Goldman SecDB immutable log |
| **验证（Verify）** | 密码学完整性——哈希链 + HMAC 签名 + Merkle 树聚合 | Microsoft AGT Merkle-chain |
| **归因（Attribute）** | Agent 级不可否认性——Ed25519 Agent 签名 + 委托链验证 | Microsoft AGT Ed25519 / IATP |
| **检测（Detect）** | 异常行为签名 + 蓝图漂移检测 + 权限违规告警 + 间接操作 + 供应链风险 | ISACA 2025 / OWASP ASI-10 / NIST 2026 |
| **进化（Evolve）** | 三角闭环反馈——审计数据回写 Policy 驱动规则演进 + 反馈自审计 | Netflix 混沌反馈 / ADR-0010 D2-B |

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 多 IDE 并发（TRAE/Cursor/RooCode） | 审计日志必须跨 IDE 统一——JSONL 是唯一所有 IDE 都能 append 的格式；需要 Lamport 逻辑时钟解决时序；需要跨 IDE 一致性交叉验证 |
| 10+ 并发对话 | 审计量可能很大——需要两层粒度 + 自动摘要，不能全是文件级 |
| 1 人 + AI，99% AI 维护 | 无人监控审计系统健康 → 必须自监控（heartbeat + 自检 + 自动修复）；审计日志读者 99% 是 AI → 查询结果必须是 AI 零推理可消费的结构；需要外部独立验证端点（AI 不能自证清白） |
| 先干后验模式 | 审计日志是后验的基础——没有审计就没有后验；需要 Dry-Run 预审计模式；Dry-Run vs Real 差异检测 |
| 100% AI 施工 | 审计系统自身的代码也是 AI 写的 → 元审计和自监控是刚性需求；审计代码不可用于自证（需要外部 verifier） |

### 1.4 当前痛点

| # | 痛点 | 后果 | 本蓝图如何解决 |
|---|------|------|-------------|
| 1 | 只有 blueprint_reads.jsonl（蓝图读取日志） | AI 改了代码但不知道它读了哪些蓝图、跳过了哪些门禁 | 全量文件级审计（TaskAuditSummary + FileAuditDetail）|
| 2 | session-logs/ 是人工维护 | 不完整、不及时、格式不统一 | 自动化不可变审计替代人工日志 |
| 3 | Provenance 三件套强制要求但无运行时执行 | 大部分操作没有草稿和仲裁——要求形同虚设 | 分级 Provenance（always_allow 轻量 / auto_guard 完整 / blocked 全量）|
| 4 | 审计日志可修改 | SQLite 存储可被 AI 直接 UPDATE——违反不可变原则 | JSONL 为唯一真源 + SQLite 为派生查询索引 |
| 5 | 没有唯一真源 | SQLite 和 JSONL 各写各的——数据可能不一致 | JSONL SSoT + CI 门禁校验一致性 |
| 6 | 无密码学篡改证明 | JSONL 只是 append-only，不是 tamper-evident——AI 可删除某行后重新 append 伪造行 | 哈希链 + HMAC 签名 + 完整性自检 |
| 7 | 无异常行为检测 | 不知道什么是"可疑的 AI 操作"——AI 越权改文件、批量删除、非工作时间操作均无感知 | 行为基线 + 异常签名 + 自动告警 |
| 8 | 无蓝图漂移对账 | 不知道 AI 实际做了什么 vs 蓝图规定该做什么 | Blueprint vs Actual 实时对账 |
| 9 | 无 Agent 级不可否认性 | HMAC 只能证明"来自本系统"，不能证明"是 Agent X 操作的"——Agent B 可伪造 Agent A 的操作记录 | Agent 级 Ed25519 数字签名 + DID |
| 10 | 无 LLM 推理过程回溯 | 只知道 AI 做了什么，不知道它为什么这样做——决策根因分析不可行 | CoT 推理链摘要 + 完整 CoT 哈希引用 |

---

## 2. 核心架构

### 2.1 两层审计粒度（决策 D-020-01）

> **决策 D-020-01**：审计粒度采用两层——任务级摘要（快速浏览）+ 文件级明细（问题定位）。任务级记录是主表，文件级记录是明细表，通过 task_id 关联。
>
> **决策依据**：1人+AI场景，审计日志主要是给 Owner"有空时翻翻"用的，任务级摘要就够了；但出了问题需要定位时，文件级明细不可少。对标 SecDB 的 trade-level + tick-level 两层审计。

```python
class TaskAuditSummary(BaseModel):
    """任务级审计摘要——快速浏览"""
    event_id: str = Field(..., description="格式 AUD-T-{UUID7}-{SEQ}")
    timestamp: datetime = Field(..., description="UTC 毫秒精度")
    agent_id: str = Field(..., description="执行者——引用 AgentIdentity.agent_id")
    ide_source: str = Field(..., description="来源 IDE——trae/cursor/roocode")
    lamport_counter: int = Field(..., description="Lamport 逻辑时钟计数器")
    session_id: str = Field(..., description="会话 ID")
    task_id: str = Field(..., description="任务 ID")
    task_type: str = Field(..., description="任务类型——architect/implementer/governor")
    action_summary: str = Field(..., description="操作摘要——如'实现 MOD-INF-018 scaffold'")
    files_affected: int = Field(..., description="影响文件数")
    result: str = Field(..., description="success/fail/partial/rolled_back")
    permission_level: str = Field(..., description="always_allow/auto_guard/blocked")
    provenance_depth: ProvenanceDepth = Field(..., description="Provenance 深度——由权限级别决定")
    tokens_used: int | None = Field(default=None, description="Token 消耗")
    cost_estimate_usd: float | None = Field(default=None, description="估算费用 USD")
    duration_ms: int | None = Field(default=None, description="操作耗时 ms")

class FileAuditDetail(BaseModel):
    """文件级审计明细——问题定位"""
    event_id: str = Field(..., description="格式 AUD-F-{UUID7}-{SEQ}")
    task_audit_id: str = Field(..., description="关联的任务级审计 ID")
    timestamp: datetime
    lamport_counter: int = Field(..., description="Lamport 逻辑时钟计数器")
    file_path: str = Field(..., description="文件路径")
    action_type: FileActionType = Field(..., description="read/write/create/delete")
    sha256_before: Optional[str] = Field(default=None, description="操作前 SHA-256")
    sha256_after: Optional[str] = Field(default=None, description="操作后 SHA-256")
    diff_size_bytes: int | None = Field(default=None, description="diff 大小 (bytes)")

class FileActionType(str, Enum):
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
```

### 2.2 JSONL 为唯一真源 + 密码学完整性（决策 D-020-02 + D-020-04）

> **决策 D-020-02**：JSONL 文件是审计日志的**唯一真源（SSoT）**，SQLite 是从 JSONL 派生的查询索引。写入流程：AI 操作 → 追加写入 JSONL → 异步重建 SQLite 索引。查询流程：读 SQLite → 如果 SQLite 不可用则回退读 JSONL。

> **决策 D-020-04**（新增）：每条 JSONL 条目自带密码学完整性保证——**哈希链**（`prev_entry_hash` 链接前一条）+ **条目级 HMAC-SHA256 签名**（`hmac_signature`）+ **周期性 Merkle 树根哈希存储**（每小时生成 Merkle root 写入独立 `.merkle` 文件，供快速批量验证）。JSONL 从"append-only"升级为"append-only + tamper-evident"。

```yaml
storage_ssoT:
  primary:
    format: "JSONL"
    path: "data/audit/audit-trail.jsonl"
    write_mode: "append-only——每个操作追加一行"
    rotation: "按日轮转——audit-trail-2026-05-05.jsonl"
    retention: "permanent——ttl=permanent，永不删除（但按 §6 分层存储策略冷归档）"
    git_tracked: false
    git_isolation: "审计 JSONL 独立于 git 工作区存储，不受 git reset/rebase 影响——防止审计日志随代码回滚而丢失；data/audit/ 加入 .gitignore"

  # === 密码学完整性 ===
  cryptographic_integrity:
    hash_chain:
      enabled: true
      algorithm: "SHA-256"
      field: "prev_entry_hash"
      description: "每条条目含前一条的 SHA-256——形成不可逆哈希链，删除中间条目立即可检测"

    hmac_signing:
      enabled: true
      algorithm: "HMAC-SHA256"
      secret_source: "环境变量 ZEPHYR_AUDIT_HMAC_SECRET（256-bit）"
      field: "hmac_signature"
      description: "HMAC-SHA256(entry_without_signature, audit_secret)——伪造来源立即可检测"

    merkle_aggregation:
      enabled: true
      interval: "每小时"
      path: "data/audit/merkle/audit-merkle-{YYYY-MM-DDTHH}.json"
      description: "每小时生成 Merkle 根哈希——O(log n) 批量验证，无需逐条校验"

    integrity_check:
      frequency: "每次查询前自动检验 + 每周全量扫描"
      on_failure: "P0 告警 → integrity_failure 审计事件 → 通知 Owner → 隔离可疑段"

  derived:
    format: "SQLite"
    path: "data/audit/audit-index.db"
    write_mode: "异步重建——从 JSONL 派生，5s 延迟"
    rebuild_trigger: "JSONL 追加后 5s / 手动触发 / CI 启动时 / 索引损坏自动触发"
    purpose: "查询加速——按 agent/target/时间/任务类型/permission_level/anomaly 查询"

  consistency_check:
    ci_gate: "CI 门禁校验 SQLite 记录数 == JSONL 行数 + 哈希链连续性 + HMAC 有效性"
    rebuild_script: "scripts/governance/rebuild_audit_index.py"
    self_healing: "索引损坏 → 自动从 JSONL 重建（零人工干预）"
```

### 2.3 分级 Provenance（决策 D-020-03）

> **决策 D-020-03**：Provenance 深度由权限级别决定——always_allow 只记录轻量 provenance，auto_guard 记录标准 provenance（含决策依据+后验检查），blocked 记录全量 provenance（含阻断原因+违反规则）。版本从 v0.2.0 的 3 级扩展到 v1.0.0 的 3 级不变，但 Light 级补充 `decision_brief`。

```python
class ProvenanceDepth(str, Enum):
    LIGHT = "light"        # always_allow 操作
    STANDARD = "standard"  # auto_guard 操作
    FULL = "full"          # blocked 操作（阻断记录）

class ProvenanceLight(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    decision_brief: str = Field(default="", description="一句话决策依据——如'按 MOD-INF-018 §2.2'")

class ProvenanceStandard(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    decision_basis: list[str] = Field(default_factory=list, description="决策依据——读了哪些蓝图/ADR/门禁结果")
    guard_checks_executed: list[str] = Field(default_factory=list, description="执行的后验检查项")
    guard_checks_passed: list[str] = Field(default_factory=list)
    guard_checks_failed: list[str] = Field(default_factory=list)
    guard_result: Optional[str] = Field(default=None, description="后验结果——pass/fail/rolled_back")
    confidence_level: str = Field(default="high", description="AI 决策置信度——high/medium/low")

class ProvenanceFull(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    blocked_reason: str = Field(..., description="阻断原因")
    attempted_action: str = Field(..., description="尝试的操作")
    rule_violated: str = Field(..., description="违反的规则ID")
    escalation_triggered: bool = Field(default=False, description="是否触发了升级/委托")
    escalation_target: Optional[str] = Field(default=None, description="升级目标——human_owner/supervisor_agent")
```

### 2.4 密码学完整性数据模型（新增 SSoT 条目体）

```python
class AuditEntryV1(BaseModel):
    """审计条目 v1.1.0——密码学完整性 + Agent 签名 + CoT 推理链 + 时序一致性 + 成本归属 + 漂移检测"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    # === 身份与版本 ===
    entry_id: str = Field(..., description="UUID7——时间有序，毫秒精度")
    schema_version: str = Field(default="1.1.0")
    entry_type: AuditEventType = Field(..., description="事件类型（见 §3）")

    # === 密码学完整性（决策 D-020-04）===
    prev_entry_hash: str = Field(..., description="前一条目的 SHA-256（首条 = genesis）")
    entry_hash: str = Field(..., description="SHA-256(本条目不含 entry_hash+hmac_signature+agent_signature 的规范 JSON)")
    hmac_signature: str = Field(..., description="HMAC-SHA256(canonical_json, ZEPHYR_AUDIT_HMAC_SECRET)——系统级完整性")

    # === Agent 级不可否认性（决策 D-020-14）===
    agent_did: str | None = Field(default=None, description="Agent DID——did:zephyr:{ed25519_fingerprint}")
    agent_signature: str | None = Field(default=None, description="Ed25519 签名(entry_hash)——Agent 级不可否认")
    agent_public_key_pem: str | None = Field(default=None, description="Agent Ed25519 公钥 PEM——供离线验证")

    # === 委托链（决策 D-020-16）===
    delegation_chain: list[str] = Field(default_factory=list, description="委托链——[root_agent_did, ..., executor_agent_did]")
    delegation_depth: int = Field(default=0, description="委托深度——0=直接操作")

    # === Merkle ===
    merkle_batch_id: str | None = Field(default=None, description="所属 Merkle 批次 ID")

    # === 时序一致性（决策 D-020-09）===
    lamport_clock: tuple[str, int] = Field(..., description="(ide_source, counter)——Lamport 逻辑时钟")
    utc_timestamp: datetime = Field(..., description="UTC 毫秒精度——用于人类阅读，非排序依据")

    # === 操作上下文 ===
    agent_id: str
    ide_source: str
    session_id: str
    task_id: str
    task_type: str | None = None
    permission_level: str
    provenance_depth: str

    # === 渐进信任（决策 D-020-17）===
    trust_score: float | None = Field(default=None, description="操作时的 Agent 信任分数——0.0~1.0，连续值，随时间衰减")

    # === 操作内容 ===
    action_type: str
    file_path: str | None = None
    sha256_before: str | None = None
    sha256_after: str | None = None

    # === 间接操作（决策 D-020-21）===
    indirect_operation: bool = False
    indirect_method: str | None = None  # symlink / hardlink / generated_script / cron / mcp_delegation
    indirect_target: str | None = None   # 最终受影响的目标

    # === 决策溯源 —— Provenance Standard+ ===
    decision_basis: list[str] = Field(default_factory=list)
    guard_checks_passed: list[str] = Field(default_factory=list)
    guard_checks_failed: list[str] = Field(default_factory=list)
    confidence_level: str = "high"

    # === LLM 推理链（决策 D-020-15）===
    reasoning_trace: str | None = Field(default=None, description="CoT 推理链摘要——<500 chars")
    cot_hash: str | None = Field(default=None, description="SHA-256(完整 CoT 原始文本)——存于外部 reasoning/ 目录")

    # === 蓝图漂移（决策 D-020-06）===
    blueprint_expected_action: str | None = None
    drift_detected: bool = False
    drift_severity: str | None = None  # low/medium/high/critical
    drift_detail: str | None = None

    # === 异常标记（决策 D-020-07）===
    anomaly_detected: bool = False
    anomaly_type: str | None = None
    anomaly_score: float | None = None  # 0.0~1.0

    # === 成本归属 ===
    tokens_used: int | None = None
    cost_estimate_usd: float | None = None
    duration_ms: int | None = None

    # === Dry-Run vs Real 差异（决策 D-020-22）===
    dry_run: bool = False
    dry_run_real_diff: str | None = None  # "AI 在 dry-run 时期望做 X，实际做了 Y"——差异描述
    dry_run_real_diff_score: float | None = None  # 0.0~1.0 差异度

    # === 外部调用链（决策 D-020-20）===
    parent_entry_id: str | None = None  # 父审计条目 ID——外部调用链关联
    external_tool_calls: list[dict] = Field(default_factory=list, description="外部 MCP/API 调用链")

    # === 供应链（决策 D-020-23）===
    supply_chain_info: dict | None = Field(default=None, description="包名+版本+SHA-256+来源——供供应链审计")

    # === 隐私治理 ===
    contains_pii: bool = False
    redaction_policy: str = "none"  # none / masked / hashed
    retention_tier: str = "hot"     # hot / warm / cold
```

### 2.5 逻辑时钟——多 IDE 时序一致性（决策 D-020-09）

> **决策 D-020-09**（新增）：多 IDE 并发场景下，每个 IDE 维护独立 Lamport 逻辑时钟 `(ide_source: str, counter: int)`。写入 JSONL 时递增 counter；读取排序时以 `(max(local, received) + 1)` 规则合并。不对操作系统时钟做任何假设——`utc_timestamp` 仅用于人类阅读。

> **短术语**：`(trae, 42)` < `(cursor, 15)` 无法直接比较大小——Lamport 只保证因果顺序（happens-before），不保证全序。全序由 `(counter, ide_source)` 字典序打破——对标 Dynamo Vector Clock 简化版。

```python
class LamportClock:
    """单 IDE 逻辑时钟——Happens-Before 关系追踪"""
    def __init__(self, ide_source: str) -> None:
        self._ide = ide_source
        self._counter = 0

    def tick(self) -> tuple[str, int]:
        """操作前递增——返回当前时钟"""
        self._counter += 1
        return (self._ide, self._counter)

    def merge(self, received: tuple[str, int]) -> None:
        """接收外部事件时合并——Lamport merge 规则"""
        self._counter = max(self._counter, received[1]) + 1

    def now(self) -> tuple[str, int]:
        """返回当前时钟（不递增）"""
        return (self._ide, self._counter)

def audit_entry_sort_key(entry: AuditEntryV1) -> tuple[int, str]:
    """审计条目全序排序键：(counter, ide_source) 字典序"""
    return (entry.lamport_clock[1], entry.lamport_clock[0])
```

### 2.6 三层存储架构（决策 D-020-10）

> **决策 D-020-10**（新增）：审计日志按时间分三层存储——热（≤7d JSONL 本地 SSD，<5ms 读写）、温（8~90d gzip JSONL 本地 HDD，<100ms）、冷（>90d Parquet 归档压缩，日级查询）。自动执行分层迁移，保留期到期自动清理（按 GOV-CMP-002 AUD-001~004 规定）。

```yaml
storage_tiers:
  hot:
    format: "JSONL"
    path: "data/audit/hot/"
    age: "≤ 7 天"
    storage: "本地 SSD"
    latency: "< 5ms P99 write"
    compression: "none"

  warm:
    format: "gzip JSONL"
    path: "data/audit/warm/"
    age: "8 ~ 90 天"
    storage: "本地 HDD"
    latency: "< 100ms query"
    compression: "gzip level 6"
    migration: "日均 cron——每日 00:00 UTC 扫描 hot/ → >7d 条目迁移至 warm/"

  cold:
    format: "Parquet"
    path: "data/audit/cold/"
    age: "> 90 天"
    storage: "本地 HDD 或对象存储"
    latency: "日级查询（batch scan）"
    compression: "Parquet snappy + zstd"
    migration: "周均 cron——每周日 02:00 UTC 扫描 warm/ → >90d 条目迁移至 cold/"

retention_enforcement:
  schedule: "monthly"
  script: "scripts/governance/enforce_audit_retention.py"
  policy_ref: "GOV-CMP-002 AUD-001~004"
  safe_mode: "dry-run 先行——实际删除前生成报告供 Owner 审批"
```

### 2.7 自监控——1人+AI 维护的刚需

审计系统无人运维 → 必须自监控。对标 Goldman SecDB Prometheus probing + PagerDuty escalation。

```yaml
self_monitoring:
  heartbeat:
    interval: "60s"
    check: "写入 1 条 heartbeat 条目 → 读回验证哈希链 → 延迟 < 5ms"
    on_failure: "连续 3 次失败 → P0 audit_system_down 告警 → 写入 emergency fallback log"

  health_metrics:
    - name: "write_latency_p99_ms"
      threshold: "5 ms"
      alert: "> 10 ms P99 → P1"
    - name: "disk_usage_pct"
      threshold: "80%"
      alert: "> 80% → P1，> 90% → P0"
    - name: "jsonl_file_count"
      threshold: "每 IDE ≤ 365 文件"
      alert: "超过 → P2"
    - name: "hash_chain_integrity"
      threshold: "100% pass"
      alert: "任一 fail → 立即 P0 阻断"
    - name: "hmac_validity_rate"
      threshold: "100% pass"
      alert: "任一 fail → 立即 P0 阻断"
    - name: "sqlite_index_health"
      threshold: "online"
      alert: "offline > 60s → P1 + auto-rebuild"
    - name: "agent_signature_validity_rate"
      threshold: "100% pass"
      alert: "任一 fail → 立即 P0 阻断"
    - name: "delegation_chain_validity"
      threshold: "100% pass"
      alert: "链断裂或权限放大 → P0"
    - name: "trust_score_trend"
      threshold: "下降 > 0.3 / 7d"
      alert: "P1——Agent 行为趋势恶化"
    - name: "cross_ide_consistency"
      threshold: "100% pass"
      alert: "不一致 > 0 → P1"

### 2.8 Agent 级数字签名——不可否认性（决策 D-020-14）

> **决策 D-020-14**（新增）：HMAC 只能证明"数据来自知道 secret 的系统"，不能证明"具体是哪个 Agent 操作的"。引入 Agent 级 Ed25519 数字签名实现不可否认性（non-repudiation）。每个 Agent 拥有独立的 Ed25519 密钥对，操作时用私钥对 `entry_hash` 签名，审计条目携带 `agent_signature` + `agent_did` + 公钥 PEM。任何第三方可以离线验证签名，不需要知道 HMAC secret。

```yaml
agent_signing:
  algorithm: "Ed25519"
  key_generation:
    trigger: "Agent 身份创建时（MOD-INF-018 AgentIdentity 初始化）"
    storage: "Agent 私钥存储在密钥库（非审计系统），公钥写入 AgentIdentity 元数据"
    rotation: "每 90 天或 Agent 权限升级时重新生成"

  signing:
    description: "Agent 私钥签名(entry_hash) → agent_signature 写入审计条目"
    verification: "公钥验证(entry_hash, agent_signature)——任何第三方可离线验证"

  did:
    format: "did:zephyr:{sha256(Ed25519_public_key)[:16]}"
    example: "did:zephyr:a1b2c3d4e5f6g7h8"
    binding: "DID 绑定到 Ed25519 公钥——不可伪造"

  non_repudiation_chain:
    description: "HMAC（系统级）证明'来自本系统' + Ed25519（Agent 级）证明'来自 Agent X' —— 双重保障"
    hmac_only: "完整性 + 来源验证（弱——不区分 Agent）"
    ed25519: "完整性 + 来源验证 + 不可否认性（强——区分 Agent，法庭可采信）"
```

```python
class AgentSigner:
    """Agent 级 Ed25519 签名器"""

    def __init__(self, agent_did: str, private_key_pem: str) -> None:
        self._did = agent_did
        self._private_key = Ed25519PrivateKey.from_pem(private_key_pem)
        self._public_key_pem = self._private_key.public_key().to_pem()

    def sign(self, entry_hash: str) -> str:
        """对 entry_hash 签名——返回 base64 签名"""
        return base64.b64encode(self._private_key.sign(entry_hash.encode())).decode()

    @staticmethod
    def verify(entry_hash: str, signature: str, public_key_pem: str) -> bool:
        """离线验证签名——无需任何 secret"""
        key = Ed25519PublicKey.from_pem(public_key_pem)
        try:
            key.verify(base64.b64decode(signature), entry_hash.encode())
            return True
        except Exception:
            return False

class DIDRegistry:
    """DID → 公钥映射注册表"""
    def register(self, did: str, public_key_pem: str, agent_metadata: dict) -> None: ...
    def resolve(self, did: str) -> str | None: ...  # 返回公钥 PEM
    def revoke(self, did: str, reason: str) -> None: ...
```

### 2.9 LLM 推理链（CoT）审计（决策 D-020-15）

> **决策 D-020-15**（新增）：对标 OWASP ASI-10 "完整可观测性" + FCA 监管文件审查 "推理"维度。每条审计条目记录 LLM 推理链摘要（`reasoning_trace` <500 chars）+ 完整 CoT 的 SHA-256 引用（`cot_hash`）。完整 CoT 文本存储在 `reasoning/` 目录（独立于审计日志，按 session 组织）。Phase scaffold 记录摘要，Phase experimental 起记录完整 CoT。

```yaml
cot_audit:
  summary_level:
    field: "reasoning_trace"
    max_length: 500  # chars
    format: "Markdown 摘要——关键推理步骤 + 最终决策"

  full_trace:
    field: "cot_hash"
    storage_path: "data/reasoning/{session_id}/{entry_id}.cot.json"
    format: "JSON —— [{'step': 1, 'thought': '...', 'action': '...', 'observation': '...'}, ...]"
    retention: "随审计日志分层存储——hot 7d / warm 90d / cold archive"

  retrieval:
    description: "通过 cot_hash 查找完整 CoT —— SHA-256(完整 CoT 文件) == cot_hash → 可信"
    query: "AuditQuery.by_task(task_id) → 获取 cot_hash → reasoning_store.fetch(cot_hash)"
```

### 2.10 委托链审计（决策 D-020-16）

> **决策 D-020-16**（新增）：对标 Microsoft AGT DelegationChain + NIST 2026 "委托身份追踪"。Agent A 委托 Agent B 执行操作时，审计条目记录完整委托链 `[root_agent_did, ..., executor_agent_did]` + `delegation_depth`。委托链约束：(a) 子 Agent 权限必须是父 Agent 权限的子集（capability narrowing），(b) 委托深度上限为 3（configurable），(c) 委托链断裂立即 P0 告警。

```python
class DelegationChainAuditor:
    """委托链完整性审计器"""

    def validate_chain(self, entry: AuditEntryV1) -> bool:
        """校验委托链：深度 ≤ 3 + 权限逐级缩小 + 链内 DID 均有效"""

    def detect_chain_break(self, entry: AuditEntryV1) -> bool:
        """检测委托链断裂——中间 DID 不可解析或权限异常放大"""

    def trace_root(self, entry: AuditEntryV1) -> str:
        """追溯到委托链根 Agent——用于最终责任归属"""
```

### 2.11 渐进信任分数（决策 D-020-17）

> **决策 D-020-17**（新增）：对标 ISACA "trust degrades without continued good behavior" + Microsoft AGT Trust Scoring。信任从离散 RBAC 角色扩展为连续浮点数 `trust_score: 0.0~1.0`。每个操作记录操作时的 trust_score。信任规则：(a) 每次成功操作 +0.001（缓慢上升），(b) 每次 anomaly -0.2（快速下降），(c) 每天无活动 -0.005（自然衰减），(d) trust_score < 0.5 → 自动降级权限级别。

```python
class TrustScoreEngine:
    DEFAULT_SCORE: float = 0.6
    SUCCESS_INCREMENT: float = 0.001
    ANOMALY_DECREMENT: float = 0.2
    DAILY_DECAY: float = 0.005
    DEMOTION_THRESHOLD: float = 0.5

    def update(self, agent_did: str, event: AuditEventType, anomaly_score: float | None) -> float: ...
    def current(self, agent_did: str) -> float: ...
    def trend(self, agent_did: str, days: int = 7) -> list[float]: ...
```

### 2.12 外部独立验证端点（决策 D-020-18）

> **决策 D-020-18**（新增）：100% AI 施工语境下的刚性需求——"AI 不能自己写测试验证自己写的代码"。引入 `ExternalAuditVerifier`，独立于 `audit_trail/` 模块。CI/CD 中使用外部 verifier 而非内部 `verify_integrity()`。外部 verifier 仅做审计完整性校验，不依赖 audit_trail 模块的任何代码。

```yaml
external_verifier:
  script: "scripts/governance/verify_audit_integrity.py"
  independence: "零依赖 audit_trail/ 模块——仅使用 stdlib hashlib + hmac + json"
  checks:
    - "哈希链连续性（从 genesis 遍历到末尾）"
    - "HMAC 签名全量验证（使用 ZEPHYR_AUDIT_HMAC_SECRET）"
    - "Agent Ed25519 签名抽样验证（10% 随机抽样）"
    - "Merkle 根哈希重建对比"
    - "JSONL 行数 vs SQLite 索引记录数一致性"
    - "委托链完整性（深度 + 权限缩小）"
  ci_integration:
    trigger: "pre-commit / CI 门禁 / 定时 cron"
    on_failure: "CI ❌ → 阻止合并 → 通知 Owner"
```

### 2.13 跨 IDE 一致性交叉验证（决策 D-020-19）

> **决策 D-020-19**（新增）：对标 Goldman SecSync 不一致检测。多 IDE 并发场景下，两个 IDE 可能对同一操作记录了相互矛盾的信息（TRAE 记录"成功"，Cursor 记录"失败"）。新增 `CrossIDEConsistencyChecker`：定期扫描所有 IDE 的 JSONL，通过 `(task_id, action_type, file_path, lamport_clock 时间窗口)` 匹配同一操作，检测内容矛盾并标记。

```python
class CrossIDEConsistencyChecker:
    """跨 IDE 审计一致性验证器——对标 Goldman SecSync"""

    def find_conflicts(self, window: timedelta = timedelta(seconds=10)) -> list[ConsistencyConflict]:
        """扫描所有 IDE JSONL，检测同一操作的多版本矛盾"""

    def merge_consensus(self, task_id: str) -> ConsensusView:
        """合并多 IDE 对同一操作的视角——多数一致 → 可信"""

class ConsistencyConflict(BaseModel):
    entry_a_id: str
    entry_b_id: str
    field: str  # 冲突字段名
    value_a: str
    value_b: str
    ide_a: str
    ide_b: str
    severity: str  # low/high/critical
```

### 2.14 确定性重放——审计日志→系统状态重建（决策 D-020-34）

> **决策 D-020-34**（新增）：对标 Goldman trade reconstruction——审计日志的最高价值是支持"回到任意时刻，精确重建系统状态"。仅记录"谁做了什么"不够——必须记录操作前后的完整状态快照。关键文件操作记录 `sha256_before` → `sha256_after`，通过重放审计日志可验证重建状态的 SHA-256 是否与记录一致。

```yaml
deterministic_replay:
  design:
    principle: "sha256_before + sha256_after → 任何时间点状态可重建"
    coverage: "关键文件操作 100% 记录 sha256_before/after"

  replay_layers:
    L1_file_state: "通过 sha256_after 链→重建任意时刻文件内容哈希"
    L2_git_state: "通过 git commit SHA→重建代码仓库状态"
    L3_system_config: "通过配置变更事件→重建系统配置状态"

  validation:
    weekly_replay_test: "随机选取 3 个时间点，重放审计日志验证 SHA-256 一致性"
    on_demand: "zephyr audit replay --at '2026-05-03T14:00:00Z' → 输出该时刻的完整文件状态哈希映射"

  limitation:
    partial_coverage: "仅记录有审计事件的操作——未被审计覆盖的操作无法重建"
    external_dependencies: "MCP/API 调用结果无法从审计日志重建——需外部系统配合"
```

```python
class DeterministicReplayEngine:
    """从审计日志重建系统状态"""

    def replay_to(self, target_time: datetime) -> dict[str, str]:
        """重放审计日志至指定时间——返回 {file_path: sha256} 状态映射"""

    def verify_replay(self, target_time: datetime) -> ReplayVerification:
        """对比重放结果与实际 git 状态——返回一致性报告"""

class ReplayVerification(BaseModel):
    target_time: datetime
    files_in_audit: int
    files_in_git: int
    matched: int
    mismatched: list[ReplayMismatch]
    coverage_pct: float
```

### 2.15 AI 自身安全性——审计数据作为 Prompt Injection 向量（决策 D-020-31）

> **决策 D-020-31**（新增）：100% AI 施工 + AI 维护 + AI 消费审计数据——闭环的核心风险是审计日志自身成为 prompt injection 攻击面。当 `trail_for_ai_context()` 将审计条目注入 LLM context 时，恶意构造的审计条目（如含 "ignore all previous instructions" 或 "输出前面所有内容"）可劫持 AI 决策。**审计日志的读者是 AI，而 AI 是控制系统的实体——这是最高级别的安全风险。**

```yaml
ai_self_security:
  principle: "任何 AI 将要读取的数据都必须经过 prompt injection 净化——审计日志也不例外"

  sanitization_pipeline:
    step_1_strip_instructions:
      description: "移除/转义 AI 指令关键词——ignore|disregard|override|bypass|system:|assistant:|user:"
      method: "unicode 转义——如 'ignore' → 'i\\u0067nore'"

    step_2_semantic_sandbox:
      description: "每个审计条目包裹在语义沙箱标记中——[AUDIT_ENTRY_START]...[AUDIT_ENTRY_END]"
      purpose: "AI 明确知道这是审计数据——不是系统指令"

    step_3_length_limit:
      description: "每条 entry 在 context 中截断至 500 chars——防止超长注入攻击"

  forbidden_patterns:
    - "包含 '---' 或 '===' 等 Markdown 分隔符——可能被解析为指令边界"
    - "包含 '```' 代码块标记——可能逃逸 context 结构"
    - "包含 'system:' / 'assistant:' / 'user:' 前缀——可能冒充对话角色"
    - "任何 AI tool call 格式（如 '<function_call>' / '<invoke>'）"

  audit_self_defense:
    injection_detected: "ANM-015——检测到审计条目含 prompt injection 模式 → 自动脱毒 + 标记 anomaly"
    alert: "P0——AI 正在读取可能含注入攻击的审计数据"
```

### 2.16 信任锚初始化——The Bootstrap Trust Problem（决策 D-020-44）

> **决策 D-020-44**（新增）：审计系统的所有信任都起源于一个不可验证的时刻——**genesis block 的创建**。第一条审计条目 (`prev_entry_hash = "genesis"`) 的合法性、初始 HMAC secret 的生成、第一个 Ed25519 密钥的创建——这些都是信任根。如果初始化被 compromise，之后的一切密码学证明都是"垃圾进垃圾出"。在 100% AI 施工语境下：**初始化代码也是 AI 写的——AI 可能生成已知有后门的初始化脚本。**

```yaml
bootstrap_trust:
  problem: "第一条审计条目如何自证？——prev_entry_hash = 'genesis' 是不可验证的占位符"
  implication: "genesis 之前的状态永远不可知——接受这是已知盲点，显式声明而非隐藏"

  initialization_ceremony:
    description: "审计系统首次启动时执行的可审计初始化流程"

    steps:
      step_1_secret_gen:
        action: "从 /dev/urandom 或操作系统 CSPRNG 读取 256-bit → HMAC secret"
        verification: "SHA-256(secret) 写入 genesis_manifest.txt——可事后验证但不可逆"

      step_2_genesis_entry:
        action: "写入第一条审计条目 AUDIT_SYSTEM_BOOTSTRAP——prev_entry_hash='genesis', entry_hash=SHA256(entry), hmac=HMAC(entry, secret)"
        verification: "外部 verifier 检查 genesis entry 的 entry_hash 自我一致性"

      step_3_agent_key_gen:
        action: "生成 Owner Agent 的 Ed25519 密钥对——DID 注册 + 公钥入 genesis 条目"
        verification: "Owner 离线验证公钥指纹"

      step_4_witness:
        action: "将 genesis_manifest.txt (含 genesis entry_hash + Ed25519 公钥 SHA) 写入外部独立介质——USB / 纸质 QR / 云存储"
        purpose: "独立见证——不是系统自我声明，而是有外部独立见证的起源"

  self_referential_paradox:
    description: "AI 写的初始化代码验证 AI 写的审计系统——Münchhausen trilemma"
    mitigation:
      - "初始化脚本最小化——<200行 Python，任何具备基础编程能力的人可审计"
      - "外部 verifier 独立初始化——不使用 audit_trail/ 模块的任何代码"
      - "初始化见证写入外部介质——不依赖审计系统自身存储"
      - "规则：genesis 创建者 ≠ 日常操作者（由 Owner 手动执行初始化，AI 辅助）"
```
```

---

## 3. 审计事件类型全模型

### 3.1 事件类型枚举

```python
class AuditEventType(str, Enum):
    # === 操作记录 ===
    TASK_SUMMARY = "task_summary"           # 任务级摘要
    FILE_DETAIL = "file_detail"             # 文件级明细

    # === AI 行为异常（对标 ISACA 2025 + OWASP ASI-09/10）===
    ANOMALY_DETECTED = "anomaly_detected"           # 行为基线偏离
    PERMISSION_VIOLATION = "permission_violation"   # 越权操作
    BULK_OPERATION = "bulk_operation"               # 批量操作（>N 文件/秒）
    GATE_BYPASS = "gate_bypass"                     # 门禁跳过（检测到的）
    OFF_HOURS_ACTIVITY = "off_hours_activity"       # 非工作时间大量操作

    # === 蓝图漂移（决策 D-020-06）===
    DRIFT_DETECTED = "drift_detected"               # 蓝图 vs 实际不一致

    # === 系统治理（决策 D-020-05 元审计）===
    INDEX_REBUILD = "index_rebuild"                 # 索引重建
    LOG_ROTATION = "log_rotation"                   # 日志轮转
    TIER_MIGRATION = "tier_migration"               # 存储分层迁移
    INTEGRITY_CHECK = "integrity_check"             # 完整性校验
    INTEGRITY_FAILURE = "integrity_failure"         # 完整性失败（P0）
    AUDIT_QUERY = "audit_query"                     # 元审计：谁查询了审计日志
    AUDIT_SYSTEM_HEALTH = "audit_system_health"     # 自监控 heartbeat

    # === 集成事件 ===
    POLICY_FEEDBACK_SENT = "policy_feedback_sent"   # 三角闭环：反馈已发送
    DRY_RUN_AUDIT = "dry_run_audit"                 # Dry-Run 预审计
    COLD_START_BOOTSTRAP = "cold_start_bootstrap"   # Cold Start 历史回溯

    # === 新增 v1.1.0 ===
    # Agent 身份与信任
    AGENT_IMPERSONATION = "agent_impersonation"         # Agent 冒充检测（B16）
    DELEGATION_CHAIN_ISSUE = "delegation_chain_issue"   # 委托链异常（B24）
    TRUST_SCORE_CHANGE = "trust_score_change"           # 信任分数大幅变化

    # 外部与间接操作
    EXTERNAL_TOOL_CALL = "external_tool_call"           # 外部 MCP/API 调用（B26）
    INDIRECT_OPERATION = "indirect_operation"           # 间接操作检测（B25）
    SUPPLY_CHAIN_INSTALL = "supply_chain_install"       # 包安装操作（B35）

    # 高级检测
    LATENT_RISK_DETECTED = "latent_risk_detected"       # 延时风险/时间炸弹（B33）
    COLLUSION_PATTERN = "collusion_pattern"             # 多 Agent 协同规避检测（B27）
    DRY_RUN_MISMATCH = "dry_run_mismatch"               # Dry-Run vs Real 差异异常（B11）
    KB_POISONING_ATTEMPT = "kb_poisoning_attempt"       # Knowledge Base 投毒尝试（B37）
    FEEDBACK_LOOP_SELF_REINFORCING = "feedback_loop_self_reinforcing"  # 反馈自指循环检测（B34）
    VOLUME_DOS = "volume_dos"                           # 海量小操作 DoS（B38）

    # 跨 IDE
    CROSS_IDE_CONFLICT = "cross_ide_conflict"           # 跨 IDE 审计记录矛盾（B18）
```

### 3.2 文件组成

| 文件 | 职责 |
|------|------|
| `models.py` | 全量 Pydantic V2 模型——`AuditEntryV1` + `TaskAuditSummary` + `FileAuditDetail` + 分级 Provenance + 事件类型枚举 + DID 模型 |
| `writer.py` | 不可变写入器——JSONL append + 哈希链生成 + HMAC 签名 + Ed25519 Agent 签名 + Lamport 时钟递增 + 异步 SQLite 索引重建 |
| `query.py` | 审计查询接口——SQLite 优先 + JSONL 回退 + 查询前完整性快速校验 + 元审计记录 + `trail_for_ai_context()` |
| `integrity.py` | 密码学完整性验证器——哈希链连续性 / HMAC 批量验证 / Ed25519 签名验证 / Merkle 树重建校验 |
| `anomaly.py` | 异常检测引擎——行为基线模型 + 异常签名匹配（13 种）+ 告警发射 + 协同规避检测 |
| `drift.py` | 蓝图漂移对账——`blueprint_expected_action` vs 实际记录的 diff 生成 |
| `lifecycle.py` | 数据生命周期——三层存储迁移 + 隐私脱敏 + 保留期执行 + CoT 文件生命周期 |
| `self_monitor.py` | 自监控——heartbeat 写入/验证 + 健康指标采集 + 自动修复触发器 + 信任分数趋势 |
| `agent_signer.py` | Agent 级 Ed25519 签名器——密钥管理 + 签名/验证 + DID 注册表（Phase scaffold） |
| `delegation.py` | 委托链审计器——链验证 + 深度控制 + 权限缩小校验（Phase experimental） |
| `trust_score.py` | 渐进信任引擎——分数计算 + 衰减 + 趋势分析 + 自动降级触发（Phase experimental） |
| `supply_chain.py` | 供应链审计——包安装检测 + 来源验证 + SHA-256 对比（Phase beta） |
| `cross_ide.py` | 跨 IDE 一致性——冲突检测 + 共识合并 + 矛盾告警（Phase experimental） |
| `evidence_pack.py` | 监管证据包导出——一键生成完整证据链 + 合规框架映射（Phase beta） |
| `cli.py` | CLI 审计面板——`zephyr audit query/trail/integrity/health/evidence` |
| `rebuild_index.py` | 索引重建脚本——JSONL → SQLite + 完整性校验（scripts/governance/）|
| `verify_audit_integrity.py` | 外部独立验证脚本——零依赖 audit_trail/，CI 门禁用（scripts/governance/） |

---

## 4. 审计查询接口与元审计

### 4.1 查询接口

```python
class AuditQuery:
    def by_task(self, task_id: str) -> TaskAuditSummary:
        """查询任务级摘要——快速浏览"""

    def by_task_details(self, task_id: str) -> list[FileAuditDetail]:
        """查询任务关联的文件级明细——问题定位"""

    def by_agent(self, agent_id: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]:
        """查询某个 Agent 在某时段的所有操作"""

    def by_target(self, file_path: str) -> list[FileAuditDetail]:
        """查询某个文件被谁操作过——完整 lineage"""

    def by_permission_level(self, level: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]:
        """查询某个权限级别的所有操作"""

    def by_anomaly(self, anomaly_type: str | None = None, min_score: float = 0.7) -> list[AuditEntryV1]:
        """查询异常事件——按类型/最小分数过滤"""

    def by_drift(self, severity: str | None = None) -> list[AuditEntryV1]:
        """查询蓝图漂移事件——按严重度过滤"""

    def by_cost(self, min_cost_usd: float = 0.0, time_range: tuple[datetime, datetime] | None = None) -> list[AuditEntryV1]:
        """按成本查询——FinOps 审计"""

    def trail_for_ai_context(self, session_id: str) -> str:
        """为 AI agent 生成当前 session 的审计摘要——Markdown 格式，AI 零推理可消费"""

    def rebuild_index(self) -> int:
        """从 JSONL 重建 SQLite 索引——返回重建记录数"""

    def verify_integrity(self, fast_mode: bool = True) -> IntegrityReport:
        """校验密码学完整性——fast_mode 仅校验 Merkle root，否则逐条校验"""

class IntegrityReport(BaseModel):
    is_valid: bool
    total_entries: int
    hash_chain_breaks: list[int]  # 断裂处的 JSONL 行号
    hmac_failures: list[int]
    merkle_mismatches: list[str]  # Merkle 批次 ID
    checked_at: datetime
```

### 4.2 元审计——审计系统自身的治理

```python
class MetaAuditLogger:
    """记录审计系统自身的操作——对标 GOV-CMP-002 AUD-001"""

    def log_audit_query(self, querier: str, query_params: AuditQuery) -> None:
        """记录谁执行了什么查询"""

    def log_index_rebuild(self, trigger: str, entries_count: int) -> None:
        """记录索引重建——谁触发的、重建了多少条"""

    def log_integrity_check(self, result: IntegrityReport) -> None:
        """记录完整性校验——检查结果"""

    def log_retention_enforcement(self, deleted_entries: int, dry_run: bool) -> None:
        """记录保留期执行——删除条目数 + 是否为 dry-run"""

### 4.3 监管证据包导出（决策 D-020-24）

> **决策 D-020-24**（新增）：对标 FCA 监管文件审查格式 + SEC 17a-4 审计要求。输入 task_id → 一键生成完整 PDF/JSON 证据包。证据包含：操作链时间线 + 决策依据（读过的蓝图/ADR）+ 门禁结果 + CoT 推理摘要 + Agent 身份链 + HMAC + Ed25519 签名 + Merkle 证明。律师/监管可离线验证。

```python
class EvidencePackExporter:
    """监管证据包导出器"""

    def export_json(self, task_id: str) -> EvidencePack:
        """导出完整 JSON 证据包——机器可读 + 可编程验证"""

    def export_pdf(self, task_id: str) -> bytes:
        """导出 PDF 证据包——人类可读 + 律师友好"""

    def export_for_regulator(self, task_id: str) -> bytes:
        """FCA 格式——数据源+规则+推理+置信度+最终动作"""

class EvidencePack(BaseModel):
    task_id: str
    generated_at: datetime
    timeline: list[TimelineEntry]  # 完整操作时间线
    decision_dossier: DecisionDossier  # 决策档案——FCA 五维
    cryptographic_proofs: CryptoProofs  # 密码学证明
    agent_identity_chain: list[AgentIdentityProof]  # 身份链
    blueprint_references: list[str]  # 引用的蓝图
    signatures: list[str]  # 所有签名

class CryptoProofs(BaseModel):
    hmac_verified: bool
    hash_chain_intact: bool
    ed25519_signatures_verified: list[bool]
    merkle_proof: str | None = None
```

### 4.4 合规框架条款映射（决策 D-020-25）

> **决策 D-020-25**（新增）：对标 Microsoft Agent Compliance 自动合规验证。建立合规框架→具体条款→ZephyrAlpha 实现的映射表。CI 自动校验覆盖度。

```yaml
compliance_map:
  gdpr:
    art_30: "数据处理活动记录 → audit_trail 全量操作日志"
    art_5_1_f: "数据完整性与保密性 → 哈希链 + HMAC + Ed25519 三重保障"
    art_17: "删除权 → 隐私脱敏策略（hash/mask）+ 保留期执行"

  hipaa:
    sec_164_312_b: "审计控制 → task_summary + file_detail 两层审计"
    sec_164_312_c_2: "传输完整性 → HMAC + Ed25519 双重签名"
    sec_164_312_e_1: "传输加密 → JSONL 不出本地 IDE 网络边界"

  eu_ai_act:
    art_12: "记录保存 → retain_period: permanent + 三层存储"
    art_14: "人工监督 → human_gated escalation + Gate Engine 联动"

  nist_ai_rmf:
    map_1_4: "AI 组件唯一标识 → Agent DID + Ed25519 公钥绑定"
    measure_2_6: "持续监测 → self_monitoring + anomaly detection"
    manage_3_2: "事件响应 → kill_switch + rollback audit + external verifier"
```
```

---

## 5. 异常检测与三角闭环反馈

### 5.1 AI 行为异常签名（决策 D-020-07）

> **决策 D-020-07**（更新 v1.1.0）：定义 AI 行为异常签名——从 v1.0.0 的 7 种扩展到 13 种。检测到异常时写入 `anomaly_detected` 事件 + 计算 anomaly_score + 按 score 触发告警（>0.7 P1 / >0.9 P0）。

| 签名 ID | 异常模式 | 检测逻辑 | 严重度 |
|:---:|------|------|:---:|
| ANM-001 | 越权操作 | Agent 操作了它权限级别外的文件路径 | 🔴 P0 |
| ANM-002 | 批量删除 | 单次任务删除 > 5 文件 | 🔴 P0 |
| ANM-003 | 门禁跳过 | 文件修改但无对应 guard_checks_passed 记录 | 🔴 P0 |
| ANM-004 | 非工作时间 | UTC 22:00-06:00 期间 > 20 操作/小时（支持动态工作时间） | 🟡 P1 |
| ANM-005 | 高频操作 | > 100 文件操作/分钟（异常速率） | 🟡 P1 |
| ANM-006 | 跨 Agent 冲突 | 同一文件在 5 分钟内被 3+ 不同 agent 修改 → 自动加锁 | 🔴 P0 |
| ANM-007 | 审计日志异常 | 哈希链断裂 / HMAC 失败 / Ed25519 签名验证失败 / 日志被外部修改 | 🔴 P0 |
| ANM-008 | Agent 冒充 | Agent B 使用了 Agent A 的 DID 但签名验证失败——身份伪造 | 🔴 P0 |
| ANM-009 | 委托链异常 | 委托深度 > 3 / 权限放大 / 链中 DID 不可解析 | 🔴 P0 |
| ANM-010 | 协同规避 | 多 Agent 在同一时间窗口内对同一资源进行操作，整体效果 > 单个阈值（如 3 个 Agent 各删除 4 文件，总计 12 > 5） | 🔴 P0 |
| ANM-011 | 间接操作规避 | Agent 通过 symlink / script / cron / MCP 间接操作受限文件 | 🟡 P1 |
| ANM-012 | 信任趋势恶化 | trust_score 在 7 天内下降 > 0.3 或低于 0.5 阈值 | 🟡 P1 |
| ANM-013 | Dry-Run 差异异常 | Dry-Run 预期操作 vs 实际操作差异 > 阈值 | 🟡 P1 |

### 5.2 蓝图漂移检测（决策 D-020-06）

> **决策 D-020-06**（新增）：每条 `FILE_DETAIL` 审计条目对比"蓝图规定的操作"与"AI 实际操作"。漂移来源：(a) AI 跳过了蓝图规定的检查项，(b) AI 执行了蓝图未授权的操作，(c) AI 修改了 immutable 文件。

```python
class DriftDetector:
    """蓝图 vs 实际操作漂移检测器"""

    def compare(self, entry: AuditEntryV1, blueprint_constraints: BlueprintConstraints) -> DriftResult:
        """单条目漂移检测"""

    def batch_compare(self, entries: list[AuditEntryV1]) -> DriftReport:
        """批量漂移检测——生成报告"""

class DriftResult(BaseModel):
    entry_id: str
    drift_detected: bool
    drift_type: str | None = None  # unauthorized_op / skipped_check / immutable_violation
    expected: str | None = None
    actual: str | None = None
    severity: str | None = None
    blueprint_ref: str | None = None
```

### 5.3 三角闭环——审计反馈回写 Policy（决策 D-020-08）

> **决策 D-020-08**（新增）：对接 ADR-0010 §4.4 "Runtime → Policy 反馈"接口。审计 Trail 作为 Runtime 层的"数据生产者"，定期聚合异常/漂移/权限违规数据，通过 `feedback_to_policy.py` 推送至 Policy 层，驱动规则演进。

```yaml
feedback_loop:
  # ADR-0010 §4.4 接口 ④：Runtime → Policy（反馈）
  producer: "audit_trail.aggregator"
  consumer: "feedback_to_policy.py"  # Policy 层 PR 生成器

  aggregation:
    schedule: "daily 00:30 UTC"
    dimensions:
      - top_anomalies: "当日 Top 10 异常事件"
      - drift_summary: "当日蓝图漂移摘要——按模块分组"
      - permission_trends: "本周权限违规趋势"
      - cost_anomalies: "单操作 > $0.50 的高成本事件"

  output:
    format: "Markdown policy_evolution_pr_body"
    target: "GitHub PR → docs/01_policies_and_standards/ 对应规则文件"
    approval: "human_gated——Owner 审批后合并"

  # ADR-0010 激活路径 Sprint 11：L6 OPA Gatekeeper + D2-B 反馈回写闭环
  activation_sprint: "Sprint 11"
```

### 5.4 外部工具调用链审计（决策 D-020-20）

> **决策 D-020-20**（新增）：Agent→MCP Server→外部 API 的完整调用链审计。每次外部调用产生子审计条目（`parent_entry_id` 关联父条目），形成树状审计链。外部调用失败/超时也记录，不计为 Agent 失败（不可控因素）。

```python
class ExternalToolCallAudit:
    """外部工具调用链审计器"""

    def trace_call_chain(self, entry_id: str) -> list[AuditEntryV1]:
        """追溯完整外部调用链——从 Agent 操作 → MCP → 外部 API"""

    def detect_call_loop(self, entry_id: str) -> bool:
        """检测无限递归调用链——Agent→MCP→Agent→MCP→..."""

    def blame_boundary(self, entry_id: str) -> str:
        """故障边界判定——是 Agent 的错还是外部 API 的错？"""
```

### 5.5 间接操作检测（决策 D-020-21）

> **决策 D-020-21**（新增）：Agent 可能不直接修改目标文件，而是通过 symlink、hardlink、生成脚本、cron job、MCP 委托等方式间接操作。检测方法：(a) Agent 写入的任何内容扫描潜在执行路径（脚本/shebang/shell），(b) 写入文件后短时间内被执行→关联审计，(c) MCP 操作记录携带 `indirect_operation=True`。

```python
class IndirectOperationDetector:
    """间接操作检测器——对标 ANM-011"""

    def scan_generated_scripts(self, entry: AuditEntryV1) -> bool:
        """检测 Agent 是否生成了可执行脚本——潜在间接操作"""

    def correlate_write_execute(self, write_entry: AuditEntryV1, exec_entry: AuditEntryV1) -> float:
        """关联写入→执行——返回关联度 0.0~1.0"""

    def trace_indirect_path(self, entry: AuditEntryV1) -> list[str]:
        """追踪间接操作路径——symlink→target, script→cron→target"""
```

### 5.6 反馈循环自审计（决策 D-020-26）

> **决策 D-020-26**（新增）：三角闭环反馈本身可能产生自指循环——AI 从自己的审计日志中学了坏模式，然后反馈给 Policy，Policy 强化了坏模式。引入 `FeedbackSelfAudit`：检测 Policy 变更是否仅强化过去错误而非纠正，设立 human_gated 审批。

```python
class FeedbackSelfAudit:
    """反馈自指循环检测器"""

    def detect_self_reinforcement(self, policy_pr: PolicyPR) -> float:
        """检测 Policy 变更是否在强化过去的错误——0.0=纠正，1.0=完全自指"""

    def validate_evolution_direction(self, before: PolicyState, after: PolicyState) -> str:
        """验证演进方向——forward/backward/self_reinforcing"""
```

---

## 6. 数据生命周期与隐私治理

### 6.1 隐私脱敏策略（决策 D-020-11）

> **决策 D-020-11**（新增）：审计日志虽不可变，但敏感字段在写入时即脱敏——路径含密钥名 → hash、个人信息 → mask。脱敏不可逆——原始值不存储在审计日志中。

```yaml
privacy:
  pii_detection:
    enabled: true
    patterns:
      - "file_path 含 .env / secrets / credentials / key / token → hash 存储"
      - "file_path 含 邮箱/手机号/身份证 → mask('***')"
      - "agent_id 含真实姓名 → hash 存储"

  redaction_policy:
    none: "无敏感信息"
    masked: "局部掩码——如 file_path: 'src/**/secrets/***.py'"
    hashed: "完全替换为 SHA-256——不可逆"

  access_control:
    query_audit_log: "仅 Auditor + Owner 角色（GOV-CMP-002 AUD-003）"
    query_with_pii: "仅 Owner + 需 2FA 验证"
```

### 6.2 自动保留期执行（决策 D-020-12）

> **决策 D-020-12**（新增）：按 GOV-CMP-002 + GOV-DATA-003 规定的保留期，自动执行过期审计日志清理。清理前必须：(a) dry-run 生成报告 → (b) Owner 审批 → (c) 冷归档迁移检查 → (d) 执行删除 → (e) 写入 `tier_migration` 元审计事件。

```python
class RetentionEnforcer:
    def dry_run(self) -> RetentionReport:
        """扫描过期条目——不删除，仅生成报告"""

    def enforce(self, approval_token: str) -> RetentionReport:
        """执行保留期清理——需要 Owner 审批 token"""

class RetentionReport(BaseModel):
    entries_to_delete: int
    total_size_bytes: int
    oldest_entry_date: datetime
    tiers_affected: list[str]
    dry_run: bool
```

### 6.3 Cold Start——历史操作回溯

> **决策 D-020-13**（新增）：审计系统首次启动时（Cold Start），扫描现有 git log + session-logs/ 目录，生成历史审计基线 `bootstrap_audit_baseline.jsonl`。基线条目标记 `entry_type=cold_start_bootstrap` + `confidence_level=low`（历史数据不可完全验证）。

```python
class ColdStartBootstrapper:
    def scan_git_log(self, since: datetime | None = None) -> int:
        """扫描 git log → 生成历史审计基线条目"""

    def scan_session_logs(self) -> int:
        """扫描 session-logs/ 目录 → 标准化为审计条目"""

    def merge_to_baseline(self) -> Path:
        """合并 → 写入 bootstrap_audit_baseline.jsonl → 返回路径"""
```

### 6.4 Git 隔离——审计日志独立存储（决策 D-020-27）

> **决策 D-020-27**（新增）：审计 JSONL 存储在 `data/audit/` 目录，该目录加入 `.gitignore`。防止 `git reset --hard`/`git rebase` 导致审计日志随代码回滚而丢失。完整备份通过独立于 git 的备份机制（rsync / snapshot / cloud sync）。`data/audit/` 不在 git 工作区内跟踪。

```yaml
git_isolation:
  path: "data/audit/"
  gitignore: true
  rationale: "审计日志是时间机器——不能跟着代码版本回滚。git reset → 代码回滚 ✅ 审计日志回滚 ❌"
  backup:
    method: "独立于 git 的备份——每日 rsync → backup disk / 每周 snapshot"
    restore: "从备份恢复历史审计数据——不受 git 操作影响"
  migration_note: "Phase 1 迁移：现有 data/audit/audit-trail.jsonl 从 git tracking 中移除 + .gitignore 添加 data/audit/"
```

### 6.5 Knowledge Base 投毒防护（决策 D-020-28）

> **决策 D-020-28**（新增）：审计数据被喂入 Knowledge Base 前进行安全过滤。(a) 标记 `KB_POISONING_ATTEMPT` 的条目永久排黑，(b) 审计数据进入 KB 前经过 provenance 评分——仅 `trust_score >= 0.5` 的 Agent 产生的数据可被 KB 接受，(c) 投毒检测：异常高 confidence（0.99+）+ 异常低 anomaly_score（0.0）= 潜在构造数据。

```python
class KBAuditGate:
    """Knowledge Base 审计门禁——防止审计数据投毒 KB"""

    def filter_before_kb_ingest(self, entries: list[AuditEntryV1]) -> list[AuditEntryV1]:
        """过滤不适合进入 KB 的审计条目——POISONING_ATTEMPT / anomaly_score > 0.5 / confidence < 0.3"""

    def score_for_kb_trust(self, entry: AuditEntryV1) -> float:
        """评估单条审计记录对 KB 的 trustworthiness——0.0~1.0"""

    def detect_constructed_pattern(self, entries: list[AuditEntryV1]) -> bool:
        """检测人工构造的审计模式——confidence 异常高 + anomaly_score 异常低"""
```

---

## 7. 施工 Phase 规划

| Phase | 名称 | 任务 | 验收标准 | 状态 |
|:---:|------|------|---------|:---:|
| **scaffold** | 法医账本 | `AuditEntryV1` 完整模型 + JSONL append-only 写入 + 哈希链 + Lamport 时钟 + 基础查询 + 元审计 + 完整性自检 + heartbeat 自监控 + Git 隔离审计日志 + Agent Ed25519 签名（不含密钥管理全部功能）+ 外部独立验证脚本 | 1. 7+12 个事件类型全量通过 Pydantic V2 校验 2. 哈希链 1000 条连续无断裂 3. 写入延迟 < 5ms P99 4. `zephyr audit health` CLI 可用 5. 外部 verifier 零依赖 self-check 6. 5/5 单元测试通过 | 🔨 In Progress (42%) |
| **experimental** | 免疫系统 | 分级 Provenance 全量落地 + HMAC 签名 + Merkle 树聚合 + 异常检测（13 签名全量）+ 蓝图漂移检测 + Gate Engine/RBAC/Feedback Loop 全集成 + Dry-Run 预审计 + 间接操作检测 + 外部调用链审计 + 委托链验证 + 渐进信任分数 + 跨 IDE 一致性交叉验证 | 1. 13 种异常签名全部触发过真实/模拟事件 2. 漂移检测覆盖 10 份蓝图 3. Gate Engine 联动阻断验证通过 4. HMAC + Ed25519 签名 100% 验证 5. trust_score 趋势可见 | 📋 Backlog |
| **beta** | 闭环进化 | 三角闭环反馈（aggregator → feedback_to_policy.py → Policy PR）+ 反馈自审计 + 审计仪表盘 + 冷启动历史回溯 + 三层存储迁移自动化 + 保留期自动执行 + CI 一致性校验全量 + 隐私 PII 检测 + 监管证据包导出 + 合规框架映射 + KB 投毒防护 + 供应链审计 | 1. Policy PR 生成脚本可用 2. 仪表盘覆盖 8+ 种查询维度 3. 三层迁移零数据丢失 4. PII 检测 0 漏报 5. 证据包可离线验证 6. CI 门禁全通过 | 📋 Backlog |
| **production** | 公证处 | Agent DID 全量密钥管理基础设施 + Ed25519 密钥旋转自动化 + IATP 握手协议 + 分布式信誉证明 + WORM 兼容备份 + 损益（P&L）关联审计 | Phase 3 需求——不纳入 v1.1 施工范围 | 📋 Backlog |

### 施工文件对照（Phase scaffold）

| 文件 | 类型 | 职责 |
|------|------|------|
| `src/zephyr/audit_trail/__init__.py` | Package | 模块入口 + `__all__` |
| `src/zephyr/audit_trail/models.py` | Pydantic V2 | 全量审计事件模型 + AuditEventType 枚举（29 种）+ DID 模型 |
| `src/zephyr/audit_trail/writer.py` | Runtime | 不可变写入器（JSONL + 哈希链 + HMAC + Ed25519 + Lamport） |
| `src/zephyr/audit_trail/query.py` | Query | 审计查询接口（SQLite + JSONL + 元审计 + trail_for_ai_context） |
| `src/zephyr/audit_trail/integrity.py` | Crypto | 密码学完整性验证器（哈希链 + HMAC + Ed25519 + Merkle） |
| `src/zephyr/audit_trail/anomaly.py` | Detection | 异常检测引擎（experimental 阶段——13 签名） |
| `src/zephyr/audit_trail/drift.py` | Detection | 蓝图漂移对账（experimental 阶段） |
| `src/zephyr/audit_trail/agent_signer.py` | Crypto | Ed25519 Agent 签名器 + DID 注册（scaffold） |
| `src/zephyr/audit_trail/supply_chain.py` | Detection | 供应链审计——包安装检测（experimental 阶段） |
| `src/zephyr/audit_trail/delegation.py` | Governance | 委托链审计器（experimental 阶段） |
| `src/zephyr/audit_trail/trust_score.py` | Governance | 渐进信任引擎（experimental 阶段） |
| `src/zephyr/audit_trail/cross_ide.py` | Integrity | 跨 IDE 一致性交叉验证（experimental 阶段） |
| `src/zephyr/audit_trail/evidence_pack.py` | Governance | 监管证据包导出（beta 阶段） |
| `src/zephyr/audit_trail/lifecycle.py` | Lifecycle | 三层存储迁移 + 保留期执行（beta 阶段） |
| `src/zephyr/audit_trail/self_monitor.py` | Monitor | 自监控 heartbeat + 信任分数趋势 + 健康采集 |
| `src/zephyr/audit_trail/cli.py` | CLI | 审计命令行面板——query/trail/integrity/health/evidence |
| `scripts/governance/rebuild_audit_index.py` | Script | JSONL → SQLite 索引重建 |
| `scripts/governance/verify_audit_integrity.py` | Script | 外部独立验证——零依赖 audit_trail/，CI 门禁用 |
| `scripts/governance/enforce_audit_retention.py` | Script | 保留期强制执行 + CoT 文件生命周期（beta 阶段） |

---

## 8. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 | 对应盲点 |
|---|------|:---:|:---:|------|:---:|
| R1 | 审计日志膨胀——大量操作导致 JSONL 文件过大 | 高 | 中 | 按日轮转 + gzip/Parquet 分层存储 + 保留期自动执行 | B12/B13 |
| R2 | JSONL 写入冲突——多 IDE 同时追加同一文件 | 中 | 高 | 文件锁（fcntl/msvcrt）+ 重试机制 + Lamport 时钟保证因果序 | B5/B6 |
| R3 | SQLite 索引延迟——异步重建导致查询不到最新记录 | 中 | 低 | 查询时先检查 JSONL 最新 N 行 + 5s 重建间隔 | — |
| R4 | 审计日志被篡改——AI 修改 JSONL | 低 | 🔴极高 | 哈希链 + HMAC 签名 + Merkle 根 + 外部 verifier + pre-commit SHA-256 校验 | B1/B2/B3 |
| R5 | HMAC secret 泄露——攻击者可伪造审计条目 | 低 | 🔴极高 | Secret 存储在环境变量 + 定期轮转 + 轮转时重签历史条目（迁移脚本）+ Shamir Secret Sharing 分片（2/3）+ 独立保管 | B2/B31 |
| R6 | 自监控自身故障——heartbeat 假阳性/假阴性 | 低 | 中 | Heartbeat 3 次失败才告警 + emergency fallback 独立于主写入器 + 外部独立 verifier 交叉验证 | B7/B8/B53 |
| R7 | 异常检测误报——Owner 告警疲劳 | 中 | 中 | anomaly_score 阈值可配置 + 首次部署仅 warn 模式（dry-run 观察 2 周）+ daily_report_composer 聚合日报 | B9 |
| R8 | 隐私脱敏遗漏——含 PII 的路径未检测到 | 低 | 高 | PII pattern 正则维护在受控词表中 + CI 扫描新增文件路径模式 | B11 |
| R9 | 冷启动生成的基线不可靠——git log 不完整 | 高 | 低 | baseline 明确标记 confidence=low + 不作为合规证据——仅作参考 + 隔离存储于 bootstrap 文件 | B18/B54 |
| R10 | 三角闭环反馈质量差——Policy 层收到无价值的 PR | 中 | 低 | Aggregator 仅推送 anomaly_score >0.8 事件 + PR 含 Owner 审批步骤 + 反馈自审计过滤自指循环 | B14/B34 |
| R11 | Dry-Run 审计与真实执行行为不一致 | 中 | 中 | RI-14 DryRunSimulator 沙箱环境与真实环境隔离 + Dry-Run 记录独立标记 `dry_run=True` + dry_run_real_diff 差异检测 | B17 |
| R12 | 分层存储迁移中断——Warm→Cold 过程中断电 | 低 | 中 | 迁移脚本先写入新文件 → 验证 SHA-256 → 再删除旧文件（两阶段） | B13 |
| R13 | Agent 冒充——Agent B 使用 Agent A 的 DID 操作 | 低 | 🔴极高 | Ed25519 Agent 级签名——签名验证失败 → P0 阻断 + ANM-008 检测 | B16 |
| R14 | 委托链断裂——中间 Agent 不可追溯 | 低 | 高 | 委托链完整记录 + 深度 ≤ 3 + 权限缩小校验 + ANM-009 检测 | B24 |
| R15 | 多 Agent 协同规避——分头操作绕过单阈值 | 低 | 高 | ANM-010 协同规避检测——跨 Agent 时间窗口聚合分析 | B27/B39 |
| R16 | AI 上下文污染——审计数据投毒 AI 决策 | 中 | 高 | KB 投毒防护门禁 + 信任分数过滤 + 投毒签名检测 | B37/B48 |
| R17 | 间接操作——Agent 通过 symlink/script/cron 越权 | 中 | 中 | ANM-011 间接操作检测 + 写入→执行关联分析 | B25 |
| R18 | 时间炸弹——代码当时安全但含延迟漏洞 | 低 | 高 | LatentRiskScanner——定期扫描最近 30 天 AI 写代码中的 eval/exec/os.system 模式 | B33 |
| R19 | 反馈自指循环——Policy 被审计反馈强化了错误 | 低 | 中 | FeedbackSelfAudit——检测 Policy 变更是否仅强化过去错误 | B34 |
| R20 | 审计日志体积 DoS——Agent 生成海量小操作 | 低 | 高 | 速率限制——单 Agent >1000 操作/分钟 → 限流 + ANM-005 触发 + volume_dos 计数 | B38 |
| R21 | Git 回滚致审计日志丢失——git reset 删除了审计历史 | 中 | 🔴极高 | Git 隔离——data/audit/ 加入 .gitignore + 独立备份 | B22/B43 |
| R22 | 供应链风险——Agent 安装的包未经审计 | 中 | 高 | 每次 pip/npm install 产生 audit 事件 + 记录包 SHA-256 + untrusted_external 标记 | B35 |
| R23 | **Prompt 注入攻击——恶意审计条目劫持 AI 决策** | 中 | 🔴极高 | trail_for_ai_context() 输入净化 + audit entry 中禁止包含 AI 指令关键词 + 语义沙箱包裹 | B55 |
| R24 | **Vibe Drift——AI 模型版本变化致审计代码不兼容** | 中 | 中 | AuditEntry 中记录 model_version + CI 定期多模型交叉验证 + schema 版本前向兼容 | B56 |
| R25 | **AI 审计算法幻觉——分析审计数据时生成虚假发现** | 中 | 中 | 分析结果逐条关联源条目 entry_id + 置信度标注 + human_gated 告警 | B57 |
| R26 | **确定性重放不可行——无法从审计日志重建准确状态** | 中 | 高 | 关键操作记录 sha256_before/after + 分层 deterministic replay 测试 | B58 |
| R27 | **单人密钥仪式失败——Shamir 分片需多保管人** | 低 | 高 | 替代方案：HSM 模拟分片 + 物理备份 + 遗嘱托管（dead man's switch）| B59/B60 |
| R28 | **Bus Factor = 1——维护者不可用致审计系统死亡** | 低 | 高 | 全自动化自愈 + 零人工干预 + 外部 verifier 独立 + 遗嘱托管方案 | B60 |
| R29 | **审计质量渐进退化——无 peer review 发现问题** | 高 | 中 | auto_regression_test 周检 + 覆盖率趋势 + 审计漂移告警 | B62 |
| R30 | **GDPR 删除权 vs 审计不可变性之不可调和矛盾** | 中 | 中 | 脱敏替代删除 + legal_hold 标记 + 法律意见书 | B63 |
| R31 | **明文存储——审计日志未加密** | 低 | 中 | AES-256-GCM 透明加密层——写入前加密 + 查询时解密 + key 派生自 HMAC secret | B64 |
| R32 | **磁盘满——审计写入静默失败** | 低 | 🔴极高 | 磁盘水位预警（>80% P1）+ 写失败→P0 阻断 + fallback 写入内存缓冲区 | B66 |
| R33 | **MCP/原生工具绕过审计写入路径** | 中 | 高 | audit_coverage_gap_scanner——定期检测未记录的文件变更 | B72 |
| R34 | **Genesis 初始化被 compromise——所有后续信任崩塌** | 低 | 🔴极高 | 初始化仪式：独立 CSPRNG + 外部见证介质 + Owner 手动执行（非 AI）| B77/B87 |
| R35 | **哈希链分叉——两个 IDE 产生两条合法审计链** | 中 | 高 | fork_detection + fork_reconciliation + 最早分支时间点告警 | B78 |
| R36 | **撕裂写入——OS 崩溃/断电致 JSONL 行损坏** | 低 | 高 | torn_write_detector + 原子 append + 最后一行完整性回退 | B79 |
| R37 | **Unicode 同形字绕过净化——Cyrillic "іgnore" 注入** | 中 | 🔴极高 | NFKC 归一化 → 同形字映射 → 净化——净化前必须归一化 | B80 |
| R38 | **多会话协同攻击——跨天/周的低强度渗透** | 中 | 高 | ANM-016 跨 session 聚合 + long_term_window 配置 | B81 |
| R39 | **AI 学习审计模式后针对性规避——读 JSONL 学格式** | 中 | 高 | AI 读审计日志→元审计记录 + audit_schema_obfuscation | B82 |
| R40 | **依赖版本漂移——Pydantic v3 无法加载 v2 审计数据** | 中 | 中 | frozen_dependencies.txt + migration CI test + Docker 旧环境留存 | B84 |
| R41 | **告警疲劳→系统实质上无监控** | 高 | 🔴极高 | operator_responsiveness_model + 响应率 < 30%→P0 escalation→外部通知 | B85 |
| R42 | **信任漂移——Operator 逐渐认为"AI 不会出错"** | 高 | 中 | trust_calibration：实际 anomaly 率 vs Operator 审核通过率趋势对比 | B86 |

---

## 9. 能力边界声明（v1.1.0 明确不覆盖项）

> **设计哲学**："已知盲点 = 已管理风险"——不追求 v1.1.0 消除所有盲点，而是每个盲点都显式声明、评估风险、记录缓解策略。ISACA "Embedded not paper" 实践落地。

| 盲点 ID | 盲点内容 | v1.1.0 覆盖策略 | v2.0 计划 |
|:---:|------|------|:---:|
| B15 | Agent 级 Ed25519 签名——完整密钥管理基础设施 | scaffold：AgentSigner 基础签名 + 验证 + DID 注册（不含密钥旋转/分布式密钥管理）| Phase production |
| B16 | Agent 冒充检测（IATP Challenge-Response 握手） | experimental：Ed25519 签名验证 → 冒充检测（ANM-008）| Phase production |
| B17 | LLM 完整 CoT 推理链 | scaffold：`reasoning_trace` 摘要字段（<500 chars）；完整 CoT 在 experimental 阶段记录 | Phase experimental |
| B18 | 跨 IDE 一致性交叉验证 | experimental：CrossIDEConsistencyChecker | Phase experimental |
| B19 | 监管证据包 PDF 导出 | beta：EvidencePackExporter (JSON + PDF) | Phase beta |
| B20 | 外部独立验证端点 | scaffold：`verify_audit_integrity.py`（零依赖） | Phase scaffold ✅ |
| B21 | 合规框架条款→实现的完整映射 | beta：compliance-map.yml 骨架 | Phase beta |
| B22 | 审计日志 Git 隔离 | scaffold：data/audit/ 加入 .gitignore | Phase scaffold ✅ |
| B23 | 渐进信任分数——连续值 + 时间衰减 | experimental：TrustScoreEngine | Phase experimental |
| B24 | Agent-to-Agent 委托链审计 | experimental：DelegationChainAuditor | Phase experimental |
| B25 | 间接操作检测 | experimental：IndirectOperationDetector | Phase experimental |
| B26 | 外部工具调用链闭环审计 | experimental：ExternalToolCallAudit | Phase experimental |
| B27 | 多 Agent 协同规避检测 | experimental：ANM-010 协同检测 | Phase experimental |
| B28 | 行为基线模型（ML 偏离检测） | experimental：规则签名（13 种），ML 基线不纳入 v1.1 | v2.0 |
| B29 | 权限持续重新验证 | Phase production（需无状态策略引擎重构）| Phase production |
| B30 | 审计查询注入防御 | scaffold：全部查询参数化 + 白名单校验 | Phase scaffold ✅ |
| B31 | HMAC Secret 泄露——伪造审计条目 | 缓解：Shamir 分片（2/3）— experimental | Phase experimental |
| B32 | Bit Rot 静默存储损坏 | experimental：silent_corruption_detector 周检 | Phase experimental |
| B33 | 时间炸弹——延迟触发漏洞 | experimental：LatentRiskScanner | Phase experimental |
| B34 | 反馈自指循环 | experimental：FeedbackSelfAudit | Phase experimental |
| B35 | 供应链接入审计 | experimental：SupplyChainAudit | Phase beta |
| B36 | Session 边界攻击 | 不覆盖——当前依赖会话级监控 | v2.0 |
| B37 | 审计数据 AI 上下文投毒 | experimental：KBAuditGate | Phase beta |
| B38 | 海量操作 DoS | scaffold：rate_limit + ANM-005 + volume_dos | Phase scaffold ✅ |
| B39 | Gradual Permission Escalation | experimental：trust_score 降级 + 阈值 <-0.5 自动降级 | Phase experimental |
| B40 | 运行时配置渐进漂移 | 不覆盖——当前蓝图漂移仅检测蓝图 vs 操作偏差 | v2.0 |
| B41 | Emergency Access 的审计 | 不覆盖——危机场景依赖外部日志 | v2.0 |
| B42 | Schema Evolution 悖论 | 不覆盖——v1.1 仅 AuditEntryV1；V2 需独立迁移方案 | v2.0 |
| B43 | Audit Trail 依赖死锁 | scaffold：按 depends_on 顺序施工 + 外部 verifier 独立 | Phase scaffold ✅ |
| B44 | 人操作 vs AI 操作统一审计 | 不覆盖——当前仅 AI Agent 操作；人操作使用 git log + session-logs | v2.0 |
| B45 | Provenance 数据的 Provenance 验证 | experimental：blueprint_reads 条目交叉验证 | Phase experimental |
| B46 | Lamport 时钟边缘竞赛 | scaffold：merge 规则 `max(local, received)+1` + 冲突检测 | Phase scaffold ✅ |
| B47 | Rollback 自身审计链 | 不覆盖——回滚操作的审计链拓扑复杂 | v2.0 |
| B48 | Knowledge Base 投毒 | experimental：KBAuditGate 过滤 | Phase beta |
| B49 | 审计日志作为侧信道 | 不覆盖——当前场景个人信息极低 | v2.0 |
| B50 | 审计日志膨胀到 Context Window 溢出 | scaffold：trail_for_ai_context() token 预算控制 | Phase scaffold ✅ |
| B51 | Multi-Tenant 审计隔离 | 不覆盖——当前单租户 | v2.0 |
| B52 | 非工作时间定义的动态性 | 不覆盖——当前使用 UTC 固定窗口 | v2.0 |
| B53 | Heartbeat 假阴性检测 | experimental：external verifier 交叉验证 | Phase experimental |
| B54 | Cold Start 基线法律风险 | scaffold：confidence=low 标记 + 隔离存储 | Phase scaffold ✅ |
| B55 | Prompt 注入——恶意审计条目劫持 AI 决策 | experimental：trail_for_ai_context() 语义沙箱 + 禁止 AI 指令关键词 | Phase beta |
| B56 | Vibe Drift——AI 模型升级致审计代码不兼容 | experimental：model_version 元数据 + CI 多模型交叉验证 | Phase beta |
| B57 | AI 幻觉——审计分析/日报生成虚假发现 | experimental：分析结果逐条关联 entry_id + 置信度标注 + human_gated | Phase experimental |
| B58 | 确定性重放——无法从审计日志重建系统状态 | experimental：sha256_before/after 全覆盖 + 分层重放测试 | Phase experimental |
| B59 | 单人密钥仪式——Shamir 需 3 人独立保管分片 | 替代方案：HSM 模拟 + 物理备份 + dead man's switch | v2.0 |
| B60 | Bus Factor = 1——维护者不可用致审计系统死亡 | 缓解：全自动化自愈 + 零人工干预 + 遗嘱托管 + 外部 verifier 独立 | v2.0 |
| B61 | 无 Peer Review——审计告警无人二次确认 | scaffold：human_gated escalation 审批 + AI 自 review | Phase scaffold ✅ |
| B62 | 审计质量渐进退化——无 peer review 感知衰减 | experimental：auto_regression_test 周检 + coverage_trend 监控 | Phase beta |
| B63 | GDPR Art.17 删除权 vs 审计不可变性 | 缓解：脱敏替代删除 + legal_hold 标记 | v2.0 |
| B64 | 明文存储——审计日志未加密 at rest | experimental：AES-256-GCM 透明加密层——写入前加密 + 查询时解密 | Phase experimental |
| B65 | 可信时间戳缺失——Ed25519 签名无法定时间效力 | 不覆盖——需 RFC 3161 TSA 外部服务 | v2.0 |
| B66 | 磁盘满静默失败——审计写入丢弃 | scaffold：disk_watermark + 写失败→P0 阻断 + 内存缓冲区 fallback | Phase scaffold ✅ |
| B67 | 审计写入阻塞主操作——"先审计还是先执行" | scaffold：异步写入（fire-and-forget）+ 写失败不影响主操作 + 内存队列 | Phase scaffold ✅ |
| B68 | Schema 迁移完整性——v1→v2 迁移可验证 | experimental：schema_migration_verifier + 双写过渡期 + 迁移证明 | Phase beta |
| B69 | 审计工具链完整性——Python/OS/fs 被篡改 | 不覆盖——信任链终止于操作系统层 | v2.0 |
| B70 | 隐身 Agent——生成合法但恶意的审计条目（Mimicry） | experimental：行为-审计一致性检查 + ANM-014 学习模式检测 | v2.0 |
| B71 | 时序攻击——操纵 Lamport 时钟/系统时间制造混乱 | experimental：时钟跳变检测 + NTP 源对比 + 时钟漂移告警 | Phase experimental |
| B72 | MCP/原生工具绕过审计——操作未记录 | scaffold：audit_coverage_gap_scanner + 文件变更→审计条目交叉校验 | Phase scaffold ✅ |
| B73 | 影子审计——Agent 意外创建第二条审计机制 | experimental：audit_writer_uniqueness_check + 未知 JSONL 文件扫描 | Phase experimental |
| B74 | Vibe Coding 覆盖缺口——AI 跳过边界条件审计 | experimental：coverage_fuzzer + edge_case_injector + 覆盖率提升 PR | Phase beta |
| B75 | AI 代码相似性混淆——生成相似但不相同的审计模式 | experimental：code_fingerprint + pattern_clustering + 误报降权 | Phase experimental |
| B76 | 模板/脚手架伪审计——AI 生成代码产生虚假审计条目 | experimental：template_origin_tag + 模板生成代码独立追踪 | Phase experimental |
| B77 | 法庭可采性——审计证据链的 chain of custody 缺失 | experimental：custody_log 独立记录 + 访问者身份 + 时间 + 目的 + 数字签名 | Phase beta |
| B78 | 哈希链分叉——两个 IDE 并发写同一 prev_entry_hash | experimental：fork_detection + fork_reconciliation + fork 分支标记 | Phase experimental |
| B79 | 部分写入/撕裂写入——OS 崩溃致 JSONL 行不完整 | scaffold：torn_write_detector + 最后一行完整性校验 + 原子写入策略 | Phase scaffold ✅ |
| B80 | Unicode 同形字绕过净化——"іgnore"（Cyrillic і）绕过过滤器 | experimental：NFKC Unicode 归一化 + homoglyph_mapper + 净化前归一化 | Phase experimental |
| B81 | 多会话协同攻击——单会话低于阈值、跨会话总和超标 | experimental：ANM-016——跨 session 时间窗口聚合分析 + long_term_threshold | Phase experimental |
| B82 | AI 学习规避审计——AI 通过读原始 JSONL 学习审计模式 | experimental：audit_schema_obfuscation + AI 访问审计日志需元审计记录 | Phase experimental |
| B83 | 格式寿命——JSONL 在 20 年内仍可解析？ | scaffold：格式规范锁定 + 自描述 schema + 参考解析器（纯 stdlib Python） | Phase scaffold ✅ |
| B84 | 依赖版本漂移——Pydantic v2→v3 审计数据无法验证 | experimental：dependency_freeze + v1→v2 migration_test + 旧版本 Docker 镜像留存 | Phase beta |
| B85 | 告警疲劳渐进建模——Operator 对 P1 响应率从 90%→10% | experimental：operator_responsiveness_model + 响应率 < 30% → P0 escalation | Phase beta |
| B86 | 信任漂移曲线——Operator 逐渐过度信任 AI 致审查松懈 | experimental：trust_calibration_check——实际 anomaly 率 vs Operator 审核通过率对比 | Phase beta |
| B87 | 新人 Onboarding 不可能——文档全是 AI 写给 AI 的 | scaffold：human_readable_onboarding.md + bootstrap 流程注解 + 3 页快速入门 | Phase scaffold ✅ |
| B88 | 审计数据恢复——JSONL 文件部分损坏时尽可能恢复数据 | experimental：damaged_line_skipper + partial_recovery + 恢复条目标记 `recovered=True` | Phase experimental |
| B89 | Tool 调用逃逸——自定义 MCP Tool 绕过审计写入路径 | experimental：MCP_tool_registry_audit + 未注册 tool 调用 → ANM-017 | Phase experimental |
| B90 | 篡改痕迹时间线重建——若篡改发生，能否精确重建作案时间？ | experimental：tamper_timeline_reconstruction + 外部介质见证对比 + 前后哈希链断点分析 | Phase experimental |
| B91 | 跨系统日志关联——审计数据需与 CI/CD/云日志交叉验证 | 不覆盖——需外部 log aggregator（ELK/Loki）| v2.0 |
| B92 | 初始化的初始化——初始化脚本的 hash 在初始化前不可知 | scaffold：bootstrapper_hash_precommit + 手动验证 + 写入外部见证介质 | Phase scaffold ✅ |
| B93 | 审计系统自身代码变更未被审计——AI 改 `writer.py` 无人知晓 | experimental：audit_self_code_change_detector + 审计模块文件哈希快照 + 变更→P0 alert | Phase experimental |
| B94 | 自然语言不一致——同一操作被不同 session 描述为不同文本 | experimental：canonical_action_vocabulary + action_normalizer + 标准化后对比 | Phase experimental |
| B95 | AI 模型供应商依赖——API 变更/倒闭/模型退役致审计系统失效 | scaffold：provider_independence_check + 双供应商兼容 + 本地 fallback 模型测试 | Phase scaffold ✅ |
| B96 | 观测者效应——被审计的 AI 行为系统性异于未被审计的 AI | 不覆盖——承认"审计改变行为"是基本物理规律，隐性审计在伦理和法律上不可行 | v2.0 |
| B97 | Goodhart 定律——AI 学会优化 trust_score/anomaly_score 而非优化行为 | experimental：metric_gaming_detector + score-vs-behavior 一致性校验 + ANM-018 | Phase beta |
| B98 | 启动期审计盲区——系统启动到审计初始化之间的操作无记录 | scaffold：boot_audit_gap_logger + systemd/launchd 启动前钩子 + 独立最小记录器 | Phase scaffold ✅ |
| B99 | "谁审计审计者？"无限递归——审计系统本身的审计链最终无外部锚点 | 承认——这是逻辑极限而非工程盲点。缓解：外部 verifier + genesis 外部见证 + 定期第三方审计计划 | v2.0 |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-020-01 | 两层审计粒度（任务级摘要+文件级明细） | 2026-05-05 | 1人场景，任务级摘要够日常浏览，文件级明细够问题定位 |
| D-020-02 | JSONL 为唯一真源，SQLite 为派生查询索引 | 2026-05-05 | 多 IDE 并发，JSONL 天然 append-only 且 git 友好；对标 GOV-CMP-002 |
| D-020-03 | Provenance 按权限级别分级（轻量/标准/全量） | 2026-05-05 | 1人+AI场景，99%操作无草稿和仲裁，强制三件套形同虚设 |
| D-020-04 | 密码学完整性——哈希链 + HMAC + Merkle | 2026-05-05 | JSONL append-only ≠ tamper-evident；AI 可删除行后重 append；对标 Microsoft AGT Merkle-chain + W3C PROV |
| D-020-05 | 元审计——审计系统自身操作留痕 | 2026-05-05 | 1人+AI 维护，无人审计审计系统本身；对标 GOV-CMP-002 AUD-001 |
| D-020-06 | 蓝图漂移检测——实际操作 vs 蓝图规定 | 2026-05-05 | 对标 ISACA 2025 "Embedded not paper" + MOD-INF-023 Drift Detector |
| D-020-07 | AI 行为异常签名——13 种自动检测模式（v1.1.0 扩展） | 2026-05-05 | 对标 OWASP ASI-10 "Lack of Observability" + ISACA 自修改AI审计 |
| D-020-08 | 三角闭环反馈——审计聚合数据回写 Policy 驱动规则演进 | 2026-05-05 | 对接 ADR-0010 §4.4 Runtime→Policy 接口；对标 Netflix 混沌反馈 |
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
| D-020-53 | 审计系统自身代码变更审计——模块文件哈希快照 | 2026-05-05 | AI 可能修改 audit_trail/ 自身代码绕过审计——审计系统需自我防御 |
| D-020-54 | 自然语言标准化——canonical_action_vocabulary | 2026-05-05 | 不同 session 对同一操作的文本描述不一致→跨 session 分析失真 |
| D-020-55 | AI 模型供应商独立性——双供应商兼容 + 本地 fallback | 2026-05-05 | AI 供应商 API 变更/倒闭→审计系统依赖的 AI 推理能力丧失 |
| D-020-56 | Goodhart 防御——metric_gaming_detector + ANM-018 | 2026-05-05 | 指标成为目标时即失效——AI 学会优化 trust_score 而非行为质量 |
| D-020-57 | 启动期审计盲区——boot_audit_gap_logger + 启动前钩子 | 2026-05-05 | 系统启动到审计 init 间的操作无人记录——独立最小记录器填补 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 1.4.0 | **🔮 blueprint v1.4.0——从"法医实验室 + 免疫系统 + 公证处 + 安全边界 + 取证科学"升级为"法医实验室 + 免疫系统 + 公证处 + 安全边界 + 取证科学 + 元认知"。** generation 6→7。终极审查维度——外部取证专家视角发现最后 7 个盲点 (B93-B99)：(1) 审计系统自身代码变更审计 (2) 自然语言标准化 (3) AI 模型供应商独立性 (4) 观测者效应承认 (5) Goodhart 定律防御—指标博弈 ANM-018 (6) 启动期审计盲区 (7) "谁审计审计者？"无限递归—承认逻辑极限。风险 42。决策 52→57。盲点 92→99。至此——**重大盲点已穷尽。** 以下为 99 盲点未覆盖的"已知不可解"问题的显式声明。 |
| 2026-05-05 | 1.3.0 | **🔬 blueprint v1.3.0——+取证科学。** generation 5→6。四个新维度：取证科学 + 对抗性AI + 长期存档 + 运维心理学 → 16 盲点 (B77-B92)。新 §2.16 Genesis 信任锚初始化。 |
| 2026-05-05 | 1.2.0 | **🛡️ blueprint v1.2.0——+安全边界。** 22 盲点 (B55-B76)：Prompt 注入防护 + 确定性重放 + Vibe Drift + AI 幻觉 + 加密 + GDPR。新 §2.14-2.15。 |
| 2026-05-05 | 1.1.0 | **🔄 blueprint v1.1.0——+公证处。** Agent Ed25519 + CoT + 委托链 + 信任分数 + 外部验证 + 跨IDE + 证据包 + 合规映射 + 供应链。 |
| 2026-05-05 | 1.0.0 | **🎉 blueprint v1.0.0——法医实验室 + 免疫系统。** 全文重构。 |
| 2026-05-05 | 0.2.0 | D-020-01~03——两层粒度 + JSONL SSoT + 分级 Provenance |
| 2026-05-05 | 0.1.0 | 初始创建 |


---

## 施工落盘确认（2026-05-07 审计）
| 维度 | 状态 |
|------|------|
| construction_progress | phase_1_scaffold_partial（核心写入+完整性验证可用，异常检测/漂移对账/Merkle树待施工） |
| 源码路径 | `src/zephyr/audit_trail/` |
| 源码文件数 | 9 个 .py/.yaml |
| 测试路径 | `tests/unit/ + tests/infrastructure/` |
| 关键入口 | `audit_trail.trail.AuditTrail (不可变审计+密码学Provenance)` |
