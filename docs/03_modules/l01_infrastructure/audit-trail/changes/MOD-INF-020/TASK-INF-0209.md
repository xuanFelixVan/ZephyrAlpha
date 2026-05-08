---
task_id: "TASK-INF-0209"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.2 JSONL SSoT + 密码学完整性（决策 D-020-02 + D-020-04）"

title: "实现不可变写入器——JSONL append-only + 哈希链生成 + HMAC 签名 + Lamport 递增 + 异步 SQLite 索引触发"
description: |
  实现 `src/zephyr/audit_trail/writer.py` 中的 `AuditWriter` 不可变写入器：
  - append_only JSONL 写入（file lock fcntl/msvcrt 防并发）
  - 哈希链：每条写入前读取上一条 SHA-256 → prev_entry_hash
  - entry_hash 计算：SHA-256(canonical JSON without entry_hash/hmac/agent_signature)
  - HMAC 签名：HMAC-SHA256(canonical_json, ZEPHYR_AUDIT_HMAC_SECRET)
  - Agent 签名调用 AgentSigner.sign(entry_hash)
  - Lamport 时钟 tick()
  - 写入后异步触发 SQLite 索引重建（5s 延迟）
  - 轮转：按日轮转 audit-trail-{YYYY-MM-DD}.jsonl
  - Git 隔离：写入 data/audit/ 目录（.gitignore）
  落地决策 D-020-02 + D-020-04 + D-020-27。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\writer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\agent_signer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\writer.py"
    description: "完整实现 AuditWriter——JSONL+哈希链+HMAC+Ed25519+Lamport+轮转+异步索引"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_writer.py"
    description: "单元测试——1000条连续写入/哈希链连续性/HMAC验证/并发写入冲突/轮转正确性"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\writer.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_writer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\data\\**\\*"
  - "D:\\ZephyrAlpha\\.gitignore"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——AuditEntryV1 作为输入"
  - module_id: "GOV-CMP-002"
    section: "AUD-001~004"
    reason: "审计操作留痕规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.2——JSONL SSoT 写入流程 + D-020-02/04/27 决策"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\agent_signer.py"
    reason: "AgentSigner.sign() 调用接口"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 75

acceptance_criteria:
  - "AuditWriter.append(entry) → 追加一行到 JSONL + 返回完整 AuditEntryV1（含所有签名字段）"
  - "1000 条连续写入后哈希链无断裂——prev_entry_hash 首尾一致"
  - "HMAC 签名可与外部 verifier 验签一致"
  - "Agent 签名：Ed25519 verify(entry_hash, agent_signature, pubkey) = True"
  - "写入延迟 P99 < 5ms（不含异步索引触发）"
  - "并发写入：两个进程同时写 → 无 JSONL 行损坏"
  - "按日轮转：日期变化后新条目写入新 JSONL 文件"
  - "写入 data/audit/ 目录——不对 git 工作区产生 dirty 状态"

rollback_instructions: |
  1. 删除 writer.py 实现内容
  2. 删除 test_writer.py
  3. 清理测试期间写入的 data/audit/test-*.jsonl 文件

depends_on:
  - "TASK-INF-0204"
  - "TASK-INF-0205"
  - "TASK-INF-0206"
  - "TASK-INF-0207"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "data"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
