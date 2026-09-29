# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1.1(断言段 pit_assertion) + 工单 WO-B3
# [MODULE] zephyr.data.macro_vintage
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.data.ch_writer (strict 写通道); zephyr.infrastructure.database_service (reader 探针);
#                 zephyr.shared.io.yaml_utils.load_vocabulary_values (词表 SSoT); zephyr.shared.utils.time_utils.now_utc
# [CONSUMERS] zephyr.data.ch_writer.write_result 的 macro_data 存证镜像钩子（补丁 0001）；工单脚本 apply/register/audit（scripts/governance/meta_question/wo_b3_macro/）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 发布时戳三态必标（pub_ts_basis 走词表，禁硬编码枚举）：
#   official_release=上游官方发布日历时点｜ingest_observed=首次观测时点（PIT 保守上界，绝不早于真实发布）
#   ｜backfill_final=一次性回补终值（pub_ts 必为 NULL，禁止伪造历史发布时戳——本模块唯一的写入口径）；
#   版次 vintage 同键严格递增且从 1 起，取值由本模块 resolve_vintages 依现存库内最大版次推导（幂等重放安全）；
#   PIT 取数默认 pub_ts IS NOT NULL AND pub_ts <= as_of（回补终值天然不参与历史时点取数）；
#   零 ALTER 业务表：c1_market.macro_data 原表结构/写入路径零触碰，vintage 存证走并行新表+视图兼容层。
# [MODIFY-GUARD] none（新建文件；入库侧改造以 patch 交付，不直改 src/）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 词表缺失/空集->ValueError 立即抛（fail-closed，禁静默放行未知 basis）；
#                  未知 indicator/value 行->跳过并计数返回（不阻断整批）；CH 不可达->RuntimeError。
# [TESTS] python scripts/governance/meta_question/wo_b3_macro/macro_vintage.py --selftest（零 DB 版次推导用例）
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=script | stability=new | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_vintage — 宏观数据发布快照（vintage）存证核心库（WO-B3，PQ-0185/PQ-0191 载体）。

业界对照（第一性原理选型依据，写进案卷）：FRED/ALFRED 的 vintage 数据模型 =
同一 (series_id, observation_date) 在多个 vintage_date 上共存，取数用
realtime_start/realtime_end 限定"当时已知"。本模块把该模型落到本仓 CH 长表：

    c1_market.macro_data            现值表（回补终值，零改动，兼容全部既有消费者）
    c1_market.macro_data_vintage    版次表（同键多版共存，ORDER BY 含 vintage）
    c1_market.macro_data_latest     视图：每键当前可得最优版（替代"读现值"口径）
    c1_market.macro_data_pit        视图：本仓现值表形状（7 列）的 vintage 侧兼容视图，
                                     消费者只需把表名 macro_data 换成 macro_data_pit
    （macro_data_pit_view 参数化 PIT 视图不建：本仓 CH 对含查询参数的视图 DESCRIBE
      返回空列实测 Code 90，PIT 取数统一走本模块 PIT_LATEST_SQL 模板）

用法（入库侧镜像，供 ch_writer 钩子调用）::

    from zephyr.data.macro_vintage import build_vintage_rows, write_vintage_rows  # 落地后路径
    rows, stats = build_vintage_rows(legacy_rows, existing=..., observed_at=now_utc())
    n = write_vintage_rows(rows)

PIT 取数::

    print(PIT_LATEST_SQL.format(as_of="2025-09-09 00:00:00", names="('FRED_CPI_US')"))

自检：``python macro_vintage.py --selftest``
# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/data/macro_vintage.yaml
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Final

from zephyr.data.table_registry import TableRegistry

# ---------------------------------------------------------------- 常量与词表

#: 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）。
#: 版次表/视图全名均由现值表名派生（加后缀拼接，求值文本与改前逐字一致——视图名差一个
#: 后缀即下游建表/查数全错，故只改派生方式不改落库字面）。
_T_MACRO: Final = TableRegistry().table("market_macro_data")
_TABLE_VINTAGE: Final = f"{_T_MACRO}_vintage"
#: 对外公开名（apply/audit 脚本引用，避免各脚本各自拼表名）
TABLE_VINTAGE: Final = _TABLE_VINTAGE
_SENTINEL_EPOCH: Final = "toDateTime64('1970-01-01 00:00:00.000', 3, 'UTC')"

