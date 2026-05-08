---
task_id: "TASK-INF-0207"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.8 Agent 级数字签名（决策 D-020-14）"

title: "实现 AgentSigner + DIDRegistry——Ed25519 Agent 级签名与 DID 管理"
description: |
  实现 `src/zephyr/audit_trail/agent_signer.py` 中的 Agent 级 Ed25519 签名器：
  - `AgentSigner`: __init__(agent_did, private_key_pem) → sign(entry_hash) 返回 base64 签名 → verify(entry_hash, signature, public_key_pem) 静态方法离线验证
  - `DIDRegistry`: register(did, public_key_pem, agent_metadata) / resolve(did) → 公钥PEM / revoke(did, reason)
  DID 格式：did:zephyr:{sha256(Ed25519_public_key)[:16]}
  Phase scaffold 阶段——基础签名+验证+DID 注册，不含密钥旋转/分布式密钥管理。
  落地决策 D-020-14。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\agent_signer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\agent_signer.py"
    description: "完整实现 AgentSigner + DIDRegistry 类"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_agent_signer.py"
    description: "单元测试——密钥生成/签名/验证/篡改检测/DID 注册与解析"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\agent_signer.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_agent_signer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0022"
    section: "§3.2"
    reason: "B 轨平台能力——audit_trail/ 独立包"
  - module_id: "GOV-SEC-001"
    section: "全篇"
    reason: "密钥管理安全策略"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.8——AgentSigner + DIDRegistry 类定义 + D-020-14 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 50

acceptance_criteria:
  - "AgentSigner.sign(entry_hash) → base64 字符串"
  - "AgentSigner.verify(entry_hash, signature, public_key_pem) → bool"
  - "正确签名 → verify=True / 篡改→verify=False / 错误公钥→verify=False"
  - "DIDRegistry.register(did, pubkey, metadata) → 成功"
  - "DIDRegistry.resolve(did) → 公钥 PEM"
  - "DIDRegistry.revoke(did, reason) → 不再可解析 / resolve 返回 None"
  - "DID 格式匹配 did:zephyr:{sha256[:16]}"
  - "99% 签名+验证延迟 < 10ms"

rollback_instructions: |
  1. 删除 agent_signer.py 内容
  2. 删除 test_agent_signer.py
  3. 清理 __init__.py 中对 AgentSigner/DIDRegistry 的引用

depends_on:
  - "TASK-INF-0200"
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
