# [BLUEPRINT] MOD-GOV | docs/_working/decision_map_campaign/links/L09_review/SKEL.md §四（沿用账本=13 号文 TRD-A01）
# [MODULE] scripts.governance.decision_chain_sentinel
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.database_service(懒加载); zephyr.shared.utils.time_utils; zephyr.data.table_registry; schemas.categories.decision_daily(表名真源)
# [CONSUMERS] schtasks ZephyrAlpha_DecisionChainSentinel(每日 09:40 盘前, scripts/register_decision_chain_sentinel_task.ps1 注册); data/runtime/process_reaper_keep.txt(防误杀条目 decision_chain_sentinel)
# [STARTUP] scheduled_task
# [MATURITY] trial
# [INVARIANTS] 只读检测禁修数: CH 访问唯一入口=DatabaseService.get_clickhouse_conn(reader)禁裸连接(宪法§9.1), 本件禁任何 DB 写;
#   参照 quality_sentinel 先例(滞后尺与污染尺两把尺禁合并, 本件只管滞后尺); 当前时间唯一入口 now_utc()(RULE-SCHEMA-TZ);
#   表名三真源零硬编码(decision_daily=DDL-as-Code TABLE_NAME, trade_calendar/kline_index=TableRegistry 品类 market_trade_calendar/market_index_kline, 同 backfill_checker 先例);
#   判定口径(★2026-09-25 治尺 DAY §②, 案卷=docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/DAY_daily_loop_skip.md):
#     期望日 E=交易日历中 >= 运行日的**首个开市日**(=本应产出的最新一日); 实评日=max(trade_date WHERE trade_date<=E);
#     E 缺行即告警("缺即告警"), lag=日历口径 (实评日, E] 开市日数。旧尺 max(trade_date) 无上界 ⇒ 任一超前于当日的行
#     (如 09-25 晨批产出 target=09-28)把 max 顶到参照日之后 ⇒ lag 恒 0 ⇒ 尾部/中间整日缺失被完全掩盖=哑火尺。
#     本件是"尺子选错"的治本, **不是放松阈值**: --lag-days(默认 2) 只在"日历腿不可用"的降级参照日口径里继续生效,
#     主判据下它不再能压制"当日无计划"这一条。期望日真源=c1_market.trade_calendar(只存开市日), **禁硬编码节假日清单**。
#     超前于期望日的行另记 decision_max_unclamped/rows_beyond_expected_day 供人工判异常, 永不参与掩盖。
#     (TRD-A01 累积哨兵, 与 dloop 圈失败的单次 ERROR 互补——SKEL S9-6⑤: 单次失败已有告警, 本件管"该有而没有"的缺勤形态),
#   参照日(降级腿与报表字段)=min(日历最近开市日, kline_index max 日期)取小(任务书口径: 日历超前于数据面时不虚计滞后),
#     仅在日历"期望日腿"不可用(查询失败/超出日历覆盖)时充当判据轴, 此时 lag 仍按 --lag-days 阈值判;
#   告警唯一出口=alert jsonl 追加行+进程退出码(任务书契约, 不另开 Alerter 通道=净零内收); 无状态每次实查(自动维护=无 state 文件防第二真源);
#   自动关闭=schtasks /change /disable(不设 disabled 标记文件, 不加任务书之外机制)。
#   ★ 数据源勘误留档(2026-09-25 实测 DESCRIBE): 任务书原文写"PG depgraph 连接 get_depgraph_pg_connection", 实测 PG 全 schema 无 decision_daily(仅 depgraph 决策图四表 decision_nodes/layers/edges/tracks);
#   决策快照真源=ClickHouse c1_backtest.decision_daily(schemas/categories/decision_daily.py DDL 唯一真源, 写侧唯一=daily_decision_orchestrator, 读侧先例=warroom.py), 统计列=trade_date(Date, 拍板生效日=次交易日);
#   按实测改走 CH reader, 防"连不存在的表"型 R-021 有名无实假通道(SKEL §5.2)。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 正常=exit 0; 期望日缺行(主判据, 不受阈值豁免) / 降级参照日口径下滞后>=N(默认2,参数化) / decision_daily 全史零行=写告警行+exit 4; DB 异常/配置非法=写 error 记录+exit 8(fail-soft, 单行日志禁裸奔抛栈);
#   期望日腿失败(日历查询异常/日历无 >=ref 的开市日)→ 降级参照日口径, ruler 字段标 "reference_day_degraded";
#   calendar/kline 单腿失败降级不致命(参照日退化到另一腿, lag_basis 降级为 calendar_days 口径并在记录里标注), 双腿全废或 decision 查询失败=error 路径。
# [TESTS] tests/governance/test_decision_chain_sentinel.py
# [A_module] module_id=MOD-GOV-decision_chain_sentinel | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""决策链哨兵（TRD-A01 / L09-C04）——期望交易日该有决策行而没有，即告警。