#: 与 legacy c1_market.macro_data 完全同列序的前缀列（兼容层依赖此顺序）
_LEGACY_COLUMNS: Final = [
    "report_date",
    "indicator_name",
    "indicator_value",
    "unit",
    "frequency",
    "data_source",
]
#: vintage 存证增量列（顺序即 INSERT 列序，pub_ts 用 Nullable 承载"发布时戳不可知"）
_VINTAGE_COLUMNS: Final = [
    "vintage",
    "pub_ts",
    "pub_ts_basis",
    "source_series_id",
    "pub_ref",
    "first_seen_ts",
    "ingest_ts",
]
ALL_COLUMNS: Final = [*_LEGACY_COLUMNS, *_VINTAGE_COLUMNS]

_BASIS_OFFICIAL: Final = "official_release"
_BASIS_OBSERVED: Final = "ingest_observed"
_BASIS_BACKFILL: Final = "backfill_final"

#: pub_ts_basis 词表真源（枚举值动态加载，禁在代码里写字面量列表——上一班四次死亡换来的处方）
#: 解析序：①本模块同级 vocab/（工单目录形态）②仓库内工单词表目录（落地 src 后的回退）。
VOCAB_FILENAME: Final = "metaq_macro_pub_ts_basis_vocabulary.yaml"


def _resolve_vocab_dir() -> Path:
    here = Path(__file__).resolve().parent / "vocab"
    if (here / VOCAB_FILENAME).exists():
        return here
    for parents in Path(__file__).resolve().parents:
        cand = parents / "scripts" / "governance" / "meta_question" / "wo_b3_macro" / "vocab"
        if (cand / VOCAB_FILENAME).exists():
            return cand
    return here  # 均缺失→交由 load_vocabulary_values(strict=True) fail-closed 抛错


VOCAB_DIR: Final = _resolve_vocab_dir()
VOCAB_FILE: Final = VOCAB_FILENAME

_DDL_VINTAGE: Final = f"""
CREATE TABLE IF NOT EXISTS {_TABLE_VINTAGE}
(
    report_date        Date,
    indicator_name     String,
    indicator_value    Decimal(18, 4),
    unit               String,
    frequency          String,
    data_source        LowCardinality(String)  DEFAULT 'akshare',
    vintage            UInt32                  DEFAULT 1,
    pub_ts             Nullable(DateTime64(3, 'UTC')),
    pub_ts_basis       LowCardinality(String)  DEFAULT '{_BASIS_OBSERVED}',
    source_series_id   String                  DEFAULT '',
    pub_ref            String                  DEFAULT '',
    first_seen_ts      DateTime64(3, 'UTC')    DEFAULT now(),
    ingest_ts          DateTime64(3, 'UTC')    DEFAULT now(),
    CONSTRAINT vintage_positive CHECK (vintage >= 1)
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(report_date)
ORDER BY (indicator_name, report_date, vintage)
"""

#: 每键"当前可得最优版"——发布时戳优先，无发布时戳者回退哨兵时刻（版次作同刻定序键）。
#: 内层预计算 ord/vintage_num：规避 CH 分析器"聚合别名自引用"（Code 184）。
_DDL_VIEW_LATEST: Final = f"""
CREATE OR REPLACE VIEW {_T_MACRO}_latest AS
SELECT
    indicator_name,
    report_date,
    argMax(indicator_value, ord) AS indicator_value,
    argMax(unit,            ord) AS unit,
    argMax(frequency,       ord) AS frequency,
    argMax(data_source,     ord) AS data_source,
    argMax(vintage_num,     ord) AS vintage,
    max(ord_ts)                  AS pub_ts_known,
    argMax(pub_ts_basis,    ord) AS pub_ts_basis,
    max(ingest_ts)               AS ingest_ts
FROM (
    SELECT indicator_name, report_date, indicator_value, unit, frequency, data_source,
           pub_ts_basis, ingest_ts,
           vintage AS vintage_num,
           if(isNull(pub_ts), {_SENTINEL_EPOCH}, pub_ts) AS ord_ts,
           tuple(if(isNull(pub_ts), {_SENTINEL_EPOCH}, pub_ts), vintage) AS ord
    FROM {_TABLE_VINTAGE}
)
GROUP BY indicator_name, report_date
"""

