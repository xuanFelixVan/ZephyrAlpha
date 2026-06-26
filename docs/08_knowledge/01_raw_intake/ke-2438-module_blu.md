---
module_id: KE-2343
status: active
title: 6. 门禁植入
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6. 门禁植入

6. 门禁植入

```
AI施工 → changed_files_check → [CodeEconomyAnalyzer.score()文件评分]
     → [ModuleBirthRegistry 若新增文件未注册 → reject]
     → [CoreIntegrityGuard 若IMMUTABLE_CORE清单文件被修改 → BLOCK]
     → contract_check → [contract_tester.py 所有ContractBus合约测试]
     → preset_pass → [代码风格检查]
     → regression_test → [全PASS才合入]
```
