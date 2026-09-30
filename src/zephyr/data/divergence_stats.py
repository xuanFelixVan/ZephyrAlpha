# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.divergence_stats
# [DOMAIN] D_DATA
# [TTL] permanent
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/zephyr/data/test_divergence_stats.py
# [STABILITY] evolving
# [SAFETY] L
# noqa: m11-perm-manual-legitimate  M11豁免: 本件=zephyr.data.scheduler._run_special_schedule("cross_validation") 槽位输出侧消费链接线（#423 两周观察供数），CLI 独立运行面=运维按需 runner（非 cron/非 daemon/非常驻服务，#ARCH-P3-FOLLOWUP-TODOS-001 裁定 B/C 通道；死袋 q-20260930-st-c9-finalw-0001 死因处置，st-c9-finalw 重投）
# [ERROR_CONTRACT] report 类型不符->DivergenceStatsError 上抛（fail-loud，宿主侧包 try 降级告警）;
#   落盘失败->DivergenceStatsError 上抛（统计缺失必须可见，禁静默丢数）
# [DEPENDENCIES] zephyr.shared.io.file_utils(safe_write_text); zephyr.shared.io.paths;
#   zephyr.shared.utils.time_utils(now_utc); zephyr.data.table_registry(表名真源, 懒加载)
# [CONSUMERS] zephyr.data.scheduler._run_special_schedule("cross_validation") 槽位输出侧
#   （#423 两周分歧率观察供数 2026-09-28）；CLI 独立运行（--stats-path 指定档案时）
# [STARTUP] imported
# [MATURITY] trial
# [INVARIANTS] 分歧率观察=裁定 #423 形态锁第二段：确定性校验先行→分歧率统计→LLM 仅裁决残余，
#   本件只做统计供数，**不判净不改数**;
#   计数语义=当日同窗（date+table+divergence_type）**覆盖式 upsert**：cross_validation 槽每次
#   跑的是同一 14h 回看窗，重跑是重测不是增量——同键覆盖、异键追加，禁 sum（重跑即双计）;
#   行字段=日期(date)/表(table)/分歧类型(divergence_type)/计数(count)，另附 total_symbols 分母
#   供分歧率=count/total_symbols 计算（#423 两周观察的读数面）;
#   分歧类型四值=price_deviation_fail｜volume_deviation_warn｜missing_in_backup｜missing_in_primary，
#   由 ValidationReport **details 逐条精确归并**（优先）；details 空（旧版校验器未填充）时按
#   计数器差值**保守推算**并在 derived=true 如实标注（禁把推算冒充精读）;
#   落盘经 safe_write_text（热文件 CAS 纪律）；stats_path 相对路径锚 REPO_ROOT;
#   测试禁写生产 data/（输出一律 tmp_path——宪法 §9.6），stats_path 参数即测试注入口;
#   当前时间统一 now_utc() 入口（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] none
"""多源分歧率统计器（#423 判净站形态锁第二段供数件）。

诞生背景（裁定 #423：F04 AI 判净站开工，形态锁定=确定性校验先行→分歧率统计→LLM 仅裁决
残余语义冲突）：CrossSourceValidator 自 2026-09-27 接入 cross_validation 槽（23:15）后只落
c1_market.cross_validation_log 逐条日志+告警，**无聚合分歧率读数**——#423 的两周观察期需要
"日期/表/分歧类型/计数"四字段的供数档，本件补该输出侧。

落档=data/divergence_stats/divergence_stats.jsonl（jsonl，一行一个 date×table×type 计数）；
同键覆盖语义（见 INVARIANTS——重测非增量）；分母 total_symbols 随行落档供分歧率计算。

诚实边界：本件是**统计器**不是判净器——分歧是否构成"语义冲突需 LLM 裁决"由
purity_adjudicator 的输入契约另行筛（残余集），本件不做任何判定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ValidationReport（cross_source_validator.validate 产物）
# - id: I2
#   name: stats_path 档案路径（默认 data/divergence_stats/divergence_stats.jsonl）
# 层: 处理
# - id: P1
#   name: report_to_rows（details 逐条归并四类分歧计数；details 空则计数器差值保守推算+derived 标注）
# - id: P2
#   name: upsert 行归并（同 date+table+type 覆盖、异键追加，读旧档全量重写）
# 层: 输出
# - id: O1
#   name: jsonl 档案（safe_write_text 原子落盘；分母 total_symbols 随行）
# 边:
# I1 -> P1 -> P2 -> O1
# I2 -> P2
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "DivergenceStatsError",
    "DIVERGENCE_TYPES",
    "report_to_rows",
    "record_report_stats",
    "main",
]

_STATS_DIR: Final = REPO_ROOT / "data" / "divergence_stats"
_STATS_FILENAME: Final = "divergence_stats.jsonl"

#: 分歧类型四值（机读词表；新增类型须先扩词表再让代码读，禁自由字符串稀释观察口径）
T_PRICE_FAIL: Final = "price_deviation_fail"
T_VOLUME_WARN: Final = "volume_deviation_warn"
T_MISSING_BACKUP: Final = "missing_in_backup"
T_MISSING_PRIMARY: Final = "missing_in_primary"
DIVERGENCE_TYPES: Final = frozenset({T_PRICE_FAIL, T_VOLUME_WARN, T_MISSING_BACKUP, T_MISSING_PRIMARY})

#: 档案 schema 版本（字段面变更时 +1，消费方按版本分派）
_SCHEMA_VERSION: Final = 1


class DivergenceStatsError(Exception):
    """统计入参非法或落盘失败（fail-loud；宿主 cross_validation 槽侧包 try 降级告警）。"""


def _default_stats_path() -> Path:
    return _STATS_DIR / _STATS_FILENAME


def report_to_rows(report: Any, *, ref_date: date | None = None, table: str | None = None) -> list[dict[str, Any]]:  # noqa: any-abuse  any-abuse豁免: ValidationReport动态投影入参，签名无法具体化
    """ValidationReport → 统计行（一行一个 date×table×type）。

    优先从 report.details 逐条精确归并（status==fail 的 price / status==warn 的 volume +
    两个 missing 计数器）；details 为空（旧版校验器未填充 details）时按计数器差值保守推算
    （failures/missing_in_primary 与 warnings/missing_in_backup 差值），derived=true 如实标注。
    """
    if not hasattr(report, "total_symbols"):
        raise DivergenceStatsError("入参非 ValidationReport 形态（缺 total_symbols 字段）")
    ref = ref_date or now_utc().astimezone().date()
    tbl = table or _resolve_tick_table()
    base: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "date": ref.isoformat(),
        "table": tbl,
        "total_symbols": int(report.total_symbols),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
    }
    counts: dict[str, int] = {t: 0 for t in sorted(DIVERGENCE_TYPES)}
    details = list(getattr(report, "details", []) or [])
    if details:
        for item in details:
            if not isinstance(item, dict):
                continue
            metric = str(item.get("metric", ""))
            status = str(item.get("status", ""))
            if metric == "price" and status == "fail":
                counts[T_PRICE_FAIL] += 1
            elif metric == "volume" and status == "warn":
                counts[T_VOLUME_WARN] += 1
        derived = False
    else:
        # 旧版校验器 details 未填充：计数器差值保守推算（failures 含 missing_in_primary、
        # warnings 含 missing_in_backup 与 volume warn——下限保护，不冒充精读）
        counts[T_PRICE_FAIL] = max(int(report.failures) - int(report.missing_in_primary), 0)
        counts[T_VOLUME_WARN] = max(int(report.warnings) - int(report.missing_in_backup), 0)
        derived = True
    counts[T_MISSING_BACKUP] = int(report.missing_in_backup)
    counts[T_MISSING_PRIMARY] = int(report.missing_in_primary)
    return [{**base, "divergence_type": dtype, "count": count, "derived": derived} for dtype, count in counts.items()]


def _resolve_tick_table() -> str:
    """表名真源=table_registry（#ARCH-CH-024，禁硬编码表名）。"""
    from zephyr.data.table_registry import get_registry

    return str(get_registry().table("market_tick"))


