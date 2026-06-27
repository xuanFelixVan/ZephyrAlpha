# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/import_linter/__init__.py | §
# [TTL] task_bound
"""Architecture Import Linter — 层依赖方向强制执行

对标 Python import-linter，检查跨层 import 路径是否违反依赖方向约束。
INV-008: 低层不得 import 高层（L00 不得 import L04+），依赖只能向上。
"""

__all__ = ["layer_boundary_check"]
