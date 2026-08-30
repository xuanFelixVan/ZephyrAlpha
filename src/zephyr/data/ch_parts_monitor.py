# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_parts_monitor
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.shared.alerts.threshold_loader; docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml (SSoT，fail-closed 加载)
# [CONSUMERS] CLI/巡检脚本；config/alert_rules.yaml ALERT-CH-001
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读探测（system.parts）；查询失败返回空违规列表+warning（宁漏报不误报阻断）；阈值唯一真源=alert_threshold_registry.yaml THD-HEALTH-005（fail-closed，禁码内第二真源）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 查询异常→log.warning+返回 []；TSV 解析容错（坏行跳过）；注册表缺失/畸形→AlertThresholdConfigError(ZA-SH-0052)；告警发送异常→log.warning 吞掉不阻断
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
阈值真源：alert_threshold_registry.yaml THD-HEALTH-005（fail-closed 统读，2026-08-28 由硬编码改统读）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Final

from zephyr.data.alerter import LEVEL_CRITICAL, Alerter
from zephyr.shared.alerts.threshold_loader import load_alert_thresholds

log = logging.getLogger(__name__)


def _load_parts_threshold(registry_path: Path | None = None) -> int:
    """从告警阈值注册表加载 parts 告警阈值（fail-closed；registry_path 为测试逃生门）。

    64号 §16.2 Q8 统读：THD-HEALTH-005（裁定值 100）。
    """
    return load_alert_thresholds(
        {"THD-HEALTH-005": "parts_threshold"},
        registry_path=registry_path,
        cast="int",
    )["parts_threshold"]


#: import 期 fail-closed 加载（注册表缺失/畸形 → import 即 raise，禁止码内第二真源兜底）
DEFAULT_PARTS_THRESHOLD: Final[int] = _load_parts_threshold()

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


def check_and_alert(
    alerter: Alerter,
    threshold: int = DEFAULT_PARTS_THRESHOLD,
    *,
    query_fn: Callable[[str, int], str] | None = None,
    timeout: int = 15,
) -> list[dict]:
    """探测 parts 超阈值并经既有 Alerter 通道产出告警（64号 §16.2 Q8「alerter 通知」落地）。

    关键路径接线：scheduler._run_schedule_dag 时段写库收尾调用——INSERT 是 parts
    的产生点，时段批次完成是最近的有效探测点。告警行为对齐 ALERT-CH-001
    （severity=critical）：有违规 → Alerter.notify(LEVEL_CRITICAL)，触达飞书
    webhook + SMTP 邮件 + 失败汇总落盘（Alerter 内置 300s 冷却防刷屏，通道未配置
    静默跳过）；无违规或查询失败（宁漏报）→ 不告警。

    Args:
        alerter: 既有告警器（scheduler 复用实例，不另造通道）。
        threshold: parts 告警阈值（默认 100，64号 Q8 裁定）。
        query_fn: 查询函数注入点（测试用）；None 走 ch_reader。
        timeout: CH 查询超时秒数。

    Returns:
        违规清单（同 check_parts_threshold；空列表=健康或查询失败，未告警）。
    """
    violations = check_parts_threshold(threshold, query_fn=query_fn, timeout=timeout)
    if not violations:
        return violations
    top = violations[0]
    try:
        alerter.notify(
            task_id="ch_data_parts_explosion",
            error=(
                f"{len(violations)} 张表 active data parts 超阈值 {threshold}"
                f"（最高 {top['database']}.{top['table']}={top['parts']}），"
                "防 parts 爆炸致 CH merge 满载崩溃（2026-07-09 事故教训），"
                "请检查写入攒批（BufferedWriter）与表引擎配置"
            ),
            level=LEVEL_CRITICAL,
            source="clickhouse",
            extra={"threshold": threshold, "violations": violations},
        )
    except Exception as e:  # noqa: BLE001 — 告警发送异常吞掉，不影响调度主流程
        log.warning("parts 告警发送异常: %s", e)
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
