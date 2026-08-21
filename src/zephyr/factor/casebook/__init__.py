# [BLUEPRINT] MOD-L02-027 | docs/03_modules/_domain_factor/casebook/blueprint.md | §D-FACTOR-CASE-01
# [MODULE] zephyr.factor.casebook
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] sqlite3(标准库); zephyr.shared.io.paths(REPO_ROOT)
# [CONSUMERS] (暂无；数据期 LLM 挖因子流程为首个计划消费者)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只存统计量不存持仓/金额（宪章 B-011）；verdict ∈ {success,failure,fixed}
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入校验失败->CasebookError(ValueError 子类，fail-closed)
# [TESTS] tests/factor/test_casebook.py
# [A_module] module_id=MOD-L02-027 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-CASE-01 因子研究案例库子包——成功/失败→修复案例的登记与检索入口。

设计依据：2026-08 架构审查报告 §4.2（ALG-03）。导出 record_case/query_similar/get_case
三件套与 CasebookError 校验错误类；实现细节见 casebook.py 模块 docstring。
"""

from __future__ import annotations

from typing import Final

from zephyr.factor.casebook.casebook import (
    VERDICTS,
    CasebookError,
    get_case,
    query_similar,
    record_case,
)

__all__: Final[list[str]] = [
    "VERDICTS",
    "CasebookError",
    "get_case",
    "query_similar",
    "record_case",
]