#: 兼容层：与 legacy macro_data 同形状（7 列），消费方只换表名即可改读 vintage 侧
_DDL_VIEW_COMPAT: Final = f"""
CREATE OR REPLACE VIEW {_T_MACRO}_compat AS
SELECT report_date, indicator_name, indicator_value, unit, frequency, data_source, ingest_ts
FROM {_T_MACRO}_latest
"""

#: PIT 参数化视图实测不可用（本仓 CH 版本对含查询参数的视图 DESCRIBE 返回空列 → Code 90，
#: 实证录于 wo_b3 波次），故不建视图；PIT 通路只保留 PIT_LATEST_SQL + pit_latest()。
#: DDL 清单放一条清理语句，幂等删除历史遗留的空视图，防"看着存在、实则不可查"的假载体。
_DDL_DROP_PIT_VIEW: Final = f"DROP VIEW IF EXISTS {_T_MACRO}_pit_view"

#: PIT 取数 SQL 模板（Python 侧参数化，视图不可用时的等价通路；判据=as_of 之前发布、同键取最新）
PIT_LATEST_SQL: Final = (
    f"SELECT indicator_name, report_date,"
    f" argMax(indicator_value, ord) AS indicator_value,"
    f" max(pub_ts) AS pub_ts, argMax(vintage_num, ord) AS vintage,"
    f" argMax(pub_ts_basis, ord) AS pub_ts_basis "
    f"FROM (SELECT indicator_name, report_date, indicator_value, pub_ts, pub_ts_basis,"
    f" vintage AS vintage_num, tuple(pub_ts, vintage) AS ord "
    f" FROM {_TABLE_VINTAGE} WHERE pub_ts <= '{{as_of}}'{{names_clause}}) "
    f"GROUP BY indicator_name, report_date"
)

#: 部署语句清单（apply/verify 脚本消费；顺序敏感=先表后视图）
DDL_STATEMENTS: Final = (
    ("vintage 表", _DDL_VINTAGE),
    ("现值优先视图 macro_data_latest", _DDL_VIEW_LATEST),
    ("兼容视图 macro_data_compat（legacy 7 列形状）", _DDL_VIEW_COMPAT),
    ("清理不可用参数化 PIT 视图（实测 Code 90）", _DDL_DROP_PIT_VIEW),
)

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。列清单由 ALL_COLUMNS 常量派生（静态）；目标表为
# 运行期入参（sandbox 与生产共用列序），故只集中前缀/后缀，动态表名由 insert_sql 拼装。
# 注：SQL 常量用普通赋值（非 : Final）——NO-BARE-SQL 豁免仅识别 ast.Assign 的 _?SQL_ 常量。
_SQL_INSERT_PREFIX = "INSERT INTO "
_SQL_INSERT_SUFFIX = f" ({', '.join(ALL_COLUMNS)}) VALUES"


def load_pub_ts_basis_values() -> frozenset[str]:
    """动态加载 pub_ts_basis 合法值（词表 SSoT）。空集=fail-closed 抛错。"""
    from zephyr.shared.io.yaml_utils import load_vocabulary_values

    values = load_vocabulary_values(VOCAB_FILE, vocab_dir=VOCAB_DIR)
    if not values:
        msg = f"pub_ts_basis 词表为空或缺失: {VOCAB_DIR / VOCAB_FILE}"
        raise ValueError(msg)
    return frozenset(values)


# ---------------------------------------------------------------- 版次推导（纯函数，零 DB 可测）


def _to_decimal_str(value: Any) -> str:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    """Decimal(18,4) 比较归一：4 位小数字符串，避免 float 尾噪误判"发生修订"。"""
    return f"{float(value):.4f}"


def _date_str(report_date: Any) -> str:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    if isinstance(report_date, datetime.date):
        return report_date.isoformat()
    return str(report_date)[:10]


