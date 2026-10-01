# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cleaning_expectation_hosting
# [DOMAIN] D_DATA
# [TTL] permanent
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/zephyr/data/test_cleaning_expectation_hosting.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# noqa: m11-perm-manual-legitimate  M11豁免: 本件=supply_sentinel 排班腿托管第四段消费侧事件链接线（L13
#   data_supply_sentinel），CLI 独立运行面=运维按需 runner（非 cron/非 daemon/非常驻服务，
#   #ARCH-P3-FOLLOWUP-TODOS-001 裁定 B/C 通道；同族先例 cleaning_rules_hosting/cleaning_anomaly_hosting）
# create-guard-not-dup: 本件=D_DATA 域期望门控+信号告警排班托管腿（承载册判据驱动只读校验+分级告警，
#   禁修数），非 cleaning_rules_hosting（DSL 第二段）/cleaning_anomaly_hosting（帧内异常第三段）/
#   quality_sentinel（变异巡检）的第二实现——本腿接的是 R-M1-06 台账里最后两台预留引擎
#   expectation_governance + data_anomaly_alerter（经 cleaning_engines 门面统一入口派发）
# [ERROR_CONTRACT] 承载册缺失/解析失败/未知键/参数非法/host 不符->ExpectationGateConfigError（CLI exit 254）；
#   单表校验或单标的检出异常->该对象 degraded 不中断全批；全批 degraded->CLI exit 253；
#   not_run/degraded_partial->托管腿 ok=False 禁冒绿（同族 cleaning_rules/anomaly hosting 口径）
# [DEPENDENCIES] zephyr.data_eng.expectation_governance(期望套件验证真身); zephyr.data_eng.data_anomaly_alerter(
#   信号检出真身); zephyr.data.cleaning_engines(门面统一入口 validate_expectations/evaluate_anomaly_signals);
#   zephyr.data.cleaning_rules_hosting(承载册读取/校验原语委托); zephyr.data.alerter(告警唯一正门);
#   zephyr.infrastructure.database_service(懒加载, CH 只读唯一入口); zephyr.shared.io.file_utils(safe_write_text);
#   zephyr.shared.io.paths; zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] zephyr.data.supply_sentinel.run_supply_sentinel -> _run_hosted_expectation_gate
#   （L13 data_supply_sentinel 排班腿托管第四段，R-M1-06 逐引擎接线收口台 2026-10-01
#   st-ffchief-20261001 lane-f04）；CLI 独立运行
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] 判据值唯一真源=config/cleaning_expectations.yaml（宪法硬规则 6 RULE-SSOT，代码禁写
#   阈值/窗口/限额/期望参数任何判据值，改册即改行为，红测钉住）;
#   只读校验禁修数：本腿只 SELECT+validate/detect 出报告与告警，不写库、不剔行、不改 ch_writer
#   写路径（修复/拦截=改生产数据，属 Owner 门位）;
#   CH 访问唯一入口=DatabaseService.get_clickhouse_conn(role=reader)，禁裸连接（宪法 §9.1）;
#   读侧安全阀三闸=read_limit_rows（表样本上限）×watchlist_size（标的数上限）×rows_per_symbol
#   （单标的行数上限），全在承载册，禁对亿行表无界 SELECT;
#   未知键=配置错上抛（键集由 dataclass 字段派生，禁手工清单——宪法 §9.5）;
#   YAML 缺失/解析失败/参数非法/host_schedule 与实调方不符/期望类型未知/严重级别非法=**fail-closed**：
#     抛 ExpectationGateConfigError，托管腿 ok=False 并出声，绝不返回"干净";
#   单表/单标的异常=degraded 不中断全批；全批 degraded=巡检未生效 ok=False（禁谎报绿）;
#   检出面诚实：期望列未进取数面=uncovered 如实披露（未检非干净，禁把"没得检"当"检过干净"）;
#   序列不足检测窗=short_series 跳过并披露（不冒充检出也不算降级）;
#   结论四态=ran_and_clean｜ran_with_findings｜degraded_partial｜not_run，**只有 ran_and_clean 允许 ok=True**;
#   节奏闸状态真源=报告文件名前 10 字符且**须验正文**（gate 自对+inspection_ran，防空文件催眠）;
#   当前时间统一 now_utc() 入口（RULE-SCHEMA-TZ）；报告经 safe_write_text 落盘;
#   引擎面宣告（四引擎接线台账）：本腿 wired=[expectation_governance, data_anomaly_alerter]，
#     此前已接 cleaning_rule_engine（第二段）与 cleaning_anomaly_engine（第三段）——至此
#     R-M1-06 台账四台全接；purity_adjudicator（AI 判净）不在四台台账内，#423 形态锁
#     standing_by_no_auto_feed（LLM 花钱点 Owner 门），预留≠断链;
#   告警分级路由不复制：alert_sink 只桥接 Alerter.notify，AL-P1~P4→通道级别映射真源=
#     data_anomaly_alerter._GRADE_TO_ROUTE_LEVEL（引擎自带，本件零判据）;
#   期望时效（freshness）时钟对=ExpectationGovernance 引擎默认本地钟（naive 本地墙钟 vs CH
#     上海业务日列，同域配对正确），本件不另注入第二时钟（禁双钟漂移）;
#   divergence/cross-source 两检测路本腿不喂（如实披露）：前者信号 metric=带符号相关系数与
#     grade() 的 ratio=metric/threshold 判据在引擎面不相容（非正阈值/负值信号进 grade 即
#     ZA-DATENG-0001），量能维度已由第三段 volume_spike 覆盖；后者已由 cross_validation 槽
#     （23:15）承担——预留≠已喂，普查对账以本宣告为准
"""期望门控+信号告警排班托管腿（R-M1-06 逐引擎接线收口台；F04 清洗三引擎 P0 断链闭环段）。

诞生背景（00_skeleton.md §3 P0#1「清洗三引擎零接线」2026-10-01 复测）：R-M1-06 台账四台
清洗引擎中前两台已接（cleaning_rules_hosting 托管第二段 2026-09-26；cleaning_anomaly_hosting
托管第三段 2026-09-28），余下 expectation_governance（期望套件门控）与 data_anomaly_alerter
（信号分级+抑制+路由）仍零生产调用点（cleaning_anomaly_hosting.ENGINE_SLOTS_RESERVED 在案）。
本件补收口台：宿主=同一条 L13 data_supply_sentinel 排班腿的**托管第四段**
（同族先例 quality_sweep/cleaning_gate/anomaly_gate，不新建平行管线、不新开排班槽位——R-021），
两台引擎统一走 cleaning_engines 门面派发（其 [CONSUMERS] 声明的"F04 C1 解锁后的接线方"即本腿）。

读侧 flag 档（出厂态，"新能力默认不改变既有产出"承诺）：本腿只 SELECT+validate/detect 出
**报告与告警**；不写库、不剔行、不改 ch_writer 写路径、不调任何修复。期望三档 verdict
（block/degrade/warn）在本腿一律只计入 findings 并出声，不执法（写侧门控=Owner 门位）。

诚实边界：本腿校验的是"表样本对期望套件的符合度"与"逐标的序列统计信号"，判定建议只进
报告与告警面，不进排班判定（同 cleaning_gate=advisory_only 家族，接线一行=总筹待登）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 承载册 config/cleaning_expectations.yaml（wiring+alerter+expectations+targets，判据值唯一真源）
# - id: I2
#   name: CH 近窗样本行（DatabaseService 只读连接；表样本=日期降序 LIMIT，标的序列=逐符号升序 LIMIT）
# 层: 处理
# - id: P1
#   name: load_rulebook 校验（schema_version/未知键/期望类型白名单/严重级别白名单；非法 fail-closed）
# - id: P2
#   name: _evaluate_target 表样本->门面 validate_expectations（期望三档）；逐标的序列->
#         detect_price_jumps(+detect_missing_rate 当 expected_rows 在册)->门面 evaluate_anomaly_signals
#         （分级+抑制+路由，alert_sink 桥接宿主 Alerter）
# - id: P3
#   name: gate_status 诚实四态（任一降级/零样本=degraded_partial，禁冒绿）
# 层: 输出
# - id: O1
#   name: 报告 JSON（safe_write_text 落 report_dir；文件名前 10 字符=节奏闸状态真源）
#   name: 期望报告 JSONL 追加存档（门面 validate_expectations archive_path，可追溯）
# - id: O2
#   name: 告警面（降级/零样本/期望失败/信号命中；引擎 AL-P1~P4 分级路由由引擎走 alert_sink，本腿只出声）
# 边:
# I1 -> P1 -> P2 -> P3 -> O1 -> O2
# I2 -> P2
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass, fields
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Protocol
from zoneinfo import ZoneInfo

from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, LEVEL_INFO, LEVEL_WARN
from zephyr.data.cleaning_rules_hosting import CleaningGateConfigError
from zephyr.data.cleaning_rules_hosting import (
    _check_identifier as _rules_check_identifier,
)
from zephyr.data.cleaning_rules_hosting import (
    _load_raw as _rules_load_raw,
)
from zephyr.data.cleaning_rules_hosting import (
    _parse_bool as _rules_parse_bool,
)
from zephyr.data.cleaning_rules_hosting import (
    _parse_positive_int as _rules_parse_positive_int,
)
from zephyr.data.cleaning_rules_hosting import (
    _reject_unknown_keys as _rules_reject_unknown_keys,
)
from zephyr.data.cleaning_rules_hosting import (
    _repo_relative as _rules_repo_relative,
)
from zephyr.data.cleaning_rules_hosting import (
    _require as _rules_require,
)
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    import pandas as pd

log = logging.getLogger(__name__)

#: 业务日界口径（同族两腿；禁 datetime.now() 散落，RULE-SCHEMA-TZ）
_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

__all__: Final = [
    "ExpectationGateConfigError",
    "STATUS_DEGRADED_PARTIAL",
    "STATUS_NOT_RUN",
    "STATUS_RAN_CLEAN",
    "STATUS_RAN_FINDINGS",
    "ENFORCEMENT_STATE",
    "ENGINE_SLOTS_WIRED",
    "ExpectationWiringConfig",
    "AlerterParams",
    "ExpectationTarget",
    "ExpectationGateRunOptions",
    "gate_status",
    "load_rulebook",
    "run_expectation_gate",
    "run_hosted_expectation_gate",
    "status_exit_code",
    "main",
]

_DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "cleaning_expectations.yaml"

#: 告警级别合法集（由 alerter 常量派生，禁自造通道/自写级别名——同族 anomaly 腿口径）
_ALLOWED_LEVELS: Final = frozenset({LEVEL_INFO, LEVEL_WARN, LEVEL_ERROR, LEVEL_CRITICAL})

#: 引擎面接线台账（机读宣告）：R-M1-06 四台至此全接。purity_adjudicator（AI 判净）不属
#: 四台台账（#423 形态锁 standing_by_no_auto_feed，LLM 花钱点 Owner 门，非断链）。
ENGINE_SLOTS_WIRED: Final = (
    "cleaning_rule_engine",
    "cleaning_anomaly_engine",
    "expectation_governance",
    "data_anomaly_alerter",
)

#: 结论消费面实况的机读自述（禁把"能跑"写成"已执法"；同族两腿口径）
ENFORCEMENT_STATE: Final = "advisory_only_half_wired"

#: SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀；标识符经白名单正则后才可入模）
_SQL_TABLE_SAMPLE = (
    "SELECT {cols} FROM {table} WHERE {date_col} "
    "BETWEEN toDate('{start}') AND toDate('{end}') "
    "ORDER BY {date_col} DESC LIMIT {limit}"
)
_SQL_SYMBOL_SERIES = (
    "SELECT {date_col}, {series_cols} FROM {table} WHERE {symbol_col} = %(symbol)s "
    "AND {date_col} BETWEEN toDate('{start}') AND toDate('{end}') "
    "ORDER BY {date_col} ASC LIMIT {limit}"
)

#: 标识符（表名/列名）白名单：只允许库内常规命名，其余=配置错（禁把 YAML 值当 SQL 片段）
_IDENTIFIER_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")

#: 期望类型/严重级别白名单（type 真源=expectation_governance._check 分发表 `_exp_<type>`；
#: severity 真源=validate 三档判定）——引擎面契约面，非判据值；未知值留到运行期才炸=
#: 晚失败，解析期拦=早失败（同族 fail-closed 纪律）
_EXPECTATION_TYPES: Final = frozenset({"schema", "not_null", "range", "distribution", "freshness"})
_EXPECTATION_SEVERITIES: Final = frozenset({"block", "degrade", "warn"})

_EXIT_PARTIAL_DEGRADED: Final = 252
_EXIT_ALL_DEGRADED: Final = 253
_EXIT_CONFIG_ERROR: Final = 254

#: 结论四态（诚实读数真源）——**只有 ran_and_clean 允许 ok=True**（值与同族两腿一致）
STATUS_RAN_CLEAN: Final = "ran_and_clean"
STATUS_RAN_FINDINGS: Final = "ran_with_findings"
STATUS_DEGRADED_PARTIAL: Final = "degraded_partial"
STATUS_NOT_RUN: Final = "not_run"
_OK_STATUS: Final = STATUS_RAN_CLEAN
_INSPECTION_COUNTS_STATUSES: Final = frozenset({STATUS_RAN_CLEAN, STATUS_RAN_FINDINGS})

#: not_run 原因（三把停用闸各有名字，禁与"跑过且干净"混成同一个 ok）
NOT_RUN_WIRING_DISABLED: Final = "wiring_disabled"
NOT_RUN_MASTER_SWITCH_OFF: Final = "master_switch_off"
NOT_RUN_CADENCE_PREFIX: Final = "cadence"

#: 报告与状态台账文件名后缀——台账刻意**不匹配**报告后缀（防"没跑"被节奏闸记成"已巡检"）
_REPORT_SUFFIX: Final = "_expectation_report.json"
_LEDGER_SUFFIX: Final = "_expectation_gate_status_ledger.json"


class ExpectationGateConfigError(Exception):
    """承载册缺失/解析失败/未知键/参数非法/host 不符（fail-closed，绝不静默当已覆盖）。"""


# class-name-alias: 期望托管腿 CH 查询最小协议（与两前腿同名协议同名不同义：本件按表取样+
# 逐符号取序的注入缝，保名以维持各腿测试注入缝独立——同族 cleaning_anomaly_hosting 先例）
class ExpectationQueryExecutor(Protocol):
    """CH 查询执行器最小协议（生产实现=clickhouse_driver.Client，经 DatabaseService 领取）。"""

    def execute(self, sql: str, parameters: dict | None = None) -> list:  # noqa: D102 - 协议即文档
        ...


@dataclass(frozen=True)
class ExpectationWiringConfig:
    """承载册 wiring 块投影（运维参数；键集=本 dataclass 字段，派生校验）。"""

    enabled: bool
    host_schedule: str
    cadence_days: int
    read_limit_rows: int
    rows_per_symbol: int
    watchlist_size: int
    alert_level: str
    report_dir: str
    disabled_flag: str


@dataclass(frozen=True)
class AlerterParams:
    """承载册 alerter 块投影（信号检出判据值唯一真源，逐键交检测器）。"""

    z_threshold: float
    window: int
    missing_warn: float


@dataclass(frozen=True)
class ExpectationTarget:
    """单表检测对象册（targets 条目投影）。"""

    table: str
    date_col: str
    symbol_col: str
    lookback_days: int
    frame_cols: tuple[str, ...] = ("close", "volume")
    check_cols: tuple[str, ...] = ()
    expected_rows: int = 0  # 0=不跑缺失率路（期望行数无真源时不硬造）


@dataclass(frozen=True)
class ExpectationGateRunOptions:
    """门控运行选项束（参数对象——同族 ExpectationGateRunOptions 先例 §5.150）。

    executor/alerter=注入缝（生产默认构造，测试注入假件零真实外呼）；
    ref_date/report_dir/notify 语义与 run_expectation_gate 同名参数逐字一致。
    """

    executor: ExpectationQueryExecutor | None = None
    alerter: Any | None = None  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    ref_date: date | None = None
    report_dir: str | Path | None = None
    notify: bool = True


_WIRING_FIELDS: Final = frozenset(_f.name for _f in fields(ExpectationWiringConfig))
_ALERTER_FIELDS: Final = frozenset(_f.name for _f in fields(AlerterParams))
_TARGET_FIELDS: Final = frozenset(_f.name for _f in fields(ExpectationTarget))


def _config_error(msg: str, **details: Any) -> ExpectationGateConfigError:
    """配置错工厂：路径等敏感/长信息走 details，不进消息文本（MSG-EXPOSURE 同族口径）。"""
    exc = ExpectationGateConfigError(msg)
    for _k, _v in details.items():
        setattr(exc, _k, _v)
    exc.details = details  # type: ignore[attr-defined]
    return exc


def _gate_error(msg: str, **details: Any) -> CleaningGateConfigError:
    """同族解析错工厂（rules 域错误类不接受 kwargs，details 走属性回填——同 rules._config_error 形态）。"""
    exc = CleaningGateConfigError(msg)
    for _k, _v in details.items():
        setattr(exc, _k, _v)
    exc.details = details  # type: ignore[attr-defined]
    return exc


def _check_identifier(value: str, *, where: str) -> str:
    """表名/列名白名单校验（正则与 rules 同族单一语义面，异常回绑本域类型）。"""
    if not _IDENTIFIER_RE.match(value or ""):
        raise _config_error("表名/列名非法（只允许标识符，禁 SQL 片段）", where=where, value=value)
    return value


def _repo_dir(value: str) -> Path:
    """承载册路径口径：相对=锚 REPO_ROOT，绝对=原样（委托 rules 同族原语，语义全等）。"""
    return _rules_repo_relative(value)


def _parse_nonneg_float(value: object, *, where: str) -> float:
    """非负浮点解析（检出阈值面）：bool/非数/负数一律配置错。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _config_error("浮点键须为数值", where=where, value=repr(value))
    val = float(value)
    if val < 0:
        raise _config_error("浮点键须 >=0（负阈值=判据不可信）", where=where, value=val)
    return val


