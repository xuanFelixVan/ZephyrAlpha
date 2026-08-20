# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_parts_monitor
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS] CLI/巡检脚本；config/alert_rules.yaml ALERT-CH-001
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读探测（system.parts）；查询失败返回空违规列表+warning（宁漏报不误报阻断）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 查询异常→log.warning+返回 []；TSV 解析容错（坏行跳过）
# [TESTS] tests/zephyr/data/test_ch_parts_monitor.py
# [A_module] module_id=MOD-L00-004-PM | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: system.parts TSV
#   fields: database\ttable\tparts（active=1 GROUP BY 表）
# 层: 算法
# - id: A1
#   name_zh: parts 阈值判定
#   name_en: check_parts_threshold
#   intro: 逐表比较 active parts 计数与阈值（默认 100），超阈记入违规清单
# 层: 输出
# - id: O1
#   name_zh: 违规清单
#   name_en: [{database, table, parts}]
#   intro: 供告警链路（ALERT-CH-001）/CLI 巡检消费；空列表=健康
"""CH data parts 爆炸监控（64号 Q8，P1，2026-08-20 AI-NIGHT-001 施工）。

裁定真源：64号 §16.2 Q8——system.parts 单表 active parts > 100 告警，
防 2026-07-09 parts 爆炸致 CH merge 满载崩溃事故重演。
配套告警规则：config/alert_rules.yaml ALERT-CH-001（Grafana 面板/alerter 通知由遥测链路消费）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable

log = logging.getLogger(__name__)

DEFAULT_PARTS_THRESHOLD = 100

# NO-BARE-SQL gate 豁免：_SQL_* 前缀常量（同 scheduler._SQL_FIND_PART 既有约定）
_SQL_ACTIVE_PARTS = (
    "SELECT database, table, count() AS parts FROM system.parts WHERE active = 1 GROUP BY database, table"
)


def _default_query(sql: str, timeout: int) -> str:
    """默认查询通道（ch_reader 统一入口，TSV 输出；失败返回空串）。"""
    from zephyr.data import ch_reader

    return ch_reader.query(sql, timeout=timeout)


def parse_parts_tsv(tsv: str) -> list[tuple[str, str, int]]:
    """解析 system.parts 查询 TSV 为 (database, table, parts) 列表（坏行容错跳过）。"""
    rows: list[tuple[str, str, int]] = []
    for line in (tsv or "").splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        try:
            rows.append((fields[0], fields[1], int(fields[2])))
        except ValueError:
            log.warning("parts TSV 坏行跳过: %s", line[:120])
    return rows


def check_parts_threshold(
    threshold: int = DEFAULT_PARTS_THRESHOLD,
    *,
    query_fn: Callable[[str, int], str] | None = None,
    timeout: int = 15,
) -> list[dict]:
    """探测单表 active parts 超阈值违规清单。

    Args:
        threshold: parts 告警阈值（默认 100，64号 Q8 裁定）。
        query_fn: 查询函数注入点（测试用）；None 走 ch_reader。
        timeout: CH 查询超时秒数。

    Returns:
        违规列表 [{"database", "table", "parts"}]，按 parts 降序；空列表=健康或查询失败。
    """
    q = query_fn or _default_query
    try:
        tsv = q(_SQL_ACTIVE_PARTS, timeout)
    except Exception as e:  # noqa: BLE001 — 探测失败宁漏报不阻断
        log.warning("system.parts 查询异常: %s", e)
        return []
    violations = [
        {"database": db, "table": tbl, "parts": parts} for db, tbl, parts in parse_parts_tsv(tsv) if parts > threshold
    ]
    violations.sort(key=lambda v: v["parts"], reverse=True)
    return violations


def main() -> int:
    """CLI 巡检入口：打印违规表，存在违规返回退出码 1（供巡检/看板脚本消费）。"""
    violations = check_parts_threshold()
    if not violations:
        print(f"OK: 无表 active parts 超阈值（{DEFAULT_PARTS_THRESHOLD}）")
        return 0
    print(f"ALERT: {len(violations)} 张表 active parts 超阈值（{DEFAULT_PARTS_THRESHOLD}）:")
    for v in violations:
        print(f"  {v['database']}.{v['table']}: {v['parts']} parts")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
