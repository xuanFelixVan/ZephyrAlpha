# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cleaning_anomaly_hosting
# [DOMAIN] D_DATA
# [TTL] permanent
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/zephyr/data/test_cleaning_anomaly_hosting.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# noqa: m11-perm-manual-legitimate  M11豁免: 本件=supply_sentinel 排班腿托管第三段消费侧事件链接线（L13 data_supply_sentinel），CLI 独立运行面=运维按需 runner（非 cron/非 daemon/非常驻服务，#ARCH-P3-FOLLOWUP-TODOS-001 裁定 B/C 通道；死袋 q-20260930-st-c9-finalw-0001 死因处置，st-c9-finalw 重投）
# create-guard-not-dup: 本件=D_DATA 域清洗异常排班托管腿（承载册判据驱动只读检测+告警，
#   禁修数），非 depgraph 领域应用/密钥供给/回测过拟合检测/YAML 锚点扫描/C1 比较器等
#   在册能力的第二实现；波13·包13.1 命中词（table target/config error）均为模块
#   docstring 泛化 bigram 误中（死袋 q-20260930-st-c9-final3-0003 死因处置，st-c9-finalw 重投）
# [ERROR_CONTRACT] 承载册缺失/解析失败/未知键/参数非法/host 不符->AnomalyGateConfigError（CLI exit 254）；
#   单标的取数或检测异常->该标的 degraded 不中断全批；全批 degraded->CLI exit 253；
#   not_run/degraded_partial->托管腿 ok=False 禁冒绿（同族 cleaning_rules_hosting 口径）
# [DEPENDENCIES] zephyr.data_eng.cleaning_anomaly_engine(五类检出真身); zephyr.data.alerter(告警唯一正门);
#   zephyr.infrastructure.database_service(懒加载, CH 只读唯一入口); zephyr.shared.io.file_utils(safe_write_text);
#   zephyr.shared.io.paths; zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] zephyr.data.supply_sentinel.run_supply_sentinel -> _run_hosted_anomaly_gate
#   （L13 data_supply_sentinel 排班腿托管第三段，R-M1-06 逐引擎接线第二台 2026-09-28）；CLI 独立运行
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] 判据值唯一真源=config/cleaning_anomaly_rules.yaml（宪法硬规则 6 RULE-SSOT，代码禁写
#   跳变阈值/倍数/窗口/限额任何判据值，改册即改行为）;
#   只读检测禁修数：本腿只跑 engine.detect 出报告+告警，**禁调 engine.repair**（修复=改生产数据，
#   属 Owner 门位；repair 语义留待写侧批）;
#   CH 访问唯一入口=DatabaseService.get_clickhouse_conn(role=reader)，禁裸连接（宪法 §9.1）;
#   读侧安全阀双闸=watchlist_size（标的数上限）×rows_per_symbol（单标的行数上限），全在承载册，
#   禁对亿行表无界 SELECT（R-M1-06 处方"读侧代价与窗口口径未定不硬接"的落地口径）;
#   未知键=配置错上抛（键集由 dataclass 字段派生，禁手工清单——宪法 §9.5）;
#   YAML 缺失/解析失败/参数非法/host_schedule 与实调方不符/表清单空=**fail-closed**：
#     抛 AnomalyGateConfigError，托管腿 ok=False 并出声，绝不返回"干净";
#   单标的异常=degraded 不中断全批；全批 degraded=巡检未生效 ok=False（禁谎报绿）;
#   检出面诚实：标的帧缺检出前提列（close/volume/adj_factor 全缺）=coverage=none 记 degraded，
#     禁把"没得检"当"检过干净"（cleaning_rules_hosting no_samples 同族防线）;
#   结论四态=ran_and_clean｜ran_with_findings｜degraded_partial｜not_run，**只有 ran_and_clean 允许 ok=True**;
#   节奏闸状态真源=报告文件名前 10 字符且**须验正文**（gate 自对+inspection_ran，防空文件催眠）;
#   当前时间统一 now_utc() 入口（RULE-SCHEMA-TZ）；报告经 safe_write_text 落盘;
#   引擎面宣告（四引擎接线台账）：本腿 wired=[cleaning_anomaly_engine]，此前已接
#     cleaning_rule_engine（cleaning_rules_hosting 托管第二段）；2026-10-01 F04 P0 断链
#     收口：expectation_governance+data_anomaly_alerter 由 cleaning_expectation_hosting
#     托管第四段接成（四台全接，本件 RESERVED 归空，普查器以各腿 wired 字段对账）
"""清洗异常引擎排班托管腿（R-M1-06 逐引擎接线第二台；裁定 #423 F04 判净站前置体）。

诞生背景（实证册 docs/_working/fullflow_mining/m1_data/wiring_C_cleaning.md §七"未完=如实报红"）：
cleaning_anomaly_engine（404 行五类检出+修复闭环+13 例测试）自晋升批起零生产调用点，
wiring_C 车道按 R-M1-06"先接线（DSL 载体 YAML + 一处调用点）再谈其余"只接了 rule_engine，
本件补第二台：宿主=同一条 L13 data_supply_sentinel 排班腿的**托管第三段**
（同族先例 quality_sweep/cleaning_gate，不新建平行管线、不新开排班槽位——R-021）。

R-M1-06 处方缺口（"anomaly engine 需按 symbol 取 OHLCV 帧，读侧代价与窗口口径未定"）的落地口径：
  窗口口径 = 承载册 lookback_days 自然日窗 + rows_per_symbol 单标的行数上限
  标的口径 = watchlist_size 上限内 SELECT DISTINCT symbol（确定性机械选取，册内可改）
  代价口径 = 全批读取上界 ≈ watchlist_size × rows_per_symbol 行（两闸都在册，代码零判据值）

读侧 flag 档（出厂态，"新能力默认不改变既有产出"承诺）：本腿只 SELECT+detect 出**报告与告警**；
不写库、不剔行、不改 ch_writer 写路径、**不调 repair**（修复闭环属写侧，Owner 门位）。

诚实边界：本腿检出的是"帧内统计异常"（跳变/量能/缺失/复权断点/重复 bar），判定建议只进
报告与告警面，不进排班判定（同 cleaning_gate=advisory_only_half_wired 家族，接线一行=总筹待登）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 承载册 config/cleaning_anomaly_rules.yaml（wiring+engines+targets，判据值唯一真源）
# - id: I2
#   name: CH 近窗行（DatabaseService 只读连接；标的清单=DISTINCT 符号×watchlist_size，帧按 symbol 分组）
# 层: 处理
# - id: P1
#   name: load_anomaly_rulebook 校验（schema_version/未知键/数值合法性；非法=AnomalyGateConfigError fail-closed）
# - id: P2
#   name: _evaluate_symbol 逐标的构帧（trade_date 升序 index）→ CleaningAnomalyEngine.detect（只检不修）
# - id: P3
#   name: gate_status 诚实四态（检出前提列全缺=degraded，禁冒绿）
# 层: 输出
# - id: O1
#   name: 报告 JSON（safe_write_text 落 report_dir；文件名前 10 字符=节奏闸状态真源）
# - id: O2
#   name: _notify_results 告警面（降级/零覆盖/命中，只出声不执法）
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
from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Protocol
from zoneinfo import ZoneInfo

import yaml

from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, LEVEL_INFO, LEVEL_WARN
from zephyr.data_eng.cleaning_anomaly_engine import AnomalyFinding, CleaningAnomalyEngine
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    import pandas as pd

log = logging.getLogger(__name__)

#: 业务日界口径（同族 cleaning_rules_hosting；禁 datetime.now() 散落，RULE-SCHEMA-TZ）
_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

__all__: Final = [
    "AnomalyGateConfigError",
    "STATUS_DEGRADED_PARTIAL",
    "STATUS_NOT_RUN",
    "STATUS_RAN_CLEAN",
    "STATUS_RAN_FINDINGS",
    "ENGINE_SLOTS_RESERVED",
    "ENGINE_SLOTS_WIRED",
    "ENFORCEMENT_STATE",
    "AnomalyWiringConfig",
    "EngineParams",
    "GateRunOptions",
    "TableTarget",
    "gate_status",
    "load_anomaly_rulebook",
    "run_anomaly_gate",
    "run_hosted_anomaly_gate",
    "status_exit_code",
    "main",
]

_DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "cleaning_anomaly_rules.yaml"

#: 告警级别合法集（由 alerter 常量派生，禁自造通道/自写级别名）
_ALLOWED_LEVELS: Final = frozenset({LEVEL_INFO, LEVEL_WARN, LEVEL_ERROR, LEVEL_CRITICAL})

#: 引擎面接线台账（机读宣告：wired=已挂生产调用点；reserved=接口位预留未接，
#: 普查器据此对账）。2026-10-01 F04 P0 断链收口：后两台由 cleaning_expectation_hosting
#: 托管第四段接成，本腿 RESERVED 归空（历史预留已清偿）。
ENGINE_SLOTS_WIRED: Final = (
    "cleaning_rule_engine",
    "cleaning_anomaly_engine",
    "expectation_governance",
    "data_anomaly_alerter",
)
ENGINE_SLOTS_RESERVED: Final = ()

#: 结论消费面实况的机读自述（禁把"能跑"写成"已执法"；同族 cleaning_rules_hosting 口径）
ENFORCEMENT_STATE: Final = "advisory_only_half_wired"

#: SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_DISTINCT_SYMBOLS = (
    "SELECT DISTINCT {symbol_col} FROM {table} WHERE {date_col} "
    "BETWEEN toDate('{start}') AND toDate('{end}') ORDER BY {symbol_col} LIMIT {limit}"
)
_SQL_FETCH_SYMBOL_FRAME = (
    "SELECT {date_col}, {frame_cols} FROM {table} WHERE {symbol_col} = %(symbol)s "
    "AND {date_col} BETWEEN toDate('{start}') AND toDate('{end}') "
    "ORDER BY {date_col} ASC LIMIT {limit}"
)

#: 标识符（表名/列名）白名单：只允许库内常规命名，其余=配置错（禁把 YAML 值当 SQL 片段）
_IDENTIFIER_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")

#: 引擎检出前提列→规则覆盖面（逐标的诚实 coverage 判定真源；缺前提列的规则=未检非干净）
_RULE_PRECONDITION_COLS: Final = {
    "price_jump": ("close",),
    "adj_break": ("adj_factor",),
    "duplicate_bar": (),  # 仅需 index，恒可检
    "volume_spike": ("volume",),
    "missing_pattern": ("open", "high", "low", "close", "volume"),  # 任一在即检
}

_EXIT_PARTIAL_DEGRADED: Final = 252
_EXIT_ALL_DEGRADED: Final = 253
_EXIT_CONFIG_ERROR: Final = 254

#: 结论四态（诚实读数真源）——**只有 ran_and_clean 允许 ok=True**
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
_REPORT_SUFFIX: Final = "_anomaly_report.json"
_LEDGER_SUFFIX: Final = "_anomaly_gate_status_ledger.json"


class AnomalyGateConfigError(Exception):
    """承载册缺失/解析失败/未知键/参数非法/host 不符（fail-closed，绝不静默当已覆盖）。"""


# class-name-alias: 清洗异常托管腿 CH 查询最小协议（与 cleaning_rules_hosting.AnomalyQueryExecutor
# 同名不同义：本件按 symbol 取帧的注入缝，对标同族先例但零 import 交互；保字节不改名以维持
# 各腿测试注入缝独立）
class AnomalyQueryExecutor(Protocol):
    """CH 查询执行器最小协议（生产实现=clickhouse_driver.Client，经 DatabaseService 领取）。"""

    def execute(self, sql: str, parameters: dict | None = None) -> list:  # noqa: D102 - 协议即文档
        ...


@dataclass(frozen=True)
class AnomalyWiringConfig:
    """承载册 wiring 块投影（运维参数；键集=本 dataclass 字段，派生校验）。"""

    enabled: bool
    host_schedule: str
    cadence_days: int
    rows_per_symbol: int
    watchlist_size: int
    alert_level: str
    report_dir: str
    disabled_flag: str


@dataclass(frozen=True)
class EngineParams:
    """承载册 engines 块投影（五类检出判据值唯一真源，逐键交引擎构造器）。"""

    price_jump_pct: float
    price_jump_z: float
    volume_spike_mult: float
    volume_z: float


@dataclass(frozen=True)
class TableTarget:
    """单表检测对象册（targets 条目投影）。"""

    table: str
    date_col: str
    symbol_col: str
    lookback_days: int
    frame_cols: tuple[str, ...] = ("close", "volume")


@dataclass(frozen=True)
class GateRunOptions:
    """门控运行选项束（参数对象——替代长参数表，§5.150；同族先例 _ScanRound/_EnvelopeCore）。

    executor/alerter=注入缝（生产默认构造，测试注入假件零真实外呼）；
    ref_date/report_dir/notify 语义与 run_anomaly_gate 原同名参数逐字一致（缺省值同源）。
    """

    executor: AnomalyQueryExecutor | None = None
    alerter: Any | None = None  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    ref_date: date | None = None
    report_dir: str | Path | None = None
    notify: bool = True


_WIRING_FIELDS: Final = frozenset(_f.name for _f in fields(AnomalyWiringConfig))
_ENGINE_FIELDS: Final = frozenset(_f.name for _f in fields(EngineParams))
_TARGET_FIELDS: Final = frozenset(_f.name for _f in fields(TableTarget))


from zephyr.data.cleaning_rules_hosting import (  # FUNCTION-DUP 内收：同族承载册解析核心单实现
    CleaningGateConfigError,
)
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


def _config_error(msg: str, **details: Any) -> AnomalyGateConfigError:
    """配置错工厂：路径等敏感/长信息走 details，不进消息文本（MSG-EXPOSURE 同族口径）。"""
    exc = AnomalyGateConfigError(msg)
    for _k, _v in details.items():  # 键级回填（与 .details 冗余双写=消费方两种读取口径都覆盖）
        setattr(exc, _k, _v)
    exc.details = details  # type: ignore[attr-defined]
    return exc


def _rebind(exc: Exception) -> AnomalyGateConfigError:
    """rules 同族 CleaningGateConfigError → 本域 AnomalyGateConfigError（details 属性搬运）。"""
    args = getattr(exc, "args", (exc,))
    out = _config_error(args[0] if args else str(exc))
    extra = getattr(exc, "details", None)
    if isinstance(extra, dict) and extra:
        out.details = {**extra, **getattr(out, "details", {})}  # type: ignore[attr-defined]
    return out


def _reject_unknown_keys(mapping: dict, *, legal: frozenset[str], where: str) -> None:
    """未知键 fail-loud（核心委托 rules 同族，异常回绑本域）。"""
    unknown = sorted(set(mapping) - legal)
    try:
        _rules_reject_unknown_keys(mapping, legal=legal, where=where)
    except CleaningGateConfigError as exc:
        raise _rebind(exc) from exc
    if unknown:  # 防御位：rules 侧漏报时本域仍 fail-loud（同一判据）
        raise _config_error(
            "异常承载册含未知键（拼错的键=该检查静默空转，禁静默忽略）",
            where=where,
            unknown=unknown,
            legal=sorted(legal),
        )


def _require(mapping: dict, key: str, *, where: str) -> Any:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方同族先例 supply_sentinel），签名无法具体化
    # FUNCTION-DUP 内收：核心委托 rules 同族；缺键时回绑本域异常面（文案保留本域语义）。
    if key not in mapping:
        raise _config_error("异常承载册缺必填键（无默认判据兜底=fail-closed）", where=where, key=key)
    try:
        return _rules_require(mapping, key, where=where)
    except CleaningGateConfigError as exc:
        raise _rebind(exc) from exc


def _parse_bool(value: object, *, where: str) -> bool:
    # FUNCTION-DUP 内收：核心委托 rules 同族实现，异常回绑本域类型。
    try:
        return _rules_parse_bool(value, where=where)
    except CleaningGateConfigError as exc:
        raise _config_error("布尔键须为 true/false", where=where, value=repr(value)) from exc


def _parse_positive_int(value: object, *, where: str) -> int:
    """正整数解析：bool 投毒必须炸（true→1 会把限额/窗口悄悄掰松）。核心委托 rules 同族。"""
    try:
        return _rules_parse_positive_int(value, where=where)
    except CleaningGateConfigError as exc:
        raise _config_error("整数键须为 >=1 的整数", where=where, value=repr(value)) from exc


def _parse_positive_float(value: object, *, where: str) -> float:
    """非负浮点解析（检出阈值面）：bool/非数/负数一律配置错。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _config_error("浮点键须为数值", where=where, value=repr(value))
    val = float(value)
    if val < 0:
        raise _config_error("浮点键须 >=0（负阈值=判据不可信）", where=where, value=val)
    return val