def _parse_col_list(value: object, *, where: str, default: tuple[str, ...], allow_empty: bool) -> tuple[str, ...]:
    """列清单解析（None=默认；非法标识符=配置错；allow_empty=false 时空列表=配置错）。"""
    if value is None:
        return default
    if not isinstance(value, list):
        raise _config_error("列清单须为列表", where=where, value=repr(value))
    cols = tuple(_check_identifier(str(c), where=where) for c in value)
    if not cols and not allow_empty:
        raise _config_error("列清单须非空（空=帧/序列无从构起）", where=where)
    return cols


def _load_rulebook(
    config_path: str | Path | None,
) -> tuple[ExpectationWiringConfig, AlerterParams, list[dict[str, Any]], list[ExpectationTarget]]:
    """承载册 -> (wiring, alerter, expectations, targets)；一切非法在此上抛，不到运行期。

    解析核心委托 cleaning_rules_hosting 同族原语（FUNCTION-DUP 内收，两前腿同先例），
    CleaningGateConfigError 在本函数单点回绑本域 ExpectationGateConfigError（真源消息进
    details.cause，本域消息保域名可读——不逐函数包壳）。
    """
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    try:
        raw = _rules_load_raw(str(path))
        if int(raw.get("schema_version") or 0) != 1:
            raise _config_error("期望承载册 schema_version 须为 1", value=raw.get("schema_version"))
        wiring = _parse_wiring(raw)
        params = _parse_alerter(raw)
        expectations = _parse_expectations(raw)
        targets = _parse_targets(raw)
        return wiring, params, expectations, targets
    except CleaningGateConfigError as exc:
        cause = str(exc.args[0]) if exc.args else str(exc)
        details = dict(getattr(exc, "details", {}) or {})
        raise _config_error("期望承载册非法（判据无真源=本腿不跑，绝不默认放行）", cause=cause, **details) from exc


