# [BLUEPRINT] MOD-ALT-EMOTION-INDEX-BUILDER | docs/_working/emotion_line/history_replay_report_v1.md
# [MODULE] zephyr.alt_data.emotion_index_replay
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] stdlib; zephyr.alt_data.emotion_index_builder（冻结公式唯一真源，本模块零公式复制）;
#                zephyr.data.ch_reader（宽窗原料抓取）; zephyr.data.ch_writer（strict 写通道）; zephyr.data.table_registry
# [CONSUMERS] 手工回放 CLI（python -m zephyr.alt_data.emotion_index_replay）；GPU 情绪条件包/D2 重考/t0 E4 重跑取数
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 回放=冻结公式纯求值：本模块不改/不复制任何成分公式，逐日调用
#              emotion_index_builder.build_emotion_index 原函数（切片缓存 reader 注入），
#              位级同构由形状等价自证+10 天活值对拍保证；切片法只对纯 GROUP BY 聚合形状合法
#              （JOIN 形状含窗界伪影→白名单外一律真查询直通）；回放行只写活管道不存在的
#              (trade_date, close_final) 键（ReplacingMergeTree ORDER BY 不含 source，撞键
#              会覆盖活行=禁）；source='replay' 行级标记防混，活管道 INSERT_COLUMNS 契约
#              （6 列）零变更零打扰；写通道=ch_writer strict 单写通道（cohort_daily_writer
#              同款），禁双写禁先删；表名经 TableRegistry 派生（禁硬编码）。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 宽窗抓取空/形状等价自证失败/写库失败→fail-visible 抛出（回放是一次性
#                  批作业，静默降级=假绿，禁）；单日 build 返回 None→如实跳过计入 skipped。
# [TESTS] tests/alt_data/test_emotion_index_replay.py
# [A_module] module_id=MOD-ALT-EMOTION-INDEX-REPLAY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""emotion_index_replay — emotion_index 全历史回放驱动（冻结公式纯求值 + 同表落库）.

把 emotion_index 从"逐日攒"改为"全历史回放"（st-emoreplay-20260923 总包）：逐日调用
冻结版 build_emotion_index，数据面用切片缓存 reader——每形状只对 CH 跑一次全史宽窗查询
（同一条 _SQL_* 常量仅替换 BETWEEN 界），此后逐日从宽窗结果按 [start, day] 切片回 TSV，
builder 拿到的字节与真窄窗查询逐位一致（纯 GROUP BY 形状可证；JOIN 形状白名单外直通
真查询）。