def _check_identifier(value: str, *, where: str) -> str:
    # FUNCTION-DUP 内收：核心委托 rules 同族（同一 _IDENTIFIER_RE 语义面），异常回绑本域。
    if not _IDENTIFIER_RE.match(value or ""):
        raise _config_error("表名/列名非法（只允许标识符，禁 SQL 片段）", where=where, value=value)
    try:
        return _rules_check_identifier(value, where=where)
    except CleaningGateConfigError as exc:
        raise _rebind(exc) from exc


def _load_raw(config_path: str | Path | None) -> dict:
    """读承载册 YAML：缺文件/非映射/解析失败/非法编码一律 AnomalyGateConfigError（fail-closed）。"""
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if not path.exists():
        raise _config_error("异常承载册缺失（判据无真源=本腿不跑，绝不默认放行）", path=str(path))
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as ex:
        raise _config_error("异常承载册非法编码（须 UTF-8；错型不外溢）", path=str(path), error=str(ex)[:200]) from ex
    except OSError as ex:
        raise _config_error("异常承载册读不到", path=str(path), error=str(ex)[:200]) from ex
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as ex:  # 解析失败=判据不可信，禁按"无规则"处理
        raise _config_error("异常承载册 YAML 解析失败", path=str(path), error=str(ex)[:200]) from ex
    if not isinstance(raw, dict):
        raise _config_error("异常承载册根节点须为映射", path=str(path), value=type(raw).__name__)
    return raw


