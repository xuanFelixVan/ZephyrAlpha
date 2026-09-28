# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cleaning_rules_hosting
# [DOMAIN] D_DATA
# [TTL] permanent
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/zephyr/data/test_cleaning_rules_hosting.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [ERROR_CONTRACT] 配置缺失/解析失败/未知键/规则 DSL 非法/host 不符->CleaningGateConfigError（CLI exit 254）；单表查询异常->degraded 不抛；全表 degraded->CLI exit 253；not_run/degraded_partial->托管腿 ok=False 禁冒绿（完整标注见下方同名字段段）
# [DEPENDENCIES] zephyr.data.cleaning_rule_engine(DSL 引擎真身); zephyr.data.alerter(告警唯一正门); zephyr.infrastructure.database_service(懒加载, CH 只读唯一入口); zephyr.shared.io.file_utils(safe_write_text); zephyr.shared.io.paths; zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] zephyr.data.supply_sentinel.run_supply_sentinel -> _run_hosted_cleaning_gate（L13 data_supply_sentinel 排班腿托管第二段，R-M1-06 接线 2026-09-26）；CLI 独立运行
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] 判据值唯一真源=config/cleaning_rules.yaml（宪法硬规则 6 RULE-SSOT，代码禁写阈值/分位/护栏/回看窗任何判据值）;
#   只读检测禁修数（CH 访问唯一入口=DatabaseService.get_clickhouse_conn(role=reader)，禁裸连接）;
#   读侧 flag 档出厂态=本腿不剔除生产行、不改 ch_writer 写路径、不改既有产出（action=block 也只计数出声）;
#   未知键=配置错上抛（wiring/table 条目键集由 dataclass 字段派生，禁手工清单——宪法 §9.5）;
#   YAML 缺失/解析失败/规则非法/host_schedule 与实调方不符/表清单为空=**fail-closed**：
#     抛 CleaningGateConfigError，托管腿转 ok=False 并出声，绝不返回"干净";
#   单表查询失败=degraded 不中断全表；全表 degraded=巡检未生效，ok=False（禁谎报绿）;
#   **读数诚实面**（W6-H 反假绿 2026-09-26，红队案卷 rb2_guard_attacks §二.9/§二.10/§三.3）：
#     结论 status 四态=ran_and_clean｜ran_with_findings｜degraded_partial（任一表降级**或** 0 行样本）
#     ｜not_run(reason)（总闸/停用标记/节奏闸），**只有 ran_and_clean 允许 ok=True**；
#     not_run 与 degraded_partial 一律 ok=False 且必出声（LEVEL_WARN）+ 写状态台账
#     （台账文件名不匹配 *_cleaning_report.json ⇒ 永不被节奏闸误记为"已巡检"）;
#   节奏闸状态真源仍=报告文件名前 10 字符，但**须验正文**（gate+inspection_ran 不合=不当已巡检，
#     rb2 §二.13"写一份当天命名的空 JSON 即可让本腿睡 7 天"的投毒面）;
#   **结论消费面实况=advisory_only_half_wired**：本件 ok 只进 Alerter 告警面与报告台账，
#     不进排班判定（宿主 supply_sentinel.run_supply_sentinel:541 存 summary["cleaning_gate"]，
#     而 scheduler 读的是断供腿 ok）⇒ 只可称"能跑＋出声"，禁称"已执法"（接线一行=总筹待登项）;
#   当前时间统一 now_utc() 入口（RULE-SCHEMA-TZ）；DateTime64/Date 谓词显式日界口径;
#   报告 JSON 落 wiring.report_dir 经 safe_write_text；报告文件名前 10 字符=节奏闸状态真源（不另立 state 文件）;
#   列名白名单=标识符正则校验后拼列（防把 YAML 值当 SQL 片段注入）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置缺失/解析失败/未知键/规则 DSL 非法/host 不符->CleaningGateConfigError（CLI exit 254）;
#   承载册非法编码（UnicodeDecodeError）亦归本错型，禁裸 traceback 冒给运维;
#   单表查询异常->degraded 记录不抛; 全表 degraded->CLI exit 253; 部分降级/零样本->CLI exit 252;
#   not_run/degraded_partial->托管腿 ok=False（禁冒绿）; 托管腿全程不抛（宿主负责出声）
# [TESTS] tests/zephyr/data/test_cleaning_rules_hosting.py
# [A_module] module_id=MOD-L00-004-CRH | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""清洗规则引擎排班托管腿（R-M1-06 "建了没接" 接线第一刀）。

诞生背景（实证册 docs/_working/fullflow_mining/m1_data/90_backfill_wave.md §三 3.1 /
02_cleaning.md C1）：cleaning_rule_engine（DSL 引擎，418 行+65 例测试）自晋升批起
**零生产调用点**，且 config/ 无 DSL 承载文件=既无插头插座。本件补插座并把插头接到
**既有** L13 data_supply_sentinel 排班腿（同 quality_sentinel.run_hosted_sweep 托管先例，
见 config/quality_sentinel_tables.yaml:103-106 wiring 块），不新建平行管线、不新开空槽位
（R-021：排班真源有名字、调度侧无实现=静默假通道）。

