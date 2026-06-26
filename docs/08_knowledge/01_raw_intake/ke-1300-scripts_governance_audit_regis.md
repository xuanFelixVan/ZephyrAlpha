---
module_id: KE-1213
status: active
title: 孤儿检测：`scripts/governance/audit_registration.py`
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 孤儿检测：`scripts/governance/audit_registration.py`

孤儿检测：`scripts/governance/audit_registration.py`

定期（每次 session 结束时或 Pipeline Gate 运行时）运行审计扫描：
```
python scripts/governance/audit_registration.py           # 报告孤儿
python scripts/governance/audit_registration.py --json    # JSON 输出（AI 消费）
python scripts/governance/audit_registration.py --fix     # 交互式修复
```
返回码 `0` = CLEAN，`1` = 有孤儿。