def _load_wiring(raw: dict, *, where: str = "wiring") -> AnomalyWiringConfig:
    block = raw.get("wiring")
    if not isinstance(block, dict):
        raise _config_error("异常承载册缺 wiring 块（运维参数无真源=不猜默认值）")
    _reject_unknown_keys(block, legal=_WIRING_FIELDS, where=where)
    level = str(_require(block, "alert_level", where=where)).upper()
    if level not in _ALLOWED_LEVELS:
        raise _config_error("alert_level 非法", where=where, value=level, legal=sorted(_ALLOWED_LEVELS))
    return AnomalyWiringConfig(
        enabled=_parse_bool(_require(block, "enabled", where=where), where=where),
        host_schedule=str(_require(block, "host_schedule", where=where)),
        cadence_days=_parse_positive_int(_require(block, "cadence_days", where=where), where=where),
        rows_per_symbol=_parse_positive_int(_require(block, "rows_per_symbol", where=where), where=where),
        watchlist_size=_parse_positive_int(_require(block, "watchlist_size", where=where), where=where),
        alert_level=level,
        report_dir=str(_require(block, "report_dir", where=where)),
        disabled_flag=str(_require(block, "disabled_flag", where=where)),
    )


def _load_engines(raw: dict) -> EngineParams:
    block = raw.get("engines")
    if not isinstance(block, dict):
        raise _config_error("异常承载册缺 engines 块（检出阈值无真源=不猜默认值）")
    _reject_unknown_keys(block, legal=_ENGINE_FIELDS, where="engines")
    return EngineParams(
        price_jump_pct=_parse_positive_float(
            _require(block, "price_jump_pct", where="engines"), where="engines.price_jump_pct"
        ),
        price_jump_z=_parse_positive_float(
            _require(block, "price_jump_z", where="engines"), where="engines.price_jump_z"
        ),
        volume_spike_mult=_parse_positive_float(
            _require(block, "volume_spike_mult", where="engines"), where="engines.volume_spike_mult"
        ),
        volume_z=_parse_positive_float(_require(block, "volume_z", where="engines"), where="engines.volume_z"),
    )