四要素落点（宪法 §9.3）：
  自动触发 = 宿主槽位 data_supply_sentinel（不新增排班条目）
  自动运行 = run_hosted_cleaning_gate（配置 -> DSL -> CH 只读取行 -> run_quality_gate -> 报告+告警）
  自动维护 = wiring.cadence_days 节奏闸（报告文件名即状态真源）
  自动关闭 = wiring.disabled_flag 标记文件（每次触发实查，即时生效）

读侧 flag 档（出厂态，本役"新能力默认不改变既有产出"承诺）：
  本腿 SELECT 近窗行做逐行 DSL 判定，出**报告与告警**；不写库、不剔除生产行、
  不碰 ch_writer 写路径。规则 action=block 在本腿只体现为 stats.intercepted 计数出声。
  把 block 落到写路径＝改热路径+翻默认值，属 Owner 门位（宪法 §5 production 流转），
  已登记 docs/_working/fullflow_mining/m1_data/wiring_C_cleaning.md 待登项，本件不做。

诚实边界（防"接了就当自进化在用"）：滚动分位阈值在**单次运行内**由 seed+本次观测演化，
运行间不持久化——持久化需第二状态真源（DB 表或 YAML 回写），属下一批，本件不擅自造。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 承载册 config/cleaning_rules.yaml（wiring + 表规则册，判据值唯一真源）
# - id: I2
#   name: CH 近窗行（DatabaseService 只读连接，逐表 LIMIT read_limit_rows）
# 层: 处理
# - id: P1
#   name: load_rulebook 校验（schema_version/未知键/DSL 合法性；非法=CleaningGateConfigError fail-closed）
# - id: P2
#   name: _evaluate_table 逐表判定（取数→DSL 引擎→零样本标记；单表异常=degraded 不中断全表）
# 层: 输出
# - id: O1
#   name: 报告 JSON（safe_write_text 落 report_dir；文件名前 10 字符=节奏闸状态真源）
# - id: O2
#   name: _notify_results 告警面（降级/零样本/命中/待审批，只出声不执法）
# 边:
# I1 -> P1 -> P2 -> O1 -> O2
# I2 -> P2
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass, field, fields
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final, Protocol
from zoneinfo import ZoneInfo

import yaml

from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, LEVEL_INFO, LEVEL_WARN
from zephyr.data.cleaning_rule_engine import (
    CleaningRuleEngine,
    CleaningRuleError,
    parse_rules,
    run_quality_gate,
)
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

# create-guard-not-dup: 本件是清洗规则承载册托管只读巡检腿，非字典展开门/secrets 提供方/回撤引擎/yaml 锚点扫描的第二实现，命中词 config error=通用语料噪声

log = logging.getLogger(__name__)

#: 业务日界口径（同 quality_sentinel；禁 datetime.now() 散落，RULE-SCHEMA-TZ）
_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

__all__: Final = [
    "CleaningGateConfigError",
    "STATUS_DEGRADED_PARTIAL",
    "STATUS_NOT_RUN",
    "STATUS_RAN_CLEAN",
    "STATUS_RAN_FINDINGS",
    "TableRulebook",
    "WiringConfig",
    "ENFORCEMENT_STATE",
    "gate_status",
    "load_rulebook",
    "run_cleaning_gate",
    "run_hosted_cleaning_gate",
    "status_exit_code",
    "main",
]

_DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "cleaning_rules.yaml"

#: 告警级别合法集（由 alerter 常量派生，禁自造通道/自写级别名）
_ALLOWED_LEVELS: Final = frozenset({LEVEL_INFO, LEVEL_WARN, LEVEL_ERROR, LEVEL_CRITICAL})

#: SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀约定）
_SQL_FETCH_ROWS = (
    "SELECT {columns} FROM {table} WHERE {date_col} "
    "BETWEEN toDate('{start}') AND toDate('{end}'){final_clause} "
    "ORDER BY {date_col} DESC LIMIT {limit}"
)

#: 标识符（表名/列名）白名单：只允许库内常规命名，其余=配置错（禁把 YAML 值当 SQL 片段）
_IDENTIFIER_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")

_EXIT_PARTIAL_DEGRADED: Final = 252
_EXIT_ALL_DEGRADED: Final = 253
_EXIT_CONFIG_ERROR: Final = 254
_EXIT_CODE_CAP: Final = 255

#: 结论四态（诚实读数真源）——**只有 ran_and_clean 允许 ok=True**；
#: not_run/degraded_partial 冒 ok=True 就是红队案卷 §二.9/§二.10/§三.3 的三条绕过本体。
STATUS_RAN_CLEAN: Final = "ran_and_clean"
STATUS_RAN_FINDINGS: Final = "ran_with_findings"
STATUS_DEGRADED_PARTIAL: Final = "degraded_partial"
STATUS_NOT_RUN: Final = "not_run"
_OK_STATUS: Final = STATUS_RAN_CLEAN
#: 只有"真跑了且判完"的读数才有资格占节奏闸（降级/零样本不得让本腿再睡 cadence_days 天）
_INSPECTION_COUNTS_STATUSES: Final = frozenset({STATUS_RAN_CLEAN, STATUS_RAN_FINDINGS})

