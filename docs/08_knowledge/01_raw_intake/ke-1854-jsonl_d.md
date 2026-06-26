---
module_id: KE-1763-------------------d--003
status: active
title: 2.2 JSONL 为唯一真源 + 密码学完整性（决策 D-020-02 + D-020-04）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 JSONL 为唯一真源 + 密码学完整性（决策 D-020-02 + D-020-04）

2.2 JSONL 为唯一真源 + 密码学完整性（决策 D-020-02 + D-020-04）

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