def _parse_target(entry: Any, where: str) -> TableTarget:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值，签名无法具体化
    if not isinstance(entry, dict):
        raise _config_error("targets 条目须为映射", where=where, value=repr(entry))
    _reject_unknown_keys(entry, legal=_TARGET_FIELDS, where=where)
    table = _check_identifier(str(_require(entry, "table", where=where)), where=f"{where}.table")
    date_col = _check_identifier(str(_require(entry, "date_col", where=where)), where=f"{where}.date_col")
    symbol_col = _check_identifier(str(_require(entry, "symbol_col", where=where)), where=f"{where}.symbol_col")
    lookback = _parse_positive_int(_require(entry, "lookback_days", where=where), where=f"{where}.lookback_days")
    frame_cols = entry.get("frame_cols")
    if frame_cols is None:
        cols: tuple[str, ...] = ("close", "volume")
    else:
        if not isinstance(frame_cols, list) or not frame_cols:
            raise _config_error("frame_cols 须为非空列表（空=帧无从构起）", where=where)
        cols = tuple(_check_identifier(str(c), where=f"{where}.frame_cols") for c in frame_cols)
    known = {"open", "high", "low", "close", "volume", "adj_factor"}
    unknown_cols = sorted(set(cols) - known)
    if unknown_cols:
        raise _config_error("frame_cols 含引擎五类检出未知列", where=where, unknown=unknown_cols, legal=sorted(known))
    return TableTarget(table=table, date_col=date_col, symbol_col=symbol_col, lookback_days=lookback, frame_cols=cols)


