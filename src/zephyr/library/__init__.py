# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md
# [MODULE] zephyr.library
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""zephyr.library — 终极图书馆总账域（MOD-LIB-001）。

总账=全项目资产户籍（assets/events），PG 资产总线承载；馆员唯一写路径。
分包：schema（DDL 纯常量）/ registry（馆员 Librarian）/ lookup（查询 API+CLI）/
collectors（五采集器）。真源：docs/_working/ultimate_library/08_field_dictionary_v0_1.md。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/library_init.yaml
"""

from zephyr.library.librarian import Librarian, validate_action

__all__ = ["Librarian", "validate_action"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）
