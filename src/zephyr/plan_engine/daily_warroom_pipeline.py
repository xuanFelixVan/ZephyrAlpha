# [BLUEPRINT] MOD-PLAN-018 | 待统筹登记（45号 §4 W0/W6 验证闭环 + 施工清单 P1-7 日常编排）
# [MODULE] zephyr.plan_engine.daily_warroom_pipeline
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.scenario_plan_recorder(ScenarioPlanRecorder/compute_and_record_scenario_plan/ScenarioRecorderConfig/ScenarioOutcomeVerdict); zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（market_trade_calendar 表名解析）
# [CONSUMERS] 57号日循环 SOP 环节④（盘后批：回写当日+备次日）/ 盘前管线（备当日预案）; 作战室 W0/W6 样本积累（scenario_plan+outcome 族日行落库）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 盘前段 target_date=次交易日（market_trade_calendar 真源 is_open=1 严格大于数据日 LIMIT 1）; 幂等（同日重跑不重复落库——复用 prediction_log UNIQUE(trade_date,module,prediction_type,input_hash) 保首条，编排层零自建键）; 单段失败不炸另一段（fail-open）; 落库仅经 prediction_log_writer 公共 API（零裸 SQL 写库）; 输入校验 fail-closed; 错误消息不含 session_id
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（data_date/phase 非法 fail-closed）; 次交易日解析失败→None（fail-open，盘前段 skipped:no_next_trading_day）; 盘前计算/落库异常→premarket_status=error:* 留痕不外抛; 盘后段复用 MOD-PLAN-008 全 fail-open 口径（verdict.status 留痕）
# [TESTS] tests/plan_engine/test_daily_warroom_pipeline.py
# [A_module] module_id=MOD-PLAN-018 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

DailyWarroomPipeline — 作战室样本积累日循环编排入口件 (MOD-PLAN-018)

45号作战手册 W0/W6 验证闭环 + 施工清单 P1-7 落码：scenario_plan 族需
"盘前 compute_and_record + 盘后 writeback_scenario_outcome" 每日跑才能积累
W0 窗口（20 日）校准样本。MOD-PLAN-008（落库/回写通道）已就位，本模块=唯一的
日循环编排入口（运行时挂 57 号日循环 SOP 环节④/事件驱动管线）。

两段编排（写清口径）：
    - 盘前段（phase=premarket）：target_date = 次交易日（market_trade_calendar
      真源：is_open=1 且 cal_date > 数据日，LIMIT 1）→
      compute_and_record_scenario_plan(target_date) 预案落库。盘后跑批时
      数据日=当日，target=次交易日（备明日预案）；盘前跑批时数据日=前一交易日，
      target=当日——两种挂法同一解析口径。
    - 盘后段（phase=postmarket）：writeback_scenario_outcome(data_date) 回写
      当日实际 outcome（9 格命中判定口径归 MOD-PLAN-008）。
    - phase=both（默认）：盘后日循环一次调用——先回写当日，再备次交易日。

幂等（复用 prediction_log 幂等键，编排层零自建）：
    - scenario_plan 族：payload=ScenarioPlan.to_dict() 确定性内容（无时间戳），
      同日同 target 重跑=同 input_hash → UNIQUE 保首条不重复落库。
    - outcome 族：record_outcome 幂等语义同 log_prediction（同日同模块同内容
      重复写=跳过保首条）；同日行情不变 → 同 payload → 同 hash。

不做什么：不改 MOD-PLAN-008 落库/回写口径（本模块纯编排零判定逻辑）/
         不做候选股边界批量（MOD-PLAN-012 职责）/不做盘中调度（盘后/盘前批件）。

依据: 45_warroom_playbook §4 W0/W6；施工清单 P1-7（WARROOM 遗留 3：target_date
      次交易日解析接 market_trade_calendar）；44号 §12.1 M4-②
SSoT: depgraph MOD-PLAN-018（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: data_date（数据日）+ phase（premarket/postmarket/both）+ CH（trade_calendar/kline_index/kline_etf_1min）
# 特征: 次交易日（is_open=1 严格大于数据日 LIMIT 1）
# 算法: 输入校验 fail-closed → 盘前段（解析 target → compute_and_record）→ 盘后段（writeback_outcome）→ 结果聚合
# 输出: DailyWarroomPipelineResult（逐段 status/row_id/verdict + trace 留痕）