def _load_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            log.warning("分歧统计档案存在坏行，跳过（不中断 upsert）: %.120s", line)
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row.get("date", "")), str(row.get("table", "")), str(row.get("divergence_type", "")))


def record_report_stats(
    report: Any,  # noqa: any-abuse  any-abuse豁免: ValidationReport动态投影入参，签名无法具体化
    *,
    stats_path: str | Path | None = None,
    ref_date: date | None = None,
    table: str | None = None,
) -> dict[str, Any]:
    """统计并 upsert 落档，返回 {stats_path, rows_written, upserted, appended}。

    同（date,table,divergence_type）键=覆盖（重测非增量）；异键=追加。全量重写经
    safe_write_text 原子落盘。
    """
    new_rows = report_to_rows(report, ref_date=ref_date, table=table)
    path = Path(stats_path) if stats_path else _default_stats_path()
    if not path.is_absolute():
        path = REPO_ROOT / path
    existing = _load_existing(path)
    existing_keys = {_key(row) for row in existing}
    merged: list[dict[str, Any]] = []
    replaced = 0
    for row in existing:
        if _key(row) in {_key(n) for n in new_rows}:
            continue  # 旧读数让位（覆盖式 upsert）
        merged.append(row)
    upserted = 0
    for row in new_rows:
        if _key(row) in existing_keys:
            replaced += 1
        else:
            upserted += 1
        merged.append(row)
    payload = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True, default=str) for r in merged)
    if payload:
        payload += "\n"
    try:
        safe_write_text(path, payload)
    except OSError as ex:
        raise DivergenceStatsError(f"分歧统计档案落盘失败: {str(ex)[:200]}") from ex
    log.info("分歧率统计落档: path=%s rows=%d upserted=%d appended=%d", path, len(merged), replaced, upserted)
    return {
        "stats_path": str(path),
        "rows_written": len(merged),
        "upserted": replaced,
        "appended": upserted,
        "date": new_rows[0]["date"] if new_rows else None,
        "table": new_rows[0]["table"] if new_rows else None,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI 入口（运维核对档案：打印 jsonl 尾部行）。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.divergence_stats",
        description="多源分歧率统计档案查看器（#423 两周观察供数档）",
    )
    parser.add_argument(
        "--stats-path", default=None, help="档案路径（默认 data/divergence_stats/divergence_stats.jsonl）"
    )
    parser.add_argument("--tail", type=int, default=20, help="打印末尾 N 行")
    args = parser.parse_args(argv)
    path = Path(args.stats_path) if args.stats_path else _default_stats_path()
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        print(f"no stats file yet: {path}")
        return 0
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for ln in lines[-max(args.tail, 0) :]:
        print(ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