判定语义（2026-09-25 治尺后的期望交易日口径，案卷 DAY §②）：
  E    = 交易日历中 >= 运行日的**首个开市日**（本应产出的最新目标日；真源 c1_market.trade_calendar）
  act  = max(decision_daily.trade_date WHERE trade_date <= E)   ← 带上界，超前行不参与
  act == E            → ok, lag=0
  act != E / act=None → 告警 + exit 4（"缺即告警"，不被 --lag-days 豁免）
  lag  = (act, E] 内开市日数（= 缺勤的期望交易日数）
降级路径（日历"期望日腿"不可用：查询失败 / 日历无 >=ref 的开市日）：
  ref  = min(日历最近开市日(<=今日), kline_index max(trade_date))，act=max(trade_date WHERE trade_date<=ref)
  lag  = (act, ref] 开市日数（日历腿可用）或日历日差（降级，记录标注）；lag >= N(默认 2) → 告警
时序自洽：T 日 09:40 盘前跑——拍板体 T-1 16:45（或当日晨批）应已产出 target=T 的行；T 若休市，
E 自动跳到次开市日（例：2026-09-25 中秋休市 ⇒ E=2026-09-28），节假/周末不再靠人肉判。
旧尺为何是哑火：last=max(trade_date) 无上界，只要存在任一"超前于当日"的行（09-25 晨批写 target=09-28
就是合法形态），last>ref ⇒ lag 恒 0 ⇒ 尾部整日缺失与中间跳日全被掩盖。新尺按期望日逐日点名，
超前行只在 decision_max_unclamped / rows_beyond_expected_day 两字段露出，供人工判异常，不参与判据。

用法：
  python scripts/governance/decision_chain_sentinel.py [--lag-days N] [--ref-date YYYY-MM-DD]
                                                       [--alert-log PATH]
exit: 0=正常 | 4=告警 | 8=error(fail-soft)
"""

from __future__ import annotations

__manifest__ = """
args: [--lag-days, --ref-date, --alert-log]
description: 决策链哨兵——期望交易日（日历 >=今日首个开市日）无 decision_daily 行即告警（TRD-A01/L09-C04, exit 0/4/8）。
dimensions:
- D11
priority: P2
timeout_seconds: 120
warn_only: false
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:  # schtasks 直跑文件时补仓根(同 add_deferred_design_edges.py)
    sys.path.insert(0, str(_REPO_ROOT))

from schemas.categories.decision_daily import TABLE_NAME as _TBL_DECISION_DAILY
from scripts.governance._shared.thresholds import get_int  # 阈值SSoT(ARCH-036 P3-A5)
from zephyr.data.table_registry import get_registry
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger("decision_chain_sentinel")

__all__ = ["run_sentinel", "main"]

_EXIT_OK: int = 0
_EXIT_ALERT: int = 4
_EXIT_ERROR: int = 8

_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

# dloop 第二判据数据面（L09-C04 2026-09-29）：fetch_perf 被动记录通道落盘目录
# （真源=zephyr.data.fetch_perf_recorder._DEFAULT_BASE_DIR，禁另起第二路径）。
# 判据阈值/升级口径待 L09-C04 立项定版（defer 留痕）；当前只读作取证，不改 0/4/8 出口契约。
_FETCH_PERF_DIR = _REPO_ROOT / ".runtime" / "fetch_perf"