"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.plan_engine.scenario_plan_recorder import (
    ScenarioOutcomeVerdict,
    ScenarioPlanRecorder,
    ScenarioRecorderConfig,
    compute_and_record_scenario_plan,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "PHASE_BOTH",
    "PHASE_POSTMARKET",
    "PHASE_PREMARKET",
    "DailyWarroomConfig",
    "DailyWarroomPipeline",
    "DailyWarroomPipelineResult",
    "resolve_next_trading_day",
    "run_daily_warroom_pipeline",
]

# ── 编排口径常量 ──

PHASE_PREMARKET: Final = "premarket"  # 盘前段：备次交易日预案
PHASE_POSTMARKET: Final = "postmarket"  # 盘后段：回写当日实际 outcome
PHASE_BOTH: Final = "both"  # 日循环默认：盘后一次调用两段皆跑
_PHASES: Final = frozenset({PHASE_PREMARKET, PHASE_POSTMARKET, PHASE_BOTH})

CALENDAR_CATEGORY: Final = "market_trade_calendar"  # table_registry 品类（次交易日真源）
CALENDAR_FALLBACK_TABLE: Final = "c1_market.trade_calendar"  # 注册表不可用降级表名

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 scenario_plan_recorder 同约定）
# 次交易日：is_open=1 且严格大于数据日的最近一个开市日（LIMIT 1 防全表扫）
_SQL_NEXT_TRADING_DAY: Final = (
    "SELECT cal_date FROM {table} WHERE is_open = 1 AND cal_date > '{trade_date}' ORDER BY cal_date LIMIT 1"
)


