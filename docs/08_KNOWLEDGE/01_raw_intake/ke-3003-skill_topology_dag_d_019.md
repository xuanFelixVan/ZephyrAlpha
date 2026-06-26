---
module_id: KE-2903
status: active
title: Skill Topology DAG (D-019-63)
category: module_blueprint
ttl: permanent
---

# Skill Topology DAG (D-019-63)

Skill Topology DAG (D-019-63)
```yaml
dependency_edges:
  DATA_DEPENDENCY: "Skill A needs Skill B's output"
  ORCHESTRATION_DEPENDENCY: "Skill A triggers Skill B"
  MUTUAL_EXCLUSION: "Skill A and B cannot co-execute"
  SOFT_PREFERENCE: "Skill A prefers Skill B but can work alone"
  COMPOSITION: "Skill A = Skill B + Skill C combined"
bounded_failure: "O(d^h) where d=fanout, h=depth → << O(N)"
```