_DEFAULT_THRESHOLD_LAG_DAYS = get_int("decision_chain_sentinel.default_lag_days", 2)
_DEFAULT_ALERT_LOG = _REPO_ROOT / ".runtime" / "logs" / "decision_chain_alert.jsonl"
_ALERT_LOG_ENV = "DECISION_CHAIN_SENTINEL_ALERT_LOG"
_ERROR_MSG_CAP = 500

_TBL_TRADE_CALENDAR = get_registry().table("market_trade_calendar")  # c1_market.trade_calendar
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")  # c1_market.kline_index
_CALENDAR_EXCHANGE = "SSE"  # 同 quality_sentinel: 库内当前仅此一档, 扩档再立案

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）。日历表只存开市日(is_open 恒 1),
# 仍显式带 is_open=1 谓词防表语义漂移(同 quality_sentinel 负向判定三硬约束口径)。
_SQL_DECISION_MAX_DATE = "SELECT max(trade_date) FROM {table}"
# 治尺后的实评日=带上界的 max（超前行不得参与判据, 见 [INVARIANTS] 判定口径）
_SQL_DECISION_MAX_DATE_NOT_AFTER = "SELECT max(trade_date) FROM {table} WHERE trade_date <= toDate('{bound}')"
_SQL_CALENDAR_FIRST_OPEN_ON_OR_AFTER = (
    "SELECT min(cal_date) FROM {calendar} FINAL "
    "WHERE exchange = '{exchange}' AND is_open = 1 AND cal_date >= toDate('{ref_date}')"
)
_SQL_CALENDAR_LAST_OPEN = (
    "SELECT max(cal_date) FROM {calendar} FINAL "
    "WHERE exchange = '{exchange}' AND is_open = 1 AND cal_date <= toDate('{ref_date}')"
)
_SQL_KLINE_MAX_DATE = "SELECT max(trade_date) FROM {table}"
_SQL_OPEN_DAYS_AFTER = (
    "SELECT count() FROM {calendar} FINAL "
    "WHERE exchange = '{exchange}' AND is_open = 1 "
    "AND cal_date > toDate('{start}') AND cal_date <= toDate('{end}')"
)


class DecisionChainQueryExecutor(Protocol):
    """CH 查询执行器最小协议（生产=DatabaseService reader 连接, 同 quality_sentinel）。"""

    def execute(self, sql: str) -> list:  # noqa: D102 - 协议即文档
        ...


def _default_executor() -> DecisionChainQueryExecutor:
    """CH 只读连接——唯一 Client 构造点 DatabaseService（宪法 §9.1 禁裸连接）。"""
    from zephyr.infrastructure.database_service import get_db_service

    return get_db_service().get_clickhouse_conn(role="reader", slot="decision_chain_sentinel")


def _default_alert_log() -> Path:
    import os

    return Path(os.environ.get(_ALERT_LOG_ENV) or _DEFAULT_ALERT_LOG)


def _fetch_perf_evidence(fetch_perf_dir: Path | None = None) -> dict | None:
    """dloop 第二判据数据面（L09-C04 2026-09-29）：读 fetch_perf 落盘近况作取证。

    fetch_perf_recorder 每任务收尾落 fetch_perf_YYYYMMDD.jsonl（调度真实运行面，
    禁新 DDL 故不入 CH）。第二判据的阈值/升级口径待 L09-C04 定版（defer 留痕），
    当前只读不判：取最近一份日报的最后一条记录摘要素作 evidence 附加进 record；
    空目录/缺文件/不可读一律返回 None——绝不影响主判据 0/4/8 出口契约（禁阻塞）。
    """
    base = Path(fetch_perf_dir) if fetch_perf_dir is not None else _FETCH_PERF_DIR
    try:
        if not base.is_dir():
            return None
        daily = sorted(base.glob("fetch_perf_*.jsonl"))
        if not daily:
            return None
        last_line = ""
        for line in daily[-1].read_text(encoding="utf-8").splitlines():
            if line.strip():
                last_line = line
        if not last_line:
            return None
        payload = json.loads(last_line)
        return {
            "source_file": daily[-1].name,
            "ts": payload.get("ts"),
            "task_id": payload.get("task_id"),
            "status": payload.get("status"),
        }
    except (OSError, ValueError):
        return None