def _parse_wiring(raw: dict) -> ExpectationWiringConfig:
    """wiring 块投影（运维参数；缺键=配置错，不猜默认值）。"""
    block = raw.get("wiring")
    if not isinstance(block, dict):
        raise _gate_error("期望承载册缺 wiring 块（运维参数无真源=不猜默认值）")
    _rules_reject_unknown_keys(block, legal=_WIRING_FIELDS, where="wiring")
    level = str(_rules_require(block, "alert_level", where="wiring")).upper()
    if level not in _ALLOWED_LEVELS:
        raise _gate_error("alert_level 非法", where="wiring", value=level, legal=sorted(_ALLOWED_LEVELS))
    return ExpectationWiringConfig(
        enabled=_rules_parse_bool(_rules_require(block, "enabled", where="wiring"), where="wiring"),
        host_schedule=str(_rules_require(block, "host_schedule", where="wiring")),
        cadence_days=_rules_parse_positive_int(_rules_require(block, "cadence_days", where="wiring"), where="wiring"),
        read_limit_rows=_rules_parse_positive_int(
            _rules_require(block, "read_limit_rows", where="wiring"), where="wiring.read_limit_rows"
        ),
        rows_per_symbol=_rules_parse_positive_int(
            _rules_require(block, "rows_per_symbol", where="wiring"), where="wiring.rows_per_symbol"
        ),
        watchlist_size=_rules_parse_positive_int(
            _rules_require(block, "watchlist_size", where="wiring"), where="wiring.watchlist_size"
        ),
        alert_level=level,
        report_dir=str(_rules_require(block, "report_dir", where="wiring")),
        disabled_flag=str(_rules_require(block, "disabled_flag", where="wiring")),
    )