def load_anomaly_rulebook(
    config_path: str | Path | None = None,
) -> tuple[AnomalyWiringConfig, EngineParams, list[TableTarget]]:
    """承载册 -> (wiring, engines, targets)；一切非法在此上抛，不到运行期。"""
    raw = _load_raw(config_path)
    if int(raw.get("schema_version") or 0) != 1:
        raise _config_error("异常承载册 schema_version 须为 1", value=raw.get("schema_version"))
    wiring = _load_wiring(raw)
    engines = _load_engines(raw)
    entries = raw.get("targets")
    if not isinstance(entries, list) or not entries:
        # 空对象清单=本腿无检测对象却回 ok=True，正是"接线了但什么都不查"的假绿形态
        raise _config_error("异常承载册 targets 为空（无检测对象）")
    targets = [_parse_target(entry, f"targets[{idx}]") for idx, entry in enumerate(entries)]
    return wiring, engines, targets


def _repo_relative(value: str) -> Path:
    """承载册路径口径：相对=锚 REPO_ROOT，绝对=原样（FUNCTION-DUP 内收：委托 rules 同族，语义全等）。"""
    return _rules_repo_relative(value)


def _default_executor() -> AnomalyQueryExecutor:
    """CH 只读连接——全仓唯一 Client 构造点 DatabaseService（宪法 §9.1 禁裸连接）。"""
    from zephyr.infrastructure.database_service import get_db_service

    conn = get_db_service().get_clickhouse_conn(role="reader", slot="cleaning_anomaly_hosting")
    return conn  # 本腿槽位独立于 rules 腿（slot 名即隔离面），连接对象同源


def _watchlist(executor: AnomalyQueryExecutor, target: TableTarget, *, ref: date, limit: int) -> list[str]:
    """标的清单：近窗 DISTINCT 符号按名序取前 limit 个（确定性机械选取，口径在册非在码）。"""
    span = max(target.lookback_days - 1, 0)
    sql = _SQL_DISTINCT_SYMBOLS.format(
        symbol_col=target.symbol_col,
        table=target.table,
        date_col=target.date_col,
        start=(ref - timedelta(days=span)).isoformat(),
        end=ref.isoformat(),
        limit=limit,
    )
    rows = executor.execute(sql) or []
    return [str(r[0]) for r in rows if r and r[0] is not None]


def _fetch_symbol_frame(
    executor: AnomalyQueryExecutor, target: TableTarget, symbol: str, *, ref: date, limit: int
) -> list[dict[str, Any]]:
    """单标的近窗帧行（列面=date_col+frame_cols，全部由承载册派生，代码不写列名/窗口值）。"""
    span = max(target.lookback_days - 1, 0)
    sql = _SQL_FETCH_SYMBOL_FRAME.format(
        date_col=target.date_col,
        frame_cols=", ".join(target.frame_cols),
        table=target.table,
        symbol_col=target.symbol_col,
        start=(ref - timedelta(days=span)).isoformat(),
        end=ref.isoformat(),
        limit=limit,
    )
    rows = executor.execute(sql, {"symbol": symbol}) or []
    cols = [target.date_col, *target.frame_cols]
    return [dict(zip(cols, row, strict=False)) for row in rows]


def _frame_from_rows(rows: list[dict[str, Any]], target: TableTarget) -> pd.DataFrame:
    """行组→引擎帧：index=日期列升序，列=frame_cols（dtype 由引擎侧 astype 兜底）。"""
    import pandas as pd

    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    frame = frame.sort_values(target.date_col).set_index(target.date_col)
    return frame


def _rule_coverage(frame: pd.DataFrame) -> list[str]:
    """本帧实际可检的规则面（检出前提列齐备的规则；缺前提列的规则=未检，禁算进"干净"）。"""
    covered: list[str] = []
    cols = set(map(str, frame.columns)) if hasattr(frame, "columns") else set()
    for rule, pre_cols in _RULE_PRECONDITION_COLS.items():
        if not pre_cols or any(c in cols for c in pre_cols):
            covered.append(rule)
    return sorted(covered)