def _date_obj(report_date: Any) -> datetime.date:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    """Date 列写入口径：clickhouse-driver 原生批量插入需 datetime.date（str 报 AttributeError）。"""
    if isinstance(report_date, datetime.datetime):
        return report_date.date()
    if isinstance(report_date, datetime.date):
        return report_date
    return datetime.date.fromisoformat(str(report_date)[:10])


def _ts(value: Any) -> datetime.datetime | None:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=datetime.UTC)


def resolve_vintages(
    legacy_rows: Sequence[Sequence[Any]],
    existing: dict[tuple[str, str], dict[str, Any]],
    source_series_id: str = "",
    pub_ts: Any = None,  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    pub_ts_basis: str | None = None,
    pub_ref: str = "",
    observed_at: datetime.datetime | None = None,
) -> tuple[list[tuple], dict[str, int]]:
    """把 legacy 形状行（macro_data 7 列序）升格为 vintage 存证行。

    Args:
        legacy_rows: [(report_date, indicator_name, indicator_value, unit, frequency, data_source), ...]
                     允许带第 7/8 个可选位=pub_ts / pub_ts_basis（provider 若已握官方发布日历则直接带上）
        existing:    {(indicator_name, report_date_iso): {"max_vintage": int, "values": [Decimal,...]}}
                     —— 库内现存态（无记录则键缺席）
        observed_at: 本次观测时点（ingest_observed 口径的 pub_ts；None 则回落 datetime.datetime.now(UTC)）
        pub_ts/pub_ts_basis: 批级默认（provider 侧带值时逐行值优先）

    Returns:
        (rows_for_vintage_table, stats)；stats 键 new_key/unchanged_skip/revised/unknown_basis。

    判定口径（可复核，无随机）：
      ①库内无此键 → vintage=1（新版次=初值）；
      ②库内有此键且本值 ∈ 现存值集 → 不新增行（同版重放幂等，仅由 first_seen_ts 保旧）；
      ③库内有此键且本值 ∉ 现存值集 → vintage=max+1（真实修订，旧值不覆写=存证成立）；
      ④同批内重复键按首次出现处理，后到者走 ②③ 同规则（批内递增）。
    """
    known_basis = load_pub_ts_basis_values()
    if pub_ts_basis is not None and pub_ts_basis not in known_basis:
        msg = f"未知 pub_ts_basis={pub_ts_basis!r}（词表真源 {VOCAB_DIR / VOCAB_FILE}）"
        raise ValueError(msg)
    observed = observed_at or datetime.datetime.now(
        datetime.UTC
    )  # 仅探针兜底：显式 UTC（非 naive），生成器批走显式 observed_at
    out: list[tuple] = []
    stats = {"new_key": 0, "unchanged_skip": 0, "revised": 0, "unknown_basis": 0, "skipped_no_value": 0}
    seen: dict[tuple[str, str], dict[str, Any]] = {}  # 批内增量态（防同批重复键互相看不见）

    for row in legacy_rows:
        if len(row) < 6:
            msg = f"行形状不足 legacy 6 列，拒绝猜测: {row!r}"
            raise ValueError(msg)
        report_date, indicator_name, value, unit, frequency, data_source = row[:6]
        row_pub_ts = _ts(row[6]) if len(row) > 6 else None
        row_basis = str(row[7]) if len(row) > 7 and row[7] else None
        key = (str(indicator_name), _date_str(report_date))
        state = existing.get(key) or seen.get(key)
        max_v = int(state["max_vintage"]) if state else 0
        known_vals = {_to_decimal_str(v) for v in (state or {}).get("values", []) if v is not None}

        if value is None:
            stats["skipped_no_value"] += 1
            continue

        if known_vals and _to_decimal_str(value) in known_vals:
            stats["unchanged_skip"] += 1  # ②同值重放：不制造伪版次
            continue

        if max_v == 0:
            vintage = 1
            stats["new_key"] += 1
        else:
            vintage = max_v + 1
            stats["revised"] += 1

        eff_ts = row_pub_ts or _ts(pub_ts)
        eff_basis = row_basis or pub_ts_basis
        if eff_basis is None:
            eff_basis = _BASIS_OFFICIAL if eff_ts is not None else _BASIS_OBSERVED
            eff_ts = eff_ts or observed
        if eff_basis not in known_basis:
            stats["unknown_basis"] += 1
            msg = f"未知 pub_ts_basis={eff_basis!r}（indicator={indicator_name}）"
            raise ValueError(msg)
        if eff_basis == _BASIS_BACKFILL:
            eff_ts = None  # 铁律：回补终值永不含发布时戳（历史不可回补，不许伪造）
        elif eff_ts is None:
            eff_ts = observed
            eff_basis = _BASIS_OBSERVED

        out.append(
            (
                _date_obj(report_date),
                str(indicator_name),
                float(value),
                str(unit),
                str(frequency),
                str(data_source),
                vintage,
                eff_ts,
                eff_basis,
                source_series_id or "",
                pub_ref,
                observed,
                observed,
            )
        )
        seen[key] = {"max_vintage": vintage, "values": [*known_vals, _to_decimal_str(value)]}
    return out, stats