落表：c1_market.emotion_index 同表同形态，回放行 source='replay'；只写活管道不存在的键
（撞键禁写——ORDER BY (trade_date, stage) 不含 source，ReplacingMergeTree 会覆盖活行）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 六形状宽窗原料一次抓取（切片缓存）+ JOIN 形状真查询直通
# 层: 算法
# - id: A1
#   name_zh: 逐日冻结公式纯求值（build_emotion_index 原函数，reader 注入）
# - id: A2
#   name_zh: 形状等价自证（真窄窗 vs 切片回放逐字节比对）+10 天活值对拍
# 层: 输出
# - id: O1
#   name: source='replay' 行经 strict 写通道落 c1_market.emotion_index（只写非撞键行）
"""

from __future__ import annotations

import bisect
import datetime
import json
import logging
import re
from typing import Any

from zephyr.alt_data.emotion_index_builder import (
    _SQL_AD_DAILY,
    _SQL_INDEX_CLOSE,
    _SQL_LIMITUP_DAILY,
    _SQL_MARGIN_BAL,
    _SQL_NEWS_MEAN,
    _TBL_KLINE_DAILY,
    STAGE_CLOSE_FINAL,
    build_emotion_index,
)
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: list[str] = [
    "ReplaySliceReader",
    "replay_history",
    "write_replay_rows",
    "verify_slice_equivalence",
    "pit_live_value_check",
    "partition_chunks",
    "REPLAY_SOURCE",
    "GLOBAL_START",
]

REPLAY_SOURCE = "replay"
GLOBAL_START = "1980-01-01"  # 宽窗抓取下界（早于一切 _window_start 回拉）
# 表 PARTITION BY toYYYYMM：单 INSERT 块跨分区数受 CH max_partitions_per_insert_block(=100)
# 限制，全历史一次插必炸（Code 252 实证）——按分区聚块，每块 ≤90 个月分区留裕度。
_MAX_PARTITIONS_PER_BLOCK = 90

# NO-BARE-SQL：_SQL_* 常量（切片白名单键 = builder 形状指纹，输出列别名唯一）
_SQL_LIVE_KEYS = "SELECT DISTINCT trade_date FROM {tbl} FINAL WHERE stage = '{stage}'"
_SQL_INSERT = "INSERT INTO {table} {cols} VALUES"

_BETWEEN_RE = re.compile(r"BETWEEN '(\d{4}-\d{2}-\d{2})' AND '(\d{4}-\d{2}-\d{2})'")

# 切片安全形状白名单（纯 GROUP BY / 纯行选，窗口界无关每行值）。
# 不在白名单的形状（PROMOTION 自 JOIN / AUCTION 跨窗 JOIN 等）→ 真查询直通+按 (start,day) 缓存。
_SLICE_SAFE_MARKERS = (
    "AS max_consec",  # _SQL_LIMITUP_DAILY
    "AS med_turn",  # _SQL_AD_DAILY
    "AS bal",  # _SQL_MARGIN_BAL
    "scope = 'market'",  # _SQL_NEWS_MEAN（行选，无 AS 别名）
    "symbol = '000300'",  # _SQL_INDEX_CLOSE
)


def _today() -> str:
    return datetime.date.today().isoformat()


def _window_bounds_sql(sql: str, start: str, day: str) -> str:
    return _BETWEEN_RE.sub(lambda m: f"BETWEEN '{start}' AND '{day}'", sql, count=1)


class ReplaySliceReader:
    """切片缓存 reader：结构性满足 builder._Reader 协议（query(sql)->tsv str）。

    首见形状→经 source_reader 抓全史宽窗缓存（同条 SQL 仅换 BETWEEN 界，聚合语义
    由 CH 原样执行=零重实现）；后续按 [start, day] 二分切片回 TSV（ISO 日期字典序
    =时间序，行字节原样保留）。白名单外形状→真查询直通（缓存按 (start, day)）。
    """

    def __init__(self, source_reader: Any) -> None:  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
        self._src = source_reader
        self._wide: dict[str, tuple[list[str], list[str]]] = {}
        self._real_cache: dict[tuple[str, str, str], str] = {}
        self.stats = {"wide_fetch": 0, "slice_hit": 0, "real_query": 0, "real_cache_hit": 0}

    def _shape_key(self, sql: str) -> str | None:
        m = _BETWEEN_RE.search(sql)
        if not m:
            return None
        return sql[: m.start()] + sql[m.end() :]

    def _is_slice_safe(self, sql: str) -> bool:
        return any(marker in sql for marker in _SLICE_SAFE_MARKERS)

    def _ensure_wide(self, key: str, sql: str) -> tuple[list[str], list[str]]:
        if key in self._wide:
            return self._wide[key]
        wide_sql = _window_bounds_sql(sql, GLOBAL_START, _today())
        tsv = self._src.query(wide_sql)
        if tsv is None or not tsv.strip():
            raise RuntimeError(f"replay 宽窗抓取为空（ch 静默失败假绿防线）: {wide_sql[:160]}")
        dates: list[str] = []
        lines: list[str] = []
        for line in tsv.splitlines():
            if not line.strip():
                continue
            d = line.split("\t", 1)[0]
            dates.append(d)
            lines.append(line)
        self._wide[key] = (dates, lines)
        self.stats["wide_fetch"] += 1
        return self._wide[key]

    def wide_dates(self, sql: str) -> list[str]:
        """取某形状宽窗日期序列（供回放日历枚举；附带给该形状预热缓存）。"""
        key = self._shape_key(sql)
        if key is None:
            raise ValueError("wide_dates 需要 BETWEEN 界形状")
        return self._ensure_wide(key, sql)[0]

    def query(self, sql: str) -> str:
        m = _BETWEEN_RE.search(sql)
        if m is None:
            return self._src.query(sql)
        start, day = m.group(1), m.group(2)
        key = self._shape_key(sql) or ""
        if self._is_slice_safe(sql):
            dates, lines = self._ensure_wide(key, sql)
            lo = bisect.bisect_left(dates, start)
            hi = bisect.bisect_right(dates, day)
            self.stats["slice_hit"] += 1
            # 尾换行复刻 CH TSV 制表符输出（真窄窗查询以 "\n" 结尾）——逐字节同构，
            # 免等价自证因表示层差异假红。
            return "\n".join(lines[lo:hi]) + "\n" if hi > lo else ""
        ck = (key, start, day)
        if ck in self._real_cache:
            self.stats["real_cache_hit"] += 1
            return self._real_cache[ck]
        self.stats["real_query"] += 1
        out = self._src.query(sql)
        self._real_cache[ck] = out if out is not None else ""
        return self._real_cache[ck]


def replay_trade_days(reader: ReplaySliceReader, start: str, end: str) -> list[str]:
    """回放日历=kline_daily 逐日聚合日期（C3/C4 基座真源），[start, end] 内升序。"""
    sql = _SQL_AD_DAILY.format(tbl=_TBL_KLINE_DAILY, start=GLOBAL_START, day=_today())
    dates = reader.wide_dates(sql)
    lo = bisect.bisect_left(dates, start)
    hi = bisect.bisect_right(dates, end)
    return dates[lo:hi]


def replay_history(start: str, end: str, source_reader: Any | None = None) -> dict[str, Any]:  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
    """逐日冻结公式纯求值（close_final），返回 {"rows", "skipped", "days", "reader_stats"}。

    数据面=ReplaySliceReader 注入 build_emotion_index 原函数；全成分不可产日（builder
    返回 None）如实跳过。start/end 为 ISO 日期闭区间。
    """
    from zephyr.data import ch_reader as _default_reader

    src = source_reader if source_reader is not None else _default_reader
    r = ReplaySliceReader(src)
    days = replay_trade_days(r, start, end)
    rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    for d in days:
        row = build_emotion_index(d, stage=STAGE_CLOSE_FINAL, reader=r)
        if row is None:
            skipped.append(d)
            continue
        rows.append(row)
    return {
        "rows": rows,
        "skipped": skipped,
        "days": days,
        "reader_stats": dict(r.stats),
        "reader": r,
    }


def _replay_insert_columns() -> str:
    """回放 INSERT 列序=活管道 INSERT_COLUMNS 契约 + source 标记列（活插列零变更）。"""
    from schemas.categories.market.market_emotion_index import INSERT_COLUMNS

    return INSERT_COLUMNS.rstrip(")").rstrip() + ", source)"


def _live_close_final_keys(source_reader: Any) -> set[str]:  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
    """活管道已落 (trade_date, close_final) 键集合——撞键禁写防 FINAL 覆盖活行。"""
    tbl = get_registry().table("market_emotion_index")
    tsv = source_reader.query(_SQL_LIVE_KEYS.format(tbl=tbl, stage=STAGE_CLOSE_FINAL))
    if tsv is None:
        raise RuntimeError("活键查询返回 None（ch 静默失败假绿防线）")
    return {line.strip() for line in tsv.splitlines() if line.strip()}


def _partition_of(d: datetime.date | str) -> int:
    """行所属分区号（表 PARTITION BY toYYYYMM 的镜像口径）。"""
    if isinstance(d, str):
        d = datetime.date.fromisoformat(d)
    return d.year * 100 + d.month


def partition_chunks(data: list[tuple]) -> list[list[tuple]]:
    """按分区号聚块（输入须已按分区排序）；每块 distinct 分区数 ≤ 上限。"""
    blocks: list[list[tuple]] = []
    cur: list[tuple] = []
    seen: set[int] = set()
    for row in data:
        p = _partition_of(row[0])
        if p not in seen and len(seen) >= _MAX_PARTITIONS_PER_BLOCK:
            blocks.append(cur)
            cur, seen = [], set()
        cur.append(row)
        seen.add(p)
    if cur:
        blocks.append(cur)
    return blocks


def write_replay_rows(
    rows: list[dict[str, Any]],
    source_reader: Any | None = None,  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
    client: Any | None = None,  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
) -> dict[str, Any]:
    """回放行落 c1_market.emotion_index（source='replay'，只写非撞键行，strict 通道）。

    返回 {"written", "skipped_live_keys", "trade_dates"}；写库失败 fail-visible 抛出。
    """
    from zephyr.data import ch_reader as _default_reader

    src = source_reader if source_reader is not None else _default_reader
    live_keys = _live_close_final_keys(src)
    tbl = get_registry().table("market_emotion_index")
    cols = _replay_insert_columns()
    data: list[tuple] = []
    skipped_live = 0
    for row in rows:
        d = row["trade_date"]
        d_iso = d.isoformat() if isinstance(d, datetime.date) else str(d)
        if d_iso in live_keys:
            skipped_live += 1
            continue
        data.append(
            (
                d,
                row["stage"],
                row["ts"],
                row["emotion_index"],
                json.dumps(row["components"], ensure_ascii=False),
                row["version"],
                REPLAY_SOURCE,
            )
        )
    if data:
        if client is None:
            from zephyr.data.ch_writer import get_client_strict

            client = get_client_strict()
        sql = _SQL_INSERT.format(table=tbl, cols=cols)
        # 表按 toYYYYMM 分区，CH 默认 max_partitions_per_insert_block=100——全史跨度
        # 数百个月分区，单块必被拒（Code 252）；按月分块顺序写，块内分区数受上限约束。
        data.sort(
            key=lambda r: (_partition_of(r[0]), r[0].isoformat() if isinstance(r[0], datetime.date) else str(r[0]))
        )
        blocks = partition_chunks(data)
        for blk in blocks:
            client.execute(sql, blk)
        log.info("emotion_index 回放分块写入 %d 块（分区上限 %d）", len(blocks), _MAX_PARTITIONS_PER_BLOCK)
    log.info(
        "emotion_index 回放落库 %d 行（撞活键跳过 %d）-> %s source=%s",
        len(data),
        skipped_live,
        tbl,
        REPLAY_SOURCE,
    )
    return {
        "written": len(data),
        "skipped_live_keys": skipped_live,
        "trade_dates": [r[0].isoformat() if isinstance(r[0], datetime.date) else str(r[0]) for r in data],
    }


def verify_slice_equivalence(reader: ReplaySliceReader, days: list[str], source_reader: Any) -> dict[str, Any]:  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
    """形状等价自证：对抽样日逐形状比对"真窄窗查询 vs 切片回放"的 TSV 字节。

    白名单 5 形状逐字节必等（纯 GROUP BY 可证）；白名单外形状（JOIN 族）两边都走
    source_reader 同一路径，比对为恒真占位（真校验=10 天活值对拍）。任一形状不等
    → fail-visible RuntimeError。
    """
    checks: list[dict[str, Any]] = []
    for shape_sql in (
        _SQL_LIMITUP_DAILY.format(
            tbl=get_registry().table("market_daban_board_event"), start=GLOBAL_START, day=_today()
        ),
        _SQL_AD_DAILY.format(tbl=_TBL_KLINE_DAILY, start=GLOBAL_START, day=_today()),
        _SQL_INDEX_CLOSE.format(tbl=get_registry().table("market_index_kline"), start=GLOBAL_START, day=_today()),
        _SQL_MARGIN_BAL.format(tbl=get_registry().table("market_margin_trading"), start=GLOBAL_START, day=_today()),
        _SQL_NEWS_MEAN.format(
            tbl=get_registry().table("market_news_sentiment_window"), start=GLOBAL_START, day=_today()
        ),
    ):
        if not reader._is_slice_safe(shape_sql):
            continue
        for d in days:
            narrow = _window_bounds_sql(
                shape_sql,
                (datetime.date.fromisoformat(d) - datetime.timedelta(days=590)).isoformat(),
                d,
            )
            real = source_reader.query(narrow)
            sliced = reader.query(narrow)
            ok = (real or "") == (sliced or "")
            checks.append({"day": d, "shape": shape_sql[:60], "equal": ok})
            if not ok:
                raise RuntimeError(
                    f"形状等价自证失败 day={d} shape={shape_sql[:80]}——切片回放与真查询字节不一致，禁落库"
                )
    return {"checked": len(checks), "all_equal": True, "detail": checks}


def pit_live_value_check(
    start: str,
    end: str,
    sample_days: list[str],
    source_reader: Any | None = None,  # noqa: any-abuse  duck注入缝位:头注DEPENDENCIES明示duck注入,真源型不可硬绑测试假体
) -> dict[str, Any]:
    """10 天活值对拍：回放行 vs 冻结 builder 真数据面逐位比对（重叠窗必须一致）。

    抽样日逐个：replay_history 产行（切片 reader）vs build_emotion_index（真 reader）
    ——emotion_index 浮点与 components JSON 必须逐位相等，否则 fail-visible。
    """
    from zephyr.data import ch_reader as _default_reader

    src = source_reader if source_reader is not None else _default_reader
    rep = replay_history(start, end, source_reader=src)
    by_day = {
        (r["trade_date"].isoformat() if isinstance(r["trade_date"], datetime.date) else str(r["trade_date"])): r
        for r in rep["rows"]
    }
    detail: list[dict[str, Any]] = []
    for d in sample_days:
        live_row = build_emotion_index(d, stage=STAGE_CLOSE_FINAL, reader=src)
        rep_row = by_day.get(d)
        if live_row is None and rep_row is None:
            detail.append({"day": d, "match": True, "note": "both None"})
            continue
        if (live_row is None) != (rep_row is None):
            raise RuntimeError(
                f"PIT 活值对拍失败 day={d}——None 不对称（live={live_row is not None}, replay={rep_row is not None}），禁落库"
            )
        lj = json.dumps(live_row["components"], ensure_ascii=False, sort_keys=True)
        rj = json.dumps(rep_row["components"], ensure_ascii=False, sort_keys=True)
        match = live_row["emotion_index"] == rep_row["emotion_index"] and lj == rj
        detail.append(
            {
                "day": d,
                "match": match,
                "live": live_row["emotion_index"],
                "replay": rep_row["emotion_index"],
                "components_equal": lj == rj,
            }
        )
        if not match:
            raise RuntimeError(f"PIT 活值对拍失败 day={d}——回放非冻结公式纯求值，禁落库")
    return {"sampled": len(sample_days), "all_match": True, "detail": detail}