def _evaluate_symbol(
    engine: CleaningAnomalyEngine,
    executor: AnomalyQueryExecutor,
    target: TableTarget,
    symbol: str,
    *,
    ref: date,
    limit: int,
) -> dict[str, Any]:
    """单标的只读检出（detect-only；单标的异常只降级，不中断全批）。"""
    entry: dict[str, Any] = {
        "symbol": symbol,
        "degraded": False,
        "no_samples": False,
        "coverage": [],
        "findings": [],
        "findings_count": 0,
    }
    try:
        rows = _fetch_symbol_frame(executor, target, symbol, ref=ref, limit=limit)
        entry["rows_read"] = len(rows)
        if not rows:
            # 零样本=无对象可判，不是"判干净"（同族 cleaning_rules_hosting 红队防线）
            entry["no_samples"] = True
            return entry
        frame = _frame_from_rows(rows, target)
        entry["coverage"] = _rule_coverage(frame)
        if not entry["coverage"]:
            # 帧缺全部检出前提列=没得检（禁把"没得检"当"检过干净"）
            entry["degraded"] = True
            entry["error"] = "frame lacks all detect precondition columns"
            return entry
        findings: list[AnomalyFinding] = engine.detect(frame, symbol=symbol)
        entry["findings"] = [
            {"rule": f.rule.value, "timestamp": f.timestamp, "severity": f.severity, "detail": f.detail}
            for f in findings
        ]
        entry["findings_count"] = len(findings)
    except Exception as ex:  # noqa: BLE001 — 单标的取数/检测异常只降级该标的
        entry["degraded"] = True
        entry["error"] = str(ex)[:200]
        log.exception("异常托管腿单标的检出失败: %s", symbol)
    return entry


def gate_status(results: list[dict[str, Any]]) -> str:
    """逐标的结果 → 诚实四态读数（ok=True 的唯一来源=ran_and_clean）。

    判序（不可颠倒）：任一标的降级或零样本=degraded_partial（防"加一个空标的稀释红"
    的同族稀释绕过）；其次有命中=ran_with_findings；全批有样本零命中才=ran_and_clean。
    """
    if not results:
        return STATUS_NOT_RUN
    if any(r.get("degraded") or r.get("no_samples") for r in results):
        return STATUS_DEGRADED_PARTIAL
    if any(r.get("findings_count") for r in results):
        return STATUS_RAN_FINDINGS
    return STATUS_RAN_CLEAN


def _evaluate_targets(
    engine: CleaningAnomalyEngine,
    executor: AnomalyQueryExecutor,
    wiring: AnomalyWiringConfig,
    targets: list[TableTarget],
    ref: date,
) -> list[dict[str, Any]]:
    """逐表逐标的检出（读侧安全阀双闸全在承载册：watchlist_size × rows_per_symbol）。"""
    results: list[dict[str, Any]] = []
    for target in targets:
        symbols = _watchlist(executor, target, ref=ref, limit=wiring.watchlist_size)
        for symbol in symbols:
            results.append(_evaluate_symbol(engine, executor, target, symbol, ref=ref, limit=wiring.rows_per_symbol))
    return results


def run_anomaly_gate(
    wiring: AnomalyWiringConfig,
    engines: EngineParams,
    targets: list[TableTarget],
    options: GateRunOptions | None = None,
) -> dict:
    """逐表逐标的五类检出（只读出报告），返回报告 dict。

    options=None 时全缺省（executor/alerter 自动构造、当日、默认报告目录、出声）——
    与原长参数签名逐字段同义（参数对象化，§5.150；死袋 COMPLEXITY-GUARD 车道处置）。
    """
    opts = options if options is not None else GateRunOptions()
    executor = opts.executor or _default_executor()
    ref = opts.ref_date or now_utc().astimezone(_SHANGHAI_TZ).date()
    out_dir = Path(opts.report_dir) if opts.report_dir else _repo_relative(wiring.report_dir)
    engine = CleaningAnomalyEngine(
        price_jump_pct=engines.price_jump_pct,
        price_jump_z=engines.price_jump_z,
        volume_spike_mult=engines.volume_spike_mult,
        volume_z=engines.volume_z,
    )
    results: list[dict[str, Any]] = _evaluate_targets(engine, executor, wiring, targets, ref)

    all_degraded = bool(results) and all(r["degraded"] for r in results)
    status = gate_status(results)
    empty_watchlist = not results and bool(targets)
    if empty_watchlist:
        # 近窗 DISTINCT 零标的=跑了却无对象可判（表空/窗口写歪/列错）——归 degraded_partial
        # 禁当 not_run（not_run 语义=根本没跑），更禁冒 ran_and_clean（rb2 §二.10 同族防线）
        status = STATUS_DEGRADED_PARTIAL
    degraded_symbols = [r["symbol"] for r in results if r["degraded"]]
    no_sample_symbols = [r["symbol"] for r in results if not r["degraded"] and r["no_samples"]]
    findings_count = sum(int(r.get("findings_count") or 0) for r in results)
    report: dict[str, Any] = {
        "gate": "cleaning_anomaly_hosting",
        "schema_version": 1,
        "host_schedule": wiring.host_schedule,
        "ref_date": ref.isoformat(),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "read_side_only": True,
        "repair_invoked": False,
        "status": status,
        "inspection_ran": status in _INSPECTION_COUNTS_STATUSES,
        "engine_slots": {"wired": list(ENGINE_SLOTS_WIRED), "reserved": list(ENGINE_SLOTS_RESERVED)},
        "targets_checked": [t.table for t in targets],
        "symbols_checked": len(results),
        "results": results,
        "degraded_symbols": degraded_symbols,
        "no_sample_symbols": no_sample_symbols,
        "findings_count": findings_count,
        "all_degraded": all_degraded,
        "empty_watchlist": empty_watchlist,
        "enforcement_state": ENFORCEMENT_STATE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{ref.isoformat()}{_REPORT_SUFFIX}"
    safe_write_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, default=str))
    report["report_path"] = str(report_path)

    if opts.notify and opts.alerter is not None:
        _notify_results(opts.alerter, wiring, report)
    return report


