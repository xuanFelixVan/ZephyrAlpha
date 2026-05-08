---
task_id: "TASK-INF-0126"
module_id: "MOD-INF-024"
title: "Tamper-Evident Audit Trail — 追加不可变 SHA-256 Hash Chain + Ed25519 签名 + Immutability Guarantee（§2.27 + D-024-25）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: v0_7_0
blueprint_section: "§2.27"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\tamper_evident_log.py"
  - "D:\\ZephyrAlpha\\data\\audit\\tamper_evident_chain.jsonl"
acceptance_criteria:
  - "AC-01: TamperEvidentLog 使用 SHA-256 哈希链——每个 entry 包含 previous_hash, current_data, sequence_number, timestamp"
  - "AC-02: Append-Only 保证——日志条目写入后不可修改、不可删除、不可乱序"
  - "AC-03: Ed25519 签名——每个 entry 用 Owner Ed25519 私钥签名（验证公钥写在 config/budget_policy.yaml audit_security 段）"
  - "AC-04: Integrity Verification——verify() 方法检查完整哈希链的有效性和签名合法性"
  - "AC-05: verify fail → IMMEDIATE_ALERT + 标记系统为 'integrity_compromised'"
  - "AC-06: Tamper detection——任何对历史条目修改/删除/插入 → verify() abort 返回非法条目 index"
  - "AC-07: 数据存储 data/audit/tamper_evident_chain.jsonl——与现有 audit trail (MOD-INF-020) 互补"
  - "AC-08: 性能——每条 log entry append 延迟 < 50ms，verification 全部条目 < 5s per 10K entries"
  - "AC-09: recovery——如果链损坏，提供 last_valid_index → 可以从该 point 开始 rewrite chain"
  - "AC-10: 零 LLM dependency——纯加密学操作，在 8GB 消费者级机器运行无障碍"
rollback_instructions: "删除 tamper_evident_log.py + data/audit/tamper_evident_chain.jsonl。系统退化为无加密学完整性保护——trust MOD-INF-020 写入不可逆"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1251-L1282 (§2.27 Tamper-Evident)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [tamper-evident, hash-chain, sha-256, ed25519, audit-integrity, v0.7.0]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0126: Tamper-Evident Audit Trail

## 1. 任务目标

实现加密学防篡改审计日志——确保 Budget Enforcer 的所有金融事件（锁定、熔断、超支、签名交易）不可被 Agent 或恶意进程篡改。SHA-256 哈希链 + Ed25519 签名，append-only 不可变。

## 2. 背景

蓝图 §2.27（决策 D-024-25，v0.7.0 新增）：区块链最小可行版本——只需哈希链表 + 签名。防止 Agent 调用系统导致金融隧道（financial tunneling）。

## 3. 实施步骤

```python
import hashlib, json, time
from cryptography.hazmat.primitives.asymmetric import ed25519

class TamperEvidentLog:
    def __init__(self, output_path: str, signing_key: ed25519.Ed25519PrivateKey):
        self.path = output_path
        self.key = signing_key
        self._entries: list[dict] = []
        self._load_existing()

    def append(self, data: dict) -> int:
        seq = len(self._entries)
        prev_hash = self._entries[-1]["hash"] if self._entries else "GENESIS"
        entry = {
            "seq": seq, "timestamp": time.time(),
            "previous_hash": prev_hash, "data": data,
        }
        entry["hash"] = self._hash_entry(entry)
        entry["signature"] = self._sign(entry["hash"])
        self._entries.append(entry)
        self._write_to_disk(entry)
        return seq

    def verify(self) -> tuple[bool, int | None]:
        for i, entry in enumerate(self._entries):
            expected_hash = self._hash_entry({k: entry[k] for k in ["seq","timestamp","previous_hash","data"]})
            if entry["hash"] != expected_hash:
                return False, i
            if i > 0 and entry["previous_hash"] != self._entries[i-1]["hash"]:
                return False, i
            if not self._verify_signature(entry["hash"], entry["signature"]):
                return False, i
        return True, None

    def _hash_entry(self, entry: dict) -> str:
        content = json.dumps(entry, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/tamper_evident_log.py` | 新建 |