def _single_date(rows: list) -> date | None:
    """单行单列查询结果 -> date（空表/None 值=None）。"""
    if not rows or rows[0] is None or rows[0][0] is None:
        return None
    value = rows[0][0]
    return value if isinstance(value, date) else date.fromisoformat(str(value)[:10])


def _append_jsonl(path: Path, record: dict) -> bool:
    """告警/错误行追加（append-only jsonl, 同 resource_sampler 样本流制式）。"""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return True
    except OSError as e:
        log.error("哨兵记录写入失败 path=%s: %s", path, e)
        return False


def _resolve_expected_day(executor: DecisionChainQueryExecutor, ref_date: date) -> tuple[date | None, str, str | None]:
    """期望日 E=日历中 >= ref_date 的首个开市日（=本应产出的最新目标日, 交易日历真源, 禁硬编码节假日）。

    Returns: (expected_day, ruler, degrade_reason)——日历腿失败或超出日历覆盖时 expected_day=None,
    由调用方降级到参照日口径（ruler="reference_day_degraded"）, 不静默出绿。
    """
    try:
        expected = _single_date(
            executor.execute(
                _SQL_CALENDAR_FIRST_OPEN_ON_OR_AFTER.format(
                    calendar=_TBL_TRADE_CALENDAR, exchange=_CALENDAR_EXCHANGE, ref_date=ref_date.isoformat()
                )
            )
        )
    except Exception as e:  # noqa: BLE001 - 期望日腿失败降级（ERROR_CONTRACT）
        log.warning("期望日腿降级（日历查询失败）, 改走参照日口径: %s", e)
        return None, "reference_day_degraded", f"calendar_query_failed: {type(e).__name__}"
    if expected is None:
        return None, "reference_day_degraded", "calendar_has_no_open_day_on_or_after_ref"
    return expected, "expected_open_day", None


def _resolve_reference_day(
    executor: DecisionChainQueryExecutor, ref_date: date
) -> tuple[date, str, date | None, date | None]:
    """参照日=min(日历最近开市日, kline_index max)；单腿失败降级另一腿, 双腿全废=抛(走 error 路径)。

    Returns: (reference_day, basis, calendar_day, kline_day)
    """
    calendar_day: date | None = None
    try:
        calendar_day = _single_date(
            executor.execute(
                _SQL_CALENDAR_LAST_OPEN.format(
                    calendar=_TBL_TRADE_CALENDAR, exchange=_CALENDAR_EXCHANGE, ref_date=ref_date.isoformat()
                )
            )
        )
    except Exception as e:  # noqa: BLE001 - 单腿降级不致命（ERROR_CONTRACT）
        log.warning("日历腿降级: %s", e)
    kline_day: date | None = None
    try:
        kline_day = _single_date(executor.execute(_SQL_KLINE_MAX_DATE.format(table=_TBL_KLINE_INDEX)))
    except Exception as e:  # noqa: BLE001
        log.warning("kline_index 腿降级: %s", e)

    candidates = [(d, tag) for d, tag in ((calendar_day, "calendar"), (kline_day, "kline")) if d is not None]
    if not candidates:
        raise RuntimeError(
            f"参照日双腿全废（calendar/kline 均不可用, ref_date={ref_date.isoformat()}）, 拒绝出数防假绿"
        )
    reference_day, basis = min(candidates, key=lambda pair: (pair[0], pair[1]))
    if len(candidates) == 1:
        basis = f"{basis}_only"
    else:
        basis = "min_calendar_kline"
    return reference_day, basis, calendar_day, kline_day


def _compute_lag(executor: DecisionChainQueryExecutor, last: date, ref: date) -> tuple[int, str]:
    """(last, ref] 的缺勤量: 日历腿可用=开市日数(trading_days); 降级=日历日差(calendar_days, 保守偏大)。"""
    try:
        rows = executor.execute(
            _SQL_OPEN_DAYS_AFTER.format(
                calendar=_TBL_TRADE_CALENDAR,
                exchange=_CALENDAR_EXCHANGE,
                start=last.isoformat(),
                end=ref.isoformat(),
            )
        )
        return int(rows[0][0]), "trading_days"
    except Exception as e:  # noqa: BLE001 - lag 腿降级（ERROR_CONTRACT）
        log.warning("lag 交易日口径降级为日历日差: %s", e)
        return (ref - last).days, "calendar_days"