def _notify_results(alerter: Any, wiring: AnomalyWiringConfig, report: dict) -> None:  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    """报告告警面（读侧只出声不执法）：降级/零样本/命中各走 _alert 唯一正门。"""
    for entry in report["results"]:
        if entry["degraded"]:
            _alert(
                alerter,
                wiring.alert_level,
                f"清洗异常门控未生效: {entry['symbol']} [{entry.get('error')}]",
                extra={"symbol": entry["symbol"], "degraded": True},
            )
            continue
        if entry["no_samples"]:
            _alert(
                alerter,
                LEVEL_WARN,
                f"清洗异常门控零样本（无检出对象，不得当已巡检干净）: {entry['symbol']}",
                extra={"symbol": entry["symbol"], "no_samples": True},
            )
        if entry.get("findings_count"):
            by_rule: dict[str, int] = {}
            for f in entry["findings"]:
                by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
            _alert(
                alerter,
                wiring.alert_level,
                f"清洗异常命中: {entry['symbol']} findings={entry['findings_count']} by_rule={by_rule}"
                "（读侧只出声，未改生产数据、未调 repair）",
                extra={"symbol": entry["symbol"], "by_rule": by_rule},
            )
    if report["status"] == STATUS_DEGRADED_PARTIAL:
        _alert(
            alerter,
            LEVEL_WARN,
            "清洗异常门控读数降级（status=degraded_partial，禁冒 ok=True）: "
            f"degraded={report['degraded_symbols']} no_samples={report['no_sample_symbols']}",
            extra={"status": report["status"]},
        )


def _alert(alerter: Any, level: str, message: str, *, extra: dict) -> None:  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    """告警唯一正门=Alerter.notify（禁自造通道）；通道故障只 log 不抛。"""
    try:
        alerter.notify("cleaning_anomaly_gate", message, level=level, source="cleaning_anomaly_hosting", extra=extra)
    except Exception:  # noqa: BLE001 — 告警通道故障不阻断巡检
        log.exception("清洗异常门控告警写入失败")


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
            log.warning("清洗异常门控节奏闸状态文件不可读，不记为已巡检: %s [%s]", path, str(ex)[:120])
            continue
        if not isinstance(body, dict) or body.get("gate") != "cleaning_anomaly_hosting":
            log.warning("清洗异常门控节奏闸状态文件 gate 不自对，不记为已巡检: %s", path)
            continue
        if body.get("status") not in _INSPECTION_COUNTS_STATUSES or not body.get("inspection_ran"):
            log.warning("清洗异常门控上次读数非「真跑完」（status=%s），不占节奏闸: %s", body.get("status"), path)
            continue
        dates.append(stamp)
    return max(dates) if dates else None


