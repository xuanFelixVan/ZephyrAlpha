---
module_id: KE-1877
status: active
title: 2.3 skill_loader.py 加载器骨架
category: module_blueprint
---

# 2.3 skill_loader.py 加载器骨架

2.3 skill_loader.py 加载器骨架

```python
class SkillLoader:
    def load_l0(self) -> dict: ...
    def load_l1_metadata(self, skill_id: str) -> dict: ...
    def load_l2_body(self, skill_id: str) -> str: ...
    def load_l3_references(self, skill_id: str, ref_name: str) -> str: ...
    def progressive_load(self, skill_id: str, level: ProgressiveLevel) -> dict: ...
```
