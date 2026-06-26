---
module_id: KE-2885
status: active
title: scripts/governance/run_all.py
category: module_blueprint
ttl: permanent
---

# scripts/governance/run_all.py

scripts/governance/run_all.py
def run_all_dimensions(dimensions: list[str] = None) -> dict:
    """运行全维度或指定维度的审计扫描"""
    ...

def run_single_dimension(dimension: str) -> list[Finding]:
    """运行单维度审计扫描"""
    ...
```