def _parse_alerter(raw: dict) -> AlerterParams:
    """alerter 块投影（信号检出判据值；缺键=配置错）。"""
    block = raw.get("alerter")
    if not isinstance(block, dict):
        raise _gate_error("期望承载册缺 alerter 块（检出阈值无真源=不猜默认值）")
    _rules_reject_unknown_keys(block, legal=_ALERTER_FIELDS, where="alerter")
    return AlerterParams(
        z_threshold=_parse_nonneg_float(
            _rules_require(block, "z_threshold", where="alerter"), where="alerter.z_threshold"
        ),
        window=_rules_parse_positive_int(_rules_require(block, "window", where="alerter"), where="alerter.window"),
        missing_warn=_parse_nonneg_float(
            _rules_require(block, "missing_warn", where="alerter"), where="alerter.missing_warn"
        ),
    )


def _parse_expectations(raw: dict) -> list[dict[str, Any]]:
    """期望套件投影（判据册真源：type/column/params/severity 四键面，引擎语义）。"""
    entries = raw.get("expectations")
    if not isinstance(entries, list) or not entries:
        # 空期望套件=本腿无判据却回 ok=True，正是"接线了但什么都不查"的假绿形态
        raise _gate_error("期望承载册 expectations 为空（无判据即上岗=假绿）")
    parsed: list[dict[str, Any]] = []
    for idx, item in enumerate(entries):
        parsed.append(_parse_expectation_entry(item, idx))
    return parsed


def _parse_expectation_entry(item: object, idx: int) -> dict[str, Any]:
    """单条期望投影（未知键/未知类型/非法级别一律配置错——拼错键=该期望静默空转）。"""
    where = f"expectations[{idx}]"
    if not isinstance(item, dict):
        raise _gate_error("期望条目须为映射", where=where, value=repr(item))
    unknown = sorted(set(item) - {"type", "column", "params", "severity"})
    if unknown:
        raise _gate_error("期望条目含未知键", where=where, unknown=unknown)
    etype = str(_rules_require(item, "type", where=where))
    if etype not in _EXPECTATION_TYPES:
        raise _gate_error(
            "期望类型非法（引擎分发表未知=运行期才炸，解析期拦）",
            where=where,
            value=etype,
            legal=sorted(_EXPECTATION_TYPES),
        )
    column = _check_identifier(str(_rules_require(item, "column", where=where)), where=f"{where}.column")
    severity = str(item.get("severity", "warn"))
    if severity not in _EXPECTATION_SEVERITIES:
        raise _gate_error(
            "期望严重级别非法（block/degrade/warn）", where=where, value=severity, legal=sorted(_EXPECTATION_SEVERITIES)
        )
    params = item.get("params") or {}
    if not isinstance(params, dict):
        raise _gate_error("期望 params 须为映射", where=where, value=repr(params))
    return {"type": etype, "column": column, "params": params, "severity": severity}


def _parse_targets(raw: dict) -> list[ExpectationTarget]:
    """targets 块投影（检测对象清单；空清单=无对象可判，禁当已覆盖）。"""
    entries = raw.get("targets")
    if not isinstance(entries, list) or not entries:
        raise _gate_error("期望承载册 targets 为空（无检测对象）")
    return [_parse_target_entry(entry, idx) for idx, entry in enumerate(entries)]


