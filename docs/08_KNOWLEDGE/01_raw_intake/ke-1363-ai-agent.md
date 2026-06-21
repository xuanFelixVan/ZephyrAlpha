---
module_id: KE-1274
title: 0.2 AI Agent 分派表 —— 你该读蓝图的哪部分
category: module_blueprint
---

# 0.2 AI Agent 分派表 —— 你该读蓝图的哪部分

0.2 AI Agent 分派表 —— 你该读蓝图的哪部分

| 如果你负责开发... | 你该读的 CT-* 合同 | 关联 Schema | 预计 tokens |
|------------------|-------------------|------------|:---:|
| **Orchestrator** (任务系统) | CT-ORC-SCRIPT, CT-ORC-CE, CT-ORC-VMS, CT-ORC-GATE, CT-ORC-DB | TaskCard, Finding | ~1800 |
| **Script System** (脚本系统) | CT-ORC-SCRIPT, CT-SCRIPT-KB, CT-SCRIPT-GATE, CT-FEATUREFLAG | Finding, KE | ~1400 |
| **Knowledge Base** (知识库) | CT-SCRIPT-KB, CT-KB-VMS, CT-DATA-LIFECYCLE | KE | ~1000 |
| **Context Engine** (CE) | CT-ORC-CE, CT-CE-VMS, CT-CE-LSG, CT-BULKHEAD | TaskCard | ~1400 |
| **Gate Engine** (门控引擎) | CT-ORC-GATE, CT-SCRIPT-GATE, CT-FEATUREFLAG | TaskCard | ~900 |
| **Feedback Loop** (FLE) | CT-FLE-ORC, CT-FLE-DB, CT-TELE-FLE, CT-WATCHDOG | — | ~1200 |
| **Pipeline** | CT-PIPE-ORC | TaskCard | ~400 |
| **Vector Memory** (VMS) | CT-ORC-VMS, CT-CE-VMS, CT-KB-VMS, CT-BULKHEAD | — | ~900 |
| **Database** (db) | CT-FLE-DB, CT-ORC-DB, CT-DLQ, CT-BACKUP | — | ~700 |
| **LLM Security** (LSG) | CT-CE-LSG, CT-SECRETS | — | ~500 |
| **System Telemetry** | CT-TELE-FLE, CT-WATCHDOG | — | ~400 |
| 跨系统管控（横向） | CT-HEALTH, CT-CBAC, CT-CDC, CT-CONFIG, CT-FEATUREFLAG, CT-CHAOS, CT-RECONCILE, CT-STARTUP, CT-TEARDOWN, CT-MODEL-REGISTRY, CT-DEPS, CT-KNOWLEDGE-FRESHNESS, CT-HOUSEKEEPING, CT-SESSION-HANDOFF, CT-STABILITY, CT-CANARY, CT-INCIDENT, CT-RACE-CONDITIONS, CT-COST-BUDGET, CT-DISK-GUARD, CT-NETWORK-PARTITION, CT-BENCH, CT-DEPLOY, CT-SCHEMA-MIGRATE, CT-DEGRADE-CASCADE, CT-AUTONOMY, CT-AGENT-QUALITY, CT-PROMPT-VERSION, CT-SESSION-CONFLICT, CT-LEAN, CT-BLUEPRINT-HEALTH, CT-TRANSFER, CT-KE-QUALITY | — | ~1600 |

---
---
