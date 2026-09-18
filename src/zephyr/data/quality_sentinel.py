# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.quality_sentinel
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.alerter; zephyr.data.calendar(懒加载); zephyr.data.table_registry(TableRegistry 表名真源); zephyr.infrastructure.database_service(懒加载); zephyr.shared.io.file_utils; zephyr.shared.utils.time_utils
# [CONSUMERS] zephyr.data.supply_sentinel.run_supply_sentinel -> run_hosted_sweep（L13 data_supply_sentinel 排班腿托管，2026-09-18 全流通战役 st-ff-sentinel 接线）；CLI 独立运行
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] 只读检测禁修数; CH 访问唯一入口=DatabaseService.get_clickhouse_conn(reader)禁裸连接(宪法§9.1); 告警唯一正门=Alerter.notify禁自造通道; 当前时间统一 now_utc() 入口禁 datetime.now()/time.time() 散落(RULE-SCHEMA-TZ); DateTime64 列显式 Asia/Shanghai 口径; 报告 JSON 落 data/quality_sentinel/ 经 safe_write_text; 单表查询失败=degraded 不中断全表巡检; epoch/tz/empty 三腿计数不带 FINAL(ReplacingMergeTree 未合并重复对变异检测无影响)，non_trading_day 腿例外必带 FINAL(幽灵日计数要与 B15 案卷的 FINAL 口径逐日可比，且手册硬约束"ReplacingMergeTree 查询必须带 FINAL"); non_trading_day 腿判据只准用库内权威日历的**负向**谓词(NOT IN 开市日)，禁 dayOfWeek 类日历函数判周末(实测 ClickHouse 返回 ISO 序与官方文档相反)、禁 is_open=0 判非交易日(该表只存开市日⇒恒空=假绿); exit code=发现变异数(0=干净,封顶255)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单表单查失败->degraded 记录不抛; 全表 degraded->CLI exit 253; 配置缺失/非法->QualitySentinelError->CLI exit 254; 告警失败->log 不抛(同 Alerter 契约)
# [TESTS] tests/zephyr/data/test_quality_sentinel.py
# [A_module] module_id=MOD-GOV-quality_sentinel | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 检测器本体无驻留循环，CLI=按需手动触发+排班宿主经 run_sentinel() 函数调用（integrity_check 同族），常驻化由 tasks.yaml+schedule.yaml 注册正门另行接线（repair_etf_minute_tz_split.py:23 同族先例）
"""数据质量常驻哨兵——1970 纪元 / 时区偏移 / 空段 / 非交易日有行四类变异检测器（WO-④-01 + C-36）。

背景（docs/_working/automation/campaign/mining/04_洗数据/工段作业簿.md §2.2/§4/§8）：
仓内已发生三起亿行级数据变异事故——tick_data 1970 残留、kline_1min 2635 万行 1970
错位、行情时区 -8h 偏移 15.6 亿行——全部人工发现。1970 哨兵此前只是**约定**（写侧
1970-01-01 占位 + 查询侧 pit_query 1970-01-02 过滤），盘面无常驻巡检。本模块补上
第三端：每晚对关键 CH 大表做变异检测（现四类，见下）。

四类检测：
  1) epoch          纪元变异：业务时间列出现 < epoch_cutoff（默认 1990-01-01）的行
                    （覆盖 date_col Date 列与 ts_col DateTime64 列两路）；
  2) tz_shift       时区偏移：ts_col 小时分布中 suspect_hours（默认 0-7 点）行占比
                    超阈值（-8h 事故把 09:30-15:00 整体挪进 01:30-07:00，必然触发）；
  3) empty_segment  空段：最近 N 个交易日（交易日历口径）整表零行；
  4) non_trading_day 污染尺（C-36，2026-09-19 续工车道 st-sentpoll-20260919）：
                    业务日期列落在**非交易日**上的行数 > 容忍上限即告警。
                    诞生理由（B15 实测）：c1_market.daily_valuation 有 77,668/259,238 FINAL 行
                    （29.96%）落在 14 个周末幽灵日，而 zephyr.data.supply_sentinel 的两条现成腿
                    只量"新鲜度+填充率"⇒ 这类"日期根本不该有数"的脏数据全仓不可见。
                    ★ 滞后尺（多久没写）与污染尺（写进来的是不是真值）是两把尺，禁合并；
                    ★ 本腿走**业务日期列**（date_col），与 supply_sentinel 的 ingest_ts 心跳腿无关，
                      两条腿各测各的（心跳腿绿只证明"我们在写"）。
                    谓词三条硬约束（实测出处=CONSTRUCTION_DISCIPLINE.md §7 + 本仓 system.columns）：
                      ① 负向判定：`date_col NOT IN (SELECT cal_date FROM c1_market.trade_calendar
                         FINAL WHERE exchange='SSE' AND is_open=1)`；
                      ② 禁 dayOfWeek 判周末——ClickHouse 26.6.1 实测返回 ISO 序（周一=1…周日=7），
                         与官方文档相反，`dayOfWeek IN (1,7)` 会把 7 个真周一判成幽灵（假阳）+
                         漏掉 7 个真周六（假阴），条数还对得上 ⇒ 只有库内权威日历可作真源；
                      ③ 禁 is_open=0 判非交易日——该表只存开市日（实测 exchange='SSE' 8797 行
                         sum(is_open)=count(*)=8797），该谓词恒空 ⇒ 尺子永远不响＝机器面假绿。

排班登记说明（工单要求，留档防丢）：
  2026-09-18 全流通战役 st-ff-sentinel-20260918 实测更正：本仓**特殊时段类槽位（L11
  integrity_check / L10.7 catchup_guard / L13 data_supply_sentinel / consensus_crosscheck）
  一律不走 tasks.yaml**——tasks.yaml 条目须绑 source/capability/provider 三件，
  哨兵不是数据源，硬塞一条"任务"就是 R-021 型假通道（排班真源 config 里有个名字、调度器侧无实现=
  调度器空跑并 log"时段 X 无任务"后静默返回成功）。故本件的排班正门=**由 L13
  data_supply_sentinel 槽位托管**（run_hosted_sweep，见 config/quality_sentinel_tables.yaml
  的 wiring 块），不为哨兵族另开第二个空槽位。C-36 本腿沿用同一条托管腿，**不新建守护、
  不加 cron/Timer**（宪法 §9.3）。
  独立触发：python -m zephyr.data.quality_sentinel [--tables t1,t2] [--days N]

使用方式：
  CLI      python -m zephyr.data.quality_sentinel [--tables ...] [--days N]
           exit code = 发现变异数（0=干净；>255 封顶 255；253=全表 degraded；
           254=配置错误）
  编程接口 run_sentinel(specs, executor=..., calendar=..., alerter=..., ...) -> dict
  表配置   config/quality_sentinel_tables.yaml（表清单/date_col/ts_col/阈值）

SSoT: docs/03_modules/_domain_data/data_source_integrator_blueprint.md
      docs/_working/automation/campaign/mining/04_洗数据/工段作业簿.md §10
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, fields
from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Final, Protocol
from zoneinfo import ZoneInfo

import yaml

from zephyr.data.table_registry import get_registry
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:  # 仅类型注解（避免测试/导入期拖入日历数据加载）
    from zephyr.data.calendar.base import MarketCalendar

log = logging.getLogger(__name__)

__all__: Final = [
    "TableSpec",
    "SentinelFinding",
    "SentinelOutput",
    "QualitySentinelError",
    "load_specs",
    "check_epoch",
    "check_tz_shift",
    "check_empty_segment",
    "check_non_trading_day",
    "run_sentinel",
    "run_hosted_sweep",
    "main",
]

_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

_DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "quality_sentinel_tables.yaml"
_DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "quality_sentinel"

#: 服务总闸（宪法 §9.3 四要素之"自动关闭"在排班批里的家族制式：标记文件存在=停用，
#: 每次触发实查、即时生效、无需重启宿主调度器——同 nightly_sentiment/consensus_crosscheck）
_DISABLED_FLAG_PATH = REPO_ROOT / "data" / "runtime" / "quality_sentinel.disabled"

#: 托管巡检默认节奏（日）；真源=config/quality_sentinel_tables.yaml 的 wiring.sweep_cadence_days
_DEFAULT_SWEEP_CADENCE_DAYS: Final = 7

#: exit code 保留段（变异数占 0-255；253/254 为运维保留码，见 ERROR_CONTRACT）
_EXIT_ALL_DEGRADED = 253
_EXIT_CONFIG_ERROR = 254
_EXIT_CODE_CAP = 255

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）。
# 计数不带 FINAL：ReplacingMergeTree 未合并的重复行对"变异行计数"无影响，
# 免掉亿行表 FINAL 全归并开销（INVARIANTS 已声明）。
_SQL_EPOCH_COUNT_DATE = "SELECT count() FROM {table} WHERE {col} < toDate('{cutoff}')"
_SQL_EPOCH_COUNT_TS = (
    "SELECT count() FROM {table} WHERE {col} < toDateTime64('{cutoff} 00:00:00', 3, 'Asia/Shanghai')"
)
_SQL_TZ_HOUR_PROFILE = (
    "SELECT toHour({ts_col}), count() FROM {table} "
    "WHERE {date_col} >= toDate('{start}') AND {date_col} <= toDate('{end}') "
    "GROUP BY toHour({ts_col}) ORDER BY toHour({ts_col})"
)
_SQL_RANGE_COUNT = (
    "SELECT count() FROM {table} "
    "WHERE {date_col} >= toDate('{start}') AND {date_col} <= toDate('{end}')"
)

# ============== 污染尺（C-36）的库内权威日历常量 ==============
# 三条实测口径（D-17：断言必须写库名 + 从活库 system.columns / 活表读，禁凭记忆）：
#   ① 引擎=ReplacingMergeTree（system.tables 实测）⇒ 本腿两段查询都带 FINAL；
#   ② 活列名是 **cal_date**（不是 calendar_date，写错被 CH Code: 47 打回）；
#   ③ 该表**只存开市日**：exchange='SSE' 8797 行、sum(is_open)=count(*)=8797、
#      countIf(is_open=0)=0 ⇒ "非交易日"只能用**负向**谓词 NOT IN(开市日)，
#      写 is_open=0 得到的空集会让本尺恒不响（机器面假绿，D-18 同族）。
# exchange 取值实测（FINAL GROUP BY exchange）：当前库内只有 'SSE' 一档，
# 故本腿的日历切片是单点真源而非配置项（不自造新键）；港股/交易所扩档时再立案。
# 表名走 TableRegistry 真源（#ARCH-CH-024：品类 market_trade_calendar → c1_market.trade_calendar，
# 同 backfill_checker._TBL_TRADE_CALENDAR 先例；返回值即全名，勿再叠加库前缀）。
_TBL_TRADING_CALENDAR: Final = get_registry().table("market_trade_calendar")
_TRADING_CALENDAR_DATE_COL: Final = "cal_date"
_TRADING_CALENDAR_EXCHANGE: Final = "SSE"
#: 幽灵日清单在告警文案里最多展开这么多天（其余以"等 N 日"收口，防文案爆炸；全量清单进 metric）
_MAX_DATES_IN_DETAIL: Final = 5
_MAX_DATES_IN_METRIC: Final = 60

_SQL_NON_TRADING_CAL_GUARD = (
    "SELECT count() AS open_days, countIf(isNull({cal_date_col})) AS null_cal_days "
    "FROM {calendar_table} FINAL WHERE exchange = '{exchange}' AND is_open = 1"
)
_SQL_NON_TRADING_ROWS = (
    "SELECT {date_col}, count() FROM {table} FINAL "
    "WHERE {date_col} NOT IN (SELECT {cal_date_col} FROM {calendar_table} FINAL "
    "WHERE exchange = '{exchange}' AND is_open = 1) "
    "GROUP BY {date_col} ORDER BY {date_col}"
)


class QualitySentinelError(Exception):
    """哨兵配置/运行级错误（区别于单表 degraded——那类不抛）。"""


def _config_error(msg: str, **details) -> QualitySentinelError:
    """配置级错误工厂：敏感信息（路径等）走 details 结构化字段，不进消息文本（MSG-EXPOSURE 5.99.20）。"""
    exc = QualitySentinelError(msg)
    exc.details = details  # type: ignore[attr-defined]
    return exc


class QueryExecutor(Protocol):
    """CH 查询执行器最小协议（生产实现=clickhouse_driver.Client，经 DatabaseService 领取）。"""

    def execute(self, sql: str) -> list:  # noqa: D102 - 协议即文档
        ...


@dataclass(frozen=True)
class TableSpec:
    """单表哨兵配置（config/quality_sentinel_tables.yaml 的强类型投影）。"""

    table: str
    date_col: str
    ts_col: str | None = None
    epoch_cutoff: str = "1990-01-01"
    epoch_max_rows: int = 0
    tz_suspect_hours: tuple[int, ...] = tuple(range(0, 8))
    tz_max_suspect_ratio: float = 0.05
    tz_check_days: int = 7
    empty_gap_trading_days: int = 3
    #: 污染尺容忍上限（C-36）：None=本腿不启用（逐表显式配 0 即零容忍）。
    #: 命名与取值方向照 epoch_max_rows 既有先例——"脏行数 > 上限即告警"。
    non_trading_max_rows: int | None = None


#: 配置合法键集＝TableSpec 字段名（派生，禁手工维护清单——宪法 §9.5）
_SPEC_FIELD_NAMES: Final = frozenset(_f.name for _f in fields(TableSpec))


def _reject_unknown_keys(mapping: dict, *, where: str) -> None:
    """未知键 fail-loud。

    拼错的阈值名（如 `non_trading_max_row`）过去被静默忽略 ⇒ 该条腿整腿不跑、
    报告里看起来"该表已巡检"＝指标自证清白型假绿（同族：无 else 的白名单分派）。
    """
    unknown = sorted(set(mapping) - _SPEC_FIELD_NAMES)
    if unknown:
        raise _config_error(
            "哨兵配置含未知键（拼错的阈值名会让对应腿静默不跑却看起来在岗）",
            where=where,
            unknown=unknown,
            legal=sorted(_SPEC_FIELD_NAMES),
        )


@dataclass(frozen=True)
class SentinelFinding:
    """一条变异发现（exit code 与告警的计数单元）。"""

    table: str
    check: str  # epoch | tz_shift | empty_segment | non_trading_day
    severity: str  # Alerter 级别：CRITICAL / ERROR
    detail: str
    metric: dict


# ============== 配置加载 ==============


def _parse_optional_int(value: object, *, field: str) -> int | None:
    """可选整数解析：缺省 None=该腿未启用；bool 投毒必须炸，禁静默变成"腿关掉了"。

    YAML `non_trading_max_rows: true` 若被 int() 吞成 1，就是"零容忍"被悄悄放宽；
    若按 `value or None` 的惯用法走，`0`（最严档）又会和 None（不启用）混为一谈。
    故显式三分支：None→None、bool→报错、其余走 int()（非数值同样报错，收敛为配置错）。
    """
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field} 不可为布尔值（true/false 会被 int() 静默换算，语义走偏）")
    return int(value)  # 非数值由调用方 except ValueError 收敛为配置错


def _parse_spec_fields(entry: dict, merged: dict, days: int | None) -> TableSpec:
    """YAML 条目 -> TableSpec。类型投毒（date_col: 123 / tz_suspect_hours: [a]）收敛为
    QualitySentinelError，禁裸 ValueError 炸穿 254 契约（ERROR_CONTRACT）。"""
    try:
        suspect_hours = merged.get("tz_suspect_hours")
        return TableSpec(
            table=str(entry["table"]),
            date_col=str(entry["date_col"]),
            ts_col=str(merged["ts_col"]) if merged.get("ts_col") else None,
            epoch_cutoff=str(merged.get("epoch_cutoff") or TableSpec.epoch_cutoff),
            epoch_max_rows=int(merged.get("epoch_max_rows") or 0),
            tz_suspect_hours=tuple(int(h) for h in suspect_hours) if suspect_hours else TableSpec.tz_suspect_hours,
            tz_max_suspect_ratio=float(merged.get("tz_max_suspect_ratio") or TableSpec.tz_max_suspect_ratio),
            tz_check_days=int(days) if days else int(merged.get("tz_check_days") or TableSpec.tz_check_days),
            empty_gap_trading_days=(
                int(days) if days else int(merged.get("empty_gap_trading_days") or TableSpec.empty_gap_trading_days)
            ),
            non_trading_max_rows=_parse_optional_int(
                merged.get("non_trading_max_rows"), field="non_trading_max_rows"
            ),
        )
    except (TypeError, ValueError) as e:
        raise _config_error(f"哨兵表字段类型非法: {e}", entry=repr(entry.get("table"))) from e


def _validate_spec(spec: TableSpec) -> None:
    """标识符白名单（表/列名直拼 SQL 模板，投毒片段在此拦死）+ cutoff 格式 + 阈值语义。"""
    ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
    for ident_field in ("table", "date_col", "ts_col"):
        ident = getattr(spec, ident_field)
        if ident and not ident_re.match(ident):
            raise _config_error(
                f"哨兵表 {ident_field} 含非法字符（只允许 [A-Za-z0-9_.]，防 SQL 投毒）", ident=repr(ident)
            )
    try:
        date.fromisoformat(spec.epoch_cutoff)
    except ValueError as e:
        raise _config_error(
            f"哨兵表 {spec.table} epoch_cutoff 须 ISO 日期（YYYY-MM-DD）", cutoff=repr(spec.epoch_cutoff)
        ) from e
    _validate_thresholds(spec)


def _validate_thresholds(spec: TableSpec) -> None:
    """阈值语义校验：负值/越界会让哨兵永久误报或永久沉默（两种都比"炸"更危险）。"""
    if spec.epoch_max_rows < 0:
        raise _config_error(f"哨兵表 {spec.table} epoch_max_rows 不可为负", value=spec.epoch_max_rows)
    if not 0 < spec.tz_max_suspect_ratio <= 1:
        raise _config_error(
            f"哨兵表 {spec.table} tz_max_suspect_ratio 须在 (0,1] 内", value=spec.tz_max_suspect_ratio
        )
    bad_hours = [h for h in spec.tz_suspect_hours if not 0 <= h <= 23]
    if bad_hours:
        raise _config_error(f"哨兵表 {spec.table} tz_suspect_hours 越界 [0,23]", value=bad_hours)
    if spec.tz_check_days < 1 or spec.empty_gap_trading_days < 1:
        raise _config_error(
            f"哨兵表 {spec.table} 回看窗须 >=1",
            tz_check_days=spec.tz_check_days, empty_gap_trading_days=spec.empty_gap_trading_days,
        )
    if spec.non_trading_max_rows is not None and spec.non_trading_max_rows < 0:
        # 负上限=连"零幽灵行"都过不了（干净表也永久误报），与 epoch_max_rows 同口径拦死
        raise _config_error(
            f"哨兵表 {spec.table} non_trading_max_rows 不可为负", value=spec.non_trading_max_rows
        )


def _specs_from_entries(table_entries: list, defaults: dict, days: int | None) -> list[TableSpec]:
    """逐条目投影+校验（投毒条目 fail-closed）。"""
    specs: list[TableSpec] = []
    for entry in table_entries:
        if not isinstance(entry, dict) or not entry.get("table") or not entry.get("date_col"):
            raise _config_error("哨兵表条目非法（须含 table/date_col）", entry=repr(entry))
        _reject_unknown_keys(entry, where=f"tables[{entry['table']}]")
        merged = {**defaults, **{k: v for k, v in entry.items() if k != "table"}}
        spec = _parse_spec_fields(entry, merged, days)
        _validate_spec(spec)
        specs.append(spec)
    return specs


def _filter_specs(specs: list[TableSpec], tables: list[str] | None) -> list[TableSpec]:
    """表名过滤（全名或短名，大小写不敏感）。"""
    if not tables:
        return specs
    wanted = {t.strip().lower() for t in tables if t.strip()}
    return [s for s in specs if s.table.lower() in wanted or s.table.split(".")[-1].lower() in wanted]


def load_specs(
    config_path: str | Path | None = None,
    tables: list[str] | None = None,
    days: int | None = None,
) -> list[TableSpec]:
    """加载表清单配置并投影为 TableSpec 列表。

    Args:
        config_path: 配置路径，None 用 config/quality_sentinel_tables.yaml。
        tables: 表名过滤（全名 c1_market.x 或短名 x），None=全部。
        days: CLI --days 覆盖 tz_check_days 与 empty_gap_trading_days。

    Raises:
        QualitySentinelError: 配置缺失/非法。
    """
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if not path.exists():
        raise _config_error("哨兵表配置缺失", path=str(path))
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise _config_error(f"哨兵表配置 YAML 非法: {e}", path=str(path)) from e
    table_entries = raw.get("tables")
    if not isinstance(table_entries, list) or not table_entries:
        raise _config_error("哨兵表配置缺少 tables 列表", path=str(path))

    defaults = raw.get("defaults") or {}
    if not isinstance(defaults, dict):
        raise _config_error("哨兵表配置 defaults 须为映射", value=repr(defaults))
    _reject_unknown_keys(defaults, where="defaults")
    if days is not None and int(days) < 1:
        # 0/负数窗口会让回看窗失效、巡检静默空转还谎报"干净"——哨兵最危险形态，fail-closed
        raise _config_error("days 须 >=1（0/负数=巡检静默空转）", value=days)
    specs = _specs_from_entries(table_entries, defaults, days)
    return _filter_specs(specs, tables)


# ============== 四类检测（每类返回 SentinelFinding 列表，查不到变异=空表） ==============


def check_epoch(executor: QueryExecutor, spec: TableSpec) -> list[SentinelFinding]:
    """检测 a) 纪元变异：date_col 与 ts_col（若有）各查一遍 < epoch_cutoff 的行数。

    全史扫描（不加日期窗）：1970 残留按 trade_date 分区落在 197001 老分区，
    只有全史谓词才兜得住历史段事故（tick_data 残留先例）。
    """
    findings: list[SentinelFinding] = []
    cols = [spec.date_col] if spec.date_col else []
    if spec.ts_col:
        cols.append(spec.ts_col)
    # 同列去重：无独立 date 列的表（本轮实测 kline_5min）date_col==ts_col，
    # 不去重会把同一张亿行表的全史纪元扫描跑两遍。
    cols = list(dict.fromkeys(cols))
    for col in cols:
        if col == spec.ts_col:
            sql = _SQL_EPOCH_COUNT_TS.format(table=spec.table, col=col, cutoff=spec.epoch_cutoff)
        else:
            sql = _SQL_EPOCH_COUNT_DATE.format(table=spec.table, col=col, cutoff=spec.epoch_cutoff)
        (count,) = executor.execute(sql)[0]
        count = int(count)
        if count > spec.epoch_max_rows:
            findings.append(
                SentinelFinding(
                    table=spec.table,
                    check="epoch",
                    severity="CRITICAL",
                    detail=(
                        f"{spec.table}.{col} 出现 {count} 行早于 {spec.epoch_cutoff} 的纪元残留"
                        f"（容忍上限 {spec.epoch_max_rows}）"
                    ),
                    metric={"column": col, "epoch_rows": count, "cutoff": spec.epoch_cutoff,
                            "max_rows": spec.epoch_max_rows},
                )
            )
    return findings


def check_tz_shift(
    executor: QueryExecutor,
    spec: TableSpec,
    ref_date: date,
) -> list[SentinelFinding]:
    """检测 b) 时区偏移：tz_check_days 窗口内 ts_col 小时分布，suspect 小时占比超阈值即告警。

    -8h 偏移把 A股 09:30-15:00 整体挪进 01:30-07:00（≈100% 落入 suspect 窗），
    阈值默认 5% 也能兜住局部混入；期货夜盘表按表级配置放宽。
    无 ts_col 或窗口零行（空段由 empty_segment 负责）则跳过。
    """
    if not spec.ts_col:
        return []
    start = ref_date - timedelta(days=spec.tz_check_days - 1)
    sql = _SQL_TZ_HOUR_PROFILE.format(
        table=spec.table, ts_col=spec.ts_col, date_col=spec.date_col,
        start=start.isoformat(), end=ref_date.isoformat(),
    )
    rows = executor.execute(sql)
    total = sum(int(c) for _, c in rows)
    if total <= 0:
        return []
    suspect = sum(int(c) for h, c in rows if int(h) in spec.tz_suspect_hours)
    ratio = suspect / total
    if ratio > spec.tz_max_suspect_ratio:
        findings = [
            SentinelFinding(
                table=spec.table,
                check="tz_shift",
                severity="CRITICAL",
                detail=(
                    f"{spec.table}.{spec.ts_col} 近 {spec.tz_check_days} 日 suspect 小时"
                    f"（{list(spec.tz_suspect_hours)} 点）占比 {ratio:.1%} "
                    f"> 阈值 {spec.tz_max_suspect_ratio:.0%}，疑似时区偏移"
                ),
                metric={
                    "ts_col": spec.ts_col,
                    "window_start": start.isoformat(),
                    "window_end": ref_date.isoformat(),
                    "total_rows": total,
                    "suspect_rows": suspect,
                    "ratio": round(ratio, 6),
                    "max_ratio": spec.tz_max_suspect_ratio,
                },
            )
        ]
        return findings
    return []


def check_empty_segment(
    executor: QueryExecutor,
    spec: TableSpec,
    ref_date: date,
    calendar: "MarketCalendar",
) -> list[SentinelFinding]:
    """检测 c) 空段：最近 empty_gap_trading_days 个已完成交易日整表零行。

    只看 ref_date 之前的已完成交易日（当日行数达标检查归 integrity_check 班）。
    """
    n = spec.empty_gap_trading_days
    trading_days = _last_trading_days(calendar, ref_date, n)
    if not trading_days:
        log.warning("%s 空段检查跳过：交易日历在回看窗内无交易日", spec.table)
        return []
    start, end = trading_days[0], trading_days[-1]
    sql = _SQL_RANGE_COUNT.format(
        table=spec.table, date_col=spec.date_col, start=start.isoformat(), end=end.isoformat()
    )
    (count,) = executor.execute(sql)[0]
    count = int(count)
    if count <= 0:
        return [
            SentinelFinding(
                table=spec.table,
                check="empty_segment",
                severity="ERROR",
                detail=(
                    f"{spec.table} 最近 {len(trading_days)} 个交易日"
                    f"（{start.isoformat()}~{end.isoformat()}）整表零行"
                ),
                metric={"trading_days": [d.isoformat() for d in trading_days], "rows": count},
            )
        ]
    return []


def _last_trading_days(calendar: "MarketCalendar", ref_date: date, n: int) -> list[date]:
    """取 ref_date 之前最近 n 个交易日（升序）。日历回看窗按 2n+10 日历日缓冲覆盖长假。"""
    end = ref_date - timedelta(days=1)
    start = end - timedelta(days=n * 2 + 10)
    days = calendar.trading_days_in_range(start, end)
    return list(days)[-n:]


def _as_date_text(value: object) -> str:
    """CH 返回的日期值 -> 可 JSON 序列化文本（driver 对 Date 列给 datetime.date，HTTP 降级给字符串）。"""
    isoformat = getattr(value, "isoformat", None)
    return str(isoformat() if callable(isoformat) else value)


def check_non_trading_day(executor: QueryExecutor, spec: TableSpec) -> list[SentinelFinding]:
    """检测 d) 非交易日有行（污染尺，C-36）：业务日期落在权威开市日历外的行数 > 上限即告警。

    与 a) epoch 的分工：纪元变异是"日期值本身坏掉"，本腿是"这个日期根本不该有数"——
    幽灵日的值可以完全落在合法值域内（B15 实测 2026-08-01..09-13 共 14 个周末日 77,668 行，
    pe/pb 都是正经数值），所以 epoch/新鲜度/填充率三条腿一起绿着也看不见它。
    与 zephyr.data.supply_sentinel 的分工：那条腿量"多久没写"（滞后尺，含 ingest_ts 心跳腿），
    本腿量"写进来的是不是真值"（污染尺），两把尺禁合并（CONSTRUCTION_DISCIPLINE.md §7）。

    全史扫描（不加日期窗），与 epoch 同策：幽灵段一旦落下就在历史分区里，只有全史兜得住。
    代价较高，故本腿**按表 opt-in**（`non_trading_max_rows` 缺省 None=不启用），
    只给已证实有病灶的表配（出厂册：c1_market.daily_valuation 一张）。
    """
    if spec.non_trading_max_rows is None:
        return []
    cal_ref = f"{_TBL_TRADING_CALENDAR}(exchange='{_TRADING_CALENDAR_EXCHANGE}', is_open=1)"
    # 日历守卫：空日历会让 NOT IN 空集把整表判成幽灵（假红），而"误写成 is_open=0"得到的
    # 恒空集会让本尺永远不响（假绿）——两种都比"不响"更坏，故拒绝出数、以 degraded 出声。
    guard_sql = _SQL_NON_TRADING_CAL_GUARD.format(
        cal_date_col=_TRADING_CALENDAR_DATE_COL,
        calendar_table=_TBL_TRADING_CALENDAR,
        exchange=_TRADING_CALENDAR_EXCHANGE,
    )
    guard_rows = executor.execute(guard_sql)
    if not guard_rows:
        raise _config_error("交易日历守卫查询无返回，污染尺拒绝出数", table=spec.table, calendar=cal_ref)
    open_days, null_cal_days = (int(v) for v in tuple(guard_rows[0])[:2])
    if open_days <= 0:
        raise _config_error(
            f"权威交易日历不可用（{cal_ref} 返回 0 个开市日）——判据分母为空，污染尺拒绝出数",
            table=spec.table, calendar=cal_ref, open_days=open_days,
        )
    if null_cal_days:
        raise _config_error(
            f"{cal_ref} 有 {null_cal_days} 行 {_TRADING_CALENDAR_DATE_COL} 为 NULL"
            "——NOT IN 遇 NULL 走三值逻辑会把真幽灵静默放行（假绿），污染尺拒绝出数",
            table=spec.table, calendar=cal_ref, null_cal_days=null_cal_days,
        )
    sql = _SQL_NON_TRADING_ROWS.format(
        date_col=spec.date_col, table=spec.table,
        cal_date_col=_TRADING_CALENDAR_DATE_COL,
        calendar_table=_TBL_TRADING_CALENDAR,
        exchange=_TRADING_CALENDAR_EXCHANGE,
    )
    rows = executor.execute(sql) or []
    per_day_rows = {_as_date_text(r[0]): int(r[1]) for r in rows}  # dict 保序=SQL 的 ORDER BY {date_col}
    ghost_dates = list(per_day_rows)
    ghost_rows = sum(per_day_rows.values())
    if ghost_rows <= spec.non_trading_max_rows:
        return []
    head = ", ".join(f"{d}({per_day_rows[d]}行)" for d in ghost_dates[:_MAX_DATES_IN_DETAIL])
    tail = f" 等共 {len(ghost_dates)} 个非交易日" if len(ghost_dates) > _MAX_DATES_IN_DETAIL else ""
    return [
        SentinelFinding(
            table=spec.table,
            check="non_trading_day",
            severity="CRITICAL",
            detail=(
                f"{spec.table}.{spec.date_col} 有 {ghost_rows} 行落在非交易日（权威日历 {cal_ref} 无此开市日）"
                f"：{head}{tail}（容忍上限 {spec.non_trading_max_rows}）"
            ),
            metric={
                "column": spec.date_col,
                "non_trading_rows": ghost_rows,
                "max_rows": spec.non_trading_max_rows,
                "non_trading_dates": ghost_dates[:_MAX_DATES_IN_METRIC],
                "rows_per_non_trading_date": {d: per_day_rows[d] for d in ghost_dates[:_MAX_DATES_IN_METRIC]},
                "non_trading_date_count": len(ghost_dates),
                "calendar": cal_ref,
                "calendar_open_days": open_days,
            },
        )
    ]


# ============== 编排：巡检 + 报告 + 告警 ==============


@dataclass(frozen=True)
class SentinelOutput:
    """输出控制参数对象（报告落盘 + 告警开关）。

    report_dir=None=不落盘；None 以外路径=报告目录；notify=False 禁用告警。
    """

    report_dir: Path | None = None
    notify: bool = True


def _check_one_table(
    executor: QueryExecutor,
    calendar: "MarketCalendar",
    spec: TableSpec,
    ref_date: date,
) -> tuple[dict, list[SentinelFinding]]:
    """单表四类检测；任一检查失败降级记录不中断全表巡检（ERROR_CONTRACT）。"""
    entry: dict = {"table": spec.table, "checks": {}, "degraded": []}
    found_all: list[SentinelFinding] = []
    checks = (
        ("epoch", lambda: check_epoch(executor, spec)),
        ("tz_shift", lambda: check_tz_shift(executor, spec, ref_date)),
        ("empty_segment", lambda: check_empty_segment(executor, spec, ref_date, calendar)),
        # 污染尺按表 opt-in（spec.non_trading_max_rows is None 时内部直接返回 []，不打 CH）
        ("non_trading_day", lambda: check_non_trading_day(executor, spec)),
    )
    for name, fn in checks:
        try:
            found = fn()
            entry["checks"][name] = {"finding_count": len(found)}
            found_all.extend(found)
        except Exception as e:  # noqa: BLE001 — 单表失败降级不中断全表巡检（ERROR_CONTRACT）
            entry["degraded"].append(f"{name}: {type(e).__name__}: {e}")
            log.error("哨兵检查降级 table=%s check=%s: %s", spec.table, name, e)
    return entry, found_all


def _notify_findings(alerter, findings: list[SentinelFinding]) -> None:
    """逐条告警正门；单条失败 log 不抛（同 Alerter 契约）。"""
    for f in findings:
        try:
            alerter.notify(
                f"quality_sentinel_{f.table}",
                f.detail,
                level=f.severity,
                source="quality_sentinel",
                extra={"check": f.check, **f.metric},
            )
        except Exception as e:  # noqa: BLE001 — 告警失败不抛（同 Alerter 契约）
            log.error("哨兵告警发送失败 table=%s: %s", f.table, e)


def run_sentinel(
    specs: list[TableSpec],
    *,
    executor: QueryExecutor | None = None,
    calendar: "MarketCalendar | None" = None,
    alerter=None,
    output: SentinelOutput | None = None,
    ref_date: date | None = None,
) -> dict:
    """哨兵主入口：逐表四类检测 -> 报告 JSON -> 超阈值告警。

    Args:
        specs: 表配置（load_specs 产出）。
        executor: CH 查询执行器；None=经 DatabaseService 领 reader 连接（唯一正门）。
        calendar: 交易日历；None=A股日历。
        alerter: 告警器；None=Alerter() 正门（notify=False 时不装配）。
        output: 输出控制（SentinelOutput）；None=默认目录落盘+发告警。
        ref_date: 检测基准日；None=上海时区今日（经 now_utc 统一入口，RULE-SCHEMA-TZ）。

    Returns:
        报告 dict（含 findings 列表与 findings_count；CLI exit code 取 findings_count）。
    """
    output = output or SentinelOutput()
    if executor is None:
        executor = _default_executor()
    if calendar is None:
        calendar = _default_calendar()
    if alerter is None and output.notify:
        alerter = _default_alerter()
    if ref_date is None:
        # RULE-SCHEMA-TZ：当前时间唯一入口 now_utc()，此地仅做上海日界换算
        ref_date = now_utc().astimezone(_SHANGHAI_TZ).date()

    results: list[dict] = []
    findings: list[SentinelFinding] = []
    for spec in specs:
        entry, found = _check_one_table(executor, calendar, spec, ref_date)
        findings.extend(found)
        results.append(entry)

    report: dict = {
        "sentinel": "quality_sentinel",
        "schema_version": 1,
        "ref_date": ref_date.isoformat(),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "tables_checked": [s.table for s in specs],
        "results": results,
        "findings": [
            {
                "table": f.table,
                "check": f.check,
                "severity": f.severity,
                "detail": f.detail,
                "metric": f.metric,
            }
            for f in findings
        ],
        "findings_count": len(findings),
    }

    if output.report_dir is not None:
        out = Path(output.report_dir)
        report_path = out / f"{ref_date.isoformat()}_report.json"
        report["report_path"] = str(report_path)
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        result = safe_write_text(report_path, payload)
        if not result.written:
            log.error("哨兵报告写入失败: %s", report_path)
        else:
            log.info("哨兵报告已写入: %s", report_path)

    if findings and alerter is not None:
        _notify_findings(alerter, findings)

    degraded_count = sum(1 for r in results if r["degraded"])
    log.info(
        "哨兵巡检完成: ref_date=%s tables=%d findings=%d degraded=%d",
        ref_date.isoformat(), len(specs), len(findings), degraded_count,
    )
    return report


# ============== 默认依赖装配（懒加载，测试注入 fake 不触发） ==============


def _default_executor() -> QueryExecutor:
    """CH 只读连接——全仓唯一 Client 构造点 DatabaseService（宪法 §9.1 禁裸连接）。"""
    from zephyr.infrastructure.database_service import get_db_service

    return get_db_service().get_clickhouse_conn(role="reader", slot="quality_sentinel")


def _default_calendar() -> "MarketCalendar":
    from zephyr.data.calendar import get_market_calendar

    return get_market_calendar("ashare")


def _default_alerter():
    from zephyr.data.alerter import Alerter

    return Alerter()


def _to_exit_code(findings_count: int) -> int:
    """变异数 -> 进程退出码（>255 封顶 255，POSIX 退出码语义）。"""
    return min(int(findings_count), _EXIT_CODE_CAP)


# ============== 排班托管（L13 data_supply_sentinel 腿，四要素正门） ==============


def _load_wiring(config_path: str | Path | None = None) -> dict:
    """读 wiring 块（托管节奏等运维参数）；缺块=用默认值，非映射=配置错。"""
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if not path.exists():
        raise _config_error("哨兵表配置缺失", path=str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    wiring = raw.get("wiring") or {}
    if not isinstance(wiring, dict):
        raise _config_error("哨兵配置 wiring 须为映射", value=repr(wiring))
    return wiring


def _latest_report_date(report_dir: Path) -> date | None:
    """最近一次巡检日（**报告文件名即状态真源**，不另立 state 文件造成第二真源）。"""
    if not report_dir.is_dir():
        return None
    dates: list[date] = []
    for path in report_dir.glob("*_report.json"):
        try:
            dates.append(date.fromisoformat(path.name[:10]))
        except ValueError:
            continue
    return max(dates) if dates else None


def run_hosted_sweep(
    alerter: object | None = None,
    *,
    config_path: str | Path | None = None,
    report_dir: str | Path | None = None,
    ref_date: date | None = None,
) -> dict:
    """由 L13 `data_supply_sentinel` 排班腿托管的变异巡检（§4.3 自动化四要素的正门形态）。

    四要素各自的落点：
      自动触发 = 宿主槽位（宿主排班批经 L13 data_supply_sentinel 槽位；本件是数据哨兵不是
                 自愈 reconciler 环，故不适用宪法 §9.3"reconciler 必须事件触发"令）；
      自动运行 = 本函数（配置 -> load_specs -> run_sentinel，CH 只读经 DatabaseService）；
      自动维护 = sweep_cadence_days 节奏闸（全史 epoch 扫描代价高，按报告日期自愈节流）；
      自动关闭 = data/runtime/quality_sentinel.disabled 标记文件（实查、即时生效）。

    Args:
        alerter: 复用宿主 Alerter（None 则 run_sentinel 自装配正门 Alerter）。
        config_path: 表配置路径（None=config/quality_sentinel_tables.yaml）。
        report_dir: 报告目录（None=data/quality_sentinel/；测试传 tmp_path 禁写生产目录）。
        ref_date: 基准日（None=上海时区今日，经 now_utc 统一入口）。

    Returns:
        {ok, findings_count, tables_checked, degraded_tables, report_path} 或
        {ok: True, skipped: <原因>}（总闸关闭 / 节奏未到）。
    """
    if _DISABLED_FLAG_PATH.exists():
        log.info("质量哨兵总闸关闭（%s 存在），本次托管巡检跳过", _DISABLED_FLAG_PATH)
        return {"ok": True, "skipped": "master_switch_off"}
    wiring = _load_wiring(config_path)
    raw_cadence = wiring.get("sweep_cadence_days", _DEFAULT_SWEEP_CADENCE_DAYS)
    try:
        cadence_days = int(raw_cadence)
    except (TypeError, ValueError) as ex:
        raise _config_error("sweep_cadence_days 须为整数", value=repr(raw_cadence)) from ex
    if cadence_days < 1:
        # 0/负数=每班都跳过却回 ok=True（巡检静默空转还谎报干净），比报错更危险，fail-closed
        raise _config_error("sweep_cadence_days 须 >=1（0/负数=巡检静默空转）", value=cadence_days)
    out_dir = Path(report_dir) if report_dir else _DEFAULT_OUTPUT_DIR
    ref = ref_date or now_utc().astimezone(_SHANGHAI_TZ).date()
    last = _latest_report_date(out_dir)
    if last is not None and (ref - last).days < cadence_days:
        log.info("质量哨兵按节奏跳过: last=%s cadence=%dd", last.isoformat(), cadence_days)
        return {"ok": True, "skipped": f"cadence_{cadence_days}d_last_{last.isoformat()}"}
    specs = load_specs(config_path)
    if not specs:
        raise _config_error("托管巡检无可巡检表（配置 tables 过滤后为空）")
    report = run_sentinel(
        specs, alerter=alerter, output=SentinelOutput(report_dir=out_dir), ref_date=ref
    )
    degraded = sum(1 for r in report["results"] if r["degraded"])
    all_degraded = bool(report["results"]) and degraded == len(report["results"])
    return {
        "ok": report["findings_count"] == 0 and not all_degraded,
        "findings_count": report["findings_count"],
        "tables_checked": len(report["results"]),
        "degraded_tables": degraded,
        "all_degraded": all_degraded,
        "report_path": report.get("report_path"),
        "ref_date": ref.isoformat(),
    }


# ============== CLI ==============


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。exit code = 发现变异数（0=干净；253=全表 degraded；254=配置错误）。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.quality_sentinel",
        description="数据质量常驻哨兵：1970 纪元/时区偏移/空段/非交易日有行四类变异检测（WO-④-01 + C-36）",
    )
    parser.add_argument("--tables", default=None, help="逗号分隔表名过滤（短名或全名），默认全表")
    parser.add_argument(
        "--days", type=int, default=None,
        help="回看窗口（日历日/交易日数）：覆盖 tz_check_days 与 empty_gap_trading_days",
    )
    parser.add_argument("--config", default=None, help=f"表配置路径（默认 {_DEFAULT_CONFIG_PATH}）")
    parser.add_argument("--output-dir", default=None, help=f"报告目录（默认 {_DEFAULT_OUTPUT_DIR}）")
    parser.add_argument("--no-report", action="store_true", help="只检测不写报告文件")
    parser.add_argument("--no-alert", action="store_true", help="只检测不发告警")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    tables = [t for t in args.tables.split(",")] if args.tables else None
    try:
        specs = load_specs(args.config, tables=tables, days=args.days)
    except QualitySentinelError as e:
        log.critical("哨兵配置错误: %s details=%s", e, getattr(e, "details", None))
        return _EXIT_CONFIG_ERROR
    if not specs:
        # 过滤零命中（表名拼错/全空白）≠ 全表 degraded——all([]) 恒真会谎报 253 误鸣 CH 断连
        log.critical("哨兵表过滤零命中（--tables=%r），没有可巡检对象", args.tables)
        return _EXIT_CONFIG_ERROR

    report = run_sentinel(
        specs,
        output=SentinelOutput(
            report_dir=None if args.no_report else (Path(args.output_dir) if args.output_dir else _DEFAULT_OUTPUT_DIR),
            notify=not args.no_alert,
        ),
    )
    if all(r["degraded"] for r in report["results"]):
        # 全表 degraded = 巡检未生效（如 CH 不可达），不能谎报"干净"
        log.critical("哨兵全表降级，巡检未生效（详见日志）")
        return _EXIT_ALL_DEGRADED
    return _to_exit_code(report["findings_count"])


if __name__ == "__main__":
    sys.exit(main())
