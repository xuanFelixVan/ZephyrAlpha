---
module_id: KE-4116
title: 4.5 触发条件汇总
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.5 触发条件汇总

4.5 触发条件汇总

| 触发 | 确定性 | 机械验证点 | Severity | 下一步 |
|------|:---:|-----------|:---:|------|
| A: 文件失联 | 100% | `Path.exists()` | RED | → Stage 6（LLM 生成修复文本） |
| B: 系统超越 | 100% | 数值比较 `M > N` | YELLOW | → 报告，需人工裁决"改规则 or 裁冗余" |
| C: 结构缺失 | ~97% | ID ∈ Registry? | RED | → Stage 6（LLM 生成修复文本） |

---