def build_vintage_rows(
    legacy_rows: Sequence[Sequence[Any]],
    *,
    source_series_ids: Iterable[str] = (),
    pub_ts: Any = None,  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    pub_ts_basis: str | None = None,
    pub_ref: str = "",
    observed_at: datetime.datetime | None = None,
) -> tuple[list[tuple], dict[str, int]]:
    """写库入口便捷包装：自行探针库内现存态后推导版次（ch_writer 钩子的调用面）。"""
    existing = fetch_existing_state(legacy_rows)
    series = next(iter(source_series_ids), "") if source_series_ids else ""
    return resolve_vintages(
        legacy_rows,
        existing,
        source_series_id=series,
        pub_ts=pub_ts,
        pub_ts_basis=pub_ts_basis,
        pub_ref=pub_ref,
        observed_at=observed_at,
    )


def fetch_existing_state(legacy_rows: Sequence[Sequence[Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """探针 vintage 表内现存 (indicator, report_date) 的最大版次与值集（只读，经 DatabaseService）。"""
    names = sorted({str(r[1]) for r in legacy_rows if len(r) > 1})
    dates = sorted({_date_str(r[0]) for r in legacy_rows})
    if not names or not dates:
        return {}
    from zephyr.infrastructure.database_service import DatabaseService

    sql = (
        f"SELECT indicator_name, report_date, max(vintage), groupArray(indicator_value) "
        f"FROM {_TABLE_VINTAGE} WHERE indicator_name IN ({_q_list(names)}) "
        f"AND report_date IN ({_q_list(dates, quote=True)}) "
        f"GROUP BY indicator_name, report_date"
    )
    ch = DatabaseService().get_clickhouse_conn(role="reader")
    try:
        rows = ch.execute(sql)
    finally:
        ch.disconnect()
    return {(str(n), _date_str(d)): {"max_vintage": int(mv), "values": list(vals)} for n, d, mv, vals in rows}


def _q_list(values: Sequence[str], *, quote: bool = True) -> str:
    """渲染 SQL 值清单（值来源=本函数入参的行内值，非用户输入；单引号转义防注入）。"""
    if quote:
        return ", ".join("'" + str(v).replace("'", "''") + "'" for v in values)
    return ", ".join(str(v) for v in values)


def insert_sql(table: str = _TABLE_VINTAGE) -> str:
    """列序真源渲染 INSERT 模板（sandbox 目标表与生产表共用同一列序）。"""
    return _SQL_INSERT_PREFIX + table + _SQL_INSERT_SUFFIX


_INSERT_BATCH: Final = 5000


def write_vintage_rows(rows: Sequence[Sequence[Any]], *, table: str = _TABLE_VINTAGE) -> int:
    """strict 写通道落库（禁裸 duckdb/裸 HTTP；连接归一 ch_writer）。返回写入行数。"""
    if not rows:
        return 0
    from zephyr.data import ch_writer

    client = ch_writer.get_client_strict()
    try:
        stmt = insert_sql(table)
        for i in range(0, len(rows), _INSERT_BATCH):
            client.execute(stmt, list(rows[i : i + _INSERT_BATCH]), types_check=False)
    finally:
        client.disconnect()
    return len(rows)


# ---------------------------------------------------------------- 镜像钩子（ch_writer 补丁调用面）

_MACRO_TABLE_RE = re.compile(r"\bmacro_data\b")


def is_macro_mirror_target(table: str) -> bool:
    """判定是否 macro_data 镜像目标（现值表名精确匹配，视图/自身表不回灌）。"""
    return str(table).strip().rstrip(";") == _T_MACRO


def mirror_from_legacy_rows(
    legacy_rows: Sequence[Sequence[Any]],
    *,
    source_series_id: str = "",
    observed_at: datetime.datetime | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """入库侧镜像：legacy 行 → vintage 行（含版次推导）→ 落库。异常不抛出，返回留痕字典。"""
    try:
        rows, stats = build_vintage_rows(
            legacy_rows,
            source_series_ids=(source_series_id,) if source_series_id else (),
            observed_at=observed_at,
        )
        written = 0 if dry_run else write_vintage_rows(rows)
        return {"ok": True, "written": written, "stats": stats, "error": ""}
    except Exception as exc:  # noqa: BLE001 — 镜像失败绝不可阻断主写入（存证旁路 fail-visible 于日志/审计）
        return {"ok": False, "written": 0, "stats": {}, "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------- 历史存量登记（不可回补→如实登记）


def build_backfill_rows(
    legacy_rows: Sequence[Sequence[Any]],
    *,
    registered_at: datetime.datetime | None = None,
) -> list[tuple]:
    """历史存量 → vintage 表登记行：vintage=1、pub_ts=NULL、basis=backfill_final（零伪造）。

    入参行形状 = legacy 6 列 + 可选第 7 位=现值表 ingest_ts（真实采集时戳，作 first_seen_ts）
    + 可选第 8 位=source_series_id。first_seen_ts/ingest_ts 非 Nullable，缺第 7 位时回落
    registered_at（本次登记时点，由调用方经 now_utc() 供给，本模块不自取时钟）。
    """
    known = load_pub_ts_basis_values()
    if _BASIS_BACKFILL not in known:
        msg = f"词表缺 {_BASIS_BACKFILL}（历史回补无发布时戳的如实登记口径）"
        raise ValueError(msg)
    out: list[tuple] = []
    for row in legacy_rows:
        report_date, indicator_name, value, unit, frequency, data_source = row[:6]
        seen_ts = _ts(row[6]) if len(row) > 6 else None
        series_id = str(row[7]) if len(row) > 7 and row[7] else ""
        stamp = seen_ts or _ts(registered_at)
        if stamp is None:
            msg = f"缺现值采集时戳且未传 registered_at，拒绝猜测时戳：{indicator_name}/{report_date}"
            raise ValueError(msg)
        out.append(
            (
                _date_obj(report_date),
                str(indicator_name),
                None if value is None else float(value),
                str(unit),
                str(frequency),
                str(data_source),
                1,
                None,
                _BASIS_BACKFILL,
                series_id,
                "backfill_final: 2026-08 一次性回补终值，发布时戳不可回补（WO-B3 如实登记）",
                stamp,
                stamp,
            )
        )
    return out


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。data_source 值清单（quoted）为运行期入参由
# inventory_sql 传入，故只集中静态前缀/后缀；现值表/版次表名走派生常量。
_SQL_INVENTORY_PREFIX = (
    "SELECT report_date, indicator_name, indicator_value, unit, frequency, data_source, "
    f"ingest_ts, '' FROM {_T_MACRO} FINAL WHERE data_source IN ("
)
_SQL_INVENTORY_SUFFIX = (
    ") AND (indicator_name, report_date) NOT IN "
    f"(SELECT indicator_name, report_date FROM {_TABLE_VINTAGE}) "
    "ORDER BY indicator_name, report_date"
)


def inventory_sql(sources: Sequence[str]) -> str:
    """从现值表取存量行（含真实 ingest_ts；vintage 表已有键自动排除→重放幂等不造伪版次）。"""
    quoted = ", ".join("'" + str(s).replace("'", "''") + "'" for s in sources)
    return _SQL_INVENTORY_PREFIX + quoted + _SQL_INVENTORY_SUFFIX


# ---------------------------------------------------------------- 自检


def _selftest() -> int:
    """零 DB 版次推导自检（四情形 + 回补零伪造）。"""
    existing: dict[tuple[str, str], dict[str, Any]] = {
        ("FRED_CPI_US", "2025-06-01"): {"max_vintage": 1, "values": [318.0]},
        ("EIA_CRUDE_INVENTORY", "2025-06-06"): {"max_vintage": 3, "values": [420000.0, 421500.0, 422000.0]},
    }
    rows = [
        ("2025-06-01", "FRED_CPI_US", 318.0, "指数", "monthly", "fred"),  # 同值重放 → 跳过
        ("2025-06-01", "FRED_CPI_US", 318.2, "指数", "monthly", "fred"),  # 真修订 → vintage=2
        ("2025-06-06", "EIA_CRUDE_INVENTORY", 423000.0, "千桶", "weekly", "eia"),  # 修订 → vintage=4
        ("2024-01-01", "FRED_UNRATE_US", 4.0, "百分比", "monthly", "fred"),  # 新键 → vintage=1
        ("2024-01-01", "FRED_UNRATE_US", 4.0, "百分比", "monthly", "fred"),  # 批内重复 → 跳过
    ]
    observed = datetime.datetime(2026, 9, 24, 3, 0, 0, tzinfo=datetime.UTC)
    out, stats = resolve_vintages(
        rows,
        existing,
        source_series_id="CPIAUCSL",
        observed_at=observed,
    )
    checks = {
        "同值重放跳过": stats["unchanged_skip"] == 2,
        "真修订版次": [r[6] for r in out] == [2, 4, 1],
        "新键版次从1起": stats["new_key"] == 1,
        "PIT 保守上界": all(r[7] == observed for r in out),
        "未知 basis 拒收": _raises_unknown_basis(),
        "回补零伪造": all(
            r[7] is None and r[8] == _BASIS_BACKFILL and r[11] == observed
            for r in build_backfill_rows(rows, registered_at=observed)
        ),
        "回补缺时戳拒猜": _raises_no_stamp(rows),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=1))
    return 0 if all(checks.values()) else 1


def _raises_unknown_basis() -> bool:
    try:
        resolve_vintages(
            [("2025-06-01", "X", 1.0, "u", "monthly", "fred")],
            {},
            pub_ts_basis="oracle_says",  # type: ignore[arg-type]
        )
    except ValueError:
        return True
    return False


def _raises_no_stamp(rows: Sequence[Sequence[Any]]) -> bool:
    """无现值采集时戳且未供给登记时点→拒猜（fail-closed，禁编造时戳）。
    # #
    # # 边:
    # # I1 -.->|断点| F1
    # # I2 -.->|断点| F1
    # # I3 -.->|断点| F1
    # # I4 -.->|断点| F1
    # # F1 --> A1
    # # A1 --> O1
    # [/ALGO_FLOW]
    """
    try:
        build_backfill_rows(rows)
    except ValueError:
        return True
    return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="macro_vintage 自检/工具面")
    parser.add_argument("--selftest", action="store_true", help="零 DB 版次推导自检")
    parser.add_argument("--print-ddl", action="store_true", help="打印 vintage DDL/视图（供 DDL-as-Code 挂接）")
    parser.add_argument("--pit-sql", metavar="AS_OF", help="打印指定 as_of 的 PIT 取数 SQL")
    args = parser.parse_args(argv)
    if args.print_ddl:
        print(_DDL_VINTAGE)
        print(_DDL_VIEW_LATEST)
        print(_DDL_VIEW_COMPAT)
        print(_DDL_DROP_PIT_VIEW)
        return 0
    if args.pit_sql:
        print(PIT_LATEST_SQL.format(as_of=args.pit_sql, names_clause=""))
        return 0
    return _selftest()


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免 自检CLI按需点火，非常驻daemon不自动触发
    raise SystemExit(main())
