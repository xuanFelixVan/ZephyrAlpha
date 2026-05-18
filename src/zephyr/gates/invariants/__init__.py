# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §
from __future__ import annotations

"""ZephyrAlpha — Architectural Invariant Gates (EN-001 ~ EN-003)

P0 结构不变量门禁（非 task-based，与 G0-G7 互补）：
  - EN-001: 循环依赖扫描器（topological sort on layer import graph）
  - EN-002: 强制模式 validator（contract enforcement 声明校验）
  - EN-003: 契约兼容性检查器（dataclass field ↔ contract spec diff）
"""

__all__ = ['en_001_circular_dependency', 'en_002_enforcement_validator', 'en_003_contract_compatibility', 'en_process_lifecycle_gateway', 'zero_residue_check']