#: not_run 原因（三把停用闸各有名字，禁与"跑过且干净"混成同一个 ok）
NOT_RUN_WIRING_DISABLED: Final = "wiring_disabled"
NOT_RUN_MASTER_SWITCH_OFF: Final = "master_switch_off"
NOT_RUN_CADENCE_PREFIX: Final = "cadence"

#: 结论消费面实况的机读自述（禁把"能跑"写成"已执法"）
ENFORCEMENT_STATE: Final = "advisory_only_half_wired"
ENFORCEMENT_NOTE: Final = (
    "本件结论只进 Alerter 告警面＋报告/状态台账；宿主 supply_sentinel.run_supply_sentinel 虽调本腿，"
    "但 scheduler 读的是断供腿 ok，cleaning_gate.ok 至今无人消费＝半接线（接排班判定一行=总筹待登项）"
)

#: 报告与状态台账文件名后缀——台账刻意**不匹配** ``*_cleaning_report.json``，
#: 防"根本没跑"被节奏闸误记成"当天已巡检"（rb2 §二.13 命名投毒面的同族防线）
_REPORT_SUFFIX: Final = "_cleaning_report.json"
_LEDGER_SUFFIX: Final = "_cleaning_gate_status_ledger.json"


class CleaningGateConfigError(Exception):
    """承载册缺失/解析失败/未知键/规则非法/host 不符（fail-closed，绝不静默当已覆盖）。"""


# class-name-alias: 清洗托管腿 CH 查询最小协议（与 quality_sentinel.QueryExecutor 同名不同义：本件只读巡检的注入缝，对标其 hosted_sweep 同款先例但零 import 交互；保字节捞回不改名以维持原车道可追溯性）
class QueryExecutor(Protocol):
    """CH 查询执行器最小协议（生产实现=clickhouse_driver.Client，经 DatabaseService 领取）。"""

    def execute(self, sql: str) -> list:  # noqa: D102 - 协议即文档
        ...


@dataclass(frozen=True)
class WiringConfig:
    """承载册 wiring 块投影（运维参数；键集=本 dataclass 字段，派生校验）。"""

    enabled: bool
    host_schedule: str
    cadence_days: int
    read_limit_rows: int
    alert_level: str
    report_dir: str
    disabled_flag: str


@dataclass(frozen=True)
class TableRulebook:
    """单表规则册（tables 条目投影）。rules 原样交 DSL 引擎 parse_rules。"""

    table: str
    date_col: str
    lookback_days: int
    use_final: bool = False
    rules: list[dict[str, Any]] = field(default_factory=list)


_WIRING_FIELDS: Final = frozenset(_f.name for _f in fields(WiringConfig))
_TABLE_FIELDS: Final = frozenset(_f.name for _f in fields(TableRulebook))


def _config_error(msg: str, **details: Any) -> CleaningGateConfigError:
    """配置错工厂：路径等敏感/长信息走 details，不进消息文本（MSG-EXPOSURE 同族口径）。"""
    exc = CleaningGateConfigError(msg)
    exc.details = details  # type: ignore[attr-defined]
    return exc


def _reject_unknown_keys(mapping: dict, *, legal: frozenset[str], where: str) -> None:
    """未知键 fail-loud：拼错的键会让该条检查静默不跑却看起来在岗（装饰性护栏母型）。"""
    unknown = sorted(set(mapping) - legal)
    if unknown:
        raise _config_error(
            "清洗承载册含未知键（拼错的键=该检查静默空转，禁静默忽略）",
            where=where,
            unknown=unknown,
            legal=sorted(legal),
        )


def _require(mapping: dict, key: str, *, where: str) -> Any:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    if key not in mapping:
        raise _config_error("清洗承载册缺必填键（无默认判据兜底=fail-closed）", where=where, key=key)
    return mapping[key]


def _parse_bool(value: Any, *, where: str) -> bool:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    if not isinstance(value, bool):
        raise _config_error("布尔键须为 true/false", where=where, value=repr(value))
    return value


