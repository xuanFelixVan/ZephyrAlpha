# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-P3 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0063)
# [MODULE] scripts.governance.meta_question.wo_a2legs.probe_unmatched_880_identity
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service (reader)
# [CONSUMERS] build_sector_name_registry.py 未配码处置决策
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读；机械判定：close 序列逐位等值比例 ≥0.99 才算同一标的，禁凭名称直觉。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单码查询失败→记 error 继续，末行汇总。
# [TESTS] 无（一次性取证脚本）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-P3 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""对 TDX 主数据未配的 880 码，用 kline_index close 序列做机械同源判定（取证用）。"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402

# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_SECTOR_880 = TableRegistry().table("market_sector_kline_880")
_T_KLINE_INDEX = TableRegistry().table("market_index_kline")

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。
# 注：_SQL_IDENTITY 以 .format(code=...) 取运行期码，故 {{code}} 须转义（求值文本与改前逐字一致）。
_SQL_IDENTITY = f"""
SELECT b.symbol, b.name, count() AS n,
       countIf(abs(toFloat64(a.close) - toFloat64(b.close)) < 0.05) AS eq
FROM (SELECT trade_date, close FROM {_T_SECTOR_880} FINAL
      WHERE sector_code = '{{code}}' AND period = '1d') AS a
INNER JOIN (SELECT trade_date, symbol, any(name) AS name, any(close) AS close
            FROM {_T_KLINE_INDEX} GROUP BY trade_date, symbol) AS b
  ON a.trade_date = b.trade_date
GROUP BY b.symbol, b.name
HAVING n > 50
ORDER BY eq DESC LIMIT 3
"""
_SQL_TARGET_CODES = (
    f"SELECT DISTINCT sector_code FROM {_T_SECTOR_880} "
    "WHERE sector_code IN ('880001.SH','880002.SH','880003.SH','880004.SH',"
    "'880005.SH','880006.SH','880007.SH','880008.SH','880009.SH','880595.SH')"
)


def main() -> None:
    conn = DatabaseService().get_clickhouse_conn(role="reader")
    targets = [r[0] for r in conn.execute(_SQL_TARGET_CODES)]
    out = {}
    for code in sorted(targets):
        try:
            out[code] = [list(r) for r in conn.execute(_SQL_IDENTITY.format(code=code))]
        except Exception as exc:  # noqa: BLE001 — fail-visible per-code
            out[code] = {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