def _write_status_ledger(out_dir: Path, *, ref: date, status: str, reason: str, wiring: AnomalyWiringConfig) -> str:
    """未跑/降级台账（必留痕；文件名刻意不匹配报告后缀，防被节奏闸读成"当天已巡检"）。"""
    payload: dict[str, Any] = {
        "gate": "cleaning_anomaly_hosting",
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
    wiring: AnomalyWiringConfig,
    *,
    out_dir: Path,
    ref: date,
    alerter: Any,  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    reason: str,
    note: str,
) -> dict[str, Any]:
    """「根本没跑」的统一诚实出口：ok=False + status=not_run + 出声 + 台账（三者缺一不可）。"""
    ledger_path = _write_status_ledger(out_dir, ref=ref, status=STATUS_NOT_RUN, reason=reason, wiring=wiring)
    log.warning("清洗异常门控未执行（status=not_run reason=%s）：%s", reason, note)
    _alert(
        alerter,
        LEVEL_WARN,
        f"清洗异常门控未执行（status=not_run，禁当已巡检）: reason={reason} {note}",
        extra={"status": STATUS_NOT_RUN, "not_run_reason": reason},
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


def run_hosted_anomaly_gate(
    alerter: Any | None = None,  # noqa: any-abuse  any-abuse豁免: Alerter注入缝（同族先例），签名无法具体化
    *,
    config_path: str | Path | None = None,
    report_dir: str | Path | None = None,
    ref_date: date | None = None,
    executor: AnomalyQueryExecutor | None = None,
    host_schedule: str = "data_supply_sentinel",
    force: bool = False,
) -> dict:
    """由 L13 `data_supply_sentinel` 排班腿托管的清洗异常门控（四要素正门形态）。

    全程不抛：配置错/故障 → {ok: False, ...} + 出声（宿主只读键，不改宿主既有结论）。
    """
    if alerter is None:
        from zephyr.data.alerter import Alerter

        alerter = Alerter()
    try:
        wiring, engines, targets = load_anomaly_rulebook(config_path)
    except AnomalyGateConfigError as ex:
        # fail-closed：判据不可信时绝不回"干净"
        log.error("清洗异常承载册配置错误: %s details=%s", ex, getattr(ex, "details", None))
        _alert(alerter, LEVEL_ERROR, f"清洗异常门控未执行（承载册故障）: {str(ex)[:200]}", extra={"config_error": True})
        return {
            "ok": False,
            "status": STATUS_NOT_RUN,
            "not_run_reason": "config_error",
            "inspection_ran": False,
            "config_error": str(ex),
            "details": getattr(ex, "details", None),
            "enforcement_state": ENFORCEMENT_STATE,
        }

    out_dir = Path(report_dir) if report_dir else _repo_relative(wiring.report_dir)
    ref = ref_date or now_utc().astimezone(_SHANGHAI_TZ).date()
    try:
        if wiring.host_schedule != host_schedule:
            raise AnomalyGateConfigError(f"承载册声明宿主={wiring.host_schedule} 与实调宿主={host_schedule} 不符")
        if not force and not wiring.enabled:
            return _not_run(
                wiring,
                out_dir=out_dir,
                ref=ref,
                alerter=alerter,
                reason=NOT_RUN_WIRING_DISABLED,
                note="承载册 wiring.enabled=false（总闸停用，本次零检测）",
            )
        flag_path = _repo_relative(wiring.disabled_flag)
        if flag_path.exists() and not force:
            return _not_run(
                wiring,
                out_dir=out_dir,
                ref=ref,
                alerter=alerter,
                reason=NOT_RUN_MASTER_SWITCH_OFF,
                note=f"停用标记存在 {flag_path}（自动关闭闸，本次零检测）",
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
        report = run_anomaly_gate(
            wiring,
            engines,
            targets,
            GateRunOptions(executor=executor, alerter=alerter, ref_date=ref, report_dir=out_dir),
        )
    except AnomalyGateConfigError as ex:
        log.error("清洗异常门控配置错误: %s", ex)
        _alert(
            alerter,
            wiring.alert_level,
            f"清洗异常门控未执行（配置故障）: {str(ex)[:200]}",
            extra={"config_error": True},
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
        log.exception("清洗异常门控托管腿失败")
        _alert(
            alerter, wiring.alert_level, f"清洗异常门控未执行（腿故障）: {str(exc)[:200]}", extra={"leg_error": True}
        )
        return {
            "ok": False,
            "status": STATUS_NOT_RUN,
            "not_run_reason": "leg_error",
            "inspection_ran": False,
            "error": str(exc)[:200],
            "enforcement_state": ENFORCEMENT_STATE,
        }

    status = str(report["status"])
    ok = status == _OK_STATUS
    log.info(
        "清洗异常门控巡检完成: status=%s targets=%d symbols=%d findings=%d degraded=%d no_samples=%d",
        status,
        len(report["targets_checked"]),
        report["symbols_checked"],
        report["findings_count"],
        len(report["degraded_symbols"]),
        len(report["no_sample_symbols"]),
    )
    return {
        "ok": ok,
        "status": status,
        "inspection_ran": bool(report["inspection_ran"]),
        "findings_count": report["findings_count"],
        "symbols_checked": report["symbols_checked"],
        "targets_checked": report["targets_checked"],
        "degraded_symbols": report["degraded_symbols"],
        "no_sample_symbols": report["no_sample_symbols"],
        "all_degraded": report["all_degraded"],
        "empty_watchlist": report["empty_watchlist"],
        "report_path": report.get("report_path"),
        "ref_date": ref.isoformat(),
        "enforcement_state": ENFORCEMENT_STATE,
    }


def status_exit_code(status: str, *, findings_count: int = 0) -> int:
    """CLI 退出码与四态对齐：降级绝不回 0（0=跑过且判干净）。"""
    if status in (STATUS_NOT_RUN, STATUS_DEGRADED_PARTIAL):
        return _EXIT_PARTIAL_DEGRADED
    if status == STATUS_RAN_FINDINGS:
        return min(int(findings_count), 255)
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI 入口（运维手动复查）。exit code：0=跑过且判干净｜N=命中数｜
    252=部分降级/零样本/未跑（禁当绿）｜253=全批降级｜254=配置错。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.cleaning_anomaly_hosting",
        description="清洗异常引擎托管腿：按 config/cleaning_anomaly_rules.yaml 逐标的五类检出（只读不修）",
    )
    parser.add_argument("--config", default=None, help=f"承载册路径（默认 {_DEFAULT_CONFIG_PATH}）")
    parser.add_argument("--report-dir", default=None, help="报告目录覆盖（默认取承载册 report_dir）")
    parser.add_argument("--no-alert", action="store_true", help="只检测不发告警")
    parser.add_argument("--force", action="store_true", help="跳过节奏闸与停用标记")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        wiring, engines, targets = load_anomaly_rulebook(args.config)
    except AnomalyGateConfigError as ex:
        log.critical("清洗异常承载册配置错误: %s details=%s", ex, getattr(ex, "details", None))
        return _EXIT_CONFIG_ERROR
    cli_alerter = None
    if not args.no_alert:
        from zephyr.data.alerter import Alerter

        cli_alerter = Alerter()
    report = run_anomaly_gate(
        wiring,
        engines,
        targets,
        GateRunOptions(alerter=cli_alerter, report_dir=args.report_dir, notify=not args.no_alert),
    )
    if report["all_degraded"]:
        log.critical("清洗异常门控全批降级，巡检未生效（status=%s）", report["status"])
        return _EXIT_ALL_DEGRADED
    return status_exit_code(str(report["status"]), findings_count=int(report["findings_count"]))


if __name__ == "__main__":
    raise SystemExit(main())
