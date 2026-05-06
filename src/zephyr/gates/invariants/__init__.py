"""ZephyrAlpha — Architectural Invariant Gates (EN-001 ~ EN-003)

P0 结构不变量门禁（非 task-based，与 G0-G7 互补）：
  - EN-001: 循环依赖扫描器（topological sort on layer import graph）
  - EN-002: 强制模式 validator（contract enforcement 声明校验）
  - EN-003: 契约兼容性检查器（dataclass field ↔ contract spec diff）
"""

from __future__ import annotations
