---
task_id: "TASK-INF-0221"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.16 信任锚初始化——Bootstrap Trust Problem（决策 D-020-44）"

title: "实现 Genesis 初始化仪式——信任锚创建流程 + genesis_manifest.txt + 外部见证介质"
description: |
  实现审计系统的信任锚初始化流程 `bootstrap_audit.py`（scripts/governance/）：
  1. HMAC Secret 生成——从 CSPRNG(os.urandom(32)) 读取 256-bit → 写入环境变量
  2. Genesis Entry 创建——prev_entry_hash='genesis', entry_hash=SHA256, hmac=HMAC
  3. Agent 密钥生成——Owner Agent 的 Ed25519 密钥对 + DID 注册 + 公钥入 genesis 条目
  4. Genesis Manifest——含 genesis entry_hash + Ed25519 公钥 SHA → 写入外部介质
  5. External Witness——genesis_manifest.txt 写入外部独立介质（USB/纸质QR/云存储）
  规则：genesis 创建者 ≠ 日常操作者——初始化脚本由 Owner 手动执行（非 AI）。
  落地决策 D-020-44。覆盖风险 R34。覆盖盲点 B77 + B87 + B92。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\agent_signer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\bootstrap_audit.py"
    description: "Genesis 初始化仪式脚本——<200 行 Python"
  - path: "D:\\ZephyrAlpha\\data\\audit\\genesis_manifest.txt"
    description: "Genesis 清单——entry_hash + Ed25519 公钥 SHA"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\bootstrap_audit.py"
  - "D:\\ZephyrAlpha\\data\\audit\\genesis_manifest.txt"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\**\\*.py"
  - "D:\\ZephyrAlpha\\.env"

applicable_rules:
  - module_id: "GOV-SEC-001"
    section: "全篇"
    reason: "密钥初始化安全策略"
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "初始化仪式需记录为审计事件"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.16——Bootstrap Trust 设计 + D-020-44 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 40

acceptance_criteria:
  - "bootstrap_audit.py < 200 行 Python——任何人可手动审计"
  - "HMAC secret 32字节——从 os.urandom(32) 生成，不硬编码"
  - "Genesis entry 写入 data/audit/hot/genesis-{date}.jsonl"
  - "genesis_manifest.txt 含 genesis entry_hash + 公钥 SHA-256"
  - "初期化脚本零依赖 audit_trail/ 模块——uses stdlib only"
  - "Genesis 创建后外部 verifier 可验证 entry_hash 自我一致性"

rollback_instructions: |
  1. 删除 bootstrap_audit.py
  2. 删除 data/audit/genesis_manifest.txt
  3. 删除生成的 genesis JSONL 文件
  4. 重新生成 HMAC secret（旧 secret 即刻废止）

depends_on:
  - "TASK-INF-0207"
  - "TASK-INF-0209"
blocked_by: []

status: "created"

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
