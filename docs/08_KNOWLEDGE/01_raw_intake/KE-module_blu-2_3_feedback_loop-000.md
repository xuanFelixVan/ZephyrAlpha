---
module_id: KE-module_blu-2_3_feedback_loop-000
title: 2.3 Feedback Loop 集成
category: module_blueprint
---

# 2.3 Feedback Loop 集成

2.3 Feedback Loop 集成

```python
class SkillFeedbackLoop:
    def predict(skill_id: str) -> float: ...
    def detect(skill_id: str) -> GateResult: ...
    def diagnose(skill_id: str) -> RootCauseAnalysis: ...
    def act(skill_id: str) -> AutoFixSuggestion: ...
    def verify(skill_id: str, fix: AutoFixSuggestion) -> bool: ...
```