def _parse_target_entry(entry: object, idx: int) -> ExpectationTarget:
    """单表对象投影（标识符白名单+正整数窗口+列面派生）。"""
    where = f"targets[{idx}]"
    if not isinstance(entry, dict):
        raise _gate_error("targets 条目须为映射", where=where, value=repr(entry))
    _rules_reject_unknown_keys(entry, legal=_TARGET_FIELDS, where=where)
    table = _check_identifier(str(_rules_require(entry, "table", where=where)), where=f"{where}.table")
    date_col = _check_identifier(str(_rules_require(entry, "date_col", where=where)), where=f"{where}.date_col")
    symbol_col = _check_identifier(str(_rules_require(entry, "symbol_col", where=where)), where=f"{where}.symbol_col")
    lookback = _rules_parse_positive_int(
        _rules_require(entry, "lookback_days", where=where), where=f"{where}.lookback_days"
    )
    frame_cols = _parse_col_list(
        entry.get("frame_cols"), where=f"{where}.frame_cols", default=("close", "volume"), allow_empty=False
    )
    check_cols = _parse_col_list(entry.get("check_cols"), where=f"{where}.check_cols", default=(), allow_empty=True)
    expected_rows = int(entry.get("expected_rows") or 0)
    if expected_rows < 0:
        raise _gate_error("expected_rows 须 >=0（0=不跑缺失率路）", where=where, value=expected_rows)
    return ExpectationTarget(
        table=table,
        date_col=date_col,
        symbol_col=symbol_col,
        lookback_days=lookback,
        frame_cols=frame_cols,
        check_cols=check_cols,
        expected_rows=expected_rows,
    )


def load_rulebook(
    config_path: str | Path | None = None,
) -> tuple[ExpectationWiringConfig, AlerterParams, list[dict[str, Any]], list[ExpectationTarget]]:
    """承载册加载公共入口（CLI 与托管门共用；一切非法在此上抛）。"""
    return _load_rulebook(config_path)


def _default_executor() -> ExpectationQueryExecutor:
    """CH 只读连接——全仓唯一 Client 构造点 DatabaseService（宪法 §9.1 禁裸连接）。"""
    from zephyr.infrastructure.database_service import get_db_service

    conn = get_db_service().get_clickhouse_conn(role="reader", slot="cleaning_expectation_hosting")
    return conn  # 本腿槽位独立于前两腿（slot 名即隔离面），连接对象同源


def _window_span(target: ExpectationTarget, ref: date) -> tuple[str, str]:
    """近窗 [start, end] 日期对面（自然日窗，窗口值在册非在码）。"""
    span = max(target.lookback_days - 1, 0)
    start = date.fromordinal(ref.toordinal() - span)
    return start.isoformat(), ref.isoformat()


def _fetch_table_sample(
    executor: ExpectationQueryExecutor, target: ExpectationTarget, wiring: ExpectationWiringConfig, *, ref: date
) -> list[dict[str, Any]]:
    """表级近窗样本（日期降序 LIMIT read_limit_rows；列面全由承载册派生，代码零列名）。"""
    cols = list(dict.fromkeys([target.date_col, target.symbol_col, *target.check_cols]))
    start, end = _window_span(target, ref)
    sql = _SQL_TABLE_SAMPLE.format(
        cols=", ".join(cols),
        table=target.table,
        date_col=target.date_col,
        start=start,
        end=end,
        limit=wiring.read_limit_rows,
    )
    rows = executor.execute(sql) or []
    return [dict(zip(cols, row, strict=False)) for row in rows]


def _fetch_symbol_series(
    executor: ExpectationQueryExecutor,
    target: ExpectationTarget,
    symbol: str,
    wiring: ExpectationWiringConfig,
    *,
    ref: date,
) -> list[dict[str, Any]]:
    """单标的近窗序列（升序 LIMIT rows_per_symbol；列面=date+frame_cols）。"""
    start, end = _window_span(target, ref)
    sql = _SQL_SYMBOL_SERIES.format(
        date_col=target.date_col,
        series_cols=", ".join(target.frame_cols),
        table=target.table,
        symbol_col=target.symbol_col,
        start=start,
        end=end,
        limit=wiring.rows_per_symbol,
    )
    rows = executor.execute(sql, {"symbol": symbol}) or []
    cols = [target.date_col, *target.frame_cols]
    return [dict(zip(cols, row, strict=False)) for row in rows]


def _frame_from_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """样本行组→期望校验帧（列面=行键，dtype 由引擎侧 to_numeric/isna 兜底）。"""
    import pandas as pd

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def _clean_floats(rows: list[dict[str, Any]], col: str) -> list[float]:
    """序列行组→浮点列表（None/NaN/非数剔除——禁让空值进 numpy 对数运算）。"""
    out: list[float] = []
    for row in rows:
        val = row.get(col)
        if val is None:
            continue
        try:
            num = float(val)
        except (TypeError, ValueError):
            continue
        if num == num:  # NaN!=NaN，剔除
            out.append(num)
    return out


# FUNCTION-DUP 内收（w5_1 同真源必并）：gate_status/status_exit_code 与第三段
# cleaning_anomaly_hosting 同构同语义（四态值同源），单实现委托导入+re-export，
# 本件不再持第二副本。
from zephyr.data.cleaning_anomaly_hosting import (
    gate_status,
    status_exit_code,
)


def _expectation_leg(
    target: ExpectationTarget,
    expectations: list[dict[str, Any]],
    sample_rows: list[dict[str, Any]],
    *,
    archive_path: Path | None,
    entry: dict[str, Any],
) -> None:
    """期望套件校验腿（表样本 → 门面 validate_expectations；结果写进 entry）。"""
    from zephyr.data.cleaning_engines import validate_expectations
    from zephyr.data_eng.expectation_governance import Expectation

    frame_cols = set(sample_rows[0]) if sample_rows else set()
    covered = [e for e in expectations if e["column"] in frame_cols]
    entry["expectation_uncovered"] = sorted(set(e["column"] for e in expectations) - set(e["column"] for e in covered))
    if not sample_rows:
        entry["no_samples"] = True
        return
    exps = [
        Expectation(type=e["type"], column=e["column"], params=e["params"], severity=e["severity"]) for e in covered
    ]
    report = validate_expectations(
        _frame_from_rows(sample_rows), exps, suite_name=target.table, archive_path=archive_path
    )
    failed = [
        {
            "type": r.expectation.type,
            "column": r.expectation.column,
            "severity": r.expectation.severity,
            "detail": r.detail,
        }
        for r in report.results
        if not r.passed
    ]
    entry["expectation_verdict"] = report.verdict.value
    entry["expectation_failed"] = failed
    entry["findings_count"] += len(failed)


