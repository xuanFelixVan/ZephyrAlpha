---
module_id: KE-1892---------------ssot-000
status: active
title: 2.4 密码学完整性数据模型（新增 SSoT 条目体）
category: module_blueprint
---

# 2.4 密码学完整性数据模型（新增 SSoT 条目体）

2.4 密码学完整性数据模型（新增 SSoT 条目体）

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
    drift_severity: str | None = None  # low/medium/h
