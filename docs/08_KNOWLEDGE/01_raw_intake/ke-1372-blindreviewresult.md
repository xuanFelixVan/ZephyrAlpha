---
module_id: KE-1283
status: active
title: 1. BlindReviewResult
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1. BlindReviewResult

1. BlindReviewResult

```python
class BlindReviewResult(BaseModel):
    generator_output: ModuleResult   # M3生成结果
    reviewer_output: ModuleResult    # M7审查结果
    consensus: bool                  # True=一致通过, False=存在分歧
    disagreement_points: list[str]   # 分歧点摘要
    consensus_details: dict          # 共识详情
```