def _alerter_leg(
    executor: ExpectationQueryExecutor,
    target: ExpectationTarget,
    wiring: ExpectationWiringConfig,
    params: AlerterParams,
    symbols: list[str],
    *,
    ref: date,
    entry: dict[str, Any],
    alert_sink: Any | None,  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
) -> None:
    """信号告警腿（逐标的 price_jump(+missing_rate) → 门面 evaluate_anomaly_signals 分级路由）。"""
    from zephyr.data.cleaning_engines import evaluate_anomaly_signals
    from zephyr.data_eng.data_anomaly_alerter import detect_missing_rate, detect_price_jumps

    signals: list[Any] = []
    checked = 0
    short: list[str] = []
    errors: list[str] = []
    for symbol in symbols:
        try:
            rows = _fetch_symbol_series(executor, target, symbol, wiring, ref=ref)
        except Exception as ex:  # noqa: BLE001 — 单标的取数异常只降级该标的，不中断全批
            errors.append(f"{symbol}: {str(ex)[:120]}")
            continue
        closes = _clean_floats(rows, target.frame_cols[0])
        if len(closes) < params.window + 2:
            short.append(symbol)
            continue
        checked += 1
        signals.extend(detect_price_jumps(closes, symbol, z_threshold=params.z_threshold, window=params.window))
        if target.expected_rows > 0:
            # actual 钳到 expected（行数超期望=零缺失语义；禁喂 actual>expected 触引擎 fail-closed）
            actual = min(len(rows), target.expected_rows)
            signals.extend(detect_missing_rate(target.expected_rows, actual, symbol, warn=params.missing_warn))
    entry["symbols_checked"] = checked
    entry["short_series_symbols"] = short
    if errors:
        entry["degraded"] = True
        entry["error"] = "; ".join(errors)[:200]
    if not signals:
        return
    alerts, _events = evaluate_anomaly_signals(
        signals, now_utc=now_utc(), source="cleaning_expectation_hosting", alert_sink=alert_sink
    )
    entry["alerts"] = [
        {
            "kind": a.signal.kind.value,
            "symbol": a.signal.symbol,
            "grade": a.grade.value,
            "silenced": a.silenced,
            "metric_value": a.signal.metric_value,
            "threshold": a.signal.threshold,
            "detail": a.signal.detail,
        }
        for a in alerts
    ]
    entry["findings_count"] += len(entry["alerts"])


def _evaluate_target(
    executor: ExpectationQueryExecutor,
    wiring: ExpectationWiringConfig,
    params: AlerterParams,
    expectations: list[dict[str, Any]],
    target: ExpectationTarget,
    *,
    ref: date,
    archive_path: Path | None,
    alert_sink: Any | None,  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
) -> dict[str, Any]:
    """单表双腿校验（期望腿+信号腿；单表异常只降级，不中断全批）。"""
    entry: dict[str, Any] = {
        "table": target.table,
        "degraded": False,
        "no_samples": False,
        "rows_read": 0,
        "expectation_uncovered": [],
        "expectation_verdict": "",
        "expectation_failed": [],
        "symbols_checked": 0,
        "short_series_symbols": [],
        "alerts": [],
        "findings_count": 0,
    }
    try:
        sample_rows = _fetch_table_sample(executor, target, wiring, ref=ref)
        entry["rows_read"] = len(sample_rows)
        _expectation_leg(target, expectations, sample_rows, archive_path=archive_path, entry=entry)
        if not entry["no_samples"]:
            symbols = sorted(
                {str(r.get(target.symbol_col)) for r in sample_rows if r.get(target.symbol_col) is not None}
            )
            _alerter_leg(
                executor,
                target,
                wiring,
                params,
                symbols[: wiring.watchlist_size],
                ref=ref,
                entry=entry,
                alert_sink=alert_sink,
            )
    except Exception as ex:  # noqa: BLE001 — 单表校验异常只降级该表
        entry["degraded"] = True
        entry["error"] = str(ex)[:200]
        log.exception("期望托管腿单表校验失败: %s", target.table)
    return entry


def run_expectation_gate(
    wiring: ExpectationWiringConfig,
    params: AlerterParams,
    expectations: list[dict[str, Any]],
    targets: list[ExpectationTarget],
    options: ExpectationGateRunOptions | None = None,
) -> dict:
    """逐表期望校验+逐标的信号检出（只读出报告），返回报告 dict。

    options=None 时全缺省（executor/alerter 自动构造、当日、默认报告目录、出声）——
    与同族 run_anomaly_gate 参数对象化口径一致（§5.150）。
    """
    opts = options if options is not None else ExpectationGateRunOptions()
    executor = opts.executor or _default_executor()
    ref = opts.ref_date or now_utc().astimezone(_SHANGHAI_TZ).date()
    out_dir = Path(opts.report_dir) if opts.report_dir else _repo_dir(wiring.report_dir)
    archive_path = out_dir / "expectation_archive.jsonl"
    alert_sink = _resolve_alert_sink(opts)

    results = [
        _evaluate_target(
            executor, wiring, params, expectations, t, ref=ref, archive_path=archive_path, alert_sink=alert_sink
        )
        for t in targets
    ]

    report = _build_report(wiring, targets, results, ref=ref)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{ref.isoformat()}{_REPORT_SUFFIX}"
    safe_write_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, default=str))
    report["report_path"] = str(report_path)
    if opts.notify and opts.alerter is not None:
        _notify_results(opts.alerter, wiring, report)
    return report


def _resolve_alert_sink(opts: ExpectationGateRunOptions) -> Any | None:  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    """alert_sink 三态仲裁：不出声=哑槽（禁引擎默认 Alerter 悄悄外呼）；出声+有宿主=宿主 notify；
    出声+无宿主=None（交引擎默认通道——CLI 独立运行形态）。"""
    if not opts.notify:
        return lambda *args, **kwargs: True
    if opts.alerter is not None:
        return opts.alerter.notify
    return None