def _validate_iso_date(value: object, field_name: str) -> str:
    """ISO 交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} 非法（须 YYYY-MM-DD 字符串）: {value!r}")
    try:
        datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} 非真实日期: {value!r}") from exc
    return value


# ── 配置契约 ──


@dataclass(frozen=True)
class DailyWarroomConfig:
    """编排配置（默认值=45号设计口径）。"""

    calendar_category: str = CALENDAR_CATEGORY  # 次交易日真源品类
    calendar_fallback_table: str = CALENDAR_FALLBACK_TABLE  # 降级表名
    recorder_config: ScenarioRecorderConfig | None = None  # 回写判定口径（None=MOD-PLAN-008 默认）

    def __post_init__(self) -> None:
        for name in ("calendar_category", "calendar_fallback_table"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"{name} 非法（须非空字符串）: {v!r}")
        if self.recorder_config is not None and not isinstance(self.recorder_config, ScenarioRecorderConfig):
            raise ValueError(
                f"recorder_config 非法（须 ScenarioRecorderConfig）: {type(self.recorder_config).__name__}"
            )


DEFAULT_CONFIG: Final = DailyWarroomConfig()


# ── 输出契约 ──


@dataclass(frozen=True)
class DailyWarroomPipelineResult:
    """日循环编排结果（MOD-PLAN-018 输出契约，JSON 可序列化）。"""

    data_date: str  # 数据日（盘后段回写日/盘前段解析基准日）
    phase: str  # 实际执行段（premarket/postmarket/both）
    target_date: str | None  # 盘前段预案目标日（次交易日；未执行/解析失败=None）
    premarket_status: str  # ok / skipped:no_next_trading_day / skipped:phase / error:*
    premarket_row_id: int | None  # scenario_plan 落库行 id（-1=落库失败 fail-open 留痕）
    postmarket_status: str  # ok / skipped:* / error:* / skipped:phase
    outcome_verdict: ScenarioOutcomeVerdict | None  # 盘后段回写结论（未执行=None）
    trace: dict[str, Any] = field(default_factory=dict)  # 通道/解析留痕

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return {
            "data_date": self.data_date,
            "phase": self.phase,
            "target_date": self.target_date,
            "premarket_status": self.premarket_status,
            "premarket_row_id": self.premarket_row_id,
            "postmarket_status": self.postmarket_status,
            "outcome_verdict": self.outcome_verdict.to_dict() if self.outcome_verdict is not None else None,
            "trace": dict(self.trace),
        }


# ── 日循环编排器 ──


class DailyWarroomPipeline:
    """作战室样本积累日循环编排器（MOD-PLAN-018）。

    CH 数据经 ch_client 注入（测试 mock/离线）；未注入走项目默认 CH 通道
    （zephyr.data.ch_reader.query）。库路径经 db_path 注入（None=DB_PATH SSoT，
    测试注入临时库，与 MOD-PLAN-008/012 同款隔离先例）。
    """

    def __init__(
        self,
        ch_client: Callable[[str], str] | None = None,
        db_path: str | Path | None = None,
        config: DailyWarroomConfig | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._ch = ch_client
        self._db_path = db_path

    # ── 基础设施 ──────────────────────────────────────────────────────────

    def _calendar_table(self, trace: dict[str, Any]) -> str:
        """按品类解析日历全限定表名；注册表不可用降级 fallback（fail-open）。"""
        try:
            from zephyr.data.table_registry import get_registry

            return get_registry().table(self._config.calendar_category)
        except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
            log.warning(
                "日历表名解析失败 %s，降级 %s: %s",
                self._config.calendar_category,
                self._config.calendar_fallback_table,
                exc,
            )
            trace["channels"]["calendar_table"] = f"fallback:{type(exc).__name__}"
            return self._config.calendar_fallback_table

    def _query(self, sql: str, channel: str, trace: dict[str, Any]) -> str:
        """执行 CH 查询；异常→返回空串+trace 留痕（fail-open，由调用方判降级）。"""
        try:
            if self._ch is not None:
                result = self._ch(sql)
            else:
                from zephyr.data import ch_reader

                result = ch_reader.query(sql)
            trace["channels"][channel] = "ok"
            return result
        except Exception as exc:  # noqa: BLE001 — fail-open：单通道异常不炸整体
            log.warning("通道 %s 查询异常，降级跳过: %s", channel, exc)
            trace["channels"][channel] = f"error:{type(exc).__name__}"
            return ""

    # ── 次交易日解析 ──────────────────────────────────────────────────────

    def resolve_next_trading_day(self, data_date: str, trace: dict[str, Any] | None = None) -> str | None:
        """次交易日解析：market_trade_calendar 真源（is_open=1 严格大于数据日 LIMIT 1）。

        Args:
            data_date: 数据日（YYYY-MM-DD，fail-closed）。
            trace: 留痕 dict（None=内部新建，调用方编排时注入共享 trace）。

        Returns:
            次交易日 ISO 字符串；日历无覆盖/通道异常 → None（fail-open）。

        Raises:
            ValueError: data_date 非法（fail-closed，仅此一类外抛）。
        """
        v_date = _validate_iso_date(data_date, "data_date")
        tr = trace if trace is not None else {"channels": {}}
        table = self._calendar_table(tr)
        tsv = self._query(_SQL_NEXT_TRADING_DAY.format(table=table, trade_date=v_date), "trade_calendar", tr)
        for line in tsv.strip().split("\n") if tsv and tsv.strip() else []:
            cand = line.strip().split("\t")[0].strip()
            if not cand:
                continue
            try:  # 日历行防御性校验（异常行跳过不炸）
                datetime.date.fromisoformat(cand)
            except ValueError:
                continue
            if cand > v_date:  # 严格大于（SQL 已保证，防御双保险）
                return cand
        return None

    # ── 编排主入口 ────────────────────────────────────────────────────────

    def run(
        self,
        data_date: str,
        *,
        phase: str = PHASE_BOTH,
        asof_ts: str | None = None,
        **compute_kwargs: Any,
    ) -> DailyWarroomPipelineResult:
        """日循环编排主入口：盘前备次日预案 + 盘后回写当日 outcome。

        Args:
            data_date: 数据日（盘后段回写日；盘前段次交易日解析基准日，fail-closed）。
            phase: 执行段（premarket/postmarket/both，fail-closed）。
            asof_ts: 落库时点 ISO8601；None=当前 UTC（透传 MOD-PLAN-008）。
            **compute_kwargs: 透传 compute_scenario_plan（config/revision/boundary）。

        Returns:
            DailyWarroomPipelineResult（逐段留痕；单段失败不炸另一段）。

        Raises:
            ValueError: data_date/phase 非法（fail-closed，仅此一类外抛）。
        """
        v_date = _validate_iso_date(data_date, "data_date")
        if not isinstance(phase, str) or phase not in _PHASES:
            raise ValueError(f"phase 非法（须 {sorted(_PHASES)} 之一）: {phase!r}")

        trace: dict[str, Any] = {"channels": {}}
        target_date: str | None = None
        premarket_status = "skipped:phase"
        premarket_row_id: int | None = None
        postmarket_status = "skipped:phase"
        verdict: ScenarioOutcomeVerdict | None = None

        # ── 盘前段：备次交易日预案（compute_and_record，幂等保首条）──
        if phase in (PHASE_PREMARKET, PHASE_BOTH):
            target_date = self.resolve_next_trading_day(v_date, trace)
            if target_date is None:
                premarket_status = "skipped:no_next_trading_day"
            else:
                try:
                    _plan, premarket_row_id = compute_and_record_scenario_plan(
                        target_date,
                        ch_client=self._ch,
                        db_path=self._db_path,
                        asof_ts=asof_ts,
                        **compute_kwargs,
                    )
                    premarket_status = "ok"
                    if premarket_row_id == -1:
                        trace["premarket_persist"] = "fail-open:row_id=-1"
                except Exception as exc:  # noqa: BLE001 — fail-open：盘前失败不炸盘后段
                    log.warning("盘前段异常 fail-open（target=%s）: %s: %s", target_date, type(exc).__name__, exc)
                    premarket_status = f"error:premarket:{type(exc).__name__}"
                    premarket_row_id = None

        # ── 盘后段：回写当日实际 outcome（MOD-PLAN-008 全 fail-open 口径）──
        if phase in (PHASE_POSTMARKET, PHASE_BOTH):
            try:
                verdict = ScenarioPlanRecorder(
                    ch_client=self._ch,
                    db_path=self._db_path,
                    config=self._config.recorder_config,
                ).writeback_outcome(v_date, asof_ts=asof_ts)
                postmarket_status = verdict.status
            except Exception as exc:  # noqa: BLE001 — fail-open：盘后失败不炸盘前段成果
                log.warning("盘后段异常 fail-open（date=%s）: %s: %s", v_date, type(exc).__name__, exc)
                postmarket_status = f"error:postmarket:{type(exc).__name__}"
                verdict = None

        return DailyWarroomPipelineResult(
            data_date=v_date,
            phase=phase,
            target_date=target_date,
            premarket_status=premarket_status,
            premarket_row_id=premarket_row_id,
            postmarket_status=postmarket_status,
            outcome_verdict=verdict,
            trace=trace,
        )


# ── 函数级入口 ──


def resolve_next_trading_day(
    data_date: str,
    ch_client: Callable[[str], str] | None = None,
) -> str | None:
    """次交易日解析函数级入口（MOD-PLAN-018）。

    Args:
        data_date: 数据日（YYYY-MM-DD，fail-closed）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道。

    Returns:
        次交易日 ISO 字符串；日历无覆盖/通道异常 → None（fail-open）。
    """
    return DailyWarroomPipeline(ch_client=ch_client).resolve_next_trading_day(data_date)


def run_daily_warroom_pipeline(
    data_date: str,
    *,
    phase: str = PHASE_BOTH,
    ch_client: Callable[[str], str] | None = None,
    db_path: str | Path | None = None,
    config: DailyWarroomConfig | None = None,
    asof_ts: str | None = None,
    **compute_kwargs: Any,
) -> DailyWarroomPipelineResult:
    """作战室日循环编排函数级主入口（MOD-PLAN-018）。

    Args:
        data_date: 数据日（盘后段回写日；盘前段次交易日解析基准日）。
        phase: 执行段（premarket/postmarket/both，默认 both=日循环一次两段）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        config: 编排配置（None=默认 DailyWarroomConfig()）。
        asof_ts: 落库时点 ISO8601；None=当前 UTC。
        **compute_kwargs: 透传 compute_scenario_plan（config/revision/boundary）。

    Returns:
        DailyWarroomPipelineResult（JSON 可序列化；幂等复用 prediction_log 键）。
    """
    return DailyWarroomPipeline(ch_client=ch_client, db_path=db_path, config=config).run(
        data_date,
        phase=phase,
        asof_ts=asof_ts,
        **compute_kwargs,
    )
