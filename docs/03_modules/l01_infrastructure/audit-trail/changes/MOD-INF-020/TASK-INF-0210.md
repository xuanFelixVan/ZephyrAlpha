---
task_id: "TASK-INF-0210"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.2 哈希链/HMAC/Merkle 完整性 + §4.1 verify_integrity()"

title: "实现密码学完整性验证器——哈希链连续性/HMAC批量验证/Ed25519签名验证/Merkle树重建"
description: |
  实现 `src/zephyr/audit_trail/integrity.py` 中的 `IntegrityVerifier`：
  - `check_hash_chain()`: 从 genesis 遍历到末尾，验证每条的 prev_entry_hash == SHA-256(前一条)
  - `verify_hmac_batch()`: 批量 HMAC-SHA256(entry_without_sig, secret) 验证
  - `verify_ed25519_signatures()`: 随机抽样 10% Ed25519 签名验证
  - `rebuild_merkle_root()`: 重建 Merkle 树根哈希 → 对比存储的 .merkle 文件
  - `fast_check()`: 仅验证最后一小时条目 + Merkle root（< 100ms）
  - `full_check()`: 全量逐条验证（周检）
  - 输出完整 IntegrityReport。
  落地决策 D-020-04 + D-020-05。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\integrity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\integrity.py"
    description: "完整实现 IntegrityVerifier——哈希链+HMAC+Ed25519+Merkle+fast/full mode"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integrity.py"
    description: "单元测试——篡改检测/断裂点精确定位/HMAC伪造检测/签名验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\integrity.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integrity.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.jsonl"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "审计操作留痕——完整性校验自身也需记录"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.2——密码学完整性设计 + D-020-04/05"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 60

acceptance_criteria:
  - "check_hash_chain() 检测到中间条目删除→返回断裂行号"
  - "verify_hmac_batch() 检测到伪造条目→返回失败行号列表"
  - "verify_ed25519_signatures() 随机抽样10%→全部通过"
  - "rebuild_merkle_root() 计算结果与 .merkle 文件一致"
  - "fast_check() 延迟 < 100ms（10000 条数据量）"
  - "full_check() 10000 条 < 5s"
  - "完整性失败→自动触发 integrity_failure 事件写入"

rollback_instructions: |
  1. 删除 integrity.py 内容
  2. 删除 test_integrity.py

depends_on:
  - "TASK-INF-0204"
  - "TASK-INF-0205"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
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
