# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-PROBE | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单
# [MODULE] scripts.governance.meta_question.wo_a2legs._probe
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service (reader 只读探针)
# [CONSUMERS] WO-A2LEGS 案卷取证（docs/_working/meta_question_answers/build/WO-A2LEGS.yaml）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读：仅走 DatabaseService role='reader'，零写通道；输出 JSON 到 stdout；
#              任何结论以本探针实跑数字为准，禁凭登记册文本推断。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常直接抛出（fail-visible），不做静默吞异常。
# [TESTS] 无（一次性取证辅助，同族 scripts/ch/backfill_* 探针先例）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-PROBE | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WO-A2LEGS 通用 CH 只读探针：python .../_probe.py "<SQL>" → JSON 行。"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402


def run(sql: str) -> list:
    conn = DatabaseService().get_clickhouse_conn(role="reader")
    return [list(r) for r in conn.execute(sql)]


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), ensure_ascii=False, default=str))