def _parse_positive_int(value: Any, *, where: str) -> int:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    """正整数解析：bool 投毒必须炸（true→1 会把节奏闸/行数上限悄悄掰松）。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise _config_error("整数键须为整数", where=where, value=repr(value))
    if value < 1:
        # 0/负数=每班跳过或零行读取，却回 ok=True（静默空转谎报干净），比报错更危险
        raise _config_error("整数键须 >=1（0/负数=本腿静默空转）", where=where, value=value)
    return value


def _check_identifier(value: str, *, where: str) -> str:
    if not _IDENTIFIER_RE.match(value or ""):
        raise _config_error("表名/列名非法（只允许标识符，禁 SQL 片段）", where=where, value=value)
    return value


def _load_raw(config_path: str | Path | None) -> dict:
    """读承载册 YAML：缺文件/非映射/解析失败/**非法编码**一律 CleaningGateConfigError（fail-closed）。"""
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if not path.exists():
        raise _config_error("清洗规则承载册缺失（判据无真源=本腿不跑，绝不默认放行）", path=str(path))
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as ex:
        # rb2 §二.14 实测绕过：非法字节抛未声明错型，CLI 只捕 CleaningGateConfigError=裸 traceback
        raise _config_error(
            "清洗规则承载册非法编码（须 UTF-8；错型不外溢）", path=str(path), error=str(ex)[:200]
        ) from ex
    except OSError as ex:
        raise _config_error("清洗规则承载册读不到", path=str(path), error=str(ex)[:200]) from ex
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as ex:  # 解析失败=判据不可信，禁按"无规则"处理
        raise _config_error("清洗规则承载册 YAML 解析失败", path=str(path), error=str(ex)[:200]) from ex
    if not isinstance(raw, dict):
        raise _config_error("清洗规则承载册根节点须为映射", path=str(path), value=type(raw).__name__)
    return raw


def _load_wiring(raw: dict, *, where: str = "wiring") -> WiringConfig:
    block = raw.get("wiring")
    if not isinstance(block, dict):
        raise _config_error("清洗承载册缺 wiring 块（运维参数无真源=不猜默认值）")
    _reject_unknown_keys(block, legal=_WIRING_FIELDS, where=where)
    level = str(_require(block, "alert_level", where=where)).upper()
    if level not in _ALLOWED_LEVELS:
        raise _config_error("alert_level 非法", where=where, value=level, legal=sorted(_ALLOWED_LEVELS))
    return WiringConfig(
        enabled=_parse_bool(_require(block, "enabled", where=where), where=where),
        host_schedule=str(_require(block, "host_schedule", where=where)),
        cadence_days=_parse_positive_int(_require(block, "cadence_days", where=where), where=where),
        read_limit_rows=_parse_positive_int(_require(block, "read_limit_rows", where=where), where=where),
        alert_level=level,
        report_dir=str(_require(block, "report_dir", where=where)),
        disabled_flag=str(_require(block, "disabled_flag", where=where)),
    )


def _parse_table_entry(entry: Any, where: str) -> TableRulebook:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    """单表规则册条目解析与校验（COMPLEXITY-GUARD 治本：自 load_rulebook 拆出，行为等价）。"""
    if not isinstance(entry, dict):
        raise _config_error("tables 条目须为映射", where=where, value=repr(entry))
    _reject_unknown_keys(entry, legal=_TABLE_FIELDS, where=where)
    table = _check_identifier(str(_require(entry, "table", where=where)), where=f"{where}.table")
    date_col = _check_identifier(str(_require(entry, "date_col", where=where)), where=f"{where}.date_col")
    lookback = _parse_positive_int(_require(entry, "lookback_days", where=where), where=f"{where}.lookback_days")
    use_final = _parse_bool(entry.get("use_final", False), where=f"{where}.use_final")
    rules = entry.get("rules")
    if not isinstance(rules, list) or not rules:
        raise _config_error("表规则册 rules 为空（有表无尺=假覆盖）", where=where, table=table)
    for rule in rules:
        if not isinstance(rule, dict):
            raise _config_error("rule 须为映射", where=f"{where}.rules", value=repr(rule))
        if "field" in rule:
            _check_identifier(str(rule["field"]), where=f"{where}.rules.field")
    try:
        parse_rules(rules)  # DSL 合法性在加载期即校验（op/必填字段/action）
    except CleaningRuleError as ex:
        raise _config_error("清洗规则 DSL 非法", where=where, table=table, error=str(ex)) from ex
    return TableRulebook(
        table=table,
        date_col=date_col,
        lookback_days=lookback,
        use_final=use_final,
        rules=list(rules),
    )


def load_rulebook(
    config_path: str | Path | None = None,
    *,
    tables: list[str] | None = None,
) -> tuple[WiringConfig, list[TableRulebook]]:
    """承载册 -> (wiring, 表规则册列表)；一切非法在此上抛，不到运行期。"""
    raw = _load_raw(config_path)
    if int(raw.get("schema_version") or 0) != 1:
        raise _config_error("清洗承载册 schema_version 须为 1", value=raw.get("schema_version"))
    wiring = _load_wiring(raw)
    entries = raw.get("tables")
    if not isinstance(entries, list) or not entries:
        # 空表清单=本腿无对象却回 ok=True，正是"接线了但什么都不查"的假绿形态
        raise _config_error("清洗承载册 tables 为空（无巡检对象）")
    books = [_parse_table_entry(entry, f"tables[{idx}]") for idx, entry in enumerate(entries)]
    if tables:
        wanted = set(tables)
        books = [b for b in books if b.table in wanted or b.table.split(".")[-1] in wanted]
        if not books:
            # 过滤零命中≠全表降级：拿 --tables 拼错表名会得到"没有对象"，必须判配置错
            raise _config_error("表名过滤零命中（拼错表名≠已巡检）", requested=sorted(wanted))
    return wiring, books


def _repo_relative(value: str) -> Path:
    """承载册路径口径：相对=锚 REPO_ROOT，绝对=原样（测试须指 tmp_path，禁写生产目录）。"""
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _default_executor() -> QueryExecutor:
    """CH 只读连接——全仓唯一 Client 构造点 DatabaseService（宪法 §9.1 禁裸连接）。"""
    from zephyr.infrastructure.database_service import get_db_service

    return get_db_service().get_clickhouse_conn(role="reader", slot="cleaning_rules_hosting")


def _fetch_rows(executor: QueryExecutor, book: TableRulebook, *, ref: date, limit: int) -> list[dict[str, Any]]:
    """按表规则册取近窗行（列面=规则字段∪date_col，全部由承载册派生，代码不写列名/窗口值）。"""
    columns = sorted({book.date_col, *(str(r["field"]) for r in book.rules if r.get("field"))})
    span = max(book.lookback_days - 1, 0)
    sql = _SQL_FETCH_ROWS.format(
        columns=", ".join(columns),
        table=book.table,
        date_col=book.date_col,
        start=(ref - timedelta(days=span)).isoformat(),
        end=ref.isoformat(),
        final_clause=" FINAL" if book.use_final else "",
        limit=limit,
    )
    rows = executor.execute(sql) or []
    return [dict(zip(columns, row, strict=False)) for row in rows]


def _evaluate_table(executor: QueryExecutor, book: TableRulebook, *, ref: date, limit: int) -> dict:
    """单表只读判定（COMPLEXITY-GUARD 治本：自 run_cleaning_gate 拆出，行为等价）。

    单表异常只降级该表，不中断全表巡检（fail-open per-table，结果面如实标记 degraded）。
    """
    entry: dict[str, Any] = {
        "table": book.table,
        "degraded": False,
        "no_samples": False,
        "lookback_days": book.lookback_days,
        "stats": {},
        "pending_approvals": [],
    }
    try:
        rows = _fetch_rows(executor, book, ref=ref, limit=limit)
        engine = CleaningRuleEngine(parse_rules(book.rules))
        clean, stats = run_quality_gate(engine, book.table, rows)
        entry["rows_read"] = len(rows)
        # rb2 §二.10 实测绕过：0 行（表空/口径错/窗口写歪）被当"已巡检且干净"。
        # 零样本=无对象可判，不是"判干净"——单列 no_samples，读数面据此降级（家法同
        # scripts/run_post_settlement.py 的"零样本必打 WARNING＋落台账"）。
        entry["no_samples"] = len(rows) == 0
        entry["rows_kept_in_memory"] = len(clean)
        entry["stats"] = stats
        for fld in sorted({r["field"] for r in book.rules if r.get("field")}):
            values = [float(r[fld]) for r in rows if isinstance(r.get(fld), (int, float))]
            if values:
                entry["pending_approvals"] += engine.observe(str(fld), values)
        entry["pending_approvals"] = sorted(set(entry["pending_approvals"]))
        entry["clean"] = not (stats["flagged"] or stats["intercepted"])
    except CleaningRuleError as ex:  # DSL 运行期错误（加载期漏网的）=该表出声不背绿
        entry["degraded"] = True
        entry["error"] = str(ex)[:200]
        log.exception("清洗规则引擎运行期错误: %s", book.table)
    except Exception as ex:  # noqa: BLE001 — 单表查询异常只降级，不中断全表巡检
        entry["degraded"] = True
        entry["error"] = str(ex)[:200]
        log.exception("清洗门控取数失败: %s", book.table)
    return entry


def _notify_results(alerter: Any, wiring: WiringConfig, report: dict) -> None:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    """报告告警面（COMPLEXITY-GUARD 治本：自 run_cleaning_gate 拆出，行为等价）。

    读侧只出声不执法：降级/零样本/命中/待审批各走 _alert 唯一正门。
    结果面统一从 report dict 取（results/status/tables/待审批清单一应俱全）。
    """
    results: list[dict] = report["results"]
    status = report["status"]
    degraded_tables = report["degraded_tables"]
    no_sample_tables = report["no_sample_tables"]
    all_degraded = report["all_degraded"]
    pending_approval_rules = report["pending_approval_rules"]
    for entry in results:
        if entry["degraded"]:
            _alert(
                alerter,
                wiring.alert_level,
                f"清洗门控未生效: {entry['table']} [{entry.get('error')}]",
                extra={"table": entry["table"], "degraded": True},
            )
            continue
        if entry["no_samples"]:
            _alert(
                alerter,
                LEVEL_WARN,
                f"清洗门控零样本（无巡检对象，不得当已巡检干净）: {entry['table']} "
                f"近 {entry['lookback_days']}d 窗口 0 行",
                extra={"table": entry["table"], "no_samples": True},
            )
        if entry["stats"].get("flagged") or entry["stats"].get("intercepted"):
            _alert(
                alerter,
                wiring.alert_level,
                f"清洗规则命中: {entry['table']} flagged={entry['stats']['flagged']} "
                f"intercepted={entry['stats']['intercepted']} by_rule={entry['stats']['by_rule']}"
                "（读侧只出声，未改生产数据）",
                extra={"table": entry["table"], **entry["stats"]},
            )
    for rule_name in pending_approval_rules:
        _alert(
            alerter,
            wiring.alert_level,
            f"滚动分位阈值候选越界挂起，需人工审批: {rule_name}",
            extra={"pending_approval": rule_name},
        )
    if status == STATUS_DEGRADED_PARTIAL:
        _alert(
            alerter,
            LEVEL_WARN,
            "清洗门控读数降级（status=degraded_partial，禁冒 ok=True）: "
            f"degraded={degraded_tables} no_samples={no_sample_tables} all_degraded={all_degraded}",
            extra={"status": status, "degraded_tables": degraded_tables, "no_sample_tables": no_sample_tables},
        )


def run_cleaning_gate(
    wiring: WiringConfig,
    books: list[TableRulebook],
    *,
    executor: QueryExecutor | None = None,
    alerter: Any | None = None,  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    ref_date: date | None = None,
    report_dir: str | Path | None = None,
    notify: bool = True,
) -> dict:
    """逐表 DSL 清洗判定（只读出报告），返回报告 dict。"""
    executor = executor or _default_executor()
    ref = ref_date or now_utc().astimezone(_SHANGHAI_TZ).date()
    out_dir = Path(report_dir) if report_dir else _repo_relative(wiring.report_dir)
    results = [_evaluate_table(executor, book, ref=ref, limit=wiring.read_limit_rows) for book in books]

    all_degraded = bool(results) and all(r["degraded"] for r in results)
    status = gate_status(results)
    degraded_tables = [r["table"] for r in results if r["degraded"]]
    no_sample_tables = [r["table"] for r in results if not r["degraded"] and r["no_samples"]]
    findings = [
        r for r in results if not r["degraded"] and (r["stats"].get("flagged") or r["stats"].get("intercepted"))
    ]
    report: dict[str, Any] = {
        "gate": "cleaning_rules_hosting",
        "schema_version": 1,
        "host_schedule": wiring.host_schedule,
        "ref_date": ref.isoformat(),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "read_side_only": True,
        "status": status,
        "inspection_ran": status in _INSPECTION_COUNTS_STATUSES,
        "tables_checked": [b.table for b in books],
        "results": results,
        "degraded_tables": degraded_tables,
        "no_sample_tables": no_sample_tables,
        "findings_count": len(findings),
        "flagged_rows": sum(int(r["stats"].get("flagged") or 0) for r in results),
        "intercepted_rows": sum(int(r["stats"].get("intercepted") or 0) for r in results),
        "pending_approval_rules": sorted({p for r in results for p in r["pending_approvals"]}),
        "all_degraded": all_degraded,
        "enforcement_state": ENFORCEMENT_STATE,
        "enforcement_note": ENFORCEMENT_NOTE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{ref.isoformat()}{_REPORT_SUFFIX}"
    safe_write_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, default=str))
    report["report_path"] = str(report_path)

    if notify and alerter is not None:
        _notify_results(alerter, wiring, report)
    return report


def gate_status(results: list[dict[str, Any]]) -> str:
    """逐表结果 → 诚实四态读数（ok=True 的唯一来源=ran_and_clean）。

    判序（不可颠倒）：任一表**取不到数**或**零样本**=没有对象可判 = degraded_partial
    （优先于"没命中"，否则加一张表就能把失明表稀释成绿——rb2 §二.9 的稀释绕过）；
    其次命中=ran_with_findings；全表有样本且零命中才=ran_and_clean。
    """
    if not results:
        return STATUS_NOT_RUN  # 无对象=根本没跑（load_rulebook 已拦，此处留兜底不谎报）
    if any(r.get("degraded") or r.get("no_samples") for r in results):
        return STATUS_DEGRADED_PARTIAL
    if any(r["stats"].get("flagged") or r["stats"].get("intercepted") for r in results):
        return STATUS_RAN_FINDINGS
    return STATUS_RAN_CLEAN


def status_exit_code(status: str, *, findings_count: int = 0) -> int:
    """CLI 退出码与四态对齐：降级绝不回 0（0=跑过且判干净）。"""
    if status == STATUS_NOT_RUN:
        return _EXIT_PARTIAL_DEGRADED
    if status == STATUS_DEGRADED_PARTIAL:
        return _EXIT_PARTIAL_DEGRADED
    if status == STATUS_RAN_FINDINGS:
        return min(int(findings_count), _EXIT_CODE_CAP)
    return 0


def _alert(alerter: Any, level: str, message: str, *, extra: dict) -> None:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    """告警唯一正门=Alerter.notify（禁自造通道）；通道故障只 log 不抛。"""
    try:
        alerter.notify("cleaning_rules_gate", message, level=level, source="cleaning_rules_hosting", extra=extra)
    except Exception:  # noqa: BLE001 — 告警通道故障不阻断巡检
        log.exception("清洗门控告警写入失败")


def _latest_report_date(report_dir: Path) -> date | None:
    """最近一次**真巡检**日（节奏闸状态真源=报告文件名前 10 字符，但**正文须验**）。

    rb2 §二.13 实测投毒面：只认文件名 ⇒ 任何人往 report_dir 丢一份当天命名的 JSON
    就能让本腿未来 cadence_days 天不跑。故此处要求正文 gate 自对且 ``inspection_ran``
    为真；正文坏/不认=**不记为已巡检**（宁可重跑一次，不可被空文件催眠）。
    """
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
            log.warning("清洗门控节奏闸状态文件不可读，不记为已巡检: %s [%s]", path, str(ex)[:120])
            continue
        if not isinstance(body, dict) or body.get("gate") != "cleaning_rules_hosting":
            log.warning("清洗门控节奏闸状态文件 gate 不自对，不记为已巡检: %s", path)
            continue
        if body.get("status") not in _INSPECTION_COUNTS_STATUSES or not body.get("inspection_ran"):
            log.warning(
                "清洗门控上次读数非「真跑完」（status=%s），不占节奏闸: %s",
                body.get("status"),
                path,
            )
            continue
        dates.append(stamp)
    return max(dates) if dates else None


def _write_status_ledger(
    out_dir: Path, *, ref: date, status: str, reason: str, wiring: WiringConfig, extra: dict[str, Any] | None = None
) -> str:
    """未跑/降级台账（必留痕，家法同 run_post_settlement 零样本台账）。

    文件名后缀刻意不匹配 ``*_cleaning_report.json``：台账记录"没跑"这件事本身，
    绝不能被节奏闸读成"当天已巡检"。
    """
    payload: dict[str, Any] = {
        "gate": "cleaning_rules_hosting",
        "schema_version": 1,
        "host_schedule": wiring.host_schedule,
        "ref_date": ref.isoformat(),
        "generated_at_utc": now_utc().isoformat(timespec="seconds"),
        "status": status,
        "reason": reason,
        "inspection_ran": False,
        "ok": status == _OK_STATUS,
        "enforcement_state": ENFORCEMENT_STATE,
        "enforcement_note": ENFORCEMENT_NOTE,
    }
    if extra:
        payload.update(extra)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ref.isoformat()}{_LEDGER_SUFFIX}"
    safe_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return str(path)


def _not_run(wiring: WiringConfig, *, out_dir: Path, ref: date, alerter: Any, reason: str, note: str) -> dict[str, Any]:  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    """「根本没跑」的统一诚实出口：ok=False + status=not_run + 出声 + 台账（三者缺一不可）。"""
    ledger_path = _write_status_ledger(out_dir, ref=ref, status=STATUS_NOT_RUN, reason=reason, wiring=wiring)
    log.warning("清洗门控未执行（status=not_run reason=%s）：%s", reason, note)
    _alert(
        alerter,
        LEVEL_WARN,
        f"清洗门控未执行（status=not_run，禁当已巡检）: reason={reason} {note}",
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


def run_hosted_cleaning_gate(
    alerter: Any | None = None,  # noqa: any-abuse  any-abuse豁免: 承载册YAML动态值/Alerter注入缝（消费方在supply_sentinel未落地波次），签名无法具体化
    *,
    config_path: str | Path | None = None,
    report_dir: str | Path | None = None,
    ref_date: date | None = None,
    executor: QueryExecutor | None = None,
    host_schedule: str = "data_supply_sentinel",
    force: bool = False,
) -> dict:
    """由 L13 `data_supply_sentinel` 排班腿托管的清洗门控（四要素正门形态）。

    全程不抛：配置错/故障 → {ok: False, ...} + 出声（宿主只读键，不改宿主既有结论）。

    Args:
        alerter: 复用宿主 Alerter（None=自装配正门 Alerter）。
        config_path: 承载册路径（None=config/cleaning_rules.yaml）。
        report_dir: 报告目录覆盖（测试传 tmp_path，禁写生产目录）。
        ref_date: 基准日（None=今日，经 now_utc 统一入口）。
        executor: CH 只读执行器（None=DatabaseService reader 连接）。
        host_schedule: 实调宿主槽位；与承载册声明不符=配置错（防"册里挂了宿主却没接"）。
        force: 跳过节奏闸与总闸（运维手动复查用）。
    """
    if alerter is None:
        # 惰性构造（FUNCTION-DUP 治本：_default_alerter 与 quality_sentinel 同实现克隆，内收敛除）
        from zephyr.data.alerter import Alerter

        alerter = Alerter()
    try:
        wiring, books = load_rulebook(config_path)
    except CleaningGateConfigError as ex:
        # fail-closed：判据不可信时绝不回"干净"
        log.error("清洗规则承载册配置错误: %s details=%s", ex, getattr(ex, "details", None))
        _alert(alerter, LEVEL_ERROR, f"清洗门控未执行（承载册故障）: {str(ex)[:200]}", extra={"config_error": True})
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
            raise CleaningGateConfigError(f"承载册声明宿主={wiring.host_schedule} 与实调宿主={host_schedule} 不符")
        if not force and not wiring.enabled:
            # rb2 §三.3 绕过①：总闸关闭曾回 ok=True 零告警=永久静默本腿却看起来在岗
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
            # rb2 §三.3 绕过②：一个空文件曾让本腿静默停摆且零留痕
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
                # rb2 §三.3 绕过③：节奏闸命中曾回 ok=True 零告警（本次确实没跑，须出声+留痕）
                return _not_run(
                    wiring,
                    out_dir=out_dir,
                    ref=ref,
                    alerter=alerter,
                    reason=f"{NOT_RUN_CADENCE_PREFIX}_{wiring.cadence_days}d_last_{last.isoformat()}",
                    note=f"距上次巡检 {last.isoformat()} 不足 {wiring.cadence_days}d",
                )
        report = run_cleaning_gate(wiring, books, executor=executor, alerter=alerter, ref_date=ref, report_dir=out_dir)
    except CleaningGateConfigError as ex:
        log.error("清洗门控配置错误: %s", ex)
        _alert(
            alerter, wiring.alert_level, f"清洗门控未执行（配置故障）: {str(ex)[:200]}", extra={"config_error": True}
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
        log.exception("清洗门控托管腿失败")
        _alert(alerter, wiring.alert_level, f"清洗门控未执行（腿故障）: {str(exc)[:200]}", extra={"leg_error": True})
        return {
            "ok": False,
            "status": STATUS_NOT_RUN,
            "not_run_reason": "leg_error",
            "inspection_ran": False,
            "error": str(exc)[:200],
            "enforcement_state": ENFORCEMENT_STATE,
        }

    status = str(report["status"])
    # ok=True 的**唯一**合法来源=跑过且判干净（四态见 gate_status）
    ok = status == _OK_STATUS
    log.info(
        "清洗门控巡检完成: status=%s tables=%d findings=%d flagged=%d intercepted=%d degraded=%d no_samples=%d",
        status,
        len(report["tables_checked"]),
        report["findings_count"],
        report["flagged_rows"],
        report["intercepted_rows"],
        len(report["degraded_tables"]),
        len(report["no_sample_tables"]),
    )
    return {
        "ok": ok,
        "status": status,
        "inspection_ran": bool(report["inspection_ran"]),
        "findings_count": report["findings_count"],
        "flagged_rows": report["flagged_rows"],
        "intercepted_rows": report["intercepted_rows"],
        "pending_approval_rules": report["pending_approval_rules"],
        "tables_checked": report["tables_checked"],
        "degraded_tables": report["degraded_tables"],
        "no_sample_tables": report["no_sample_tables"],
        "all_degraded": report["all_degraded"],
        "report_path": report.get("report_path"),
        "ref_date": ref.isoformat(),
        "enforcement_state": ENFORCEMENT_STATE,
        "enforcement_note": ENFORCEMENT_NOTE,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI 入口（运维手动复查）。exit code：0=跑过且判干净｜N=命中表数｜
    252=部分降级/零样本/未跑（禁当绿）｜253=全表降级｜254=配置错。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.cleaning_rules_hosting",
        description="清洗规则引擎托管腿：按 config/cleaning_rules.yaml 逐表 DSL 判定（只读出报告）",
    )
    parser.add_argument("--config", default=None, help=f"承载册路径（默认 {_DEFAULT_CONFIG_PATH}）")
    parser.add_argument("--tables", default=None, help="逗号分隔表名过滤")
    parser.add_argument("--report-dir", default=None, help="报告目录覆盖（默认取承载册 report_dir）")
    parser.add_argument("--no-alert", action="store_true", help="只检测不发告警")
    parser.add_argument("--force", action="store_true", help="跳过节奏闸与停用标记")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    tables = [t.strip() for t in args.tables.split(",")] if args.tables else None
    try:
        wiring, books = load_rulebook(args.config, tables=tables)
    except CleaningGateConfigError as ex:
        log.critical("清洗承载册配置错误: %s details=%s", ex, getattr(ex, "details", None))
        return _EXIT_CONFIG_ERROR
    cli_alerter = None
    if not args.no_alert:
        # 惰性构造（FUNCTION-DUP 治本：_default_alerter 与 quality_sentinel 同实现克隆，内收敛除）
        from zephyr.data.alerter import Alerter

        cli_alerter = Alerter()
    report = run_cleaning_gate(
        wiring,
        books,
        alerter=cli_alerter,
        report_dir=args.report_dir,
        notify=not args.no_alert,
    )
    if report["all_degraded"]:
        log.critical("清洗门控全表降级，巡检未生效（status=%s）", report["status"])
        return _EXIT_ALL_DEGRADED
    if report["status"] != STATUS_RAN_CLEAN:
        log.warning(
            "清洗门控读数非 ran_and_clean: status=%s degraded=%s no_samples=%s",
            report["status"],
            report["degraded_tables"],
            report["no_sample_tables"],
        )
    return status_exit_code(str(report["status"]), findings_count=int(report["findings_count"]))


if __name__ == "__main__":
    raise SystemExit(main())
