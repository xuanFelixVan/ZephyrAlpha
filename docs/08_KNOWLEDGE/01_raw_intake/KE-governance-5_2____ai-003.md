---
module_id: KE-governance-5_2____ai-003
title: 5.2 三层 AI 员工口子清单
category: governance
---

# 5.2 三层 AI 员工口子清单

5.2 三层 AI 员工口子清单

| 层 | 口子 | 物理位置（未来）|
|---|---|---|
| **Policy** | AI 员工花名册 | `docs/01_policies_and_standards/ai-operators-registry.md`（Stage K 待建） |
| **Policy** | AI 行为规则 | `docs/01_policies_and_standards/ai-operator-guidelines.md`（Stage K 待建） |
| **Policy** | AI 决策记录模板 | KB:decisions namespace（Session Log decisions 结构化字段） |
| **Policy** | AISG 红线过滤 | `.cursorignore` + `.cursorrules`（OQ-081 硬闸门）|
| **Policy** | AISG 策略文档 | `docs/01_policies_and_standards/ai-security-gateway-policy.md`（Stage K 待建） |
| **Policy** | Scout 抓取白名单 | `docs/01_policies_and_standards/scout-agent-whitelist.md`（Stage K 待建） |
| **Factory** | AI Operator 命名空间 | `src/zephyr/{l00-l14}/_ai_operator/` · `vib/_ai_operator/` · `b01/_ai_operator/` |
| **Factory** | AI Operator 接口协议 | `shared/contracts/ai_operator_contract.py` |
| **Factory** | AISG 脱敏编译器 | `scripts/governance/aisg/compile_desensitize_rules.py` |
| **Factory** | Scout scraper 编译器 | `scripts/governance/scout/compile_scraper.py` |
| **Runtime** | AI 决策日志 schema + ledger | `scripts/audit_log/ai_decision_schema.py` + `ai_decision_ledger.jsonl`（OQ-063 28 字段）|
| **Runtime** | AI 行为审计（VIB-14）| `scripts/audit_log/vib14_ai_behavior_audit.py` |
| **Runtime** | AISG 六大模块 | `src/zephyr/l10_compliance/ai_security/`（D-01 P0 红线）|
| **Runtime** | Scout Agent 运行态 | `src/zephyr/l11_ml_platform/scout/` + `kms/daily_digest/` |
| **Runtime** | 四大引擎 K2 占位 | `l08/decision_engine/` · `l05/capital_allocation/` · `l10/failure_learning/` · `l09/market_regime/` |
