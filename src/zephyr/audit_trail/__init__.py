"""
audit_trail — MOD-INF-020 · 审计追踪：法医实验室 + 免疫系统 + 公证处
======================================================================
蓝图 v1.4.0 · Phase scaffold · P0 核心模块

职责三胞胎
----------
  1. 法医实验室 (Forensic Lab)  — 完整记录所有 AI 操作，支持事后溯源
  2. 免疫系统   (Immune System) — 实时检测异常操作模式并告警
  3. 公证处     (Notary)        — Ed25519 数字签名确保记录不可篡改

模块结构
--------
  models.py       — Pydantic V2 全量审计模型（AuditEntryV1 + 29事件类型 + 分级Provenance）
  writer.py       — 不可变写入器 (append-only, HMAC-SHA256, Lamport时钟, Merkle聚合) + 全局单例
  query.py        — 审计查询接口 (含 trail_for_ai_context() 新AI上线消费品)
  integrity.py    — 密码学完整性验证器 (哈希链 + HMAC + Ed25519签名 + Merkle)
  anomaly.py      — 异常行为签名检测（13 种异常签名）
  bridge.py       — 外部模块审计桥接入口（write_rbac_decision / write_gate_decision / write_to_core）
  contracts.py    — 契约层（3 个外部消费者的审计写入入口）
  self_monitor.py — 自监控（审计系统自身的健康检查 + heartbeat + 定时调度）
  indexer.py      — 审计索引器
  agent_signer.py — Agent Ed25519 签名器
  cli.py          — CLI 审计面板

设计原则
--------
  - API→DB→SCHEMA 严格单向：api 层 → db 层 → schema 层——不可反向依赖
  - 不可变性：每条审计记录写入后不可修改/删除
  - 合规对标：ITGC 审计标准 + SOC2 可追溯性要求
  - 版本冻结：所有依赖版本锁定，零依赖外部独立验证器
"""
from zephyr.audit_trail.anomaly import AnomalyDetector, AnomalyResult
from zephyr.audit_trail.bridge import write_to_core
from zephyr.audit_trail.orchestrator import AuditWriter as OrchestratorAuditWriter, get_audit_writer as orchestrator_get_audit_writer
from zephyr.audit_trail.compliance_map import ComplianceMapper
from zephyr.audit_trail.indexer import AuditIndexer
from zephyr.audit_trail.integrity import IntegrityVerifier, MerkleAggregator
from zephyr.audit_trail.kb_gate import KBAuditGate
from zephyr.audit_trail.supply_chain import SupplyChainAuditor
from zephyr.audit_trail.writer import AuditWriter, get_audit_writer

__all__ = [
    "models",
    "writer",
    "query",
    "integrity",
    "anomaly",
    "bridge",
    "indexer",
    "self_monitor",
    "agent_signer",
    "cli",
    "cold_start",
    "contracts",
    "delegation_auditor",
    "delegation_bridge",
    "drift_bridge",
    "evidence_pack",
    "external_tool_audit",
    "feedback_bridge",
    "feedback_policy",
    "feedback_self_audit",
    "genesis",
    "log_rotation",
    "merkle_hourly",
    "privacy",
    "replay_engine",
    "retention",
    "spec_auditor",
    "tiered_storage",
    "tiered_storage_bridge",
    "trust_bridge",
    "trust_engine",
    "provenance_tracker",
    "changelog_manager",
    "code_archaeology",
    "incremental_review",
    "observability_dashboard",
    "glossary_matrix",
    "wqa_scorer",
    "financial_compliance",
    "sbom_generator",
    "dora_metrics",
    "corporate_actions",
    "supply_chain_security",
    "api_lifecycle",
    "AnomalyDetector",
    "AnomalyResult",
    "AuditIndexer",
    "IntegrityVerifier",
    "MerkleAggregator",
    "AuditWriter",
    "get_audit_writer",
    "compliance_map",
    "ComplianceMapper",
    "kb_gate",
    "KBAuditGate",
    "supply_chain",
    "SupplyChainAuditor",
    "write_to_core",
    "orchestrator",
    "OrchestratorAuditWriter",
]