def _build_report(
    wiring: ExpectationWiringConfig,
    targets: list[ExpectationTarget],
    results: list[dict[str, Any]],
    *,
    ref: date,
) -> dict[str, Any]:
    """报告 dict 组装（含诚实四态判定与降级/零样本清单）。"""
    status = gate_status(results)
    empty_targets = not results and bool(targets)
    if empty_targets:
        # 近窗样本零行=跑了却无对象可判（表空/窗口写歪/列错）——归 degraded_partial 禁当 not_run
        status = STATUS_DEGRADED_PARTIAL
    findings_count = sum(int(r.get("findings_count") or 0) for r in results)
    return {
        "gate": "cleaning_expectation_hosting",
        "schema_version": 1,
        "host_schedule": wiring.host_schedule,
        "ref_date": ref.isoformat(),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "read_side_only": True,
        "repair_invoked": False,
        "status": status,
        "inspection_ran": status in _INSPECTION_COUNTS_STATUSES,
        "engine_slots": {"wired": list(ENGINE_SLOTS_WIRED)},
        "targets_checked": [t.table for t in targets],
        "findings_count": findings_count,
        "empty_targets": empty_targets,
        "all_degraded": bool(results) and all(r["degraded"] for r in results),
        "degraded_tables": [r["table"] for r in results if r["degraded"]],
        "no_sample_tables": [r["table"] for r in results if not r["degraded"] and r["no_samples"]],
        "results": results,
        "enforcement_state": ENFORCEMENT_STATE,
    }


def _notify_results(alerter: Any, wiring: ExpectationWiringConfig, report: dict) -> None:  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    """报告告警面（读侧只出声不执法）：降级/零样本/期望失败/信号命中各走 _alert 唯一正门。"""
    for res in report["results"]:
        if res["degraded"]:
            _alert(
                alerter,
                wiring.alert_level,
                f"期望门控未生效: {res['table']} [{res.get('error')}]",
                extra={"table": res["table"]},
            )
            continue
        if res["no_samples"]:
            _alert(
                alerter,
                LEVEL_WARN,
                f"期望门控零样本（无校验对象，不得当已巡检干净）: {res['table']}",
                extra={"table": res["table"]},
            )
        for failed in res["expectation_failed"]:
            _alert(
                alerter,
                wiring.alert_level,
                f"期望失败: {res['table']} {failed['type']}({failed['column']}) severity={failed['severity']}: {failed['detail']}"
                "（读侧只出声，未改生产数据）",
                extra={"table": res["table"], "expectation": failed["type"], "column": failed["column"]},
            )
        if res["alerts"]:
            by_kind: dict[str, int] = {}
            for a in res["alerts"]:
                by_kind[a["kind"]] = by_kind.get(a["kind"], 0) + 1
            _alert(
                alerter,
                wiring.alert_level,
                f"信号命中: {res['table']} alerts={len(res['alerts'])} by_kind={by_kind}（分级路由已由引擎走 alert_sink）",
                extra={"table": res["table"], "by_kind": by_kind},
            )
    if report["status"] == STATUS_DEGRADED_PARTIAL:
        _alert(
            alerter,
            LEVEL_WARN,
            "期望门控读数降级（status=degraded_partial，禁冒 ok=True）: "
            f"degraded={report['degraded_tables']} no_samples={report['no_sample_tables']}",
            extra={"status": report["status"]},
        )


def _alert(alerter: Any, level: str, message: str, *, extra: dict) -> None:  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    """告警唯一正门=Alerter.notify（禁自造通道）；通道故障只 log 不抛。"""
    try:
        alerter.notify(
            "cleaning_expectation_gate", message, level=level, source="cleaning_expectation_hosting", extra=extra
        )
    except Exception:  # noqa: BLE001 — 告警通道故障不阻断巡检
        log.exception("期望门控告警写入失败")


def _latest_report_date(report_dir: Path) -> date | None:
    """最近一次**真巡检**日（节奏闸状态真源=报告文件名前 10 字符，但**须验正文**防空文件催眠）。"""
    if not report_dir.is_dir():
        return None
    dates: list[date] = []
    for path in sorted(report_dir.glob(f"*{_REPORT_SUFFIX}")):
        try:
            stamp = date.fromisoformat(path.name[:10])
        except ValueError:
            continue
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as ex:
            log.warning("期望门控节奏闸状态文件不可读，不记为已巡检: %s", str(ex)[:120])
            continue
        if not isinstance(body, dict) or body.get("gate") != "cleaning_expectation_hosting":
            log.warning("期望门控节奏闸状态文件 gate 不自对，不记为已巡检: %s", path)
            continue
        if body.get("status") not in _INSPECTION_COUNTS_STATUSES or not body.get("inspection_ran"):
            log.warning("期望门控上次读数非「真跑完」（status=%s），不占节奏闸", body.get("status"))
            continue
        dates.append(stamp)
    return max(dates) if dates else None


def _write_status_ledger(out_dir: Path, *, ref: date, status: str, reason: str, wiring: ExpectationWiringConfig) -> str:
    """未跑/降级台账（必留痕；文件名刻意不匹配报告后缀，防被节奏闸读成"当天已巡检"）。"""
    payload: dict[str, Any] = {
        "gate": "cleaning_expectation_hosting",
        "schema_version": 1,
        "host_schedule": wiring.host_schedule,
        "ref_date": ref.isoformat(),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "status": status,
        "reason": reason,
        "inspection_ran": False,
        "ok": status == _OK_STATUS,
        "enforcement_state": ENFORCEMENT_STATE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ref.isoformat()}{_LEDGER_SUFFIX}"
    safe_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return str(path)


def _not_run(
    wiring: ExpectationWiringConfig,
    *,
    out_dir: Path,
    ref: date,
    alerter: Any,  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    reason: str,
    note: str,
) -> dict[str, Any]:
    """「根本没跑」的统一诚实出口：ok=False + status=not_run + 出声 + 台账（三者缺一不可）。"""
    ledger_path = _write_status_ledger(out_dir, ref=ref, status=STATUS_NOT_RUN, reason=reason, wiring=wiring)
    log.warning("期望门控未执行（status=not_run reason=%s）：%s", reason, note)
    _alert(
        alerter,
        LEVEL_WARN,
        f"期望门控未执行（status=not_run，禁当已巡检）: reason={reason} {note}",
        extra={"not_run_reason": reason},
    )
    return {
        "ok": False,
        "status": STATUS_NOT_RUN,
        "not_run_reason": reason,
        "skipped": reason,  # 旧键保留（既有运维/普查按它分类），但不再伴随 ok=True
        "reason": note,
        "inspection_ran": False,
        "enforcement_state": ENFORCEMENT_STATE,
        "ledger_path": ledger_path,
        "ref_date": ref.isoformat(),
    }


