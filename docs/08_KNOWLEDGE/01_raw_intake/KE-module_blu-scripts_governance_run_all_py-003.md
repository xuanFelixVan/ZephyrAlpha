---
module_id: KE-module_blu-scripts_governance_run_all_py-003
title: scripts/governance/run_all.py
category: module_blueprint
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
