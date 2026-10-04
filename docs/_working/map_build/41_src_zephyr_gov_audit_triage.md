---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.gov_audit（40 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.gov_audit（40 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：wired=21，wired_by_header=9，wired_dynamic=10；初判汇总：mount=40

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/gov_audit/__init__.py` | ============================================================================ | 2026-09-18（16天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/action_history.py` | ActionHistory — 操作历史持久化审计 + 去重 + 循环检测 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/agent_signer.py` | audit-trail.agent_signer — MOD-INF-020 · Agent Ed25519 签名器 | 2026-09-17（17天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/anomaly.py` | 治本（裁定#18 G3 + G-CT-002）：本文件原为桩实现——AnomalyDetector 仅有 feed/detect/scan_series | 2026-09-17（17天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/audit_schema.py` | audit_schema — 审计视图与查询入口（SH-DB-001 v2.0） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/bridges/audit_anomaly.py` | G-CT-002 Audit 异常检测器 — AnomalyEvent Pydantic V2 BaseModel. | 2026-09-17（17天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/bridges/audit_tiered_storage_bridge.py` | Audit ↔ WarmHotGate 三层存储桥接. | 2026-09-17（17天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/bridges/audit_trust_bridge.py` | Audit ↔ ContinuousTrust 信任分数桥接. | 2026-09-17（17天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/changelog_manager.py` | （无文档头，按文件名语义：changelog_manager） | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/code_archaeology.py` | （无文档头，按文件名语义：code_archaeology） | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/compliance_map.py` | audit-trail.compliance_map — MOD-INF-020 · 合规框架映射 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/corporate_actions.py` | （无文档头，按文件名语义：corporate_actions） | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/dora_metrics.py` | （无文档头，按文件名语义：dora_metrics） | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/event_store.py` | EventStore — Event Sourcing 事件追加与回放（DW-0002） | 2026-09-17（17天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/evidence_pack.py` | audit-trail.evidence_pack — MOD-INF-020 · 证据包导出器 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/feedback_self_audit.py` | audit-trail.feedback_self_audit — MOD-INF-020 · 反馈自审计 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/finding_model.py` | （无文档头，按文件名语义：finding_model） | 2026-09-17（17天） | in=8/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/forensic_package.py` | Forensic Package — v0.8.0 取证就绪: escalation event bundle+hash chain+timestamp。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/genesis.py` | audit-trail.genesis — MOD-INF-020 · 创世块管理 | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/glossary_matrix.py` | （无文档头，按文件名语义：glossary_matrix） | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/incremental_review.py` | （无文档头，按文件名语义：incremental_review） | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/integrity_verifier.py` | Integrity Verifier — v0.8.0 代码完整性验证器: hash校验+diff detection+rollback。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/kb_gate.py` | audit-trail.kb_gate — MOD-INF-020 · KB 审计门控 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/models.py` | 治本（裁定#18 G2）：本文件原为桩实现——AuditEventType/FileActionType/ProvenanceDepth/ | 2026-09-17（17天） | in=8/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/observability_dashboard.py` | （无文档头，按文件名语义：observability_dashboard） | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/privacy.py` | audit-trail.privacy — MOD-INF-020 · PII 检测与脱敏 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/provenance_tracker.py` | （无文档头，按文件名语义：provenance_tracker） | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/replay_engine.py` | ── Stage 4 公共化（2026-07-29）：只读 properties ── | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/resource_aware_pool.py` | 5.67.1 修复：添加 maxsize 背压，防止无限制提交导致内存耗尽 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/retention.py` | 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。 | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/sbom_generator.py` | LicenseType 枚举——许可证类型定义（P3 价值审判退役残留）。 | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/spec_auditor.py` | （无文档头，按文件名语义：spec_auditor） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/supply_chain_security.py` | （无文档头，按文件名语义：supply_chain_security） | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/text_to_finding_adapter.py` | （无文档头，按文件名语义：text_to_finding_adapter） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/tiered_storage.py` | （无文档头，按文件名语义：tiered_storage） | 2026-09-05（29天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/tiered_storage_bridge.py` | （无文档头，按文件名语义：tiered_storage_bridge） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/trust_bridge.py` | （无文档头，按文件名语义：trust_bridge） | 2026-09-17（17天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/trust_engine.py` | （无文档头，按文件名语义：trust_engine） | 2026-09-17（17天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/trust_ring_manager.py` | （无文档头，按文件名语义：trust_ring_manager） | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_audit/wqa_scorer.py` | （无文档头，按文件名语义：wqa_scorer） | 2026-09-17（17天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