def run_hosted_expectation_gate(
    alerter: Any | None = None,  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    *,
    config_path: str | Path | None = None,
    report_dir: str | Path | None = None,
    ref_date: date | None = None,
    executor: ExpectationQueryExecutor | None = None,
    host_schedule: str = "data_supply_sentinel",
    force: bool = False,
) -> dict:
    """由 L13 `data_supply_sentinel` 排班腿托管的期望门控（四要素正门形态）。

    全程不抛：配置错/故障 → {ok: False, ...} + 出声（宿主只读键，不改宿主既有结论）。
    """
    if alerter is None:
        from zephyr.data.alerter import Alerter

        alerter = Alerter()
    try:
        wiring, params, expectations, targets = load_rulebook(config_path)
    except ExpectationGateConfigError as ex:
        # fail-closed：判据不可信时绝不回"干净"
        log.error("期望承载册配置错误: %s details=%s", ex, getattr(ex, "details", None))
        _alert(alerter, LEVEL_ERROR, f"期望门控未执行（承载册故障）: {str(ex)[:200]}", extra={"config_error": True})
        return {
            "ok": False,
            "status": STATUS_NOT_RUN,
            "not_run_reason": "config_error",
            "inspection_ran": False,
            "config_error": str(ex),
            "details": getattr(ex, "details", None),
            "enforcement_state": ENFORCEMENT_STATE,
        }

    out_dir = Path(report_dir) if report_dir else _repo_dir(wiring.report_dir)
    ref = ref_date or now_utc().astimezone(_SHANGHAI_TZ).date()
    try:
        if wiring.host_schedule != host_schedule:
            raise ExpectationGateConfigError(f"承载册声明宿主={wiring.host_schedule} 与实调宿主={host_schedule} 不符")
        if not force and not wiring.enabled:
            return _not_run(
                wiring,
                out_dir=out_dir,
                ref=ref,
                alerter=alerter,
                reason=NOT_RUN_WIRING_DISABLED,
                note="承载册 wiring.enabled=false（总闸停用，本次零校验）",
            )
        flag_path = _repo_dir(wiring.disabled_flag)
        if flag_path.exists() and not force:
            return _not_run(
                wiring,
                out_dir=out_dir,
                ref=ref,
                alerter=alerter,
                reason=NOT_RUN_MASTER_SWITCH_OFF,
                note="停用标记存在（自动关闭闸，本次零校验）",
            )
        if not force:
            last = _latest_report_date(out_dir)
            if last is not None and (ref - last).days < wiring.cadence_days:
                return _not_run(
                    wiring,
                    out_dir=out_dir,
                    ref=ref,
                    alerter=alerter,
                    reason=f"{NOT_RUN_CADENCE_PREFIX}_{wiring.cadence_days}d_last_{last.isoformat()}",
                    note=f"距上次巡检 {last.isoformat()} 不足 {wiring.cadence_days}d",
                )
        report = run_expectation_gate(
            wiring,
            params,
            expectations,
            targets,
            ExpectationGateRunOptions(executor=executor, alerter=alerter, ref_date=ref, report_dir=out_dir),
        )
    except ExpectationGateConfigError as ex:
        log.error("期望门控配置错误: %s", ex)
        _alert(
            alerter, wiring.alert_level, f"期望门控未执行（配置故障）: {str(ex)[:200]}", extra={"config_error": True}
        )
        return {
            "ok": False,
            "status": STATUS_NOT_RUN,
            "not_run_reason": "config_error",
            "inspection_ran": False,
            "config_error": str(ex),
            "enforcement_state": ENFORCEMENT_STATE,
        }
    except Exception as exc:  # noqa: BLE001 — 托管腿故障出声不阻断宿主断供结论
        log.exception("期望门控托管腿失败")
        _alert(alerter, wiring.alert_level, f"期望门控未执行（腿故障）: {str(exc)[:200]}", extra={"leg_error": True})
        return {
            "ok": False,
            "status": STATUS_NOT_RUN,
            "not_run_reason": "leg_error",
            "inspection_ran": False,
            "error": str(exc)[:200],
            "enforcement_state": ENFORCEMENT_STATE,
        }

    status = str(report["status"])
    log.info(
        "期望门控巡检完成: status=%s targets=%d findings=%d degraded=%d no_samples=%d",
        status,
        len(report["targets_checked"]),
        report["findings_count"],
        len(report["degraded_tables"]),
        len(report["no_sample_tables"]),
    )
    return {
        "ok": status == _OK_STATUS,
        "status": status,
        "inspection_ran": bool(report["inspection_ran"]),
        "findings_count": report["findings_count"],
        "targets_checked": report["targets_checked"],
        "degraded_tables": report["degraded_tables"],
        "no_sample_tables": report["no_sample_tables"],
        "all_degraded": report["all_degraded"],
        "empty_targets": report["empty_targets"],
        "report_path": report.get("report_path"),
        "ref_date": ref.isoformat(),
        "enforcement_state": ENFORCEMENT_STATE,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI 入口（运维手动复查）。exit code：0=跑过且判干净｜N=命中数｜
    252=部分降级/零样本/未跑（禁当绿）｜253=全批降级｜254=配置错。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.cleaning_expectation_hosting",
        description="期望门控+信号告警托管腿：按 config/cleaning_expectations.yaml 逐表期望校验+逐标的信号检出（只读不修）",
    )
    parser.add_argument("--config", default=None, help=f"承载册路径（默认 {_DEFAULT_CONFIG_PATH}）")
    parser.add_argument("--report-dir", default=None, help="报告目录覆盖（默认取承载册 report_dir）")
    parser.add_argument("--no-alert", action="store_true", help="只检测不发告警")
    parser.add_argument("--force", action="store_true", help="跳过节奏闸与停用标记")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        wiring, params, expectations, targets = load_rulebook(args.config)
    except ExpectationGateConfigError as ex:
        log.critical("期望承载册配置错误: %s details=%s", ex, getattr(ex, "details", None))
        return _EXIT_CONFIG_ERROR
    cli_alerter = None
    if not args.no_alert:
        from zephyr.data.alerter import Alerter

        cli_alerter = Alerter()
    report = run_expectation_gate(
        wiring,
        params,
        expectations,
        targets,
        ExpectationGateRunOptions(alerter=cli_alerter, report_dir=args.report_dir, notify=not args.no_alert),
    )
    if report["all_degraded"]:
        log.critical("期望门控全批降级，巡检未生效（status=%s）", report["status"])
        return _EXIT_ALL_DEGRADED
    return status_exit_code(str(report["status"]), findings_count=int(report["findings_count"]))


if __name__ == "__main__":
    raise SystemExit(main())