def run_sentinel(
    executor: DecisionChainQueryExecutor,
    *,
    ref_date: date,
    threshold_lag_days: int = _DEFAULT_THRESHOLD_LAG_DAYS,
    alert_log: Path | None = None,
) -> dict:
    """哨兵主入口：问日历要期望交易日 -> 带上界查实际日 -> 期望日缺行/降级口径超阈值即写告警行。

    DB 异常向上抛（error 记录与 exit 8 由 main 收口，fail-soft 契约单点）。

    Returns:
        报告 dict（type="ok"|"alert"; alert 时已追加告警行到 alert_log, 含 ruler/expected_trade_date/
        decision_max_unclamped/rows_beyond_axis 四新字段供取证）。
    """
    if threshold_lag_days < 1:
        raise ValueError(f"threshold_lag_days 须 >=1（0/负=哨兵永久误鸣）, got {threshold_lag_days}")
    alert_path = Path(alert_log) if alert_log else _default_alert_log()

    # 主体表先查（decision_daily 失败=error 路径, 与旧版同序, 防"参照腿先炸"遮蔽真故障点）
    unclamped = _single_date(executor.execute(_SQL_DECISION_MAX_DATE.format(table=_TBL_DECISION_DAILY)))
    expected_day, ruler, degrade_reason = _resolve_expected_day(executor, ref_date)
    reference_day, ref_basis, calendar_day, kline_day = _resolve_reference_day(executor, ref_date)
    axis = expected_day or reference_day  # 主判据轴=期望交易日; 日历期望日腿不可用时=参照日

    actual = _single_date(
        executor.execute(_SQL_DECISION_MAX_DATE_NOT_AFTER.format(table=_TBL_DECISION_DAILY, bound=axis.isoformat()))
    )

    record: dict = {
        "schema_version": 1,
        "sentinel": "decision_chain_sentinel",
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "ref_date": ref_date.isoformat(),
        "threshold_lag_days": threshold_lag_days,
        "ruler": ruler,
        "ruler_degrade_reason": degrade_reason,
        "expected_trade_date": expected_day.isoformat() if expected_day else None,
        "last_decision_date": actual.isoformat() if actual else None,
        "decision_max_unclamped": unclamped.isoformat() if unclamped else None,
        "rows_beyond_axis": bool(unclamped is not None and unclamped > axis),
        "reference_day": reference_day.isoformat(),
        "reference_basis": ref_basis,
        "calendar_day": calendar_day.isoformat() if calendar_day else None,
        "kline_day": kline_day.isoformat() if kline_day else None,
    }

    if actual is None:
        # 轴前零行=决策链从未供血（比滞后超限更重的断供形态; 超前行只露出不用作判据）
        record.update(
            {
                "type": "alert",
                "lag_trading_days": None,
                "lag_basis": None,
                "detail": (
                    f"decision_daily 全史零行（{_TBL_DECISION_DAILY} 无任何快照行）——决策链断供"
                    if unclamped is None
                    else f"决策链滞后/断供: 期望日 {axis.isoformat()} 及之前零行，"
                    f"仅有超前于轴的行 max={unclamped.isoformat()}（超前行不参与判据）"
                ),
            }
        )
    elif ruler == "expected_open_day":
        if actual == expected_day:
            record.update(
                {
                    "type": "ok",
                    "lag_trading_days": 0,
                    "lag_basis": "trading_days",
                    "detail": (
                        f"决策链在供: 期望交易日 {expected_day.isoformat()}（日历 >=ref 首个开市日）已有决策行, "
                        f"lag=0 < {threshold_lag_days}"
                    ),
                }
            )
        else:
            lag, lag_basis = _compute_lag(executor, actual, expected_day)
            record.update(
                {
                    "type": "alert",
                    "lag_trading_days": lag,
                    "lag_basis": lag_basis,
                    "detail": (
                        f"决策链滞后/跳日: 期望交易日 {expected_day.isoformat()} 无 decision_daily 行"
                        f"（最近实评日 {actual.isoformat()}, 缺勤 {lag} 个"
                        f"{'交易日' if lag_basis == 'trading_days' else '日历日(降级口径)'}）"
                        f"——期望日缺行即告警，不受 --lag-days 豁免"
                    ),
                }
            )
    else:
        # 降级参照日口径: --lag-days 语义原样保留（连续 N 个开市日无新行）; 实评日带上界, 超前行不再掩盖
        lag, lag_basis = (
            _compute_lag(executor, actual, reference_day) if reference_day > actual else (0, "trading_days")
        )
        record.update({"lag_trading_days": lag, "lag_basis": lag_basis})
        if lag >= threshold_lag_days:
            record.update(
                {
                    "type": "alert",
                    "detail": (
                        f"决策链滞后(降级参照日口径): 最后快照日 {actual.isoformat()} 距参照日 {reference_day.isoformat()}"
                        f" 缺勤 {lag} 个{'交易日' if lag_basis == 'trading_days' else '日历日(降级口径)'}"
                        f" >= 阈值 {threshold_lag_days}"
                    ),
                }
            )
        else:
            record.update({"type": "ok", "detail": f"决策链在供（降级参照日口径 lag={lag} < {threshold_lag_days}）"})

    if record["type"] == "alert":
        if not _append_jsonl(alert_path, record):
            log.error("告警行落盘失败, 仅以退出码示警")
        log.warning("%s", record["detail"])
    else:
        log.info("%s", record["detail"])
    return record


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。exit: 0=正常 | 4=告警 | 8=error（fail-soft, 禁抛栈）。"""
    parser = argparse.ArgumentParser(
        prog="python scripts/governance/decision_chain_sentinel.py",
        description="决策链哨兵（TRD-A01/L09-C04）: 连续 N 个交易日无 decision_daily 新行即告警",
    )
    parser.add_argument(
        "--lag-days",
        type=int,
        default=_DEFAULT_THRESHOLD_LAG_DAYS,
        help=f"滞后阈值（交易日, >=该值告警）, 默认 {_DEFAULT_THRESHOLD_LAG_DAYS}",
    )
    parser.add_argument("--ref-date", default=None, help="基准日 YYYY-MM-DD（默认=上海时区今日; 演练/测试用）")
    parser.add_argument("--alert-log", default=None, help=f"告警 jsonl 路径（默认 {_DEFAULT_ALERT_LOG}）")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        ref_date = date.fromisoformat(args.ref_date) if args.ref_date else now_utc().astimezone(_SHANGHAI_TZ).date()
        record = run_sentinel(
            _default_executor(),
            ref_date=ref_date,
            threshold_lag_days=args.lag_days,
            alert_log=Path(args.alert_log) if args.alert_log else None,
        )
        evidence = _fetch_perf_evidence(_FETCH_PERF_DIR)  # dloop 第二判据数据面（只读取证，L09-C04）
        if evidence is not None:
            record["fetch_perf_evidence"] = evidence
        return _EXIT_ALERT if record["type"] == "alert" else _EXIT_OK
    except Exception as e:  # noqa: BLE001 - fail-soft 收口: 单行记录不抛栈（ERROR_CONTRACT）
        message = f"{type(e).__name__}: {e}"[:_ERROR_MSG_CAP].replace("\n", " ")
        log.error("决策链哨兵 error（fail-soft）: %s", message)
        _append_jsonl(
            Path(args.alert_log) if args.alert_log else _default_alert_log(),
            {
                "schema_version": 1,
                "sentinel": "decision_chain_sentinel",
                "type": "error",
                "generated_at_utc": now_utc().isoformat(timespec="seconds"),
                "ref_date": args.ref_date,
                "threshold_lag_days": args.lag_days,
                "error_type": type(e).__name__,
                "error_message": message,
            },
        )
        return _EXIT_ERROR


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: ZephyrAlpha_DecisionChainSentinel 计划任务每日 09:40 盘前系统级调度触发，__main__ 仅供人工复跑与取证
    sys.exit(main())
